.. _openafs_get_install_paths_module:


openafs_get_install_paths -- Detect installation paths from package installation.
=================================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Detect the paths of installed OpenAFS programs and detect configuration directories from installed man pages.

Supports rpm and deb packaging.






Parameters
----------

  package_mgr_type (optional, any, autodetect)
    The package manager type on the node.

    Supported values are ``rpm`` and ``deb``.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Get installation paths
      openafs_contrib.openafs.openafs_get_install_paths:
      register: results

    - debug:
        msg: >
          Bins are {{ results.bins }}
          Dirs are {{ results.dirs }}





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

