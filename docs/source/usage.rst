Usage
=====

Installation Methods
--------------------

**OpenAFS** may be installed and updated with prebuilt packages or built from
source on the remote nodes. The following installation methods are supported:

* **managed** - Install with the distro's package manager (e.g., ``yum``, ``apt``).
* **packages** - Install prebuilt packages (e.g. ``rpm``, ``dpkg``).
* **bdist** - Install a binary distribution with Transarc-style paths.
* **source** - Install from source code.
* **none** - Skip installation tasks.

Different installation methods may be used on each remote node, however the if
installing a client and server on the same node, the same installation method
must be specific for both the client and server roles.

The installation method is stored id the ``/etc/ansible/facts.d/openafs.fact``
json file on the remote node.  This file must be changed if you want to change
the installation method after OpenAFS has already been installed.


Inventory
---------

Provide an Ansible inventory file for your host configuration. Ansible
supports ``ini`` and ``yaml`` inventory files.

The **OpenAFS** ansible roles and example playbooks use the following group
name conventions:

afs_kdcs
  The Kerberos KDC server.

  Currently, only one KDC is supported. Additional KDCs can be deployed
  with custom playbooks or community supported roles.

afs_databases
  The OpenAFS database servers hosts.

afs_fileservers
  The OpenAFS fileserver hosts.

afs_clients
  The OpenAFS clients hosts.

afs_admin_client
  The OpenAFS client host used for initial cell configuration.


Note that a given host may be a member of more than one group. For example, a
given host can be in the ``afs_databases``, ``afs_fileservers``, and the
``afs_clients`` groups.


Example Inventory
^^^^^^^^^^^^^^^^^

.. code-block:: ini

   [afs_kdcs]
   kdc

   [afs_databases]
   db1
   db2
   db3

   [afs_fileservers]
   fs01
   fs02
   fs03
   fs04

   [afs_clients]
   client[01:20]

   [afs_admin_client]
   client01

   [afs_cell:children]
   afs_databases
   afs_fileservers
   afs_clients

   [afs_cell:vars]
   afs_realm = EXAMPLE.COM
   afs_cell = example.com

   [afs_clients:vars]
   afs_kdc_servers = kdc
   afs_kadmin_server = kdc
   afs_module_install_method = dkms


Cell Configuration (CellServDB)
-------------------------------

The OpenAFS cell configuration (CellServDB file) is provided as an inventory
variable or an external yaml file (with the same structure as the inventory
variable.) The cell configuration contains the list of database server IPv4
addresses.

To specify the cell configuration with an inventory variable, add the
``afs_csdb`` dictionary to your inventory for all of the hosts in your cell.
If your inventory is in ``ini`` format, then provide a ``afs_cell.yaml`` file
in the Ansible ``group_vars`` directory.

.. code-block:: yaml

   # Contents of `group_vars/afs_cell.yaml`
   afs_csdb:
     cell: example.com
     desc: My Example Cell
     hosts:
       - ip: 192.168.122.219
         name: afs02
         clone: no
       - ip: 192.168.122.154
         name: afs03
         clone: no
       - ip: 192.168.122.195
         name: afs04
         clone: no

A ``csdb.yaml`` file can be generated from a playbook and then saved for
later use. This can be especially useful when creating short lived test
cells from newly created virtual machine clusters.

.. code-block:: yaml

   # Retrieve the addresses of the database servers and generate
   # a cell configuration yaml file (csdb.yaml)
   - name: Create CellServDB
     hosts: afs_databases
     tasks:
       - include_role:
           name: openafs_contrib.openafs.openafs_common
           tasks_from: generate_csdb
         when: afs_csdb is undefined


Running playbooks
-----------------

Create a set of Ansible playbooks for your environment to deploy the OpenAFS
servers and clients. See the example playbooks in the ``playbooks`` directory
as a starting point.

Run the playbooks with ``ansible-playbook [options] <playbooks>``.

Import the ``openafs_client`` role to install and configure client machines,
and import the ``openafs_server`` role to install and configure fileserver
and database server machines. A single machine may have both a client and
server installed on it, but with the limitation the client and server
versions must match.

Use the ``openafs_volume`` module on a client machine to create and mount
the OpenAFS ``root.afs`` and ``root.cell`` volumes.  This module may also be
used to create additional volumes.

Use the ``openafs_user`` module on a client to create initial users.

See the Ansible documentation for more information on running ``ansible-playbook``.
