import pytest


def test_openafs_krbclient(molecule_test, os_name):
    rc = molecule_test(role="openafs_krbclient", scenario="default", os_name=os_name)
    assert rc == 0
