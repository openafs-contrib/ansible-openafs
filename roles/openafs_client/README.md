# Ansible Role: OpenAFS client

Install and configure OpenAFS client packages.  Optionally, this role will
build and install the client from source code with the [OpenAFS devel][1] role.

## Role Variables

    afs_cell: example.com
    afs_desc: Example
    afs_realm:  EXAMPLE.COM

The Kerberos realm name, AFS cell name, and the cell organizational
description.

    # One of: 'package-manager', 'rsync'
    afs_client_install_method: package-manager

The method used to install the OpenAFS client binaries. Values are:

* `package-manager` :  Install client packages and a pre-built kernel module
                with  the system package manager (e.g., `yum`, `apt`).
* `rsync`:      Copy the binary files. Build the client binaries and kernel module from source
                code if needed. Installs development packages in order to
                build the OpenAFS client binaries and kernel module, if needed.

    afs_openafs_client_repourl:

The URL of a yum repo containing OpenAFS client packages for the `package-manager` install method.

    afs_client_install_dkms: no

Install kernel module with DKMS for the `package-manager` install method.

    afs_client_build_force: no
    afs_client_build_builddir: "/usr/local/src/openafs_client"
    afs_client_build_destdir: "/tmp/openafs_client"
    afs_client_build_fetch_method: "git"
    afs_client_build_git_repo: "https://github.com/openafs/openafs"
    afs_client_build_git_ref: "master"

Build options for `rsync` install method.

    afs_cacheinfo_mount: /afs
    afs_cacheinfo_cache: /usr/vice/cache
    afs_cacheinfo_size: 50000

The OpenAFS cache configuration parameters; the AFS filesystem mount point, the
cache partition, and the cache manager cache size.  The cache partition should
already exist.

    afs_afsd_opts: -dynroot -fakestat -afsdb

The OpenAFS cache manager startup options.

License
-------

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates

[1]: https://github.com/openafs-contrib/ansible-role-openafs-devel
