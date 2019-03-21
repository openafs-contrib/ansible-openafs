# Ansible Roles for OpenAFS

This is a collection of Ansible roles and playbooks to deploy the [OpenAFS][1]
distributed filesystem. Support is currently limited to RedHat-based linux
systems.

## Platforms Supported

* CentOS 7
* RHEL 7

Requires Ansible 2.2 or greater.

## Playbook Setup

The playbooks can be setup by creating an inventory and group variables.
Examples are available in the `examples` directory.

## Kerberos Client Role

Install and configure the Kerberos workstation packages.

### Role Variables

    realm: EXAMPLE.COM

The Kerberos realm name.

## Kerberos Server Role

Install and configure the Kerberos master KDC on single host, create the
Kerberos database, the administrator's principal, and the OpenAFS service key.

### Role Variables

    realm: EXAMPLE.COM

The Kerberos realm name.

    admin_principal: admin

A administrator principal to be created. This principal will be used to create
the service keys and regular user principals.

    admin_password:

The administrator principal password. No default value is given.

## OpenAFS Cell Role

Setup the top level volumes in the cell. This role is to be run on a single
client host.

### Role Variables

    cell: example.com
    realm: EXAMPLE.COM

Cell and realm names.

    kdc:

The Kerberos KDC hostname. This host must be a member of the `kdcs` host group.

    root_server:
    root_part: a

The primary fileserver hostname and AFS fileserver partition id. The cell's
top-level volumes will be created on this fileserver partition.

## OpenAFS Client Role

Install and configure the OpenAFS client packages.  Optionally, build and install from
a git source checkout.

### Role Variables

    cell: example.com
    cell_description: Example
    realm:  EXAMPLE.COM

The Kerberos realm name, AFS cell name, and the cell organizational
description.

    client_install_method: yum-kmod

The method used to install the OpenAFS client binaries. Values are:

* `yum-kmod` :  Install client packages and a pre-built kernel module
                with yum.
                by `openafs_client_repourl`.
* `yum-dkms`:   Install client packages and kernel module sources with yum
                and build the kernel module using DKMS.
* `build`:      Build the client binaries and kernel module from a source
                code. Also, install development packages in order to
                build the OpenAFS client binaries and kernel module.

    openafs_client_repourl:

The URL of a yum repo containing OpenAFS client packages.

    client_build_repo:
    client_build_version: master
    client_build_path: /usr/local/src/openafs-client

The OpenAFS git repo URL, git reference, and build scratch directory for the
`build` installation method.

    cacheinfo_mount: /afs
    cacheinfo_cache: /usr/vice/cache
    cacheinfo_size: 50000

The OpenAFS cache configuration parameters; the AFS filesystem mount point, the
cache partition, and the cache manager cache size.  The cache partition should
already exist.

    opt_afsd: -dynroot -fakestat -afsdb

The OpenAFS cache manager startup options.

## OpenAFS Server Role

Install and configure the OpenAFS server packages. This role installs both the
fileserver and the database servers, which can be installed on the same hosts
or different hosts.  Optionally, build and install from a git source checkout.

This role enables OpenAFS servers to operate correctly with selinux set to
enforcing mode.

### Role Variables

    cell: example.com
    cell_description: Example
    realm:  EXAMPLE.COM

The Kerberos realm name, AFS cell name, and the cell organizational
description.

    server_install_method: yum

The method used to install the OpenAFS server binaries. Values are:

* `yum`:  Install OpenAFS server packages with yum.
* `build`: Build and install server binaries from source code.

    openafs_server_repourl:

The URL of a yum repo containing OpenAFS server packages.

    server_build_repo:
    server_build_path: /usr/local/src/openafs-server
    server_build_version: master

The OpenAFS git repo URL, git reference, and build scratch directory for the
`build` installation method.

    selinux_mode: enforcing

The selinux enforcing mode. May be one of `enforcing`, `passive`, or
`disabled`.  When `enforcing`, update the required selinux bits to allow the
servers to properly operate.

    enable_dafs: True

Install the newer Demand-Attach Filesystem (DAFS) fileserver variant when
installing a fileserver.

    opt_bosserver:
    opt_ptserver:
    opt_vlserver:
    opt_dafileserver: -L
    opt_davolserver:
    opt_salvageserver:
    opt_dasalvager:
    opt_fileserver:
    opt_volserver:
    opt_salvager:

The OpenAFS server command line options. See the OpenAFS man pages for the
server processes.

    kdc:

The Kerberos KDC hostname.

    root_server:
    root_part: a

The primary fileserver hostname and AFS fileserver partition id. The cell root
volume (root.afs, root.cell) will be created on this fileserver partition.

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates


[1]: https://www.openafs.org/
[2]: https://web.mit.edu/kerberos/
