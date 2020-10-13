# Copyright (c) 2019 Sine Nomine Associates

.PHONY: help lint test

help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  lint   lint check"
	@echo "  test   run molecule tests"

lint:
	yamllint .
	ansible-lint .

test:
	molecule test
