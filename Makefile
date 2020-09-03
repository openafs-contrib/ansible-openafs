# Copyright (c) 2019-2020 Sine Nomine Associates

.PHONY: help
help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  venv          install virtualenv"
	@echo "  lint          lint check"
	@echo "  build         build ansible galaxy collection"
	@echo "  docs          generate docs"

.venv/bin/activate: requirements.txt
	test -d .venv || /usr/bin/python3 -m venv .venv
	. .venv/bin/activate && pip install -Ur requirements.txt
	touch .venv/bin/activate

.PHONY: venv
venv: .venv/bin/activate

.PHONY: lint
lint:
	for role in roles/*; do $(MAKE) -C $$role lint || passed=no; done; \
    if [ "x$$passed" = "xno" ]; then exit 1; fi

.PHONY: build
build:
	ansible-galaxy collection build

.PHONY: docs
docs:
	# Create plan text docs for now.
	@mkdir -p docs/modules
	ansible-doc -M roles/openafs_devel/library -t module openafs_build > docs/modules/openafs_build.txt
	ansible-doc -M roles/openafs_devel/library -t module openafs_install > docs/modules/openafs_install.txt
