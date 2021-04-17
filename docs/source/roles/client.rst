openafs_client - OpenAFS Client Role
====================================

Description
-----------

Install and configure OpenAFS clients.

Requirements
-------------

Unless DNS SRV records have been configured to supply the OpenAFS database
server addresses, the names and addresses of the OpenAFS databases to setup the
server CellServDB files must be provided by the ``afs_csdb`` inventory variable,
or a separate yaml file, the path of which is specifed by the ``afs_csdb_file``
variable.

Variables
---------

See ``openafs_common`` for included common variables.

afs_module
  OpenAFS kernel module name, ``openafs`` or ``libafs``. Default: ``openafs``

afs_module_install_method
  Specifies the kernel module installation method on RPM-based systems, ``dkms`` or
  ``kmod``. Default: ``dkms``

afs_mountpoint
  The AFS filesystem mount point. Default: ``/afs``

afs_cachedir
  The path to the AFS cache. Default: ``/usr/vice/cache``

afs_cachesize
  The size of the AFS cache. Default: 50000

afs_afsd_opts
  The ``afsd`` command line arguments. Default: ``-dynroot -fakestat -afsdb``
