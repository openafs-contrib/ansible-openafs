openafs_devel - OpenAFS Development Role
========================================

Description
-----------

Install development packages needed to build OpenAFS clients and server
binaries.

Variables
---------

afs_devel_kernel_headers
  Install kernel headers matching the currently running kernel version.
  This is required to build a kernel module, either with dkms or with
  the OpenAFS build system.

  Default: yes

afs_devel_allow_kernel_update
  When the kernel headers cannot be installed for the currently running
  kernel version, automatically update the kernel and reboot.

  Default: no

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
