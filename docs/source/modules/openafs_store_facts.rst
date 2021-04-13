.. _openafs_store_facts_module:


openafs_store_facts -- Store OpenAFS facts in a json file
=========================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Store facts in the json formatted c(openafs.fact) file on the remote host. This file is located in the c(/etc/ansible/facts.d) directory or the path specified by the c(factsdir) parameter. The c(openafs.fact) file is read by Ansible when facts are gathered on subsequent plays.

The c(openafs.fact) contains a dictionary of facts which can be accessed from c(ansible_local.openafs).






Parameters
----------

  state (optional, any, None)
    c(update) update the facts


  factsdir (optional, path, /etc/ansible/facts.d)
    Path to the c(openafs.fact) file









Examples
--------

.. code-block:: yaml+jinja

    





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

