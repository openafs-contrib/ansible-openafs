# Copyright (c) 2019-2020 Sine Nomine Associates

.PHONY: help
help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  lint          lint check"
	@echo "  build         build ansible galaxy collection"

.PHONY: lint
lint:
	for role in roles/*; do $(MAKE) -C $$role lint || passed=no; done; \
    if [ "x$$passed" = "xno" ]; then exit 1; fi

.PHONY: build
build:
	ansible-galaxy collection build
