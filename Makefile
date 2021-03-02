# Copyright (c) 2019-2020 Sine Nomine Associates

.PHONY: help init lint test build docs clean distclean

PYTHON=/usr/bin/python3

help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  venv        install virtualenv"
	@echo "  lint        run lint checks"
	@echo "  test        run unit and molecule tests"
	@echo "  scenarios   generate molecule scenarios"
	@echo "  build       build openafs collection"
	@echo "  install     install openafs collection"
	@echo "  reset       reset molecule temporary directories"
	@echo "  distclean   remove generated files"
	@echo "  distclean   remove generated files and virtualenv"

.venv/bin/activate: Makefile requirements.txt
	test -d .venv || $(PYTHON) -m venv .venv
	.venv/bin/pip install -U wheel
	.venv/bin/pip install -U -r requirements.txt
	.venv/bin/pip install -U tools/afs_scenario
	touch .venv/bin/activate

venv: .venv/bin/activate

build: distclean
	ansible-galaxy collection build

install: build
	ansible-galaxy collection install openafs_contrib-openafs-*.tar.gz --force

lint:
	$(MAKE) -C roles/openafs_krbserver lint
	$(MAKE) -C roles/openafs_krbclient lint
	$(MAKE) -C roles/openafs_common lint
	$(MAKE) -C roles/openafs_devel lint
	$(MAKE) -C roles/openafs_server lint
	$(MAKE) -C roles/openafs_client lint
	$(MAKE) -C roles/openafs_robolint test

molecule scenarios:
	for r in roles/*; do $(MAKE) -C $$r molecule; done
	$(MAKE) -C tests/playbooks molecule

test: test-modules test-roles test-playbooks

test-modules:
	$(MAKE) -C tests test

test-roles:
	$(MAKE) -C roles/openafs_krbserver test
	$(MAKE) -C roles/openafs_krbclient test
	$(MAKE) -C roles/openafs_common test
	$(MAKE) -C roles/openafs_devel test
	$(MAKE) -C roles/openafs_server test
	$(MAKE) -C roles/openafs_client test
	$(MAKE) -C roles/openafs_robotest test

test-playbooks:
	$(MAKE) -C tests/playbooks test

reset:
	for r in roles/*; do $(MAKE) -C $$r reset; done
	$(MAKE) -C tests/playbooks reset

clean:
	rm -rf openafs_contrib-openafs-*.tar.gz

distclean: clean
	$(MAKE) -C tools/afs_scenario distclean
	rm -rf .venv
