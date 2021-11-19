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
are available, installed from pre-built binaries created by separate process or
playbook (see the ``openafs_devel`` role and ``build.yml`` example playbook), or
installed from source code from a git repository.

The names and addresses of the OpenAFS databases to setup the server CellServDB
files must be provided by the  ``afs_csdb`` inventory variable, or a separate
yaml file, the path of which is specified by the ``afs_csdb_file`` variable.

Variables
---------

afs_security_model
  The system security model. Should be ``none`` or ``selinux``.
  When set to ``selinux``, the selinux contexts for OpenAFS will be updated
  to allow the server to run with selinux enabled.

  default: none

afs_is_fileserver
  Indicates the node is a fileserver. By default, ``afs_is_fileserver`` is
  true when the node is a member of the ``afs_fileservers`` group.

  default: check ``afs_fileservers`` group

afs_is_dbserver
  Indicates the node is a database server. By default, ``afs_is_dbserver`` is
  true when the node is a member of the ``afs_databases`` group.

  default: check ``afs_databases`` group

afs_fileserver_type
  Determines the fileserver type the node is a fileserver.
  Valid values are ``fs`` (legacy File Server) or ``dafs`` (modern
  Demand Attach FileServer).

  Default: ``dafs``

afs_server_cold_start
  Treat this play as the initial installation of the servers, in which case wait
  for the database servers to reach quorum before starting the fileservers. This
  avoids a 5 minute delay for the fileservers to retry registration with the VLDB.

  Set to **yes** (True) to defer fileserver startup until database quorum is detected.

  Set to **no** (False) to skip cold start checks and tasks.

  Default is to detect by checking for the presence of the ``BosConfig`` file.

afs_pseudo_partitions
  The list of pseudo fileserver vice partitions to be created. Pseudo partitions
  are directories in the root partition, with the special ``AlwaysAttach`` file to
  indicate they should be attached by the fileserver. This feature is intended for
  testing. Specify the pseudo partitions by partition id, that is ``a``, ``b``, etc.

  default: []

afs_create_root
  Ensure the ``root.afs`` and ``root.cell`` volumes exist. The ``root.afs``
  volume must exist before starting clients without the ``--dynroot`` option.
  Modern clients typically are started with the ``--dynroot`` option and so
  are able to start without the presences of the root volumes.

  default: yes

afs_server_netinfo
  A single string (or list of strings) to set the contents of the server
  ``NetInfo`` configuration file. This file specifies which addresses or
  subnetworks should be used for server communication.  A specific address can
  be forced by specifying a ``f`` prefix.

afs_server_netrestrict
  A single string, or a list of strings, to set the contents of the server
  ``NetRestrict`` configuration file. This file specifies which addresses or
  subnetworks should be excluded from server communications.

afs_service_keytab
  The AFS service Kerberos keytab file. This is the file path of the keytab file
  on the controller, which should be protected with ``ansible-vault``.  The
  keytab file will be uploaded to the server nodes unless
  ``afs_service_keytab_externally_managed`` is true.  The keys will be imported with
  the ``akeyconvert`` tool on servers running OpenAFS 1.8.x (or greater).  The
  uploaded keytab file will be named ``rxkad.keytab`` for compatibility with
  OpenAFS 1.6.x.

  default: <afs_cell_files>/afs.<afs_cell>.keytab

afs_service_keytab_externally_managed
  When true, the AFS service Kerberos keytab file is managed with an external
  secrets management tool.

  default: false

afs_bosserver_restricted_mode
  Run the BosServer in restricted mode.  This mode improves the security of the
  BosServer by prohibiting bos commands which are not needed for routine
  operation.

  The following bos commands are not available when the BosServer running in
  restricted mode: ``bos exec``, ``bos uninstall``, ``bos install``, ``bos
  create``, ``bos delete``, ``bos prune``, and the ``bos getlog`` is limited to
  server log files.

  default: yes

afs_bosserver_bnodes
  Extra ``bnode`` entries to add to ``BosConfig``.

  default: []

  example:

.. code-block:: yaml

    afs_bosserver_bnodes:
      - name: backup
        type: cron
        goal: 1
        parm:
          - /usr/afs/backup/clones/lib/backup.csh daily
          - 05:00

afs_bosserver_opts
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
