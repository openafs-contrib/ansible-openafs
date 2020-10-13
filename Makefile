# Copyright (c) 2019-2020 Sine Nomine Associates

.PHONY: help init lint test build docs clean distclean

PYTHON=python3
ROLES=\
  openafs_krbserver \
  openafs_krbclient \
  openafs_server \
  openafs_client \
  openafs_cell

#openafs_devel
#openafs_robotest

help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  init [PYTHON=<path>]  install virtualenv"
	@echo "  lint                  run lint"
	@echo "  test                  run unit and molecule tests"
	@echo "  build                 build ansible galaxy collection"
	@echo "  docs                  generate docs"
	@echo "  clean                 remove generated files"
	@echo "  distclean             remove generated files and virtualenv"

.venv/bin/activate: requirements.txt
	test -d .venv || $(PYTHON) -m venv .venv
	.venv/bin/pip install -U wheel
	.venv/bin/pip install -U -r requirements.txt
	touch .venv/bin/activate

init: .venv/bin/activate

lint: init
	. .venv/bin/activate; \
	for role in roles/*; do \
		echo "linting: $$role"; \
	    $(MAKE) -C $$role lint; \
	done;

test: init
	$(MAKE) -C tests test
	for role in $(ROLES); do \
		echo "testing: $$role"; \
	    $(MAKE) -C roles/$$role test; \
	done;

build: init
	.venv/bin/ansible-galaxy collection build

docs: init
	@mkdir -p docs/modules
	for m in roles/*/library/*.py; do \
		modulepath=`dirname $$m`; \
		modulename=`basename $$m .py`; \
		.venv/bin/ansible-doc -M $${modulepath} -t module $${modulename} > docs/modules/$${modulename}.txt; \
	done

clean:

distclean: clean
	rm -rf .venv
