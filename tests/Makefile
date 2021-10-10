.PHONY: help lint test clean
PYTEST_NO_TESTS=5
PYTEST_FLAGS=

help:
	@echo "make <target>"
	@echo "targets:"
	@echo "  lint       lint test cases"
	@echo "  test       run all tests"
	@echo "  retest     rerun failed tests"
	@echo "  clean      remove installed and generated files"

lint:
	../.venv/bin/pyflakes modules/*.py

list:
	../.venv/bin/pytest --co

test: lint
	../.venv/bin/pytest --cache-clear $(PYTEST_FLAGS)

retest: install
	../.venv/bin/pytest --lf --last-failed-no-failures none $(PYTEST_FLAGS) || test $$? = $(PYTEST_NO_TESTS)

clean:
	rm -rf */__pycache__
