# Ansible Role: OpenAFS common

Common definitions for OpenAFS clients and servers.

## Role Variables

    afs_cell: example.com

The OpenAFS cell name.

    afs_realm: EXAMPLE.COM

The Kerberos realm name. Defaults to the uppercased cell name.

    afs_csdb: (undefined by default)

The CellServDB information for this cell. Example:

    afs_csdb:
      cell: example.com
      desc: Cell name
      hosts:
        - ip: 192.168.122.219
          name: afs02
          clone: no
        - ip: 192.168.122.154
          name: afs03
          clone: no
        - ip: 192.168.122.195
          name: afs04
          clone: no

The `afs_csdb` should provided in your inventory. If not defined, the
`afs_csdb` is read from the external yaml file located at `afs_csdb_file`.

    afs_csdb_file: {{ afs_cell_files }}/csdb.yaml

The path to the enternal yaml file containing CellServDB information for the
cell. This file is read when the `afs_csdb` is not defined in the inventory.
The `afs_csdb_file` can be created in a playbook with the `generate_csdb`
task. This can be useful in to automatically create a usable CellServDB file
in a test environment.

The CellServDB information for the cell. This must be provided as a inventory
variable or an external yaml file, the path specifed by `afs_csdb_file`.

    afs_admin: <username>.admin

An adminstrative user name. This is the `pts` user name, for example: `jdoe.admin`
The default value is `{{ ansible_user }}.admin`.

    afs_user: <username>
    afs_user_id: <id>

A regular user name and pts id. The default value is `ansible_user` and
the default id is `ansible_user_uid`. Set `afs_user_id` to 0 to let the
ptserver select the next available id.

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
