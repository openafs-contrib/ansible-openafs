# Ansible OpenAFS Playbooks

This directory is a collection of example Ansible playbooks for OpenAFS.
These example playbooks can be used as starting points for your playbooks.

## Playbooks

* `kerberos-realm.yml` - example play to deploy a kerberos realm
* `openafs-cell.yml`   - example plays to deploy an OpenAFS cell on one or more nodes
* `build-bdist.yml`    - example plays to build and install OpenAFS from source

## Example Ansible Configuration

* `ansible.cfg.example`  - example Ansible configuration

Copy this file to `~/.ansible.cfg` and customize as needed.

## Example Inventories

* `hosts/single`   - simple one node kerberos realm and openafs cell
* `hosts/clusters` - multiple client and server nodes
