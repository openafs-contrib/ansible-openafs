import pytest


def test_openafs_devel(molecule_test, os_name):
    rc = molecule_test(role="openafs_devel", scenario="default", os_name=os_name)
    assert rc == 0
