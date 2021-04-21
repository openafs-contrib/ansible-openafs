.. _openafs_volume_module:


openafs_volume -- Create an OpenAFS volume
==========================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create or remove a volume.

Optionally, create read-only volumes, and release the volume.

Optionally, mount the volume and set the ACL rigths in the filespace.

Volume mounting requires a client running on the remote node.

Localauth authentication may be used on server nodes, running as root. When running in this mode, volumes maybe created, but not mounted.

Keytab based authentication may be used on client nodes to mount volumes and set root directory ACLs. This requires a keytab for a user in the system:adminstrators group and a member of the UserList on all of the servers.






Parameters
----------

  state (False, str, <present>)
    ``present`` ensure the volume is present, ``absent`` ensure the volume is removed


  volume (True, str, None)
    Name of the read-write volume.


  server (optional, str, first fileserver entry found in VLDB)
    The initial volume fileserver location.

    If provided, should be the hostname or fileserver address.

    If not provided, the first fileserver address from ``vos listaddrs`` will be used.

    The volume will not be moved if it already exists on a different server.

    This option is ignored when the state is ``absent``.


  partition (optional, str, the first partition found on the fileserver)
    The initial volume partition id.

    If provided, should be the partition id; ``'a'`` ..  ``'iu'``.

    If not provided, the first partition found from ``vos listpart`` will be used.

    The volume will not be moved if it already exists on a different partition.

    This option is ignored when the state is ``absent``.


  mount (False, str, None)
    The initial mount point path.

    Should be the fully-qualified path to the mount point to be created.

    The read/write path variant will be used if it is available.

    A read/write mount point will also be created for the ``root.cell`` volume.

    The ``i`` and ``a`` ACL rights will be temporarily assigned to the mount point parent directory in order to create the mount point if those rights are missing.

    The volume containing the parent volume will be released if a mount point was created.

    The volume will be created but not mounted if the ``mount`` option is not given.

    This option is ignored when the state is ``absent``.

    This option may only be used if a client is installed on the remote node.


  acl (False, str, None)
    The access control list to be set in the volumes root directory.

    The ``acl`` option my be specified as a list of strings. Each string contains a pair of strings separated by a space. The substring names a user or group, the second indicates the access rights.

    See ``fs setacl`` for details.

    This option may only be used if a client is installed on the remote node.


  quota (False, int, 0)
    The initial volume quota.


  replicas (False, int, 0)
    The number of read-only volumes to be created, including the read-only clone on the same fileserver and partition as the read/write volume.

    The ``replicas`` option indicates the minumum number of read-only volumes desired.


  localauth (optional, bool, False)
    Indicates if the ``-localauth`` option is to be used for authentication.

    This option should only be used when running on a server.

    The ``mount`` and ``acl`` options may not be used with ``localauth``.


  auth_user (optional, str, admin)
    The afs user name to be used when ``localauth`` is False.

    The user must be a member of the ``system:administrators`` group and must be a server superuser, that is, set in the ``UserList`` file on each server in the cell.

    Old kerberos 4 '.' separators are automatically converted to modern '/' separators.

    This option may only be used if a client is installed on the remote node.


  auth_keytab (optional, str, admin.keytab)
    The path on the remote host to the keytab file to be used to authenticate.

    The keytab file must already be present on the remote host.

    This option may only be used if a client is installed on the remote node.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create afs root volume
      openafs_contrib.openafs.openafs_volume:
        state: present
        name: root.afs
        mount: /afs
        acl: "system:anyuser read"
        replicas: 3

    - name: Create cell root volume
      openafs_contrib.openafs.openafs_volume:
        state: present
        name: root.cell
        mount: /afs/example.com
        acl: "system:anyuser read"
        replicas: 3

    - name: Create a volume
      openafs_contrib.openafs.openafs_volume:
        state: present
        name: test
        mount: /afs/example.com/test
        acl:
          - "bob all"
          - "system:anyuser read"
          - "system:authuser write"

    - name: Alternate acl format
      openafs_contrib.openafs.openafs_volume:
        state: present
        name: test
        mount: /afs/example.com/test
        acl:
          bob: all
          "system:anyuser": read
          "system:authuser": write



Return Values
-------------

acl (success, list, )
  List of acl strings set in the volume root directory


mount (success, str, )
  Mount point path


volume (success, dict, )
  Volume information





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

