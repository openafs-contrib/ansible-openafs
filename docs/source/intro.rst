Introduction
============

The OpenAFS Ansible Collection is a collection of roles, plugins, and example
playbooks to deploy and manage OpenAFS clients and servers with Ansible.

OpenAFS may be installed from pre-built packages or installed from source code.
Ansible modules are provided to create OpenAFS volumes and users after the
servers and at least one client has been installed.

The fileserver and client disk partitions should be created and mounted before
importing the server and client roles. This should be done with however the
disks are managed in your environment.

Since OpenAFS requires Kerberos for authentication, roles are also provided to
deploy a Kerberos realm with some basic setup.  Alternatively, an existing
realm can be used for authentication, or other roles can be used to setup your
Kerberos KDC and clients.


Platforms supported
-------------------

* AlmaLinux 8, 9
* CentOS 7, 8
* Debian 10, 11, 12
* Fedora 39, 40
* FreeBSD 12, 13
* openSUSE 15
* OracleLinux 8, 9
* Red Hat Entrerprise Linux 7, 8, 9
* Rocky 8, 9
* Solaris 11.4
* Ubuntu 20, 22, 24
