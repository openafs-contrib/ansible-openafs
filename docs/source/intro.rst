Introduction
============

The OpenAFS Ansible Collection provides roles, modules, and example playbooks
to deploy OpenAFS clients and/or servers with Ansible.

OpenAFS binaries may be installed from pre-built packages or installed from
source code.

Ansible modules are provided to create OpenAFS volumes and users after the
servers and at least one client has been installed.

Since OpenAFS requires Kerberos for authentication, roles are provided to
deploy a Kerberos 5 realm with MIT Kerberos. Alternatively, an existing realm
can be used for authentication.
