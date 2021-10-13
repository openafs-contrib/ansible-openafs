.. _openafs_build_redhat_rpms_module:


openafs_build_redhat_rpms -- Build OpenAFS RPM packages for RedHat family distributions.
========================================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Build OpenAFS source and binary RPM packages for RedHat family distributions from an OpenAFS source distibution.

The source distribution files must be already present in the *sdist* directory on the remote node. The source distribution files can transferred to the remote node or may be created by running ``make-release`` in a git checkout on remote node.

The :ref:`openafs_build_redhat_rpms <openafs_build_redhat_rpms_module>` module will create the rpm workspace directories and populate the SPECS and SOURCES directories from the source distribution files and the file options, then will build the source and binary rpm files with ``rpmbuild``.

The RPM package version and release strings are generated from the OpenAFS version string extracted from the ``.version`` file in the source archive.

See the ``openafs_devel`` role for tasks to install the required build tools and libraries.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Tools and libraries required to build OpenAFS.
- The ``kernel-devel`` package, when building the kernel module.
- ``rpmbuild`` tool



Parameters
----------

  build (optional, str, all)
    Specifies which rpms to build.

    ``all`` build source and binary RPMs for userspace and kernel module

    ``source`` build the source RPM only

    ``userspace`` build the source RPM and the userspace RPMs

    ``modules`` build the source RPM and the kmod RPM


  sdist (True, path, None)
    The path on the remote node to the source distribution files directory on the remote node.

    The *sdist* directory must contain the ``openafs-<version>-src.tar.bz2`` source archive and the ``openafs-<version>-doc.tar.bz2`` documentation archive.

    The *sdist* directory may also contain the ``ChangeLog`` file and the ``RELNOTES-<version>`` file.


  spec (optional, str, None)
    The path on the remote node to a custom ``openafs.spec`` file to be used to build the rpm files. The ``openafs.spec`` file will be extracted from the source archive file when the *spec* option is not provided.


  relnotes (optional, str, None)
    The path on the remote node to a custom ``RELNOTES`` file to be included in the build.

    The ``RELNOTES-<version>`` in the *sdist* directory will be used when the *relnotes* option is not specified. The ``NEWS`` file will be extracted from the source archive if the ``RELNOTES-<version>`` file is not found in the *sdist* directory.


  changelog (optional, str, None)
    The path on the remote node to a custom ``ChangeLog`` file to be included in the build.

    The ``ChangeLog`` in the *sdist* directory will be used when the ``changelog`` option is not specified.  An empty ``ChangeLog`` file will be created if the  ``ChangeLog`` is not found in the *sdist* directory,


  csdb (optional, path, None)
    The path on the remote node to a custom ``CellServDB`` file to be incuded in the build.

    The ``CellServDB`` file in the *sdist* directory will be used when the *csdb* option is not specified. The ``CellServDB`` file will be extracted from the source archive if the ``CellServDB`` file is not found in the *sdist* directory.


  patchdir (optional, path, I(sdist))
    The path on the remote node of the directory containing patch files to be applied.

    Patch names are identified by the ``PatchXX`` directives in the spec file.


  kernvers (optional, str, current kernel version)
    The kernel version to be used when building the kernel module. By default, the kernel version of the running kernel will be used.


  topdir (optional, path, C(~/rpmbuild))
    The top level rpmbuild workspace directory on the remote node.


  logdir (optional, path, I(topdir)/C(BUILD))
    The path to write build log files on the remote node.


  tar (optional, path, C(tar))
    The ``tar`` program used to unpack the source archive.


  tar_extra_options (optional, str, None)
    Extra command line options to unpack the source archive.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Checkout source
      git:
        repo: "git@openafs.org/openafs.git"
        version: openafs-devel-1_9_1
        dest: "~/openafs"

    - name: Build source distribution
      command:
        cmd: perl build-tools/make-release --dir=packages HEAD
        chdir: "~/openafs"

    - name: Build rpms
      openafs_build_redhat_rpms:
        build: all
        sdist: ~/openafs/packages
      register: build_results



Return Values
-------------

version (always, dict, )
  OpenAFS and package versions extracted from the source archive.


logfiles (always, list, )
  The build log files written on the remote node.


rpms (always, list, )
  The list of rpm files created on the remote node.





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

