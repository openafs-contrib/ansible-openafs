.. _openafs_wait_for_quorum_module:


openafs_wait_for_quorum -- Wait for the dbserver connection and quorum
======================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Wait until the VLDB and PRDB database elections are completed and a sync site is set.












Examples
--------

.. code-block:: yaml+jinja

    
    - name: Wait for database quorum
      become: yes
      openafs_contrib.openafs.openafs_wait_for_quorum:
        sleep: 10
        timeout: 600
      when:
        - afs_is_dbserver





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

