# Copyright (c) 2019-2021 Sine Nomine Associates

MOLECULE_DRIVER ?= vagrant
MOLECULE_SCENARIO ?= default
MOLECULE_IMAGE ?= generic/centos7
MOLECULE_DESTROY ?= always

IMAGES = centos7 centos8 debian10
SCENARIOS = default bdist managed-dkms managed-kmod packages-dkms packages-kmod source sdist

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
	@echo ""
	@echo "Note 1: Run openafs_devel 'make test' first to build packages."

lint:
	yamllint .
	ansible-lint .

check test: test-centos7 test-centos8 test-debian10

reset:
	for s in $(SCENARIOS); do molecule reset -s $$s; done

scenario:
	AFS_IMAGE=$(MOLECULE_IMAGE) \
	molecule test \
	  --driver-name $(MOLECULE_DRIVER) \
	  --scenario-name $(MOLECULE_SCENARIO) \
	  --destroy $(MOLECULE_DESTROY)

#
# Tests by os.
#
test-centos7:
	for s in $(SCENARIOS); do $(MAKE) scenario MOLECULE_IMAGE=generic/centos7 MOLECULE_SCENARIO=$$s; done

test-centos8:
	for s in $(SCENARIOS); do $(MAKE) scenario MOLECULE_IMAGE=generic/centos8 MOLECULE_SCENARIO=$$s; done

test-debian10:
	for s in $(SCENARIOS); do $(MAKE) scenario MOLECULE_IMAGE=generic/debian10 MOLECULE_SCENARIO=$$s; done

#
# Tests by scenario.
#
test-default:
	for i in $(IMAGES); do $(MAKE) scenario MOLECULE_IMAGE=generic/$$i MOLECULE_SCENARIO=default; done

test-bdist:
	for i in $(IMAGES); do $(MAKE) scenario MOLECULE_IMAGE=generic/$$i MOLECULE_SCENARIO=bdist; done

test-packages-dkms:
	for i in $(IMAGES); do $(MAKE) scenario MOLECULE_IMAGE=generic/$$i MOLECULE_SCENARIO=packages-dkms; done

test-packages-kmod:
	for i in generic/centos7 generic/centos8; do \
	  $(MAKE) scenario MOLECULE_IMAGE=generic/$$i MOLECULE_SCENARIO=packages-kmod; \
	done

test-source:
	for i in $(IMAGES); do $(MAKE) scenario MOLECULE_IMAGE=generic/$$i MOLECULE_SCENARIO=source; done

test-sdist:
	for i in $(IMAGES); do $(MAKE) scenario MOLECULE_IMAGE=generic/$$i MOLECULE_SCENARIO=sdist; done
