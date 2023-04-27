# Copyright (c) 2019-2021 Sine Nomine Associates

.PHONY: help init lint test doc docs preview build install clean distclean \
        pylint test-plugins test-roles test-playbooks reset

PYTHON ?= /usr/bin/python3
VERSION := $(shell $(PYTHON) version.py)
UPDATE := --force --pre
PYFILES := plugins/*/*.py tests/*/*.py tests/*/*/*.py
ACPATH := $(realpath $(CURDIR)/../../..)
EXTRACT := ANSIBLE_COLLECTIONS_PATHS=$(ACPATH) ansible-doc-extractor

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
	$(EXTRACT) docs/source/modules plugins/modules/[!_]*.py
	$(EXTRACT) docs/source/plugins/lookup plugins/lookup/[!_]*.py
	$(MAKE) -C docs html

preview: docs
	xdg-open docs/build/html/index.html

builds/openafs_contrib-openafs-$(VERSION).tar.gz:
	sed -i -e 's/^version: .*/version: $(VERSION)/' galaxy.yml
	mkdir -p builds
	ansible-galaxy collection build --output-path builds .
	sed -e "s|@BUILD@|$(CURDIR)/$@|" collections.yml.in > builds/collections.yml

build: builds/openafs_contrib-openafs-$(VERSION).tar.gz

install: build
	ansible-galaxy collection install $(UPDATE) builds/openafs_contrib-openafs-$(VERSION).tar.gz

pylint:
	pyflakes $(PYFILES)
	flake8 $(PYFILES)

lint: pylint
	$(MAKE) -C roles/openafs_krbserver lint
	$(MAKE) -C roles/openafs_krbclient lint
	$(MAKE) -C roles/openafs_common lint
	$(MAKE) -C roles/openafs_devel lint
	$(MAKE) -C roles/openafs_server lint
	$(MAKE) -C roles/openafs_client lint

test: test-plugins test-roles test-playbooks

test-plugins:
	$(MAKE) -C tests test

test-roles:
	$(MAKE) -C roles/openafs_krbserver test
	$(MAKE) -C roles/openafs_krbclient test
	$(MAKE) -C roles/openafs_common test
	$(MAKE) -C roles/openafs_devel test
	$(MAKE) -C roles/openafs_server test
	$(MAKE) -C roles/openafs_client test

test-playbooks:
	$(MAKE) -C tests/playbooks test

reset:
	for r in roles/*; do $(MAKE) -C $$r reset; done
	$(MAKE) -C tests/playbooks reset

clean:
	rm -rf builds docs/build
	rm -rf */*/__pycache__ */*/.pytest_cache */*/.cache
	$(MAKE) -C tests clean

distclean: clean
	rm -rf .venv
