.. _openafs_selinux_relabel_module:


openafs_selinux_relabel -- Relabel selinux context for server files
===================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Relabel the server directories after the files have been installed and the configuration files updated.

Relabel the partition directories and the AlwaysAttach file, when present.

Safe the list of directories relabelled in the openafs local facts file to avoid running restorecon on subsequent plays.












Examples
--------

.. code-block:: yaml+jinja

    
    - name: Relabel
      become: yes
      openafs_contrib.openafs.openafs_selinux_relabel:





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

