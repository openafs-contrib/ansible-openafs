# Copyright (c) 2019-2020 Sine Nomine Associates

M_ACTION=test
M_OPTS=
M_JOBS=8
M_TESTS=\
  test-00 test-01 test-02 test-03 test-04 test-05 test-06 test-07 test-08 test-09

help:
	@echo "usage: make <target>"
	@echo "targets:"
	@echo "  lint        lint check"
	@echo "  test        default molecule test"
	@echo "  test-all    all molecule tests"
	@echo "  test-all-p  all molecule tests, parallel mode"

lint:
	pyflakes library/*.py
	yamllint .
	ansible-lint .

test: test-00

test-all: $(M_TESTS)

test-all-p:
	$(MAKE) -j $(M_JOBS) --output-sync=target --no-print-directory test-all M_OPTS=--parallel

#
# CentOS 7
#
test-00:
	M_BOX=generic/centos7 molecule $(M_ACTION) $(M_OPTS) -s build-bdist
test-01:
	M_BOX=generic/centos7 molecule $(M_ACTION) $(M_OPTS) -s build-transarc
test-02:
	M_BOX=generic/centos7 molecule $(M_ACTION) $(M_OPTS) -s build-rpms

#
# CentOS 8
#
test-03:
	M_BOX=generic/centos8 molecule $(M_ACTION) $(M_OPTS) -s build-bdist
test-04:
	M_BOX=generic/centos8 molecule $(M_ACTION) $(M_OPTS) -s build-transarc
test-05:
	M_BOX=generic/centos8 molecule $(M_ACTION) $(M_OPTS) -s build-rpms

#
# Debian 9
#
test-06:
	M_BOX=generic/debian9 molecule $(M_ACTION) $(M_OPTS) -s build-bdist
test-07:
	M_BOX=generic/debian9 molecule $(M_ACTION) $(M_OPTS) -s build-transarc

#
# Debian 10
#
test-08:
	M_BOX=generic/debian10 molecule $(M_ACTION) $(M_OPTS) -s build-bdist
test-09:
	M_BOX=generic/debian10 molecule $(M_ACTION) $(M_OPTS) -s build-transarc

clean-cache:
	rm -rf ~/.cache/ansible-openafs/binaries
