.. _openafs_user_module:


openafs_user -- Create an OpenAFS user
======================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create or remove a user.

Optionally create new groups and add the user to groups.

Localauth authentication may be used on server nodes, running as root.

Keytab based authentication may be used on client nodes. This requires a keytab for a user in the system:adminstrators group and a member of the UserList on all of the database servers.






Parameters
----------

  state (optional, str, present)
    ``present`` create user and groups when not present

    ``absent`` remove user when not present


  user (True, str, None)
    The OpenAFS username.


  id (False, int, 0)
    The OpenAFS pts id.

    The next available id will be selected if omitted or 0.


  groups (False, list, None)
    The OpenAFS group names the user is a member.

    Non-system groups will be created.


  localauth (optional, bool, False)
    Indicates if the ``-localauth`` option is to be used for authentication.

    This option should only be used when running on a server.


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

    
    - name: Create users
      openafs_contrib.openafs.openafs_user:
         name: "{{ item }}"
         group: tester
      with_items:
        - alice
        - bob
        - charlie



Return Values
-------------

user (, dictionary, )
  User information.





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

