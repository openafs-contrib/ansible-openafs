.PHONY: help install packages.apt lint test clear clean
PYTEST_NO_TESTS=5

help:
	@echo "make <target>"
	@echo "targets:"
	@echo "  install    install requirements in venv"
	@echo "  lint       lint test cases"
	@echo "  test       run all tests"
	@echo "  retest     rerun failed tests"
	@echo "  clean      remove installed and generated files"

.packages:
	sudo apt install -y python3-dev pkg-config build-essential libvirt-dev
	touch .packages

venv/bin/activate: .packages requirements.txt
	test -d venv || /usr/bin/python3 -m venv venv
	. venv/bin/activate && pip install -Ur requirements.txt
	touch venv/bin/activate

install: venv/bin/activate

lint: install
	venv/bin/pyflakes modules/*.py playbooks/*.py

test: install
	venv/bin/pytest --cache-clear

retest: install
	venv/bin/pytest --lf --last-failed-no-failures none || test $$? = $(PYTEST_NO_TESTS)

clean: clear
	rm -rf .packages venv */__pycache__
