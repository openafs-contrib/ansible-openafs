.. _openafs_get_install_paths_module:


openafs_get_install_paths -- Detect installation paths
======================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather the paths to installed OpenAFS programs from the installed packages






Parameters
----------

  package_mgr_type (optional, any, rpm)
    The package manager type on this remote node.

    Supported values are ``rpm`` and ``apt``









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Get installation paths
      openafs_contrib.openafs.openafs_get_install_paths:
        package_manager_type: apt
      register: install_results





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

