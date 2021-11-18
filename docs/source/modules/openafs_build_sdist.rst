.. _openafs_build_sdist_module:


openafs_build_sdist -- Create OpenAFS source distribution archives from a git repo.
===================================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create OpenAFS source and document source distribution archives from a git checkout.



Requirements
------------
The below requirements are needed on the host that executes this module.

- git
- autoconfig
- automake
- libtools
- tar
- gzip
- bzip2
- md5sum
- pod2man



Parameters
----------

  sdist (True, path, None)
    The path on the remote node to write the source distribution files.

    This path will be created if it does not exist.


  topdir (optional, path, C(openafs))
    git project directory on the remote node.


  logdir (optional, path, I(topdir)/.ansible)
    The path to write build log files on the remote node.


  tar (optional, path, detected)
    ``tar`` program path


  git (optional, path, detected)
    ``git`` program path


  gzip (optional, path, detected)
    ``gzip`` program path


  bzip2 (optional, path, detected)
    ``bzip2`` program path


  md5sum (optional, path, detected)
    ``md5sum`` program path









Examples
--------

.. code-block:: yaml+jinja

    
    - import_role:
        name: openafs_devel

    - name: Checkout source.
      git:
        repo: "git://git.openafs.org/openafs.git"
        version: "openafs-stable-1_8_8"
        dest: "openafs"

    - name: Make source distribution files.
      openafs_build_sdist:
        topdir: "openafs"
        sdist: "openafs/packages"



Return Values
-------------

version (always, dict, )
  OpenAFS version


files (always, list, )
  The list of sdist files created on the remote node.





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

