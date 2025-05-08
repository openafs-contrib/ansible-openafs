import pytest


def test_openafs_client_bdist(molecule_test, os_name):
    rc = molecule_test(role="openafs_client", scenario="bdist", os_name=os_name)
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
def test_openafs_client_managed_dkms(molecule_test, os_name):
    rc = molecule_test(role="openafs_client", scenario="managed-dkms", os_name=os_name)
    assert rc == 0


@pytest.mark.parametrize(
    "os_name",
    [
        "alma8",
        "alma9",
    ],
)
def test_openafs_client_managed_kmod(molecule_test, os_name):
    rc = molecule_test(role="openafs_client", scenario="managed-kmod", os_name=os_name)
    assert rc == 0


@pytest.mark.parametrize(
    "os_name",
    [
        "opensuse15",
    ],
)
def test_openafs_client_managed_kmp(molecule_test, os_name):
    rc = molecule_test(role="openafs_client", scenario="managed-kmp", os_name=os_name)
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
def test_openafs_client_packages_dkms(molecule_test, os_name):
    rc = molecule_test(role="openafs_client", scenario="packages-dkms", os_name=os_name)
    assert rc == 0


@pytest.mark.parametrize(
    "os_name",
    [
        "alma8",
        "alma9",
    ],
)
def test_openafs_client_packages_kmod(molecule_test, os_name):
    rc = molecule_test(role="openafs_client", scenario="packages-kmod", os_name=os_name)
    assert rc == 0


@pytest.mark.parametrize(
    "os_name",
    [
        "opensuse15",
    ],
)
def test_openafs_client_packages_kmp(molecule_test, os_name):
    rc = molecule_test(role="openafs_client", scenario="packages-kmp", os_name=os_name)
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
def test_openafs_client_sdist(molecule_test, os_name):
    rc = molecule_test(role="openafs_client", scenario="sdist", os_name=os_name)
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
def test_openafs_client_source(molecule_test, os_name):
    rc = molecule_test(role="openafs_client", scenario="source", os_name=os_name)
    assert rc == 0
