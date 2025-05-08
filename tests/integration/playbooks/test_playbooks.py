import pytest


def test_deploy_realm_only(molecule_test, os_name):
    rc = molecule_test(scenario="realm", os_name=os_name)
    assert rc == 0


def test_deploy_cell_on_single_machine(molecule_test, os_name):
    rc = molecule_test(scenario="default", os_name=os_name)
    assert rc == 0


def test_deploy_cell_on_cluster(molecule_test, os_name):
    rc = molecule_test(scenario="cluster", os_name=os_name)
    assert rc == 0
