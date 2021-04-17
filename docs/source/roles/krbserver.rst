openafs-krbserver - Kerberos Server Role
========================================

Description
-----------

Install and configure the MIT Kerberos master KDC on single host, create the
Kerberos database and the first administrator principal.

Variables
---------

afs_realm
  The Kerberos realm name.

  Default: EXAMPLE.COM

afs_krb_master_password
  The secret Kerberos database master password. The password is random by
  default. If a value is provided, it should be encrypted with
  ``ansible-vault``.

  Default: <random>

afs_krb_admin_principal
  A administrator principal to be created by this role. A keytab is always
  created for this principal, even when the password is also provided.

  Default: root/admin

afs_krb_admin_password
  The admin principal password. This password random by default.
  If a value is provided, it should be encrypted with ``ansible-vault``.

  Default: <random>
