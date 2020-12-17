# Ansible OpenAFS Playbooks

This directory is a collection of example Ansible playbooks for OpenAFS.
These example playbooks can be used as starting points for your playbooks.

## Playbooks

* `build.yaml`  - build and install OpenAFS from source
* `realm.yaml`  - deploy a kerberos realm
* `cell.yaml`   - deploy an OpenAFS cell on one or more nodes

## Example Ansible Configuration

* `ansible.cfg.example`  - example Ansible configuration

Copy this file to `~/.ansible.cfg` and customize as needed.

## Example Inventories

* `hosts/single`   - simple one node kerberos realm and openafs cell
* `hosts/clusters` - multiple client and server nodes
