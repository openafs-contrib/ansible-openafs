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

## Server Role Variables

    afs_admin_principal: admin

An administrator username created and added to the UserList.

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

    afs_root_server:
    afs_root_part: a

The primary fileserver hostname and AFS fileserver partition id. The cell root
volume (root.afs, root.cell) will be created on this fileserver partition.

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates
