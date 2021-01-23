# OpenAFS Server Role

Install and configure OpenAFS servers. This role installs both the fileserver
and the database servers, which can be installed on the same hosts or different
hosts.

This role configures the system to allow OpenAFS servers operate correctly in
`selinux` enforcing mode when installing from RPM packages.

## Requirements

A kerberos realm is required before creating the OpenAFS services. This can be
a pre-existing realm or can be created with the `openafs_krbserver` role.  A
service principal is required and must be exported to a keytab file. See the
`kerberos-realm.yml` example playbook.

The servers may be installed from the distribution package manager if packages
are available, installed from prebuilt binaries created by separate process or
playbook (see the `openafs_devel` role and `build.yml` example playbook), or
installed from source code from a git repository.

The names and addresses of the OpenAFS databases to setup the server CellServDB
files must be provided by the  `afs_csdb` inventory variable, or a separate
yaml file, the path of which is specifed by the `afs_csdb_file` variable.

## Common Role Variables

    afs_cell: example.com

The OpenAFS cell name.

    afs_desc: Example

The OpenAFS cell organization description.

    afs_realm: EXAMPLE.COM

The Kerberos realm name. Defaults to the uppercased cellname.

    afs_service_keytab: ~/.ansible-openafs/<cell>/rxkad.keytab

The path to the keytab file containing the kerberos keys for the AFS service.
The keytab file must already exist on the controller. It is recommended to
encrypt the keytab file with ansible-vault. See the `keberos-realm.yml`
example playbook.

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
* `sdist`: Source distribution
* `scm`: Checkout source code, build and install binaries.
* `none`: Skip installation tasks

# `managed` installation method variables

    afs_yum_repo: "https://download.sinenomine.net/openafs/rpms/el$releasever/$basearch"

Path to a yum repository containing OpenAFS packages.

## `packages`,  `bdist`, and `sdist` method variables

    afs_install_archive:

Path to the compressed archive containing the installation files. Must be set
if the installation method is `packages`, `bdist`, or `sdist`.

## `scm` installation method variables

    afs_git_repo: "git://git.openafs.org/openafs.git"
    afs_git_version: master

Git repository URL and the git reference to check out and build.

## `scm` installation method variables

    afs_git_repo: "git://git.openafs.org/openafs.git"
    afs_git_version: "master"

## Server Role Variables

    afs_admin_principal: admin

An administrator username created and added to the UserList.

    afs_fileserver_type: dafs

Determines which fileserver variation is setup when the host is a member of the
`afs_fileservers` group.  May be the legacy OpenAFS fileserver (`fs`), or the
modern demand-attach fileserver (`dafs`). The demand-attach (`dafs`) variant is
the default.

    afs_server_cold_start: detect

Set to 'yes' to defer fileserver startup until database quorom is detected.
Set to 'no' to skip cold start checks and tasks.
Default is to detect by checking for the presence of the BosConfig file.

    afs_bosserver_opts:
    afs_ptserver_opts:
    afs_vlserver_opts:
    afs_dafileserver_opts:
    afs_davolserver_opts:
    afs_salvageserver_opts:
    afs_dasalvager_opts:
    afs_fileserver_opts:
    afs_volserver_opts:
    afs_salvager_opts:

The OpenAFS server command line options. See the OpenAFS man pages for the
server processes.

    afs_root_server:
    afs_root_part: a

The primary fileserver hostname and AFS fileserver partition id. The cell root
volume (root.afs, root.cell) will be created on this fileserver partition.

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates
