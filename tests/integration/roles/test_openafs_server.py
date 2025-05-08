import pytest


def test_openafs_server_bdist(molecule_test, os_name):
    rc = molecule_test(role="openafs_server", scenario="bdist", os_name=os_name)
    assert rc == 0


@pytest.mark.parametrize(
    "os_name",
    [
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
        "oracle8",
        "oracle9",
        "rocky8",
        "rocky9",
        "ubuntu20",
        "ubuntu22",
    ],
)
def test_openafs_server_managed(molecule_test, os_name):
    rc = molecule_test(role="openafs_server", scenario="managed", os_name=os_name)
    assert rc == 0


@pytest.mark.parametrize(
    "os_name",
    [
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
        "oracle8",
        "oracle9",
        "rocky8",
        "rocky9",
        "ubuntu20",
        "ubuntu22",
    ],
)
def test_openafs_server_packages(molecule_test, os_name):
    rc = molecule_test(role="openafs_server", scenario="packages", os_name=os_name)
    assert rc == 0


@pytest.mark.parametrize(
    "os_name",
    [
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
    ],
)
def test_openafs_server_sdist(molecule_test, os_name):
    rc = molecule_test(role="openafs_server", scenario="sdist", os_name=os_name)
    assert rc == 0


@pytest.mark.parametrize(
    "os_name",
    [
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
    ],
)
def test_openafs_server_source(molecule_test, os_name):
    rc = molecule_test(role="openafs_server", scenario="source", os_name=os_name)
    assert rc == 0
