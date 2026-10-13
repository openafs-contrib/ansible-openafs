import os
import pytest
import subprocess
import pathlib
import sys
import yaml

from release_files import ReleaseFiles

ROOT_PATH = pathlib.Path(__file__).parent.parent
PODMAN_PATH = ROOT_PATH / "extensions" / "molecule" / "resources" / "podman"
CACHE_PATH = pathlib.Path.home() / ".cache" / "ansible-openafs"

# Directory for the molecule output log files and the test summary.
LOG_PATH = pathlib.Path(os.environ.get("AFS_TEST_LOGDIR", ROOT_PATH / ".cache" / "test-logs"))

# Ansible home directory for the molecule tests. Molecule installs the
# collection under test into this directory.
ANSIBLE_HOME_PATH = pathlib.Path(os.environ.get("AFS_TEST_ANSIBLE_HOME", CACHE_PATH / "ansible-home"))

# Scenarios which can not be run in containers, since they load the openafs
# kernel module or install kernel packages. (A role name of None is a
# playbook scenario.)
PODMAN_UNSUPPORTED = [
    ("openafs_client", "*"),
    ("openafs_devel_kernel", "*"),
    (None, "default"),
    (None, "cluster"),
]


def podman_images():
    with open(PODMAN_PATH / "images.yml") as f:
        return yaml.safe_load(f)["afs_podman_base_images"]


def pytest_addoption(parser):
    parser.addoption(
        "--build", metavar="GIT_REF", default=None,
        help="Build OpenAFS from the given git tag or branch to run the "
             "bdist and source scenarios. These scenarios are skipped "
             "unless this option is given.")


@pytest.fixture(
    params=[
        "alma8",
        "alma9",
        "centos6",
        "centos7",
        "centos8",
        "debian10",
        "debian11",
        "debian12",
        "fedora36",
        "fedora37",
        "freebsd12",
        "freebsd13",
        "opensuse15",
        "oracle8",
        "oracle9",
        "rocky8",
        "rocky9",
        "solaris114",
        "ubuntu20",
        "ubuntu22",
    ]
)
def os_name(request):
    return request.param


def show_output(config):
    """Show the command output on the terminal only when the pytest output
    capture is disabled (-s), since the output is saved in the log files."""
    return config.getoption("capture") == "no"


def run_and_log(cmd, cwd, env, logfile, echo=False):
    """Run a command, writing the output to a log file, and to the terminal
    if echo is true."""
    logfile.parent.mkdir(parents=True, exist_ok=True)
    with open(logfile, "w") as log:
        log.write(f"Running: {' '.join(cmd)} in {cwd}\n")
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout:
            if echo:
                sys.stdout.write(line)
            log.write(line)
        return proc.wait()


def molecule_env(os_name):
    env = os.environ.copy()
    # Molecule installs the collection under test into its own cache
    # directory. Do not give molecule a collections path which contains this
    # source tree, since some versions of molecule install the collection
    # under test into the first collections path, which removes the source
    # tree.
    env.pop("ANSIBLE_COLLECTIONS_PATH", None)
    env.pop("ANSIBLE_COLLECTIONS_PATHS", None)
    env["ANSIBLE_HOME"] = str(ANSIBLE_HOME_PATH)
    if os_name:
        env["AFS_TEST_OS"] = os_name
    return env


@pytest.fixture(scope="session")
def release_files():
    return ReleaseFiles()


@pytest.fixture(scope="session")
def bdist_builder(pytestconfig, release_files):
    """Build a binary distribution with the openafs_devel bdist scenario, once
    for each platform and git ref."""
    built = {}

    def _build(os_name, git_ref):
        if (os_name, git_ref) not in built:
            env = molecule_env(os_name)
            env["AFS_GIT_VERSION"] = git_ref
            env["AFS_BUILDS"] = str(release_files.builds)
            env["AFS_BUILD_MODULE"] = "no"  # The kernel module can not be built in a container.
            cmd = ["molecule", "test", "-s", "openafs_devel/bdist"]
            logfile = LOG_PATH / f"openafs_devel-bdist-{os_name}.log"
            print(f"\nBuilding bdist for {os_name} from {git_ref}; log: {logfile}")
            rc = run_and_log(cmd, ROOT_PATH, env, logfile, echo=show_output(pytestconfig))
            if rc != 0:
                pytest.fail(f"Failed to build bdist for {os_name}; see {logfile}")
            archive = release_files.find(os_name, "bdist")
            if not archive:
                pytest.fail(f"bdist archive for {os_name} not found in {release_files.builds}")
            built[(os_name, git_ref)] = archive
        return built[(os_name, git_ref)]

    return _build


