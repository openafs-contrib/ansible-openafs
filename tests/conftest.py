import os
import pytest
import subprocess
import pathlib


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

        root_path = pathlib.Path(__file__).parent.parent
        if role:
            path = root_path / "roles" / role
        else:
            path = root_path / "extensions"

        env = os.environ.copy()
        env["ANSIBLE_COLLECTIONS_PATH"] = root_path.parent.parent.absolute()
        if os_name:
            env["PROXMOX_TEMPLATE_NAME"] = os_name

        print(f"\nRunning: molecule test -s {scenario} [{os_name}] in {path}")
        rc = subprocess.call(["molecule", "test", "-s", scenario], cwd=path, env=env)
        return rc

    return _run
