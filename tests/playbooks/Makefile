# Copyright (c) 2019-2021 Sine Nomine Associates

MOLECULE_DRIVER ?= vagrant
PLAYBOOKS ?= ../../playbooks

.PHONY: help lint init test reset test-all \
	test-centos-7 test-centos-8 test-debian-10

help:
	@echo "usage: make <target>"
	@echo ""
	@echo "targets:"
	@echo "  lint     run lint checks"
	@echo "  test     run a single molecule scenario"
	@echo "  test-all run a series of molecule scenarios"
	@echo "  reset    reset molecule temporary directories"

lint:
	yamllint $(PLAYBOOKS)
	ansible-lint $(PLAYBOOKS)

test:
	molecule test -d $(MOLECULE_DRIVER) -s default

test-all: test-centos-7 test-centos-8 test-debian-10
	@echo "ok"

test-centos-7:
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s realm
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s cluster

test-centos-8:
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s realm
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s cluster

test-debian-10:
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s realm
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s cluster

reset:
	molecule reset -s default
	molecule reset -s realm
	molecule reset -s cluster
