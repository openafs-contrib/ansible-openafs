PYTHON=python3
PYFLAKES=pyflakes3

.PHONY: help
help:
	@echo "make <target>"
	@echo "targets:"
	@echo "  lint             lint test cases"
	@echo "  test             run all tests"
	@echo "  test_modules     run module tests"

.PHONY: lint
lint:
	$(PYFLAKES) modules/*.py
	$(PYFLAKES) playbooks/*.py

.PHONY: test
test: test_modules

.PHONY: test_modules
test_modules:
	$(PYTHON) -m unittest -v modules.test_openafs_build
