openafs_krbclient - Kerberos Client Role
========================================

Description
-----------

Install and configure Kerberos workstation packages.

Variables
---------

afs_realm
  The Kerberos realm name.

  Default: EXAMPLE.COM

afs_kdc_servers
  A comma separated list of kdc host names to be set in the krb5.conf file.
  If this variable is not defined, the hostname of the hosts in the
  ``afs_kdcs`` inventory group are used. If that group is not defined, the kdcs
  are not defined for the realm in the krb5.conf file and it is assumed they
  are defined as SRV records in DNS.

afs_kadmin_server
  The host name of the kadmin server to be set in the krb5.conf file. If this
  variable is not defined, the first host name in the `afs_kdcs` inventory
  group is used. If that group is not defined, the kadmin server hostname is
  not set in the krb5.conf file and it is assumed to be defined as SRV
  records in DNS.

  Defualt: undefined
