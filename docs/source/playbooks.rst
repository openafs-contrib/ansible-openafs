Playbooks
=========

The OpenAFS Ansible collection provides a set of playbooks which can be run
directly with ``ansible-playbook`` or imported into your custom playbooks with
the ``ansible.builtin.import_playbook`` module.

To run a playbook from the installed collection:

.. code-block:: console

    $ ansible-playbook openafs_contrib.openafs.<playbook> [options]

where ``<playbook>`` is the name of the playbook without the ``.yaml``
extension.  For playbooks that manage remote hosts, you will likely need to
specify an inventory file using the ``-i`` option.  The `--extra (-e)`` option
can be specified one or more times to override variable default values. See the
playbook ``vars`` section and the roles documentation for more information
about the supported variables.

Development Playbooks
---------------------

These playbooks are designed to be run on the directly on the local machine.
They are generally used for development and testing.

``local_devel.yaml``
   Install development tools on the local machine.

``local_cell.yaml``
   Install and setup Kerberos and OpenAFS clients and servers on the local
   machine to create a simple test realm and cell. This sets up a fully functional
   but non-distributed OpenAFS environment for local testing.

Deployment Playbooks
--------------------

These playbooks require an inventory file specifying the target systems to be
managed by Ansible.

``deploy_realm.yaml``
   Deploy a Kerberos server on a managed node defined in your inventory.
   This playbook also creates principals and keytabs for the AFS service,
   an admin user, and a regular user.

``deploy_cell.yaml``
   Deploy OpenAFS clients and servers on one or more managed nodes and ensure
   the cell has been created. This includes configuring the clients and servers
   and creating the top level volumes. This playbook assumes the Kerberos realm
   is already present and keytabs are available for the AFS service key, an admin
   user, and one regular user.

Example Inventory
-----------------

This is an example inventory file for a site with 3 servers and 2 clients.

The ``deploy_realm`` playbook will install the Kerberos KDC on ``server1`` and
create the Kerberos principals and keytabs for the AFS service, the admin user,
and a regular user.

The ``deploy_cell`` playbook will install the OpenAFS fileserver and database
servers on ``server1``, ``server2``, and ``server3``, and create the
``/vicepa`` and ``/vicepb`` "fake" partitions on the servers for testing.  The
OpenAFS kernerl module and client will be installed on ``client1`` and
``client2``.

.. code-block:: yaml

    all:
      hosts:
        server1:
          ansible_host: 192.168.56.11
          afs_server_netinfo: 192.168.56.11
        server2:
          ansible_host: 192.168.56.12
          afs_server_netinfo: 192.168.56.12
        server3:
          ansible_host: 192.168.56.13
          afs_server_netinfo: 192.168.56.13
      vars:
        afs_install_method: managed
        afs_module_install_method: kmod
        afs_cell: example.com
        afs_realm: EXAMPLE.COM
        afs_user: alice
        afs_admin: admin
        afs_csdb:
          cell: example.com
          desc: Example cell
          hosts:
            - ip: 192.168.56.11
              name: server1
              clone: false
            - ip: 192.168.56.12
              name: server2
              clone: false
            - ip: 192.168.56.13
              name: server3
              clone: false
    afs_kdcs:
      hosts:
        server1:
    afs_databases:
      hosts:
        server1:
        server2:
        server3:
    afs_fileservers:
      hosts:
        server1:
        server2:
        server3:
      vars:
        afs_pseudo_partitions:
          - a
          - b
    afs_admin_client:
      hosts:
        client1:
    afs_clients:
      hosts:
        client2:
