Installation
============

Requirements
------------

This collection requires Ansible (``ansible-core``) 2.16 or later (included in
the ``ansible`` package version 9 and later).

The target machines to be managed must be reachable via ``ssh`` and must have
a Python version supported by your version of ``ansible-core`` already
installed. Ansible is not required on the target machines.

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

See :doc:`development` to install the **OpenAFS Ansible Collection** from
source code.
