Platform notes
==============

Red Hat Enterprise Linux/CentOS
-------------------------------

SE Linux ``enforcing`` mode is only supported when OpenAFS is installed from
RPM packages.  Be sure to first set the SE Linux mode to ``permissive`` when
installing OpenAFS from source or a binary distribution.

The OpenAFS kernel module may be installed with DKMS or from a pre-built kernel
module package.  The DKMS system will automatically rebuild the kernel module
when the linux kernel is updated, but requires the module to be rebuilt on each
node and requires the kernel-devel package version to match the running kernel
version to be installed on the nodes.  The prebuilt kernel package must match
the version of the running kernel, so requires a repository which is updated
for each kernel version.

Set the host variable ``afs_module_install_method`` to ``dkms`` to install a
client with DKMS, and to ``kmod`` to install the client with a prebuilt kernel
module package.


Solaris
-------

Historically, Transarc-style binary distributions are used to install OpenAFS
on Solaris.  Please set ``afs_install_method`` on Solaris nodes to ``bdist`` or
``source`` to install from a binary distribution or from source code.  The
``openafs_build`` module will build a Transarc-style binary distribution by
default on Solaris nodes.

OpenAFS client and servers are started with legacy style ``sysv`` init scripts
on Solaris.
