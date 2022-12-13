OpenAFS Ansible Collection

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
