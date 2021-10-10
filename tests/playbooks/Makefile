# Copyright (c) 2019-2021 Sine Nomine Associates

.PHONY: help lint test

help:
	@echo "usage: make <target>"
	@echo ""
	@echo "targets:"
	@echo "  lint     run lint checks"
	@echo "  test     run molecule tests"

lint:
	yamllint $(PLAYBOOKS)
	ansible-lint $(PLAYBOOKS)

test:
	pytest -v
