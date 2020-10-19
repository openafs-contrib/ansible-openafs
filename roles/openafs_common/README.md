# Ansible Role: OpenAFS common

Common definitions for OpenAFS clients and servers.

## Role Variables

    afs_cell: example.com

The OpenAFS cell name.

    afs_desc: Example

The OpenAFS cell organization description.

    afs_realm: EXAMPLE.COM

The Kerberos realm name.

    afs_install_method: managed

The method used to install OpenAFS.

    afs_yum_repo:

OpenAFS yum/dnf repo url for the 'managed' install method.

License
-------

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates

[1]: https://github.com/openafs-contrib/ansible-role-openafs-devel
