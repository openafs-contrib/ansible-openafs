Introduction
============

The OpenAFS Ansible Collection is a collection of roles, plugins, and example
playbooks to deploy and manage OpenAFS clients and servers with Ansible.

OpenAFS may be installed from pre-built packages or installed from source code.
Ansible modules are provided to create OpenAFS volumes and users after the
servers and at least one client has been installed.

Since OpenAFS requires Kerberos for authentication, roles are provided to
deploy a Kerberos 5 realm with MIT Kerberos. Alternatively, an existing realm
can be used for authentication.

Platforms supported
-------------------

* Red Hat Entrerprise Linux 7, 8
* AlmaLinux 8
* CentOS 7, 8
* Fedora 34, 35
* Debian 10, 11
* Ubuntu 20
* Solaris 11.4
