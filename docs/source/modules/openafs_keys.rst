.. _openafs_keys_module:


openafs_keys -- Add kerberos service keys with asetkey
======================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Import the service keys from a keytab file using the OpenAFS ``asetkey`` utility.

This module uses ``asetkey`` rather than the newer ``akeyconvert`` since ``akeyconvert`` is not available on all platforms yet.

Before running this module, be sure ``asetkey`` is installed

The ``asetkey`` program requires the server ``CellServDB`` and ``ThisCell`` files to be present.

A keytab file containing the service keys must be copied to the server.






Parameters
----------

  state (False, str, None)
    c(present) to ensure keys are present in the keyfile(s)


  keytab (True, path, None)
    path to the keytab file on the remote node


  cell (True, str, None)
    AFS cell name


  realm (False, str, uppercase of the cell name)
    Kerberos realm name


  asetkey (False, path, Search the local facts, search the path.)
    asetkey program path









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Upload service keytab
      become: yes
      copy:
        src: "files/example.keytab"
        dest: "/usr/afs/etc/rxkad.keytab"
        mode: 0600
        owner: root
        group: root

    - name: Add service keys
      become: yes
      openafs_contrib.openafs.openafs_keys:
        state: present
        keytab: /usr/afs/etc/rxkad.keytab
        cell: example.com



Return Values
-------------

asetkey (success, path, )
  asetkey path found


have_extended_keys (success, bool, )
  Indicates if extended keys are supported.


keys (success, list, )
  keys found in the keytab file


imported (success, list, )
  Imported key versions


service_principal (success, str, )
  kerberos service principal





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

