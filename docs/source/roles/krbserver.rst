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

afs_kdc_servers
  A comma separated list of kdc host names to be set in the krb5.conf file.
  If this variable is not defined, the hostname of the hosts in the
  ``afs_kdcs`` inventory group are used. If that group is not defined, the kdcs
  are not defined for the realm in the krb5.conf file and it is assumed they
  are defined as SRV records in DNS.

  Default: hosts in the ``afs_kdcs`` group

afs_kadmin_server
  The host name of the kadmin server to be set in the krb5.conf file. If this
  variable is not defined, the first host name in the ``afs_kdcs`` inventory
  group is used. If that group is not defined, the kadmin server hostname is
  not set in the krb5.conf file and it is assumed to be defined as SRV
  records in DNS.

  Default: undefined

afs_krb_dns_lookup_kdc
  Define if dns_lookup_kdc mode is enabled/disabled via true/false. If this
  variable is not defined, no entry will be set which is the same like
  dns_lookup_kdc = true.

  Default: undefined

afs_krb_max_life
  KDC max ticket life.

  Default: 10h 0m 0s

afs_krb_max_renewable_life
  KDC max renewable life.

  Default: 7d 0h 0m 0s

afs_krb_supported_enctypes
  KDC supported enctypes. Specify as a list of enctype:salt values.

  Default: ['aes256-cts-hmac-sha1-96:normal', 'aes128-cts-hmac-sha1-96:normal']

afs_krb_default_principal_flags
  KDC default principal flags.

  Default: +preauth
