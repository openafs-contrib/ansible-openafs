.. _openafs_build_module:


openafs_build -- Build OpenAFS binaries from source
===================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Build OpenAFS server and client binaries from source code by running ``regen.sh``, ``configure``, and ``make``. The source code must be already present in the *projectdir* directory.

The :ref:`openafs_build <openafs_build_module>` module will run the OpenAFS ``regen.sh`` command to generate the ``configure`` script when the ``configure`` script is not already present in the *projectdir*.

Unless the *configure_options* option is specified, the configure command line arguments are determined automatically, based on the platform and :ref:`openafs_build <openafs_build_module>` options.

The ``make`` program is run to build the binaries. Unless the *target* options is specified, the make target is determined automatically.

A complete set of build log files are written on the *logdir* directory on the host for build troubleshooting.

Out-of-tree builds are supported by specifying a build directory with the *builddir* option.

``git clean`` is run in the *projectdir* when *clean* is true and a ``.git`` directory is found in the ``projectdir``.  When *clean* is true but a ``.git`` directory is not found, then ``make clean`` is run to remove artifacts from a previous build.  When *clean* is true and an out-of-tree build is being done, all of the files and directories are removed from the *builddir*.

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


  destdir (optional, path, <projectdir>/packages/dest)
    The destination directory for ``install`` and ``dest`` targets and variants.

    The tree staged in this directory may be installed with the :ref:`openafs_install_bdist <openafs_install_bdist_module>` module.


  clean (optional, bool, False)
    Run ``git clean`` in the *projectdir* when it contains a ``.git`` directory, otherwise run ``make clean``.

    Remove the *builddir* when using an out of tree build, that is the *builddir* is different than the *projectdir*.

    A *clean* build should be done to force a complete rebuild.

    The *clean* option will remove any new files you added manually on the remote node and did not commit when the *projectdir* is a git repository.


  version (optional, str, None)
    Version string to embed in built files.

    The *version* will be written to the ``.version`` file, overwritting the current contents, if any.


  make (optional, path, detect)
    The ``make`` program to be executed.


  jobs (optional, int, the number of CPUs on the system)
    Number of parallel make processes.

    Set this to 0 to disable parallel make.


  manpages (optional, bool, True)
    Generate the man-pages from POD files when running ``regen``.


  transarc_paths (optional, bool, None)
    Build binaries which use the legacy Transarc-style paths.

    This option is ignored when the *configure_options* option is specified.


  configure_options (optional, raw, None)
    The ``configure`` command arguments.

    May be specified as a string, list of strings, or a dictionary.

    When specified as a dictionary, the values of the keys ``enabled``, ``disabled``, ``with``, and ``without`` may be lists.


  target (optional, str, detect)
    The make target to be run.

    The make target will be determined automatically when this option is omitted.









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
        configure_options:
          enable:
            - debug
            - transarc_paths
            - kernel_module
          with:
            - linux_kernel_packaging

    - name: Example configure options specified as a string
      openafs_contrib.openafs.openafs_build:
        state: built-module
        projectdir: ~/src/openafs
        configure_options: "--enable-debug --enable-transarc-paths"



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

