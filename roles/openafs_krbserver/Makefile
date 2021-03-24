# Copyright (c) 2019-2021 Sine Nomine Associates

MOLECULE_DRIVER ?= vagrant

.PHONY: help init lint test test-all reset

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

test:
	molecule test -d $(MOLECULE_DRIVER) -s default

test-all:
	AFS_IMAGE=generic/centos7 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/centos8 molecule test -d $(MOLECULE_DRIVER) -s default
	AFS_IMAGE=generic/debian10 molecule test -d $(MOLECULE_DRIVER) -s default
	@echo "ok"

reset:
	molecule reset -s default
