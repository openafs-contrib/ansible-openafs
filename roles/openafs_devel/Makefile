# Copyright (c) 2019-2021 Sine Nomine Associates

MOLECULE_DRIVER ?= vagrant
MOLECULE_SCENARIO ?= default
MOLECULE_IMAGE ?= generic/centos7
MOLECULE_DESTROY ?= always

.PHONY: help init lint test test-all \
	test-centos-7 test-centos-8 test-debian-10 \
	reset

help:
	@echo "usage: make <target>"
	@echo ""
	@echo "targets:"
	@echo "  lint     run lint checks"
	@echo "  test     run a single molecule scenario"
	@echo "  test-all run a series of molecule scenarios"
	@echo "  reset    reset molecule temporary directories"
	@echo ""
	@echo "environment:"
	@echo "  MOLECULE_DRIVER=<name> (default: vagrant)"

lint:
	yamllint .
	ansible-lint .

scenario:
	AFS_IMAGE=$(MOLECULE_IMAGE) \
	molecule test \
	  --driver-name $(MOLECULE_DRIVER) \
	  --scenario-name $(MOLECULE_SCENARIO) \
	  --destroy $(MOLECULE_DESTROY)


test: test-centos-7 test-centos-8 test-debian-10

test-centos-7:
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s packages-rpms
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s sdist

test-centos-8:
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s packages-rpms
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s sdist

test-debian-10:
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s packages-debs
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s sdist

reset:
	molecule reset -s bdist
	molecule reset -s default
	molecule reset -s packages-debs
	molecule reset -s packages-rpms
	molecule reset -s sdist
