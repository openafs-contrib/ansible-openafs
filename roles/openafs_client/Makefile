# Copyright (c) 2019-2021 Sine Nomine Associates

S=default

.PHONY: help lint init test reset create

help:
	@echo "usage: make <target>"
	@echo ""
	@echo "targets:"
	@echo "  init    initialize molecule scenarios"
	@echo "  lint    run lint checks"
	@echo "  test    run a single molecule scenario"
	@echo "  tests   run a series of molecule scenarios"
	@echo "  reset   reset molecule temporary directories"
	@echo "  create  create molecule boilerplate"

init:
	afs-scenario init

lint: init
	pyflakes library/*.py
	yamllint .
	ansible-lint .

test: init
	molecule test -s $(S)

.tests:
	echo '# scenario  image' > .tests

tests: init .tests
	@grep -v '^#' .tests | while read s i; do \
		echo "Running test $$s on image $$i"; \
		AFS_IMAGE=$$i molecule test -s $$s || \
		(echo "FAIL: scenario $$s image $$i"; exit 1); \
		echo "PASS: scenario $$s image $$i"; \
	done

reset:
	ls molecule | grep -v '^__' | while read s; do molecule reset -s $$s; done

create: Makefile
	afs-scenario create -s default -r openafs_client -g afs_clients --install-method=managed --module-install-method=dkms
	afs-scenario create -s managed-dkms -r openafs_client -g afs_clients --install-method=managed --module-install-method=dkms
	afs-scenario create -s managed-kmod -r openafs_client -g afs_clients --install-method=managed --module-install-method=kmod
	afs-scenario create -s packages-dkms -r openafs_client -g afs_clients --install-method=packages --module-install-method=dkms
	afs-scenario create -s packages-kmod -r openafs_client -g afs_clients --install-method=packages --module-install-method=kmod
	afs-scenario create -s bdist -r openafs_client -g afs_clients --install-method=bdist
	afs-scenario create -s sdist -r openafs_client -g afs_clients --install-method=sdist
	afs-scenario create -s scm -r openafs_client -g afs_clients --install-method=scm
