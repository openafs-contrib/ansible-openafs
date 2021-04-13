.. _openafs_principal_module:


openafs_principal -- Create principals and keytab files
=======================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create a kerberos principal on a primary KDC using ``kadmin.local`` and export the keys to a keytab file on the KDC. The keytab may be transfered to remote nodes with ``syncrhonize`` or encrypted with ``ansible-vault`` then downloaded to the controller for distribution in subsequent plays. This

If the state is ``present``, then a principal is added if it is not already present and a keyfile is created. The initial password may be specified with the ``password`` parameter, otherwise a random key is generated. The key is not randomized when the keytab is generated.

If the state is ``absent``, then the principal and keytab files are removed if present.

If the state is ``rekey``, and the princical already exists, then new keys are generated with the given ``enctypes`` and are added to the existing keytab file. The updated keytab file must be redistributed servers to avoid authentication failures. If the state is ``rekey`` and the principal is not present, a principal is created and a keytab is generated as if the state is ``present``.

Keytabs for the principals created by the module are stored in the ``keytabs`` directory on the KDC, readable by root. The default path is ``/var/lib/ansible-openafs/keytabs``.

Currently, this module does not check the keytabs to verify if the key versions numbers are in sync with the database. If the principal's password is changed manually, remove the keytab file on the kdc before running with the ``present`` state to generate a new keytab.



Requirements
------------
The below requirements are needed on the host that executes this module.

- The Kerberos realm has been created.
- ``kadmin.local`` is installed and in the PATH.



Parameters
----------

  state (False, str, present)
    ``present`` ensure the principal and keytab file exist.

    ``absent`` ensure the principal and keytab file are removed.

    ``rekey`` generate new keys and add them to the keytab file.


  principal (True, str, None)
    Kerberos principal name.

    The name should be provided without the REALM component.

    Old kerberos 4 '.' separators are automatically converted to modern '/' separators.


  enctypes (False, list, See C(kadmin))
    Kerberos encryption and salt types.

    See ``kadmin`` documenation for possible values.


  rekey (False, bool, False)
    Generate new key versions.


  acl (False, str, None)
    Administrative permissions


  keytab_name (optional, str, principal name with '/' characters replaced by '.' characters.)
    Alternative keytab name.


  keytabs (False, path, /var/lib/ansible-openafs/keytabs)

  kadmin (False, path, search PATH)








Examples
--------

.. code-block:: yaml+jinja

    
    - name: Create an AFS service key
      become: yes
      openafs_contrib.openafs.openafs_principal:
        principal: afs/example.com
        encryption_types:
          - aes128-cts:normal
          - aes256-cts:normal
      register: service_key

    - name: Download the keytab to controller for distribution
      become: yes
      fetch:
        flat: yes
        src: "{{ service_key.keytab }}"
        dest: "rxkad.keytab"

    - name: Generate new keys
      become: yes
      openafs_contrib.openafs.openafs_principal:
        state: rekey
        principal: afs/example.com

    # Requires an old version of Kerberos.
    - name: Obsolete DES key for testing
      become: yes
      openafs_contrib.openafs.openafs_principal:
        state: present
        service: afs
        principal: afs/broken.com
        enctype: des-cbc-crc:afs3

    - name: Create some user principals
      become: yes
      openafs_contrib.openafs.openafs_principal:
        state: present
        principal: "{{ item }}"
        password: "{{ initial_password }}
      with_items:
        - alice
        - bob
        - charlie



Return Values
-------------

metadata (success, list, )
  Principal metadata from ``get_principal``


debug (always, list, )
  kadmin commands executed and output


kadmin (always, path, /sbin/kadmin.local)
  kadmin executable path


keytab (success, path, /var/lib/ansible-openafs/keytabs/afs.example.com.keytab)
  Path of the generated keytab on the remote node.


principal (success, str, afs/example.com)
  principal name


realm (, str, EXAMPLE.COM)
  realm name





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

