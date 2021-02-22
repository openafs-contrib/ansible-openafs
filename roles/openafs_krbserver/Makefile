# Copyright (c) 2019-2020 Sine Nomine Associates

.PHONY: help lint test distclean

COOK=cookiecutter \
   --no-input -f -o molecule.old \
   /home/mmeffie/src/ansible-openafs/cookiecutter/molecule-scenario driver=delegated driver_provider=libvirt driver_template_prefix=devel driver_libvirt_host=localhost \
   instance_name=m-krbserver \
   with_krbserver=yes

help:
	@echo "usage: make <target>"
	@echo ""
	@echo "targets:"
	@echo "  lint        run lint checks"
	@echo "  test        run molecule scenarios"
	@echo "  molecule    generate molecule scenarios"
	@echo "  reset       reset molecule temporary directories"
	@echo "  clean       remove molecule scenarios"

lint:
	pyflakes library/*.py
	yamllint .
	ansible-lint .

test: molecule
	molecule test --all

molecule: Makefile
	$(COOK) name=default
	touch molecule

reset:
	@if [ -d molecule ]; then \
		for s in `ls molecule`; do \
			molecule reset -s $$s; \
		done \
	fi

clean: reset
	rm -rf molecule
