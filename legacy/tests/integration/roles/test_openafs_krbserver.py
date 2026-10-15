import pytest


def test_openafs_krbserver(molecule_test, os_name):
    rc = molecule_test(role="openafs_krbserver", scenario="default", os_name=os_name)
    assert rc == 0
