.. _openafs_selinux_module_module:


openafs_selinux_module -- Create and install an selinux module from input files
===============================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Build the selinux module from the given input files.






Parameters
----------

  state (optional, any, None)
    c(present) is currently the only supported state.


  name (optional, any, openafs)
    name of the selinux module


  path (optional, any, /var/lib/ansible-openafs/selinux)
    Path to the Type Enforcement (te) and File Context (fc) input files and the destination path of the output pp and mod files.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Copy the SELinux module definitions for openafs server
      become: yes
      template:
        dest: "/var/lib/ansible-openafs/selinux/{{ item }}"
        src: "{{ role_path }}/templates/{{ item }}.j2"
      with_items:
        - openafs.te
        - openafs.fc

    - name: Build SELinux module for openafs server
      become: yes
      openafs_contrib.openafs.openafs_selinux_module:
        name: openafs
        path: /var/lib/ansible-openafs/selinux



Return Values
-------------

module (success, str, /var/lib/ansible-openafs/selinux/openafs.mod)
  Path to the module


version (success, str, )
  Module version





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

