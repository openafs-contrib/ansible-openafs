Installation
============

Requirements
------------

This collection requires Ansible 2.10 or later. Ansible may be installed with
your package manager or with Python ``pip``. A Python virtualenv is
recommended if you are installing packages with ``pip``.

The target machines to be managed must be reachable via ``ssh`` and must have
Python already installed. Ansible is not required on the target machines.

Galaxy
------

The **OpenAFS Ansible Collection** is available on `Ansible Galaxy`_. Install
the collection with the ``ansible-galaxy`` command:

.. _`Ansible Galaxy`: https://galaxy.ansible.com/openafs_contrib/openafs

.. code-block:: bash

   ansible-galaxy collection install openafs_contrib.openafs

Use the ``--force`` option to overwrite the currently installed version to
upgrade if you already have an older version of the collection installed.

Source
------

Install the **OpenAFS Ansible Collection** from source code with the
following commands:

.. code-block:: bash

   mkdir -p collections/ansible_collections/openafs_contrib
   cd collections/ansible_collections/openafs_contrib
   git clone https://github.com/openafs-contrib/ansible-openafs openafs
   cd openafs
   tox -e install
