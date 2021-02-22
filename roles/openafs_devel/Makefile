# Copyright (c) 2019-2020 Sine Nomine Associates

.PHONY: help lint test distclean

COOK=cookiecutter \
   --no-input -f -o molecule.old \
   /home/mmeffie/src/ansible-openafs/cookiecutter/molecule-scenario driver=delegated driver_provider=libvirt driver_template_prefix=devel driver_libvirt_host=localhost \
   instance_name=m-devel \
   with_devel=yes

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
	$(COOK) name=cen7                 os=centos7
	$(COOK) name=cen7-bdist-modern    os=centos7 build=bdist bdist_style=modern
	$(COOK) name=cen7-bdist-transarc  os=centos7 build=bdist bdist_style=transarc
	$(COOK) name=cen7-rpms            os=centos7 build=rpms
	$(COOK) name=cen8                 os=centos8
	$(COOK) name=cen8-bdist-modern    os=centos8 build=bdist bdist_style=modern
	$(COOK) name=cen8-bdist-transarc  os=centos8 build=bdist bdist_style=transarc
	$(COOK) name=cen8-rpms            os=centos8 build=rpms
	$(COOK) name=deb9                 os=debian9
	$(COOK) name=deb9-bdist-modern    os=debian9 build=bdist bdist_style=modern
	$(COOK) name=deb9-bdist-transarc  os=debian9 build=bdist bdist_style=transarc
	$(COOK) name=deb10                os=debian10
	$(COOK) name=deb10-bdist-modern   os=debian10 build=bdist bdist_style=modern
	$(COOK) name=deb10-bdist-transarc os=debian10 build=bdist bdist_style=transarc
	touch molecule

reset:
	@if [ -d molecule ]; then \
		for s in `ls molecule`; do \
			molecule reset -s $$s; \
		done \
	fi

clean: reset
	rm -rf molecule
