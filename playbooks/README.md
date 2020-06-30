# Ansible OpenAFS Playbooks

This directory is a collection of Ansible playbooks for OpenAFS.

## Playbooks

* `kvm.yaml`       - install a local kvm hypervisor
* `realm.yaml`     - deploy a kerberos realm
* `cell.yaml`      - deploy an OpenAFS cell
* `robotest.yaml`  - install a Robot Framework based test suite for OpenAFS
* `testcell.yaml`  - deploy a realm, a test cell, and testsuite

## Example Ansible Configuration

* `ansible.cfg.example`  - example Ansible configuration

Copy this file to `~/.ansible.cfg` and customize as needed.

## Example Inventories

* `hosts/example01` - simple one host realm and cell
