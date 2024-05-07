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
or a separate yaml file, the path of which is specified by the ``afs_csdb_file``
variable.

Variables
---------

See ``openafs_common`` for included common variables.

afs_module
  OpenAFS kernel module name, ``openafs`` or ``libafs``. Default: ``openafs``

afs_module_install_method
  Specifies the kernel module installation method on RPM-based systems.
  Must be one of: ``dkms``, ``kmod``, or ``kmp``.

  Default: ``dkms``

afs_module_enable_preload
  Specifies if the role should attempt to preload the OpenAFS module before the
  client service is started.

  Default: no

afs_mountpoint
  The AFS filesystem mount point. This value is written to the ``cacheinfo``
  file.

  Default value is auto-detected from the ``cacheinfo`` file installed by
  packages.

  Default: auto-detected, fallback to ``/afs``

afs_cachedir
  The path to the OpenAFS cache directory.  This value is written to the
  ``cacheinfo`` file.

  When installing the client from packages, the default value is detected from
  the packaged ``cacheinfo`` file.

  When installing the client from source, the default value is
  ``/var/cache/openafs`` when the client was build with modern installation
  paths, otherwise the default value is ``/usr/vice/cache`` if the client was
  built with the Transarc compatibility paths.

  Default: auto-detected, fallback to ``/var/cache/openafs``

afs_cachesize
  The size of the OpenAFS cache. This value is written to the ``cacheinfo`` file.

  Default value is auto-detected from the ``cacheinfo`` file installed by
  packages.

  Default: auto-detected, fallback to 50000

afs_afsd_opts
  The ``afsd`` command line arguments to override the value provided
  by the client installation package.

  Default: auto-detected

afs_client_netinfo
  A single string, or a list of strings, to set the contents of the client
  ``NetInfo`` configuration file.

afs_client_netrestrict
  A single string, or a list of strings, to set the contents of the client
  ``NetRestrict`` configuration file.
