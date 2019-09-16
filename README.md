# Ansible Roles for OpenAFS

This is a collection of Ansible roles and playbooks to deploy the [OpenAFS][1]
distributed filesystem.

## Requirements

* OpenAFS 1.6.5 or newer
* Ansible 2.7 or newer

## Platforms

* RHEL7/CentOS7
* Ubuntu 18.x

## Roles

* [Kerberos client](roles/openafs_krbclient/README.md)
* [Kerberos server](roles/openafs_krbserver/README.md)
* [OpenAFS cell](roles/openafs_cell/README.md)
* [OpenAFS client](roles/openafs_client/README.md)
* [OpenAFS server](roles/openafs_server/README.md)
* [OpenAFS development](roles/openafs_devel/README.md)
* [OpenAFS Robot Framework test suite](roles/openafs_robotest/README.md)

## Playbooks

* `kvm.yaml` - Setup a local KVM hypervisor for testing
* `cell.yaml` - Deploy a kerberos realm and OpenAFS cell set of machines

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates

[1]: https://www.openafs.org/
[2]: https://web.mit.edu/kerberos/
