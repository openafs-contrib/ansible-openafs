# Copyright (c) 2019-2020 Sine Nomine Associates

.PHONY: help lint test

M_SCENARIO=default

help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  lint       run linter"
	@echo "  test       run default molecule test"
	@echo "  test-all   run all molecule tests"
	@echo "  test-all-parallel"
	@echo "  test-install-managed"
	@echo "  test-install-packages"
	@echo "  test-install-bdist"

lint:
	pyflakes library/*.py
	yamllint .
	ansible-lint .

test:
	molecule test -s $(M_SCENARIO)
