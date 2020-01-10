# Ansible Roles for OpenAFS

This is a collection of Ansible roles and playbooks to deploy the [OpenAFS][1]
distributed filesystem.

## System requirements

* Ansible 2.7+
* OpenAFS 1.6.5+, 1.8.x

## Platforms supported

* Centos/RHEL 6.x, 7.x, 8.x
* Ubuntu 18.x

## Roles

* Kerberos client
* Kerberos server
* OpenAFS cell
* OpenAFS client
* OpenAFS server
* OpenAFS development
* OpenAFS Robot Framework test suite

## Playbooks

* `kvm.yaml` - Setup a local KVM hypervisor for testing
* `cell.yaml` - Deploy a Kerberos realm and OpenAFS cell
* `realm.yaml` - Deplay a Kerberos realm
* `robotest.yaml` - Install an OpenAFS Robot Framework test suite
* `testcell.yaml` - Setup test realm and cell

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates

[1]: https://www.openafs.org/
[2]: https://web.mit.edu/kerberos/
