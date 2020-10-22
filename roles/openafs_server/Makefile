# Copyright (c) 2019-2020 Sine Nomine Associates

M_ACTION=test
M_OPTS=
M_JOBS=8
M_TESTS=\
  test-00 test-01 test-02 test-03 test-04 test-05 test-06 test-07 test-08 test-09 \
  test-10 test-11 test-12 test-13 test-14 test-15 test-16 test-17 test-18 test-19 \
  test-20 test-21 test-22 test-23

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

#
# CentOS 7
#
test-00:
	M_BOX=generic/centos7 M_WITH_CLIENT=no  M_ENABLE_SELINUX=no  molecule $(M_ACTION) $(M_OPTS) -s default
test-01:
	M_BOX=generic/centos7 M_WITH_CLIENT=no  M_ENABLE_SELINUX=yes molecule $(M_ACTION) $(M_OPTS) -s default
test-02:
	M_BOX=generic/centos7 M_WITH_CLIENT=yes M_ENABLE_SELINUX=no  molecule $(M_ACTION) $(M_OPTS) -s default
test-03:
	M_BOX=generic/centos7 M_WITH_CLIENT=yes M_ENABLE_SELINUX=yes molecule $(M_ACTION) $(M_OPTS) -s default
test-04:
	M_BOX=generic/centos7 M_WITH_CLIENT=no  M_ENABLE_SELINUX=no  molecule $(M_ACTION) $(M_OPTS) -s install-packages
test-05:
	M_BOX=generic/centos7 M_WITH_CLIENT=no  M_ENABLE_SELINUX=yes molecule $(M_ACTION) $(M_OPTS) -s install-packages
test-06:
	M_BOX=generic/centos7 M_WITH_CLIENT=yes M_ENABLE_SELINUX=yes molecule $(M_ACTION) $(M_OPTS) -s install-packages
test-07:
	M_BOX=generic/centos7 M_WITH_CLIENT=no  M_ENABLE_SELINUX=no  molecule $(M_ACTION) $(M_OPTS) -s install-bdist
test-08:
	M_BOX=generic/centos7 M_WITH_CLIENT=yes M_ENABLE_SELINUX=no  molecule $(M_ACTION) $(M_OPTS) -s install-bdist
test-09:
	M_BOX=generic/centos7 M_WITH_CLIENT=yes  M_ENABLE_SELINUX=no M_TRANSARC=yes molecule $(M_ACTION) $(M_OPTS) -s install-bdist
test-10:
	M_BOX=generic/centos7 molecule $(M_ACTION) $(M_OPTS) -s install-scm
test-11:
	M_BOX=generic/centos7 M_WITH_CLIENT=yes molecule $(M_ACTION) $(M_OPTS) -s install-scm

#
# CentOS 8
# TODO: selinux on centos8
#
test-12:
	M_BOX=generic/centos8 M_WITH_CLIENT=no  M_ENABLE_SELINUX=no molecule $(M_ACTION) $(M_OPTS) -s default
test-13:
	M_BOX=generic/centos8 M_WITH_CLIENT=yes M_ENABLE_SELINUX=no molecule $(M_ACTION) $(M_OPTS) -s default
test-14:
	M_BOX=generic/centos8 M_WITH_CLIENT=no  M_ENABLE_SELINUX=no molecule $(M_ACTION) $(M_OPTS) -s install-packages
test-15:
	M_BOX=generic/centos8 M_WITH_CLIENT=yes M_ENABLE_SELINUX=no molecule $(M_ACTION) $(M_OPTS) -s install-packages
test-16:
	M_BOX=generic/centos8 M_WITH_CLIENT=no  M_ENABLE_SELINUX=no molecule $(M_ACTION) $(M_OPTS) -s install-bdist
test-17:
	M_BOX=generic/centos8 M_WITH_CLIENT=yes M_ENABLE_SELINUX=no molecule $(M_ACTION) $(M_OPTS) -s install-bdist

#
# Debian 9
# TODO: akeyconvert not available on debian9
#
test-18:
	M_BOX=generic/debian9  M_WITH_CLIENT=no  molecule $(M_ACTION) $(M_OPTS) -s install-bdist
test-19:
	M_BOX=generic/debian9  M_WITH_CLIENT=yes molecule $(M_ACTION) $(M_OPTS) -s install-bdist

#
# Debian 10
#
test-20:
	M_BOX=generic/debian10 M_WITH_CLIENT=no  molecule $(M_ACTION) $(M_OPTS) -s default
test-21:
	M_BOX=generic/debian10 M_WITH_CLIENT=yes molecule $(M_ACTION) $(M_OPTS) -s default
test-22:
	M_BOX=generic/debian10 M_WITH_CLIENT=no  molecule $(M_ACTION) $(M_OPTS) -s install-bdist
test-23:
	M_BOX=generic/debian10 M_WITH_CLIENT=yes molecule $(M_ACTION) $(M_OPTS) -s install-bdist
