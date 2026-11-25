OpenAFS Ansible Collection

November 25, 2026 - version 1.11.2

* Add openSUSE Leap 16 support to the `openafs_devel` and
  `openafs_devel_kernel` roles.

November 25, 2026 - version 1.11.1

* Fix the `openafs_store_facts` module on managed nodes running python 2.7.

* Fix the `openafs_devel` role on AlmaLinux 8 and Rocky 8. Enable the
  PowerTools repo to install `doxygen`, and remove the `perl-FindBin` and
  `perl-Sys-Hostname` packages, which are not available with the default
  perl module stream.

November 25, 2026 - version 1.11.0

* Require ansible-core 2.19 or later.

* Add the missing `ansible.posix` and `community.general` collection
  dependencies.

* Fix conditionals for ansible-core 2.19. Boolean variables given as strings,
  such as `-e afs_foo=no`, are now handled correctly, and embedded templates
  were removed from conditionals.

* Fix the SLES and openSUSE kernel-devel version checks, which always failed
  with ansible-core 2.19, causing the `openafs_devel_kernel` role to install
  kernel-devel (and possibly update the kernel and reboot) even when the
  correct kernel-devel was already installed.

* Fix the dkms status check in the `openafs_client` role, which always passed
  even when the OpenAFS kernel module was not installed.

* The `openafs_client` role managed kmod install method now installs the
  newest OpenAFS version which has a kmod-openafs package for the running
  kernel, instead of failing when the newest version (for example, a
  pre-release) has no kmod-openafs package.

* Add the `afs_bootstrap_run_once` variable to the `openafs_server` role. Set
  it to false to bootstrap each host when each host is a separate cell. The
  `local_install` playbook now bootstraps a cell on every host.

* Add the `afs_service_keytab_remote_src` variable to the `openafs_server`
  role, to use a service keytab which is already on the server nodes.

* Add the `afs_kernel_version` variable to select the kernel version to install
  kernel headers for in the `openafs_devel_kernel` role.

* Add the `afs_local_hosts` variable to run the `local_install` and
  `local_devel` playbooks on hosts other than localhost.

* Install `which` in the `openafs_devel` role.

* The `openafs_user` module now fails with a clear message when the group name
  is the name of an existing user.

* The `openafs_volume` module now detects dynroot correctly when the root.cell
  volume is missing, and retries `fs` commands on timeouts and server or
  network errors.

* Fix the `build: modules` option in the `openafs_build_packages` and
  `openafs_build_redhat_rpms` modules, which did not build the kernel module.

* Fix the `openafs_build` module failing with "log() takes 2 positional
  arguments but 3 were given" when `configure_options` is not specified.

* Fix finding the built `openafs.ko` on Debian kernels with a "+" in the
  kernel version.

* Fix list updates in the `openafs_store_facts` module. List values are now
  extended with the new items instead of appended as a single element.

* Rename the `keys` result of the `openafs_keys` module to `keytab_keys`. The
  old `keys` result is deprecated, but still returned.

* Fix the `ANSIBLE_OPENAFS_COUNTER_DIR` environment variable name in the
  `counter` lookup plugin, which was ignored.

* Deprecate the `openafs_build_redhat_rpms` module, which will be removed in
  version 2.0.0. Use the `openafs_build_packages` module instead.

* Fix module documentation and sanity check errors.

* Replace the test harness with tox-ansible and molecule. The role and playbook
  tests now run in podman containers instead of proxmox virtual machines. See
  the new development page in the documentation.

March 20, 2026 - version 1.10.4

* Add SLES support to the `openafs_pricipal` module.

* Add SLES 15 support to the `openafs_kernel_devel` role.

February 3, 2026 - version 1.10.3

* Add `afs_update_filewall_rules` variable to skip firewalld tasks.

January 30, 2026 - version 1.10.2

* Add support to install devel tools on RedHat-10.

* Skip devel tools install on Windows.

December 20, 2025 - version 1.10.1

* Add a clock-skew check on the servers before installing OpenAFS to avoid
  quorum issues.

