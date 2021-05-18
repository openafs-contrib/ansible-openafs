.. _openafs_build_module:


openafs_build -- Build OpenAFS binaries from source
===================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Build OpenAFS server and client binaries from source code.

The source code must be already present in the *projectdir* directory on the host.

The :ref:`openafs_build <openafs_build_module>` module will run the OpenAFS ``regen.sh`` command, then run ``configure`` with the given *configure_options*, and then run ``make`` with the given *target*.  The ``regen.sh`` execution is skipped when the ``configure`` file already exists.  The ``configure`` execution is skipped when the ``config.status`` file already exists.

A complete set of build log files are written on the *logdir* directory on the host for build troubleshooting.

Out-of-tree builds are supported by specifying a build directory with the *builddir* option.

Before the build starts, ``git clean`` is run in the *projectdir* directory to remove all untracked files when *clean* is true and a ``.git`` directory is found in the ``projectdir``. All of the files and directories are removed from the *builddir* when *clean* is true and an out-of-tree build is being done.

A check for a loadable kernel module is done after the build completes when the *state* is ``built-module``.  Be sure the *target* and *configure_options* are set to build a kernel module when using the ``mkodready`` state.

An installation file tree is created in the *destdir* directory when the *target* starts with ``install`` or ``dest``. The files in *destdir* may be installed with the :ref:`openafs_install_bdist <openafs_install_bdist_module>` module.

See the ``openafs_devel`` role for tasks to install required build tools and libraries on various platforms.



Requirements
------------
The below requirements are needed on the host that executes this module.

- tools and libraries required to build OpenAFS



Parameters
----------

  state (optional, str, complete)
    ``built`` Run regen.sh, configure, make

    ``built-module`` After build is complete, also verify a kernel module was built for the current running kernel version. Be sure the target and configure options are set to build a client when this state is in use.


  projectdir (True, path, None)
    The project directory.

    Source files must have been previously checkout or copied to this path.


  builddir (optional, path, <projectdir>)
    The path for out-of-tree builds.


  logdir (optional, path, <projectdir>/.ansible)
    The path to store build log files.

    The logdir may be a subdirectory of the ``projectdir``.

    The logdir may not be a subdirectory of the ``builddir`` when doing an out-of-tree build.


  clean (optional, bool, False)
    Run ``git clean`` in the *projectdir* when it contains a ``.git`` directory.

    Remove the *builddir*, if different than the *projectdir*.

    A *clean* build should be done if the source files in *projectdir* or the *configure_options* have been changed since the last time this module has been run.

    Use the *clean* option with caution!


  version (optional, str, None)
    Version string to embed in built files.

    The *version* will be written to the ``.version`` file, overwritting the current contents, if any.


  make (optional, path, detect)
    The ``make`` program to be executed.


  target (optional, str, None)
    The make target to be run.


  jobs (optional, int, the number of CPUs on the system)
    Number of parallel make processes.

    Set this to 0 to disable parallel make.


  manpages (optional, bool, True)
    Generate the man-pages from POD files when running ``regen``.


  destdir (optional, path, <projectdir>/packages/dest)
    The destination directory for ``install`` and ``dest`` targets and variants.

    The tree staged in this directory may be installed with the :ref:`openafs_install_bdist <openafs_install_bdist_module>` module.


  configure_options (optional, dict, None)
    The ``configure`` options, as a dictionary.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Build OpenAFS from source
      openafs_contrib.openafs.openafs_build:
        projectdir: ~/src/openafs

    - name: Build OpenAFS server binaries for RHEL
      openafs_contrib.openafs.openafs_build:
        state: built
        projectdir: ~/src/openafs
        clean: yes
        target: install_nolibafs
        destdir: packages/dest
        configure_options:
          prefix: /usr
          bindir: /usr/bin
          libdir: /usr/lib64
          sbindir: /usr/sbin
          disable:
            - strip_binaries
            - kernel_module
          enable:
            - debug
            - redhat_buildsys
            - transarc_paths
          with:
            - krb5: /path/to/krb5.lib
          with_linux_kernel_packaging: true
          with_swig: true
      register: build_results
      when: ansible_os_family == 'RedHat'

    - name: Build OpenAFS legacy distribution
      openafs_contrib.openafs.openafs_build:
        state: built-module
        projectdir: ~/src/openafs
        clean: yes
        target: dest
        configure_options:
          enable:
            - debug
            - transarc_paths
            - kernel_module
          with:
            - linux_kernel_packaging



Return Values
-------------

msg (always, string, Build completed)
  Informational message.


projectdir (always, string, /home/tycobb/projects/myproject)
  Absolute path to the project directory.


builddir (always, string, /home/tycobb/projects/myproject)
  Absolute path to the build directory


destdir (when destdir is specified, string, /home/tycobb/projects/myproject/packages/dest)
  Absolute path to the installation files.


logdir (, string, /home/tycobb/projects/myproject/.ansible)
  Absolute path to the log files. May be used for :ref:`openafs_install_bdist <openafs_install_bdist_module>`.


logfiles (always, list, ['/tmp/logs/build.log', '/tmp/logs/make.out', '/tmp/logs/make.err'])
  Log files written for troubleshooting


kmods (success, list, ['/home/tycobb/projects/myproject/src/libafs/MODLOAD-5.1.0-SP/openafs.ko'])
  The list of kernel modules built, if any.





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

