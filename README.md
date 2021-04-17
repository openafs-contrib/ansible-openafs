# OpenAFS Ansible Collection

This is a collection of Ansible playbooks, roles, and modules to deploy the
[OpenAFS][1] distributed filesystem.

Documentation: [https://openafs-ansible-collection.readthedocs.io][2]

## Requirements

* Ansible 2.10+
* OpenAFS 1.6.5+, 1.8.x, 1.9.x source or packages

## Platforms

* Red Hat Entrerprise Linux/CentOS 7, 8
* Debian 9, 10

## Playbooks

* `build.yaml` Build OpenAFS binaries
* `realm.yaml` Install and setup a Kerberos realm
* `cell.yaml` Install and setup an OpenAFS cell

## Roles

* `openafs_krbclient` Deploy Kerberos clients
* `openafs_krbserver` Deploy Kerberos servers
* `openafs_client` Deploy OpenAFS clients
* `openafs_server` Deploy OpenAFS servers
* `openafs_devel` Install OpenAFS development packages

## Modules

* `openafs_build` Build OpenAFS binaries from source
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

## License

BSD

## Author Information

Copyright (c) 2018-2021 Sine Nomine Associates

[1]: https://www.openafs.org/
[2]: https://openafs-ansible-collection.readthedocs.io/en/latest/
