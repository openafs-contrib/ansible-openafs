import pytest


def test_openafs_common(molecule_test, os_name):
    rc = molecule_test(role="openafs_common", scenario="default", os_name=os_name)
    assert rc == 0
