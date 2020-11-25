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


License
-------

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates

[1]: https://github.com/openafs-contrib/ansible-role-openafs-devel
