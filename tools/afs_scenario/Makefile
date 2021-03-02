.PHONY: help init lint install uninstall test \
        sdist wheel rpm deb upload \
        clean distclean \

PACKAGE_NAME=afs_scenario

PYTHON3=python3
PYTHON=.venv/bin/python
PYFLAKES=.venv/bin/pyflakes
PYTEST=.venv/bin/pytest
TWINE=.venv/bin/twine

help:
	@echo "usage: make <target>"
	@echo ""
	@echo "targets:"
	@echo "  init       create python virtual env"
	@echo "  lint       run linter"
	@echo "  test       run tests"
	@echo "  install    local installation for testing"
	@echo "  upload     upload to pypi"
	@echo "  clean      remove generated files"
	@echo "  distclean  remove generated files and virtual env"

.venv:
	$(PYTHON3) -m venv .venv
	.venv/bin/pip install -U wheel
	.venv/bin/pip install -U pyflakes pylint pytest collective.checkdocs twine

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

sdist: init
	$(PYTHON) setup.py sdist

wheel: init
	$(PYTHON) setup.py bdist_wheel

rpm: init
	$(PYTHON) setup.py bdist_rpm

deb: init
	$(PYTHON) setup.py --command-packages=stdeb.command bdist_deb

upload: init sdist wheel
	$(TWINE) upload dist/*

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf build dist .eggs *.egg-info */*.egg-info
	rm -rf .pytest_cache

distclean: clean
	rm -rf .venv
