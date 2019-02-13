# ansible-openafs
Ansible roles for OpenAFS

* Setup the systems and customize ansible variables
** Set up the base systems (afs01-afs06 in the example)
* Customize ansible variables
** Create the **hosts** file (see hosts.example as an example)
** Create **cell configuration** yaml file (the cell variable in the hosts file defines the filename. e.g. example.com.yaml)
* Run the cell.yaml playbook

# Example layout
## Base layout

Kerberos realm: EXAMPLE.COM - defined in the hosts file
AFS Cell: example.com - defined in the hosts file

### Systems
System | Services
------ | --------
afs01.example.com  | kdc, afs dbserver, afs client
afs02.example.com  | afs dbserver, afs client
afs03.example.com  | afs dbserver, afs client
afs04.example.com  | afs fileserver, afs client
afs05.example.com  | afs fileserver, afs client
afs06.example.com  | afs client

AFS Partitions: a,b,c

### Kerberos principals:

`admin@EXAMPLE.COM`     - id and password set from hosts file

## Example layout defined in the cell configuration file (example.com.yaml)
* Sets the kdc server to the first kdc server listed in the hosts file: afs01
* Sets the root fileserver to first fileserver listed in the hosts file: afs04

### AFS Volumes

Root fileserver afs04, partition a

* test
** /test
* foobar
** /test/foobar

### AFS Users

User | Principal | Group
---- | --------- | -----
user1 | `user1@EXAMPLE.COM` | group1
user2 | `user2@EXAMPLE.COM` | group1, group2
user3 | `user3@EXAMPLE.COM` | group2

