# Ansible OpenAFS Playbooks

This directory is a collection of Ansible playbooks for OpenAFS.

## Playbooks

* `cell.yaml`      - deploy a kerberos realm and OpenAFS cell on a set of hosts
* `kvm.yaml`       - install a kvm hypervisor on a local host (for testing)
* `realm.yaml`     - deploy a kerberos realm only
* `testcell.yaml`  - deploy a test cell and install Robot Framework test suites
* `robestest.yaml` - install Robot Framework test suites

## Configuration files

* `ansible.cfg`  - example Ansible configuration

## virt-lab files

TODO: document how to setup and run `virt-lab`.

* `virt-lab.cfg` - virt-lab configuration to create test cells on a local kvm hypervisor
* `testcell.sh`  - postcreate script to run playbooks and test suites

Here is an example virt-lab "local" config.

    [.global]
    key = ~/.ssh/mykey.pub
    bridge = vlbr0
    gateway = 192.168.123.1
    local_playbooks = /home/tycobb/virt/playbooks/local-dns.yaml

## Static inventory

TODO: Describe


    ~/inventories/
    └── example.com
        ├── group_vars
        │   └── all.yaml
        └── hosts


    cat ~/inventories/hosts
    [afs_kdcs]
    afs01.example.com
    
    [afs_databases]
    afs01.example.com
    afs02.example.com
    afs03.example.com
    
    [afs_fileservers]
    afs04.example.com
    afs05.example.com
    afs06.example.com
    
    [afs_clients]
    afs[01:06].example.com


    cat ~/inventories/example.com/group_vars/all.yaml
    ---
    afs_cell: example.com
    afs_desc: My example cell
    afs_realm: EXAMPLE.COM