* Fix the check for the OpenAFS kernel module in the `openafs_build` module.
  Recent versions of OpenAFS changed the path during compilation.

* Install perl-core on RedHat 9 and later in `openafs_devel` role. This
  is needed to run the OpenAFS unit tests.

* Fix CodeReady Build (CRB) and EPEL install in `openafs_devel` on RedHat.

May 11, 2025 - version 1.10.0

* Add "local" playbooks for developers to install tools and install kerberos
  and OpenAFS on a local machine.

* Add "deploy" playbooks to deploy a Kerberos realm and an OpenAFS cell on one
  or more ansible managed nodes.

* Add the `openafs_robotserver` role and `deploy_robotserver` playbook to
  deploy the Robotframework remote server on test nodes. Limited to AlmaLinux
  at this time.

* The collection development environment has been converted to tox and unit
  tests have been cleaned up.

April 2, 2025 - version 1.9.4

* server role: Add `afs_server_change_etc_hosts` to remove the loopback
  workaround in `/etc/hosts` files on Debian machines.

* devel role: Install the `perl-core` package on RedHat family distros in order
  to run OpenAFS unit tests.

December 23, 2024 - version 1.9.3

* devel role: Add AlmaLinux 10 support

* devel role: Do not install fuse-devel on AlmaLinux 9 to work around
  development tool installation issues.

* devel role: Install perl modules AlmaLinux in order to run OpenAFS unit
  tests.

December 15, 2024 - version 1.9.2

* devel role: Install dblatex and other packages needed to generate the openafs
  documents during a build on debian machines.

* devel role: Install libpod-parser-perl on Ubuntu machines.

November 16, 2024 - version 1.9.1

* Properly log the vos commands executed in the `openafs_volume` module.

* Add `afs_checkout_method` "none" value support.

* Add dynamic `afs_cachedir` default value.

* Add `remote_src` to unarchive tasks.

* Remove the `afs_transarc_build` role variable.

* Change the default DESTDIR to `packages/install_root`

May 31, 2023 - version 1.9.0

* Add Debian 12 support

December 13, 2022 - version 1.8.0

* Add support for Solaris IPS packages. A private IPS package repository is
  required at this time.

* Use SMF on Solaris instead of legacy init scripts when installing from
  source or a transarc-style binary distribution.

* Add support for FreeBSD 12 and FreeBSD 13, limited to 'source', 'sdist', and
  'bdist' install methods.  OpenAFS gerrit 15173 is required to build binaries
  for FreeBSD at this time.

* Add support for CentOS 6.

* Add `openafs_devel_kernel` role to improved support for installing required
  kernel headers and development tools when needed to build the OpenAFS kernel
  module on Linux and FreeBSD.  By default, the `openafs_devel_kernel` role will
  update the Linux kernel version and reboot if is needed to install an available
  kernel headers (kernel-devel) package.

* Add support for creating principals with Heimdal Kerberos (required for
  FreeBSD support.)

* Change the `openafs_principal` module to create a keytab only when the password
  parameter is not specified.

* Fix OracleLinux and Rocky default yum repository URLs.

* Enable Rocky 9 CRB yum repository when installing developement packages on
  Rocky 9.

* Add gerrit checkout method to build and install from a gerrit.openafs.org
  change id number.

* Fix many and various ansible-lint warnings introduced by the current
  version of ansible-lint.

* Refactor modules for improved multi-platform support.

* The ``afs_install_method`` default value is now platform dependent. The
  default value is 'source' on FreeBSD and Solaris, and is 'managed' on
  all Linux platforms.


June 8, 2022 - verision 1.7.0

* Add support for RHEL 9, CentOS 9 and, AlmaLinux 9

* Add support for Fedora 36

* Add support for Ubuntu 22

* Support moderns paths when installing from source on Solaris.

* Add support for extra environment variables during configure
  when installing from source to support customized paths, such
  as customized path to log files.

* Fix status checks in Solaris init scripts to avoid double
  bosserver starts.

* Install packages needed to build recent and development
  versions of OpenAFS when installing from source.

April 11, 2022 - version 1.6.0

* openSUSE: Add "managed" and install method support (install with zypper)

