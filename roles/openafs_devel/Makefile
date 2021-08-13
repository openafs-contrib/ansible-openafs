# Copyright (c) 2019-2021 Sine Nomine Associates

MOLECULE_DRIVER ?= vagrant
MOLECULE_SCENARIO ?= default
MOLECULE_IMAGE ?= generic/centos7
MOLECULE_DESTROY ?= always

IMAGES = centos7 centos8 debian10
SCENARIOS = default bdist packages sdist

help:
	@echo "usage: make <target>"
	@echo ""
	@echo "targets:"
	@echo "  lint            run lint checks"
	@echo "  test            run all molecule tests [note 1]"
	@echo "  reset           reset molecule directories"
	@echo "  scenario        run one molecule test scenario"
	@echo "  test-<os>       limit tests to os"
	@echo "  test-<scenario> limit tests to scenario"
	@echo ""
	@echo "where:"
	@echo "  <os> is one of: $(IMAGES)"
	@echo "  <scenario> is one of: $(SCENARIOS)"
	@echo ""
	@echo "environment:"
	@echo "  MOLECULE_DRIVER=<name> (default: vagrant)"
	@echo "  MOLECULE_SCENARIO=<scenario> (default: default)"
	@echo "  MOLECULE_IMAGE=<image> (defult: generic/centos7)"
	@echo "  MOLECULE_DESTROY='always' | 'never'"

lint:
	yamllint .
	ansible-lint .

scenario:
	AFS_IMAGE=$(MOLECULE_IMAGE) \
	molecule test \
	  --driver-name $(MOLECULE_DRIVER) \
	  --scenario-name $(MOLECULE_SCENARIO) \
	  --destroy $(MOLECULE_DESTROY)


test: test-centos-7 test-centos8 test-debian10

test-centos7:
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s packages-rpms
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s sdist

test-centos8:
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s packages-rpms
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s sdist

test-debian10:
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s packages-debs
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s sdist

test-bdist:
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s bdist

test-packages:
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s packages
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s packages
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s packages

test-sdist:
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s sdist

reset:
	molecule reset -s bdist
	molecule reset -s default
	molecule reset -s packages
	molecule reset -s sdist
