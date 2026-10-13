import os
import pytest
import subprocess
import pathlib
import yaml

ROOT_PATH = pathlib.Path(__file__).parent.parent
PODMAN_PATH = ROOT_PATH / "extensions" / "molecule" / "resources" / "podman"

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


@pytest.fixture
def molecule_test():

    def _run(role=None, scenario="default", os_name=None):

        if role:
            path = ROOT_PATH / "roles" / role
        else:
            path = ROOT_PATH / "extensions"

        if (role, "*") in PODMAN_UNSUPPORTED or (role, scenario) in PODMAN_UNSUPPORTED:
            pytest.skip(f"scenario {role or 'playbooks'}/{scenario} is not supported in containers")
        if os_name and os_name not in podman_images():
            pytest.skip(f"no container image for {os_name}")

        env = os.environ.copy()
        env["ANSIBLE_COLLECTIONS_PATH"] = str(ROOT_PATH.parent.parent.absolute())
        if os_name:
            env["AFS_TEST_OS"] = os_name

        cmd = ["molecule", "test", "-s", scenario]
        print(f"\nRunning: {' '.join(cmd)} [{os_name}] in {path}")
        rc = subprocess.call(cmd, cwd=path, env=env)
        return rc

    return _run
