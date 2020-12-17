# Ansible Roles for OpenAFS

This is a collection of Ansible roles and playbooks to deploy the [OpenAFS][1]
distributed filesystem.

## System requirements

* Ansible 2.7+
* OpenAFS 1.6.5+, 1.8.x, 1.9.x

## Platforms supported

* Centos/RHEL 7, 8
* Debian 9, 10

## Ansible roles

* Kerberos client
* Kerberos server
* OpenAFS client
* OpenAFS server
* OpenAFS development
* OpenAFS Robot Framework test suite

## Example playbooks

* build.yaml - Build OpenAFS binaries
* realm.yaml - Install and setup a Kerberos realm
* cell.yaml - Install and setup an OpenAFS cell

## License

BSD

## Author Information

Copyright (c) 2018-2021 Sine Nomine Associates

[1]: https://www.openafs.org/
[2]: https://web.mit.edu/kerberos/
