# Ansible OpenAFS Playbooks

This directory is a collection of Ansible playbooks for OpenAFS.

## Playbooks

These example playbooks can be used as starting points for your playbooks.

* `realm.yaml`     - deploy a kerberos realm
* `cell.yaml`      - deploy an OpenAFS cell
* `robotest.yaml`  - install a Robot Framework based test suite for OpenAFS
* `testcell.yaml`  - deploy a realm, a test cell, and testsuite
* `build*.yaml`    - example plays to build and install OpenAFS from source

## Example Ansible Configuration

* `ansible.cfg.example`  - example Ansible configuration

Copy this file to `~/.ansible.cfg` and customize as needed.

## Example Inventories

* `hosts/example01` - simple one host realm and cell
