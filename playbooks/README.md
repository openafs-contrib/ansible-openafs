# Ansible OpenAFS Playbooks

This directory is a collection of Ansible playbooks for OpenAFS.

## Playbooks

* `cell.yaml`      - deploy a kerberos realm and OpenAFS cell on a set of hosts
* `kvm.yaml`       - install a kvm hypervisor on a local host (for testing)
* `realm.yaml`     - deploy a kerberos realm only

## Configuration files

* `ansible.cfg`  - example Ansible configuration
* `virt-lab.cfg` - virt-lab configuration to create test cells on a local kvm hypervisor


TODO: document how to setup and run `virt-lab`.

Here's an example virt-lab "local" config.

    [.global]
    key = ~/.ssh/mykey.pub
    bridge = vlbr0
    gateway = 192.168.123.1
    local_playbooks = {playbookdir}/local-dns.yaml {playbookdir}/wait.yaml
    var.afs_admin_password = **********
