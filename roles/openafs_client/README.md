# Ansible Role: OpenAFS client

Install and configure OpenAFS clients.

## Requirements

Unless DNS SRV records have been configured to supply the OpenAFS database
server addresses, the names and addresses of the OpenAFS databases to setup the
server CellServDB files must be provided by the `afs_csdb` inventory variable,
or a separate yaml file, the path of which is specifed by the `afs_csdb_file`
variable.

## Common Role Variables

    afs_cell: example.com

The OpenAFS cell name.

    afs_desc: Example

The OpenAFS cell organization description.

    afs_realm: EXAMPLE.COM

The Kerberos realm name.

    afs_csdb:
      cell: <cell name>
      desc: <cell organization>
      hosts:
        - ip: <ipv4 address>
          name: <hostname>
          clone: <bool>
        - ip: <ipv4 address>
          name: <hostname>
          clone: <bool>
        ...

The CellServDB information for the cell. This must be provided as a inventory
variable or an external yaml file, the path specifed by `afs_csdb_file`.

    afs_install_method: managed

The method used to install OpenAFS on the remote node. The default value
is `managed`. Supported values are:

* `managed`: Install with the distro's package manager, e.g., `yum`, `apt`.
* `packages`: Install prebuilt packages, e.g. `rpm`
* `bdist`: Install prebuilt binaries, modern or transarc paths.
* `scm`: Checkout source code, build and install binaries.

## `managed` installation method variables

    afs_yum_repo: "https://download.sinenomine.net/openafs/rpms/el$releasever/$basearch"

Path to a yum repository containing OpenAFS packages.

## `packages` and `bdist` method variables

    afs_install_archive:

Path to the compressed archive containing the installation files. Must be set
if the installation method is `packages` or `bdist`.

## `scm` installation method variables

    afs_git_repo: "git://git.openafs.org/openafs.git"
    afs_git_version: master

Git repository URL and the git reference to check out and build.

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
