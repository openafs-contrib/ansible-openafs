Usage
=====

Installation Methods
--------------------

**OpenAFS** may be installed with prebuilt packages or built from source
on the remote nodes. The following installation methods are supported:

* **managed** - Install with the distro's package manager (e.g., ``yum``, ``apt``).
* **packages** - Install prebuilt packages (e.g. ``rpm``, ``dpkg``).
* **bdist** - Install binary distribution with modern or Transarc-style paths.
* **sdist** - Source distribution
* **scm** - Checkout source code with ``git`` then build and install binaries.
* **none** - Skip installation tasks; assume manual installation.

Different installation methods may be used on each remote node, however the
if installing a client and server on node, the installation method must be
the same for the client and server roles.

The last installation method is stored on the remote node in a local fact
file. Manual intervention is required if you want to change the installation
method after an initial Ansible play to deploy **OpenAFS**.

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

See the Ansible documentation for more information on running ``ansible-playbook``.


Example playbooks
^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   # realm.yml -- Create the Kerberos realm and initial principals.

   - name: Create a Kerberos realm
     hosts: afs_kdcs
     collections:
       - openafs_contrib.openafs
     tasks:
       - import_role:
           name: openafs_krbserver

       - import_role:
           name: openafs_common

       - name: Create AFS service key.
         become: yes
         openafs_principal:
           state: present
           principal: "afs/{{ afs_cell }}"
           encryption_types:
             - aes128-cts
             - aes256-cts
         register: service_key_results

       - name: Create admin principal.
         become: yes
         openafs_principal:
           state: present
           principal: "{{ afs_admin }}"
           acl: "*"
         register: admin_princ_results

       - name: Create user principal.
         become: yes
         openafs_principal:
           state: present
           principal: "{{ afs_user }}"
         register: user_princ_results

       - name: Download keytabs.
         become: yes
         fetch:
           flat: yes
           src: "{{ item }}"
           dest: "{{ afs_cell_files }}/"
         with_items:
           - "{{ service_key_results.keytab }}"
           - "{{ admin_princ_results.keytab }}"
           - "{{ user_princ_results.keytab }}"
         register: download_results

       - name: Downloaded.
         debug:
           msg: "{{ download_results.results | map(attribute='dest') | list }}"

.. code-block:: yaml

   # openafs.yml - Deploy the OpenAFS servers and clients

   - name: Install servers
     hosts: afs_databases:afs_fileservers
     collections:
       - openafs_contrib.openafs
     tasks:
       - import_role:
           name: openafs_server

   - name: Install clients
     hosts: afs_clients
     collections:
       - openafs_contrib.openafs
     tasks:
       - import_role:
           name: openafs_krbclient

       - import_role:
           name: openafs_client

.. code-block:: yaml

   # newcell.yml - Create the top-level cell volumes and some initial users.

   - name: New cell
     hosts: afs_admin_client
     collections:
       - openafs_contrib.openafs
     tasks:
       - import_role:
           name: openafs_common

       - name: Create top-level volumes
         openafs_volume:
           state: present
           name: "{{ item.name }}"
           mount: "{{ item.mount }}"
           acl: "{{ item.acl }}"
           auth_user: "{{ afs_admin }}"
           auth_keytab: "{{ afs_admin }}.keytab"
           replicas: 3
         with_items:
           - name: root.afs
             mount: /afs
             acl: "system:anyuser read"

           - name: root.cell
             mount: /afs/{{ afs_cell }}
             acl: "system:anyuser read"

           - name: projects
             mount: /afs/{{ afs_cell }}/projects
             acl:
               - "system:anyuser read"
               - "system:authuser write"

       - name: Create test user
         openafs_user:
           name: "{{ afs_user }}"
           id: "{{ afs_user_id }}"
           group: tester
           auth_user: "{{ afs_admin }}"
           auth_keytab: "{{ afs_admin }}.keytab"
