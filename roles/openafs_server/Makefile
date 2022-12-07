# Copyright (c) 2019-2022 Sine Nomine Associates

.PHONY: help lint test clean

help:
	@echo "usage: make <target>"
	@echo ""
	@echo "targets:"
	@echo "  lint    run lint checks"
	@echo "  test    run molecule tests"
	@echo "  clean   clean test files"

lint:
	yamllint .
	ansible-lint --exclude=molecule

test:
	pytest

clean:
	rm -rf .pytest_cache .cache
