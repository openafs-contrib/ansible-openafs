# OpenAFS Server Role

Install and configure OpenAFS servers. This role installs both the fileserver
and the database servers, which can be installed on the same hosts or different
hosts.  Optionally, build and install from source code.

This role configures the system to allow OpenAFS servers operate correctly in
`selinux` enforcing mode.

## Role Variables

    afs_cell: example.com
    afs_desc: Example
    afs_realm:  EXAMPLE.COM

The Kerberos realm name, AFS cell name, and the cell organizational
description.

    afs_admin_principal:
    afs_admin_password: (undefined by default)

A administrator principal and password to be used to set the AFS service key.
The password is not defined by default and must be set on the command line (-e)
or in a group variable, preferably encrypted with `ansible-vault`.

    afs_server_install_method: package-manager

The method used to install the OpenAFS server binaries. Values are:

* `package-manager`:  Install OpenAFS server packages with yum. (default)
* `rsync`: Copy binary files. Build binares from source code if needed.

    afs_openafs_server_repourl:

The URL of a yum repo containing OpenAFS server packages.

    afs_server_build_force: no
    afs_server_build_builddir: "/usr/local/src/openafs_server"
    afs_server_build_destdir: "/tmp/openafs_server"
    afs_server_build_fetch_method: "git"
    afs_server_build_git_repo: "https://github.com/openafs/openafs"
    afs_server_build_git_ref: "master"

Build from source options for the 'rsync' install method.

    afs_selinux_mode: enforcing

The selinux enforcing mode. May be one of `enforcing`, `passive`, or
`disabled`.  When `enforcing`, update the required selinux bits to allow the
servers to properly operate.

    afs_fileserver_type: dafs

Determines which fileserver variation is setup when the host is a member of the
`afs_fileservers` group.  May be the legacy OpenAFS fileserver (`fs`), or the
modern demand-attach fileserver (`dafs`). The demand-attach (`dafs`) variant is
the default.

    afs_bosserver_opts:
    afs_ptserver_opts:
    afs_vlserver_opts:
    afs_dafileserver_opts: -L
    afs_davolserver_opts:
    afs_salvageserver_opts:
    afs_dasalvager_opts:
    afs_fileserver_opts:
    afs_volserver_opts:
    afs_salvager_opts:

The OpenAFS server command line options. See the OpenAFS man pages for the
server processes.

    afs_kdc:

The Kerberos KDC hostname.

    afs_root_server:
    afs_root_part: a

The primary fileserver hostname and AFS fileserver partition id. The cell root
volume (root.afs, root.cell) will be created on this fileserver partition.

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates
