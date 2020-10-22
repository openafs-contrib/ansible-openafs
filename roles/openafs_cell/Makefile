# Copyright (c) 2019-2020 Sine Nomine Associates

M_ACTION=test
M_OPTS=
M_JOBS=8
M_TESTS=\
  test-00 test-01 test-02 test-03

help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  lint        lint check"
	@echo "  test        default molecule test"
	@echo "  test-all    all molecule tests"
	@echo "  test-all-p  all molecule tests, parallel mode"

lint:
	yamllint .
	ansible-lint .

test: test-00

test-all: $(M_TESTS)

test-all-p:
	$(MAKE) -j $(M_JOBS) --output-sync=target --no-print-directory test-all M_OPTS=--parallel

test-00:
	M_BOX=generic/centos7 molecule $(M_ACTION) $(M_OPTS) -s default

test-01:
	M_BOX=generic/centos8 molecule $(M_ACTION) $(M_OPTS) -s default

test-02:
	# missing akeyconvert
	# M_BOX=generic/debian9 molecule $(M_ACTION) $(M_OPTS) -s default

test-03:
	M_BOX=generic/debian10 molecule $(M_ACTION) $(M_OPTS) -s default
