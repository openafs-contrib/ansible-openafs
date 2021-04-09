# Ansible Role: OpenAFS client

Install and configure OpenAFS clients.

## Requirements

Unless DNS SRV records have been configured to supply the OpenAFS database
server addresses, the names and addresses of the OpenAFS databases to setup the
server CellServDB files must be provided by the `afs_csdb` inventory variable,
or a separate yaml file, the path of which is specifed by the `afs_csdb_file`
variable.

## Common Role Variables

See `openafs_common` for included common variables.

## Client Role Variables

    afs_module: openafs

OpenAFS  kernel module name, `openafs` or `libafs`.

    afs_module_install_method: dkms

Specifies the kernel module installation method on RPM-based systems, `dkms` or
`kmod`.

    afs_mountpoint: /afs

The AFS filesystem mount point for this host.

    afs_cachedir: /usr/vice/cache

The path to the AFS cache.

    afs_cachesize: 50000

The size of the AFS cache.

    afs_afsd_opts: -dynroot -fakestat -afsdb

The `afsd` command line arguments.


License
-------

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates

[1]: https://github.com/openafs-contrib/ansible-role-openafs-devel
