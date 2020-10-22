# Ansible Roles for OpenAFS

This is a collection of Ansible roles and playbooks to deploy the [OpenAFS][1]
distributed filesystem.

## System requirements

* Ansible 2.7+
* OpenAFS 1.6.5+, 1.8.x

## Platforms supported

* Centos/RHEL 7, 8
* Debian 9, 10

## Ansible roles

* Kerberos client
* Kerberos server
* OpenAFS cell
* OpenAFS client
* OpenAFS server
* OpenAFS development
* OpenAFS Robot Framework test suite

## Example playbooks

* build-bdist.yml - Build OpenAFS binaries
* kerberos-realm.yml - Install and setup a Kerberos realm
* openafs-cell.yml - Install and setup an OpenAFS cell

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates

[1]: https://www.openafs.org/
[2]: https://web.mit.edu/kerberos/
