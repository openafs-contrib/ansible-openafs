# Ansible Role: OpenAFS client

Install and configure OpenAFS clients.

## Common Role Variables

    afs_cell: example.com

The OpenAFS cell name.

    afs_desc: Example

The OpenAFS cell organization description.

    afs_realm: EXAMPLE.COM

The Kerberos realm name.

    afs_install_method: managed

The method used to install OpenAFS on the remote node. The default value
is `managed`. Supported values are:

* `managed`: Install with the distro's package manager, e.g., `yum`, `apt`.
* `packages`: Install prebuilt packages, e.g. `rpm`
* `bdist`: Install prebuilt binaries, modern or transarc paths.
* `scm`: Checkout source code, build and install binaries.

## `managed` installation method variables

    afs_yum_repo: "https://download.sinenomine.net/openafs/rpms/el$releasever/$basearch"

## `package` installation method variables

    afs_rpm_dir: "~/.cache/ansible-openafs/binaries/rpms"
    afs_rpm_dist: <distribution><major_version>
    afs_rpm_arch: <architecture>

## `bdist` installation method variables

    afs_bdist_dir: "~/.cache/ansible-openafs/binaries/bdist"
    afs_bdist_dist: <distribution><major_version>
    afs_bdist_arch: <architecture>

## `scm` installation method variables

    afs_scm_gitrepo: "git://git.openafs.org/openafs.git"
    afs_scm_gitref: "master"
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
