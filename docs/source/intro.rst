Introduction
============



Install Methods
---------------

The following install methods are supported for OpenAFS clients
and servers:

* **managed** - Install with the distro's package manager (e.g., ``yum``, ``apt``).
* **packages** - Install prebuilt packages (e.g. ``rpm``, ``dpkg``).
* **bdist** - Install binary distribution with modern or Transarc-style paths.
* **sdist** - Source distribution
* **scm** - Checkout source code with ``git``, then build and install binaries.
* **none** - Skip installation tasks; assume manual installation.

A different install method may be used on each remote node, however the
if installing a client and server on node, the install method must be the
same for the client and server roles.

The install method is stored on the remote node in a local fact on the node.
It is not possible to change the install method for a nodes between plays
without manual intervention.
