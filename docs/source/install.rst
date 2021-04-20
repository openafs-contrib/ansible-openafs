Installation
============

Galaxy
------

To install the OpenAFS Ansible Collection from Ansible Galaxy:

.. code-block:: console

   $ ansible-galaxy collection install openafs_contrib.openafs

Note: Ansible 2.9 or better is required to install collections.

Source code
-----------

To install the OpenAFS Ansible Collection from a source code checkout:

.. code-block:: console

   $ cd <your-project-directory>
   $ mkdir -p ansible_collections/openafs_contrib
   $ cd ansible_collections/openafs_contrib
   $ git clone https://github.com/openafs-contrib/ansible-openafs openafs
   $ cd openafs
   $ make init
   $ source .venv/bin/activate
   $ make install
