openafs_devel - OpenAFS Development Role
========================================

Description
-----------

Install development packages needed to build OpenAFS userspace
binaries.

Variables
---------
afs_devel_oracle_key
  Fully qualified path of your Oracle Developer Studio key on the controller.
  Used to install Oracle Developer Studio when the remote node operating system
  is Solaris.

  Default: ``~/.certs/pkg.oracle.com.key.pem``

afs_devel_oracle_cert
  Fully qualified path of your Oracle Developer Studio certificate on the
  controller. Used to install Oracle Developer Studio when the remote node
  operating system is Solaris.

  Default: ``~/.certs/pkg.oracle.com.certificate.pem``
