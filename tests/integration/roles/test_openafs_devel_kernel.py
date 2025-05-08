import pytest


def test_openafs_devel_kernel(molecule_test, os_name):
    rc = molecule_test(role="openafs_devel_kernel", scenario="default", os_name=os_name)
    assert rc == 0
