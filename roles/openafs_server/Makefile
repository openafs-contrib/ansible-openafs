# Copyright (c) 2019-2020 Sine Nomine Associates

.PHONY: help lint test test-platforms

SCENARIO=default
BOX=generic/centos7

BOXES=\
  generic/centos7 \
  generic/centos8 \
  generic/debian9 \
  generic/debian10

help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  lint   lint check"
	@echo "  test   run molecule tests"

lint:
	yamllint .
	ansible-lint .

test:
	BOX=$(BOX) molecule test -s $(SCENARIO)

test-platforms:
	for box in $(BOXES); do \
		BOX=$$box molecule test -s $(SCENARIO); \
	done
