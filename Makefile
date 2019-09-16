# Copyright (c) 2019 Sine Nomine Associates

.PHONY: help
help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  lint          lint check"

.PHONY: lint
lint:
	for role in roles/*; do $(MAKE) -C $$role lint || passed=no; done; \
    if [ "x$$passed" = "xno" ]; then exit 1; fi
