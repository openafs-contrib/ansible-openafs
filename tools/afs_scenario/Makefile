.PHONY: help init lint install uninstall test clean distclean

PACKAGE_NAME=afs_scenario

help:
	@echo "usage: make <target>"
	@echo ""
	@echo "targets:"
	@echo "  init       create python virtual env"
	@echo "  lint       run linter"
	@echo "  test       run tests"
	@echo "  install    local installation for testing"
	@echo "  clean      remove generated files"
	@echo "  distclean  remove generated files and virtual env"

.venv:
	python3 -m venv .venv
	.venv/bin/pip install -U wheel
	.venv/bin/pip install -U pyflakes pylint pytest collective.checkdocs

init: .venv

lint: init
	.venv/bin/pyflakes src/*/*.py
	.venv/bin/pyflakes tests/*.py
	.venv/bin/python setup.py checkdocs

install: lint
	.venv/bin/pip install -e .

uninstall:
	.venv/bin/pip uninstall --yes $(PACKAGE_NAME)

test: lint
	.venv/bin/pytest -v

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf build dist .eggs *.egg-info */*.egg-info
	rm -rf .pytest_cache

distclean: clean
	rm -rf .venv
