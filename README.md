# Ansible Roles for OpenAFS

This is a collection of Ansible roles and playbooks to deploy the [OpenAFS][1]
distributed filesystem.

## Platforms Supported

* OpenAFS 1.6.5+
* Ansible 2.5+
* OS Versions
    * RHEL7/CentOS7
    * Ubuntu 18.x

## Kerberos Client Role

Name: `openafs_krbclient`

Install and configure the Kerberos workstation packages.

### Role Variables

    afs_realm: EXAMPLE.COM

The Kerberos realm name.

## Kerberos Server Role

Name: `openafs_krbserver`

Install and configure the Kerberos master KDC on single host, create the
Kerberos database, the administrator's principal, and the OpenAFS service key.

### Role Variables

    afs_realm: EXAMPLE.COM

The Kerberos realm name.

    afs_kerberos_master_password: (random by default)

The secret Kerberos database master password. The password is a random string
by default. It should be set on the command line (-e) or in a group variable,
preferably encrypted with `ansible-vault`.

    afs_admin_principal: admin
    afs_admin_password: (undefined by default)

A administrator principal to be created by this role.
The password is not defined by default and must be set on the command line
(-e) or in a group variable, preferably encrypted with `ansible-vault`.

## OpenAFS Cell Role

Name: `openafs_cell`

Setup the top level volumes in the cell. This role is to be run on a single
client host.

### Role Variables

    afs_cell: example.com
    afs_realm: EXAMPLE.COM

Cell and realm names.

    afs_admin_principal: admin
    afs_admin_password: (not defined)
    afs_user_password:  (not defined)


A administrator credentials to create the regular users listed in `afs_users`
and the initial Kerberos password for those users.  The passwords are not
defined by default and must be set on the command line (-e) or in group
variables, preferably encrypted with `ansible-vault`.

    afs_kdc:

The Kerberos KDC hostname. This host must be a member of the `afs_kdcs` host group.

    afs_root_server:
    afs_root_part: a

The primary fileserver hostname and AFS fileserver partition id. The cell's
top-level volumes will be created on this fileserver partition.

    afs_volumes:

An optional list of top level volumes to be created and mounted in the cell.
This should be defined as a list of dictionaries of `name=<volume name>,
mtpt=<mount path>`, where `<mount path>` is relative to `/afs/<cell name>/`
and defaults to the `<volume-name>`.

    afs_users:

An optional list of AFS users to be created in the new cell. This should be
defined as list of dictionaries of `name=<username>`.

    afs_groups:

An optional list of AFS groups to be created in the new cell. This should be
defined as a list of dictionaries of `name=<group name>, members=<list of
usernames>`.

Example initial cell configuration:

    # contents of inventory/example.com/group_vars/all/cell.yaml
    # Initial top level volumes.
    afs_volumes:
      - name: test
        mtpt: test
    
    # Initial AFS users.
    afs_users:
      - name: user1
      - name: user2
      - name: user3
    
    # Initial AFS groups
    afs_groups:
      - name: group1
        members:
          - user1
          - user2
      - name: group2
        members:
          - user2
          - user3

## OpenAFS Client Role

Name: `openafs_client`

Install and configure the OpenAFS client packages.  Optionally, build and install from
source code.

### Role Variables

    afs_cell: example.com
    afs_desc: Example
    afs_realm:  EXAMPLE.COM

The Kerberos realm name, AFS cell name, and the cell organizational
description.

    afs_client_install_method: yum-kmod

The method used to install the OpenAFS client binaries. Values are:

* `yum-kmod` :  Install client packages and a pre-built kernel module
                with yum.
* `yum-dkms`:   Install client packages and kernel module sources with yum
                and build the kernel module using DKMS.
* `build`:      Build the client binaries and kernel module from source
                code. Also, install development packages in order to
                build the OpenAFS client binaries and kernel module.

    afs_openafs_client_repourl:

The URL of a yum repo containing OpenAFS client packages.

    afs_client_build_repo:
    afs_client_build_version: master
    afs_client_build_path: /usr/local/src/openafs-client

The OpenAFS git repo URL, git reference, and build scratch directory for the
`build` installation method.

    afs_cacheinfo_mount: /afs
    afs_cacheinfo_cache: /usr/vice/cache
    afs_cacheinfo_size: 50000

The OpenAFS cache configuration parameters; the AFS filesystem mount point, the
cache partition, and the cache manager cache size.  The cache partition should
already exist.

    afs_afsd_opts: -dynroot -fakestat -afsdb

The OpenAFS cache manager startup options.

## OpenAFS Server Role

Name: `openafs_server`

Install and configure the OpenAFS server packages. This role installs both the
fileserver and the database servers, which can be installed on the same hosts
or different hosts.  Optionally, build and install from source code.

This role enables OpenAFS servers to operate correctly with selinux set to
enforcing mode.

### Role Variables

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

    afs_server_install_method: yum

The method used to install the OpenAFS server binaries. Values are:

* `yum`:  Install OpenAFS server packages with yum.
* `build`: Build and install server binaries from source code.

    afs_openafs_server_repourl:

The URL of a yum repo containing OpenAFS server packages.

    afs_server_build_repo:
    afs_server_build_path: /usr/local/src/openafs-server
    afs_server_build_version: master

The OpenAFS git repo URL, git reference, and build scratch directory for the
`build` installation method.

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

## OpenAFS Devel Role

Name: `openafs_devel`

Install development packages and provide tasks to build an OpenAFS
binary distribution from source code.

### Role Variables

    afs_devel_build_server: yes

Build the server components.

    afs_devel_build_client: yes

Build the client components, including the OpenAFS kernel module.

    afs_devel_builddir: "/usr/local/src/openafs"

The path of the directory to perform the build.

    afs_devel_destdir: "/tmp/openafs"

The path of the directory to place the generated binary distribution.

    afs_devel_fetch_method: "git"

The method to obtain the source code. One of 'git', or 'none' (or 'skip')
Specify 'none' (or 'skip') to skip this stage.

    afs_devel_git_repo: "https://github.com/openafs/openafs"

The git url to be used to checkout the source code.

    afs_devel_git_ref: "master"

The git branch or tag to be checked out.

## OpenAFS Test Suite Role

Name: `openafs_robotest`

Install and configure a set of Robot Framework test suites for OpenAFS.

### Role Variables

TODO

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates


[1]: https://www.openafs.org/
[2]: https://web.mit.edu/kerberos/
