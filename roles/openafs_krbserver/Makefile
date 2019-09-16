# Copyright (c) 2019 Sine Nomine Associates

.PHONY: help
help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  lint   lint check"

.PHONY: lint
lint:
	yamllint .
	ansible-lint .
