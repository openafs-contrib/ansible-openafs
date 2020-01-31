PYTHON=python3
PYFLAKES=pyflakes3

.PHONY: test
test: modules

.PHONY: lint
lint:
	$(PYFLAKES) modules/*.py

.PHONY: modules
modules:
	PYTHONPATH=$$PYTHONPATH:../roles/openafs_devel/library \
    $(PYTHON) -m unittest -v modules.test_openafs_build
