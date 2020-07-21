# Copyright (c) 2019 Sine Nomine Associates

PYFLAKES=pyflakes3

.PHONY: help
help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  lint   lint check"

.PHONY: lint
lint:
	$(PYFLAKES) library/*.py
	yamllint .
	ansible-lint .