@pytest.fixture
def molecule_test(request, release_files, bdist_builder):

    def _run(role=None, scenario="default", os_name=None):

        if (role, "*") in PODMAN_UNSUPPORTED or (role, scenario) in PODMAN_UNSUPPORTED:
            pytest.skip(f"scenario {role or 'playbooks'}/{scenario} is not supported in containers")
        if os_name and os_name not in podman_images():
            pytest.skip(f"no container image for {os_name}")

        env = molecule_env(os_name)

        # The client and server install scenarios need the OpenAFS release
        # files. The sdist and packages files are downloaded, the bdist is
        # built (which is slow), and the source scenario builds from git.
        if role in ("openafs_client", "openafs_server"):
            git_ref = request.config.getoption("--build")
            archive = None
            if scenario in ("bdist", "source") and not git_ref:
                pytest.skip(f"scenario {role}/{scenario} requires the --build option")
            if scenario == "source":
                env["AFS_GIT_VERSION"] = git_ref
            elif scenario == "sdist":
                archive = release_files.sdist()
            elif scenario == "packages":
                archive = release_files.rpms(os_name) or release_files.find(os_name, "debs")
                if not archive:
                    pytest.skip(f"no packages available for {os_name}")
            elif scenario == "bdist":
                archive = bdist_builder(os_name, git_ref)
            if archive:
                env["AFS_INSTALL_ARCHIVE"] = str(archive)

        # The scenarios are located in extensions/molecule/<role>/<scenario>
        # and extensions/molecule/playbooks/<scenario>. Molecule is run from
        # the collection root directory.
        cmd = ["molecule", "test", "-s", f"{role or 'playbooks'}/{scenario}"]
        logfile = LOG_PATH / f"{role or 'playbooks'}-{scenario}-{os_name or 'default'}.log"
        request.node.user_properties.append(("log", str(logfile)))
        print(f"\nRunning: {' '.join(cmd)} [{os_name}]")
        print(f"Log: {logfile}")
        rc = run_and_log(cmd, ROOT_PATH, env, logfile, echo=show_output(request.config))
        return rc

    return _run


# Write a summary of the test results to a file, since the summary printed
# by pytest is easy to lose in the output of a long test run.

_results = []


def pytest_runtest_logreport(report):
    if "integration/" not in report.nodeid:
        return
    if report.when == "call" or (report.when == "setup" and not report.passed):
        log = dict(report.user_properties).get("log", "")
        if report.skipped and isinstance(report.longrepr, tuple):
            detail = report.longrepr[2].removeprefix("Skipped: ")
        elif report.failed:
            detail = log
        else:
            detail = ""
        outcome = "ERROR" if report.failed and report.when == "setup" else report.outcome.upper()
        nodeid = report.nodeid[report.nodeid.find("tests/integration/"):]
        _results.append((outcome, nodeid, detail))


def pytest_sessionfinish(session):
    if not _results:
        return
    LOG_PATH.mkdir(parents=True, exist_ok=True)
    counts = {}
    with open(LOG_PATH / "summary.txt", "w") as f:
        for outcome, nodeid, detail in _results:
            counts[outcome] = counts.get(outcome, 0) + 1
            f.write(f"{outcome:8} {nodeid}" + (f"  ({detail})" if detail else "") + "\n")
        f.write("\n" + ", ".join(f"{n} {o.lower()}" for o, n in sorted(counts.items())) + "\n")