* openSUSE: Add "dkms" module install method

* openSUSE: Support kmp kernel favors

* openSUSE: Fix rpm package names

* openSUSE: Fix kdestroy installation path local fact

* Fix BosConfig directory permissions when using modern installation paths

* Remove client CellServDB symlink created by bosserver

* Dump local facts to syslog as debug messages instead of info messages
  to avoid cluttering the syslog

March 18, 2022 - version 1.5.0

* Add support for openSUSE Leap 15

* Add support for the new Solaris 11.4 rolling updates

* Add default yum repo URL for AlmaLinux

* Fix `openafs_store_facts` module idempotency

* Detect afsd command line arguments installed by packages and use
  those by default

* Detect installation directories used by packages instead of assuming
  installation paths based on package type

* Add more build options to the `openafs_build` module

* Improve `openafs_principle` module error logging

* Remove redundant logging of parameters to syslog and always honor
  the `no_log` option for parameter logging

February 4, 2022 - version 1.4.0

* Add support for AlmaLinux 8 and RockLinux 8.

* Add the `afs_krb_dns_lookup_kdc` variable to the Kerberos client and
  server roles to customize the Kerberos `dns_lookup_kdc` option.

* Solaris: Disable Solaris Studio update check process to
  to improve build times.

* Test and documenation updates.

November 20, 2021 - version 1.3.0

* Add Solaris 11.4 support to OpenAFS server and client roles. Limited to
  Transarc-style binary distributions and install from source.

* Add `openafs_build_sdist` module to make source distribution tar archives
  from a git checkout.

* Add `openafs_contrib.openafs.counter` lookup plugin.

* Add `afs_checkout_method host variable` to specify how to retreive the
  source code when the `afs_install_method` is 'source'.

* Add variables to set the Kerberos KDC supported enctypes and various
  ticket and principal options.

* Remove `ansible_user` references from role host variable defaults.

* Add `module_utils` for common plugin code.

* Fix kernel header installation on Debian.

* Fix missing kheader task on Solaris.

* Fix undefined name 'module' error in `openafs_build.py` regression.

* Do not install the solaris studio GUI on Solaris.

* Various unit test improvements.

* Remove test and doc files from the galaxy build archive.


October 18, 2021 - version 1.2.0

* Add Fedora support

* Fix DKMS status check on clients when installing with DKMS packages.

* Add support for extra bnode entries on servers.

* Add support for multiple admin users.

* Add support for externally managed keytabs.

* Add the `openafs_build_redhat_rpms` module to build OpenAFS RPMs for
  RedHat-family distributions.

* Support kerberos server name variables when setting up the krb5.conf on the kdc server,
  and not just the clients.

* Improve speed and reliability of kernel-devel package installation on clients.

* Improve build logs in `openafs_build` module.

* Use pytest to run molecule role and playbook unit tests.


August 13, 2021 - version 1.1.0

* Run the bosserver in restricted mode by default

* Update SELinux policy file to support Centos 8.

* Add NetInfo/NetRestrict client and server configuration support.

* Limit bdist install method to Transarc-style paths.

* Support string and list `configure_options` in `openafs_build` module.

* Support rebuilding and re-installing when installing from source.

* Support of bzip tarballs when install from source distribution.

* Add host variables for finer control when installing from
  source: `afs_configure_options`, `afs_transarc_build`, `afs_is_server`,
  `afs_is_client`.

* Fix temporary directory permission errors.

* Fix default client csdb.yaml files.

* Additional debugging output.

* Molecule test improvements and fixes.

* Add meta/runtime.yaml to appease galaxy importer.

May 4, 2021 - version 1.0.0

* Roles for OpenAFS clients and servers. Install methods include
  managed, packages, source, sdist (source distribution), bdist
  (binary distribution).

* Roles for basic Kerberos realm deployment.

* Various modules for playbook and role tasks, including modules
  create OpenAFS volumes, users and groups.

* Example playbooks to build OpenAFS, deploy a Kerberos realm,
  and deploy an OpenAFS cell.

* Docs hosted on readthedocs.io.
