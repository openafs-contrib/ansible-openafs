# OpenAFS Ansible Collection

This is a collection of Ansible playbooks, roles, and modules to deploy the
[OpenAFS][1] distributed filesystem.

Documentation: [https://openafs-ansible-collection.readthedocs.io][2]

## Requirements

* Ansible 2.10+
* OpenAFS 1.6.5+, 1.8.x, 1.9.x source or packages

## Platforms supported

* AlmaLinux 8, 9
* CentOS 6, 7, 8
* Debian 10, 11, 12
* Fedora 36, 37
* FreeBSD 12, 13
* openSUSE 15
* OracleLinux 8, 9
* Red Hat Entrerprise Linux 7, 8, 9
* Rocky 8, 9
* Solaris 11.4
* Ubuntu 20, 22

## Playbooks

* `build.yaml` Build OpenAFS binaries
* `realm.yaml` Install and setup a Kerberos realm
* `cell.yaml` Install and setup an OpenAFS cell

## Roles

* `openafs_krbclient` Deploy Kerberos clients
* `openafs_krbserver` Deploy Kerberos servers
* `openafs_client` Deploy OpenAFS clients
* `openafs_server` Deploy OpenAFS servers
* `openafs_devel` Install development packages to build OpenAFS binaries
* `openafs_devel_kernel` Install development packages to build the OpenAFS kernel module

## Plugins

### Modules

* `openafs_build` Build OpenAFS binaries from source
* `openafs_build_redhat_rpms` Build OpenAFS RPM packages for RedHat family distributions
* `openafs_build_sdist` Create OpenAFS source distribution archives from a git repo
* `openafs_get_install_paths` Detect installation paths
* `openafs_install_bdist` Install OpenAFS binaries built from source
* `openafs_keys` Add kerberos service keys with asetkey
* `openafs_principal` Create principals and keytab files
* `openafs_selinux_module` Create and install an selinux module from input files
* `openafs_selinux_relabel` Relabel selinux context for server files
* `openafs_store_facts` Store OpenAFS facts in a json file
* `openafs_user` Create an OpenAFS user
* `openafs_volume` Create an OpenAFS volume
* `openafs_wait_for_quorum` Wait for the dbserver connection and quorum
* `openafs_wait_for_registration` Wait for the fileserver VLDB registration

### Lookup

* `openafs_contrib.openafs.counter` Increment named integer counters

## License

BSD

## Author Information

Copyright (c) 2018-2021 Sine Nomine Associates

[1]: https://www.openafs.org/
[2]: https://openafs-ansible-collection.readthedocs.io/en/latest/
