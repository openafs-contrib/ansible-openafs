# Copyright (c) 2019-2021 Sine Nomine Associates

S=default

.PHONY: help lint init test tests reset create

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
	yamllint $(PLAYBOOKS)
	ansible-lint $(PLAYBOOKS)

test: init
	molecule test -s $(S)

.tests:
	echo '# scenario  envfile' > .tests

tests: init .tests
	@grep -v '^#' .tests | while read s e; do \
		echo "Running test $$s on with vars $$e"; \
		molecule --env-file .env/$${e}.yml test -s $$s || \
		(echo "FAIL: scenario $$s vars $$e"; exit 1); \
		echo "PASS: scenario $$s vars $$e"; \
	done

reset:
	ls molecule | grep -v '^__' | while read s; do molecule reset -s $$s; done

# Playbooks
PLAYBOOKS=../../../../playbooks
NEWREALM=-p $(PLAYBOOKS)/realm.yaml
NEWCELL=-p $(PLAYBOOKS)/realm.yaml -p $(PLAYBOOKS)/cell.yaml

# Server configurations.
C0=-n 1 -g afs_kdcs
C1=-n 1 -g afs_kdcs -g afs_databases -g afs_fileservers -g afs_admin -g afs_clients
C2=-n 6 -g afs_kdcs=1 -g afs_databases=1 -g afs_fileservers=2,3 -g afs_admin=4 -g afs_clients=4,5,6

create: Makefile
	afs-scenario create -s default $(NEWCELL) $(C1)
	afs-scenario create -s realm   $(NEWREALM) $(C0)
	afs-scenario create -s cluster $(NEWCELL) $(C2)

