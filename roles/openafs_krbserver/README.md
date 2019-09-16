# Ansible Role: Kerberos server

Install and configure the MIT Kerberos master KDC on single host, create the
Kerberos database and the first administrator principal.

## Role Variables

    afs_realm: EXAMPLE.COM

The Kerberos realm name.

    afs_kerberos_master_password: (random by default)

The secret Kerberos database master password. The password is a random string
by default. It should be set on the command line (-e) or in a group variable,
preferably encrypted with `ansible-vault`.

    afs_admin_principal: admin
    afs_admin_password: (undefined by default)

A administrator principal to be created by this role.  The password is not
defined by default and must be set on the command line (-e) or in a group
variable, preferably encrypted with `ansible-vault`.

##  License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates
