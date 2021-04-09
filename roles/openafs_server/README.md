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

See `openafs_common` for included common variables.

## Server Role Variables

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

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates
