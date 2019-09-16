# Ansible Role: OpenAFS cell

Set up the top level volumes in the cell, and optionally, the initial volumes,
users, and groups for the new cell. This role is to be run on a single client
host, after the servers and at least one client has been installed.

## Role Variables

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


## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates
