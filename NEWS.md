OpenAFS Ansible Collection

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
