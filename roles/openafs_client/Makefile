# Copyright (c) 2019-2021 Sine Nomine Associates

MOLECULE_DRIVER ?= vagrant

.PHONY: help lint init test reset test-all \
		test-centos-7 test-centos-8 test-debian-10

help:
	@echo "usage: make <target>"
	@echo ""
	@echo "targets:"
	@echo "  lint      run lint checks"
	@echo "  test      run a single molecule scenario"
	@echo "  test-all  run a series of molecule scenarios"
	@echo "  reset     reset molecule temporary directories"
	@echo ""
	@echo "environment:"
	@echo "  MOLECULE_DRIVER=<name> (default: vagrant)"

lint:
	yamllint .
	ansible-lint .

test:
	molecule test -d $(MOLECULE_DRIVER)

# NOTE: The following tests require installation packages/tarballs,
#       which can be built by the openafs_devel molecule tests.
test-all: test-centos-7 test-centos-8 test-debian-10
	@echo "ok"

test-centos-7:
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s managed-dkms
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s managed-kmod
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s packages-dkms
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s packages-kmod
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s source
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s sdist

test-centos-8:
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s managed-dkms
	#AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s managed-kmod
	AFS_IMAGE=generic/centos8 molecule test -d $(DRIVER) -s packages-dkms
	AFS_IMAGE=generic/centos8 molecule test -d $(DRIVER) -s packages-kmod
	AFS_IMAGE=generic/centos8 molecule test -d $(DRIVER) -s source
	AFS_IMAGE=generic/centos8 molecule test -d $(DRIVER) -s sdist

test-debian-10:
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s bdist
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s managed-dkms
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s source
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s sdist

reset:
	molecule reset -s default
	molecule reset -s bdist
	molecule reset -s managed-dkms
	molecule reset -s managed-kmod
	molecule reset -s packages-dkms
	molecule reset -s packages-kmod
	molecule reset -s source
	molecule reset -s sdist
