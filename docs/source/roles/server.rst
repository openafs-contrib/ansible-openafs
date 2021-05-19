openafs_server - OpenAFS Server Role
====================================

Description
-----------

Install and configure OpenAFS servers. This role installs both the fileserver
and the database servers, which can be installed on the same hosts or different
hosts.

This role configures the system to allow OpenAFS servers operate correctly in
selinux enforcing mode when installing from RPM packages.

Requirements
------------

A Kerberos realm is required before creating the OpenAFS services. This can be
a pre-existing realm or can be created with the ``openafs_krbserver`` role.  A
service principal is required and must be exported to a keytab file. See the
``realm.yml`` example playbook.

The servers may be installed from the distribution package manager if packages
are available, installed from prebuilt binaries created by separate process or
playbook (see the ``openafs_devel`` role and ``build.yml`` example playbook), or
installed from source code from a git repository.

The names and addresses of the OpenAFS databases to setup the server CellServDB
files must be provided by the  ``afs_csdb`` inventory variable, or a separate
yaml file, the path of which is specified by the ``afs_csdb_file`` variable.

Variables
---------

afs_fileserver_type
  Determines which fileserver variation is setup when the host is a member of
  the ``afs_fileservers`` group. May be the legacy OpenAFS fileserver
  (``fs``), or the modern demand-attach fileserver (``dafs``). The
  demand-attach (``dafs``) variant is the default.

  Default: ``dafs``

afs_server_cold_start
  Treat this play as the initial installation of the servers, in which case wait
  for the database servers to reach quorum before starting the fileservers. This
  avoids a 5 minute delay for the fileservers to retry registration with the VLDB.

  Set to **yes** (True) to defer fileserver startup until database quorum is detected.

  Set to **no** (False) to skip cold start checks and tasks.

  Default is to detect by checking for the presence of the ``BosConfig`` file.

afs_server_netinfo
  A single string, or a list of strings, to set the contents of the server
  ``NetInfo`` configuration file. This file specifies which addresses or
  subnetworks should be used for server communication.  A specific address can
  be forced by specifying a ``f `` prefix.

afs_server_netrestrict
  A single string, or a list of strings, to set the contents of the server
  ``NetRestrict`` configuration file. This file specifies which addresses or
  subnetworks should be excluded from server communications.

afs_bosserver_opts:
  The ``bosserver`` command line options.

afs_ptserver_opts
  The ``ptserver`` command line options.

afs_vlserver_opts
  The ``vlserver`` command line options.

afs_dafileserver_opts
  The ``dafileserver`` command line options.

afs_davolserver_opts
  The ``davolserer`` command line options.

afs_salvageserver_opts
  The ``salvageserver`` command line options.

afs_dasalvager_opts
  The ``dasalvager`` command line options.

afs_fileserver_opts
  The ``fileserver`` command line options.

afs_volserver_opts
  The ``volserver`` command line options.

afs_salvager_opts
  The ``salvager`` command line options.
