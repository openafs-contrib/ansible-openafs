Installation
============

Requirements
------------

This collection requires Ansible 2.10 or later to be installed on the Ansible
controller. Ansible may be installed with your package manager or with Python
``pip``.

Target clients and server machines must be reachable via ``ssh`` and must
have python installed. Ansible is not required on target machines.

Galaxy Installation
-------------------

Install the **OpenAFS Ansible Collection** from Ansible Galaxy with the
command:

.. code-block:: console

   $ ansible-galaxy collection install openafs_contrib.openafs

Source Code Installation
------------------------

Install the **OpenAFS Ansible Collection** from source code with the
following commands:

.. code-block:: console

   $ cd <your-project-directory>
   $ mkdir -p ansible_collections/openafs_contrib
   $ cd ansible_collections/openafs_contrib
   $ git clone https://github.com/openafs-contrib/ansible-openafs openafs
   $ cd openafs
   $ make init
   $ source .venv/bin/activate
   $ make install

The directory structure show above is required for proper operation of the
molecule unit tests and the document generation.
