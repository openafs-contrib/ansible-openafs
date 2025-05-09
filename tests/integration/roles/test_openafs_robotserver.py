import pytest


@pytest.mark.parametrize(
    "os_name",
    [
        "alma9",
    ],
)
def test_openafs_robotserver(molecule_test, os_name):
    rc = molecule_test(role="openafs_robotserver", scenario="default", os_name=os_name)
    assert rc == 0
