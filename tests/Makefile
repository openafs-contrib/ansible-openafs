.PHONY: help lint test clean

help:
	@echo "make <target>"
	@echo "targets:"
	@echo "  lint       lint test cases"
	@echo "  test       run all tests"
	@echo "  retest     rerun failed tests"
	@echo "  clean      remove installed and generated files"

lint:
	pyflakes */*.py

list:
	pytest --co

test: lint
	pytest -v plugins

clean:
	rm -rf */__pycache__
