# Ansible Role: OpenAFS common

Common definitions for OpenAFS clients and servers.

## Role Variables

    afs_cell: example.com

The OpenAFS cell name.

    afs_realm: EXAMPLE.COM

The Kerberos realm name. Defaults to the uppercased cell name.

    afs_install_method: managed

The method used to install OpenAFS on the remote node. The default value
is `managed`. Supported values are:

* `managed`: Install with the distro's package manager, e.g., `yum`, `apt`.
* `packages`: Install prebuilt packages, e.g. `rpm`
* `bdist`: Install prebuilt binaries, modern or transarc paths.
* `sdist`: Source distribution
* `scm`: Checkout source code, build and install binaries.
* `none`: Skip installation tasks

## `managed` installation method variables

    afs_yum_repo: "https://download.sinenomine.net/openafs/rpms/el$releasever/$basearch"

## `packages`, `bdist`, and `sdist` method variables

    afs_install_archive:

Path to the compressed archive containing the installation files. Must be set
if the installation method is `packages`, `bdist`, or `sdist`.

## `scm` installation method variables

    afs_git_repo: "git://git.openafs.org/openafs.git"
    afs_git_version: master

Git repository URL and the git reference to check out and build.

License
-------

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates

[1]: https://github.com/openafs-contrib/ansible-role-openafs-devel
