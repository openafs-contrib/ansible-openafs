.. _openafs_install_bdist_module:


openafs_install_bdist -- Install OpenAFS binaries built from source
===================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Install OpenAFS binaries built from source code. This module will copy the files in a binary distribution tree to the system directories. Run this module as root. The paths to the installed commands are saved as Ansible local facts.







Parameters
----------

  path (True, path, None)
    Absolute path to the installation file tree to be installed.



  exclude (optional, list, None)
    List of file patterns to be excluded.










Examples
--------

.. code-block:: yaml+jinja

    
    - name: Build OpenAFS from source
      openafs_contrib.openafs.openafs_build:
        projectdir: ~/src/openafs
        target: install
        path: /tmp/openafs/bdist

    - name: Install OpenAFS binaries as root
      become: yes
      openafs_contrib.openafs.openafs_install:
        path: /tmp/openafs/bdist
        exclude: /usr/vice/etc/*



Return Values
-------------

msg (always, string, Install completed)
  Informational message.


files (success, list, ['/usr/bin/pts', '/usr/sbin/vos'])
  Files installed


excluded (success, list, ['/usr/vice/etc/afs.conf'])
  Files excluded from the installation


commands (success, dict, {'vos': '/usr/sbin/vos', 'pts': '/usr/bin/pts'})
  Command paths


logfiles (always, list, ['/tmp/logs/install.log'])
  Log files written for troubleshooting





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

