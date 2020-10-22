# Copyright (c) 2019 Sine Nomine Associates

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
