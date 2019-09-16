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

* [Kerberos client](roles/openafs-krbclient)
* [Kerberos server](roles/openafs-krbserver)
* [OpenAFS cell](roles/openafs-cell)
* [OpenAFS client](roles/openafs-client)
* [OpenAFS server](roles/openafs-server)
* [OpenAFS development](roles/openafs-devel)
* [OpenAFS Robot Framework test suite](roles/role-openafs-robotest)

## Playbooks

* `cell.yaml` - Deploy the `example.com` cell on a set of hosts

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates

[1]: https://www.openafs.org/
[2]: https://web.mit.edu/kerberos/
