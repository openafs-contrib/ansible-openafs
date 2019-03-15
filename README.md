# ansible-openafs

This is a collection of Ansible playbooks and roles for installing and setting
up a Kerberos realm and OpenAFS cell.

*Supported platforms:*

* CentOS/RHEL 7
* OpenAFS 1.8.x

*Setup:*

* Copy `hosts.example` to `hosts`.
* Edit `hosts` to match the host names at your site and set
  the host variables to set the realm and cell info.
* Copy `example.com.yaml` to `<cell>`.yaml and configure as needed.
* Optionally, copy `ansible.cfg.example` to `ansible.cfg` and
  edit to taste.
* Run `./setup.sh` once to set the Kerberos and OpenAFS administrator user name
  and password and the Kerberos database master password in an encrypted
  variable file. `ansible-vault` is used to encrypt this information.
* Run `ansible-playbook --ask-vault-pass cell.yaml` to create the Kerberos realm
  and OpenAFS cell.

## `kerberos_client` role

Install and configure the kerberos workstation packages.

| Variable   | Default     | Description |
| ---------- | ----------- | ------------- |
| `realm`    | EXAMPLE.COM | kerberos realm name |


## `kerberos_server` role

Install and configure the kerberos server packages on a single
KDC and create a kerberos realm.

| Variable          | Default     | Description |
| ----------------- | ----------- | ------------- |
| `realm`           | EXAMPLE.COM | kerberos realm name |
| `admin_principal` | admin       | kerberos admin principal |


## `openafs_cell` role

Setup the top level volumes in the cell. To be run on a client after the
server and client roles have executed.

| Variable      | Default     | Description                                |
| ------------- | ----------- | ------------------------------------------ |
| `cell`        | example.com | afs cell name                              |
| `realm`       | EXAMPLE.COM | kerberos realm name                        |
| `kdc`         | first host in `kdcs group` | primary kerberos kdc hostname |
| `root_server` | first host in `fileservers` group | primary fileserver hostname |
| `root_part`   | a           | primary fileserver afs partition id        |


## `openafs_client` role

Install and configure the OpenAFS client packages.  Optionally, build and install from
a git source checkout.

| Variable                 | Default         | Description                                         |
| ------------------------ | --------------- | --------------------------------------------------- |
| `cell`                   | example.com     | AFS cell name                                       |
| `cell_description`       | Example         | cell organization name                              |
| `realm`                  | EXAMPLE.COM     | kerberos realm                                      |
| `openafs_client_repourl` |                 | openafs yum repo for client packages                |
| `client_install_method`  | yum             | Installation method, one of: yum, build             |
| `client_build_repo`      |                 | 'build' installation git repo url                   |
| `client_build_path`      | /usr/local/src/openafs-client | 'build' installation method path      |
| `client_build_version`   | master          | 'build' installation method git reference           |
| `with_dkms`              | False           | install client with dkms when True                  |
| `cacheinfo_mount`        | /afs            | afs filesystem mount point                          |
| `cacheinfo_cache`        | /usr/vice/cache | afs cache mount point                               |
| `cacheinfo_size`         | 50000           | afs cache size                                      |
| `opt_afsd`               | -dynroot -fakestat -afsdb | afsd options                              |

## `openafs_server` role

Install and configure the OpenAFS server packages. Optionally, build and install from
a git source checkout.

| Variable                 | Default         | Description                                         |
| ------------------------ | --------------- | --------------------------------------------------- |
| `cell`                   | example.com     | afs cell name                                       |
| `cell_description`       | Example         | cell organization name                              |
| `realm`                  | EXAMPLE.COM     | kerberos realm name                                 |
| `openafs_server_repourl` |                 | openafs yum repo for server packages                |
| `selinux_mode`           | enforcing       | selinux mode                                        |
| `server_install_method`  | yum             | Installation method, one of: yum, build             |
| `server_build_repo`      |                 | 'build' installation git repo url                   |
| `server_build_path`      | /usr/local/src/openafs-server | 'build' installation method path      |
| `server_build_version`   | master          | 'build' installation method git reference           |
| `enable_dafs`            | True            | enable DAFS fileserver when True                    |
| `opt_bosserver`          |                 | bosserver options                                   |
| `opt_ptserver`           |                 | ptserver options                                    |
| `opt_vlserver`           |                 | vlserver options                                    |
| `opt_dafileserver`       | -L              | DAFS fileserver options                             |
| `opt_davolserver`        |                 | DAFS volume server options                          |
| `opt_salvageserver`      |                 | DAFS salvage server options                         |
| `opt_dasalvager`         |                 | DAFS salvager options                               |
| `opt_fileserver`         |                 | Legacy fileserver options                           |
| `opt_volserver`          |                 | Legacy volume server options                        |
| `opt_salvager`           |                 | Legacy salvager options                             |
| `kdc`                    | first host in kdcs group | Master kerberos kdc                        |
| `root_server`            | first host in fileservers group | Primary fileserver hostname         |
| `root_part`              | a               | Primary fileserver vice partition id                |


## Example layout

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

Test volumes:
* `test`, mount point /test
* `foobar`, mount point /test/foobar

### AFS Users

User | Principal | Group
---- | --------- | -----
user1 | `user1@EXAMPLE.COM` | group1
user2 | `user2@EXAMPLE.COM` | group1, group2
user3 | `user3@EXAMPLE.COM` | group2

