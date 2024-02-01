# Copyright (c) 2019-2021 Sine Nomine Associates

.PHONY: help init lint test doc docs preview build install clean distclean \
        pylint test-plugins test-roles test-playbooks reset

PYTHON ?= /usr/bin/python3.12
VERSION := $(shell $(PYTHON) version.py)
UPDATE := --force --pre
PYFILES := plugins/*/*.py tests/*/*.py tests/*/*/*.py
ACPATH := $(realpath $(CURDIR)/../../..)
EXTRACT := ANSIBLE_COLLECTIONS_PATHS=$(ACPATH) ansible-doc-extractor
ifdef VIRTUAL_ENV
VENV =
else
VENV = . .venv/bin/activate;
endif

help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  init        install virtualenv"
	@echo "  lint        run lint checks"
	@echo "  test        run unit and molecule tests"
	@echo "  doc         generate documentation"
	@echo "  build       build openafs collection"
	@echo "  install     install openafs collection"
	@echo "  reset       reset molecule temporary directories"
	@echo "  clean       remove generated files"
	@echo "  distclean   remove generated files and virtualenv"

.venv/bin/activate: requirements.txt
	test -d .venv || $(PYTHON) -m venv .venv
	.venv/bin/pip install -U pip wheel
	.venv/bin/pip install -U -r requirements.txt
	touch .venv/bin/activate

init: .venv/bin/activate

doc docs:
	mkdir -p docs/source/modules docs/source/plugins/lookup
	$(VENV) $(EXTRACT) docs/source/modules plugins/modules/[!_]*.py
	$(VENV) $(EXTRACT) docs/source/plugins/lookup plugins/lookup/[!_]*.py
	$(VENV) $(MAKE) -C docs html

preview: docs
	xdg-open docs/build/html/index.html

builds/openafs_contrib-openafs-$(VERSION).tar.gz:
	sed -i -e 's/^version: .*/version: $(VERSION)/' galaxy.yml
	mkdir -p builds
	$(VENV) ansible-galaxy collection build --output-path builds .
	sed -e "s|@BUILD@|$(CURDIR)/$@|" collections.yml.in > builds/collections.yml

build: builds/openafs_contrib-openafs-$(VERSION).tar.gz

install: build
	$(VENV) ansible-galaxy collection install $(UPDATE) builds/openafs_contrib-openafs-$(VERSION).tar.gz

pylint:
	$(VENV) pyflakes $(PYFILES)
	$(VENV) flake8 $(PYFILES)

lint: pylint
	$(VENV) $(MAKE) -C roles/openafs_krbserver lint
	$(VENV) $(MAKE) -C roles/openafs_krbclient lint
	$(VENV) $(MAKE) -C roles/openafs_common lint
	$(VENV) $(MAKE) -C roles/openafs_devel lint
	$(VENV) $(MAKE) -C roles/openafs_server lint
	$(VENV) $(MAKE) -C roles/openafs_client lint

test: test-plugins test-roles test-playbooks

test-plugins:
	$(VENV) $(MAKE) -C tests test

test-roles:
	$(VENV) $(MAKE) -C roles/openafs_krbserver test
	$(VENV) $(MAKE) -C roles/openafs_krbclient test
	$(VENV) $(MAKE) -C roles/openafs_common test
	$(VENV) $(MAKE) -C roles/openafs_devel test
	$(VENV) $(MAKE) -C roles/openafs_server test
	$(VENV) $(MAKE) -C roles/openafs_client test

test-playbooks:
	$(VENV) $(MAKE) -C tests/playbooks test

reset:
	for r in roles/*; do $(VENV) $(MAKE) -C $$r reset; done
	$(VENV) $(MAKE) -C tests/playbooks reset

clean:
	rm -rf builds docs/build
	rm -rf */*/__pycache__ */*/.pytest_cache */*/.cache

distclean: clean
	rm -rf .venv
