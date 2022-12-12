#!/usr/bin/python
# Copyright (c) 2020, Sine Nomine Associates
# BSD 2-Clause License

ANSIBLE_METADATA = {
    'metadata_version': '1.1.',
    'status': ['preview'],
    'supported_by': 'community',
}

DOCUMENTATION = r"""
---
module: openafs_volume

short_description: Create an OpenAFS volume

description:
  - Create or remove a volume.
  - Optionally, create read-only volumes, and release the volume.
  - Optionally, mount the volume and set the ACL rigths in the filespace.
  - Volume mounting requires a client running on the remote node.
  - Localauth authentication may be used on server nodes, running as root.
    When running in this mode, volumes maybe created, but not mounted.
  - Keytab based authentication may be used on client nodes to mount
    volumes and set root directory ACLs. This requires a keytab for
    a user in the system:adminstrators group and a member of the UserList
    on all of the servers.

options:

  state:
    description:
      - C(present) ensure the volume is present, C(absent) ensure the volume is
        removed
    type: str
    required: no
    default: <present>

  volume:
    description:
      - Name of the read-write volume.
    type: str
    required: yes

  server:
    description:
      - The initial volume fileserver location.
      - If provided, should be the hostname or fileserver address.
      - If not provided, the first fileserver address from C(vos listaddrs)
        will be used.
      - The volume will not be moved if it already exists on a different
        server.
      - This option is ignored when the state is C(absent).
    type: str
    default: first fileserver entry found in VLDB

  partition:
    description:
      - The initial volume partition id.

      - If provided, should be the partition id; C('a') ..  C('iu').

      - If not provided, the first partition found from C(vos listpart) will be
        used.

      - The volume will not be moved if it already exists on a different
        partition.

      - This option is ignored when the state is C(absent).

    type: str
    default: the first partition found on the fileserver

  mount:
    description:
      - The initial mount point path.

      - Should be the fully-qualified path to the mount point to be created.

      - The read/write path variant will be used if it is available.

      - A read/write mount point will also be created for the C(root.cell)
        volume.

      - The C(i) and C(a) ACL rights will be temporarily assigned to the mount
        point parent directory in order to create the mount point if those
        rights are missing.

      - The volume containing the parent volume will be released if a mount
        point was created.

      - The volume will be created but not mounted if the C(mount) option is
        not given.

      - This option is ignored when the state is C(absent).

      - This option may only be used if a client is installed on the remote
        node.
    type: str
    required: no

  acl:
    description:
      - The access control list to be set in the volumes root directory.

      - The C(acl) option my be specified as a list of strings. Each string
        contains a pair of strings separated by a space. The substring names a
        user or group, the second indicates the access rights.

      - See C(fs setacl) for details.

      - This option may only be used if a client is installed on the remote
        node.

    type: str
    required: no
    aliases:
      - acls
      - rights

  quota:
    description: The initial volume quota.
    type: int
    required: no
    default: 0

  replicas:
    description:
      - The number of read-only volumes to be created, including the read-only
        clone on the same fileserver and partition as the read/write volume.

      - The C(replicas) option indicates the minumum number of read-only
        volumes desired.

    type: int
    required: no
    default: 0

  localauth:
    description:
      - Indicates if the C(-localauth) option is to be used for authentication.

      - This option should only be used when running on a server.

      - The C(mount) and C(acl) options may not be used with C(localauth).

    type: bool
    default: no

  auth_user:
    description:
      - The afs user name to be used when C(localauth) is False.

      - The user must be a member of the C(system:administrators) group and
        must be a server superuser, that is, set in the C(UserList) file on
        each server in the cell.

      - Old kerberos 4 '.' separators are automatically converted to modern '/'
        separators.

      - This option may only be used if a client is installed on the remote
        node.

    type: str
    default: admin

  auth_keytab:
    description:
      - The path on the remote host to the keytab file to be used to
        authenticate.

      - The keytab file must already be present on the remote host.

      - This option may only be used if a client is installed on the remote
        node.

    type: str
    default: admin.keytab

author:
  - Michael Meffie
"""

EXAMPLES = r"""
- name: Create afs root volume
  openafs_contrib.openafs.openafs_volume:
    state: present
    name: root.afs
    mount: /afs
    acl: "system:anyuser read"
    replicas: 3

- name: Create cell root volume
  openafs_contrib.openafs.openafs_volume:
    state: present
    name: root.cell
    mount: /afs/example.com
    acl: "system:anyuser read"
    replicas: 3

- name: Create a volume
  openafs_contrib.openafs.openafs_volume:
    state: present
    name: test
    mount: /afs/example.com/test
    acl:
      - "bob all"
      - "system:anyuser read"
      - "system:authuser write"

- name: Alternate acl format
  openafs_contrib.openafs.openafs_volume:
    state: present
    name: test
    mount: /afs/example.com/test
    acl:
      bob: all
      "system:anyuser": read
      "system:authuser": write
"""

RETURN = r"""
acl:
  description: List of acl strings set in the volume root directory
  returned: success
  type: list
#  sample:
#    - "system:anyuser":
#        - r
#        - l

mount:
  description: Mount point path
  returned: success
  type: str
#  sample: "/afs/.example.com/test/foo"

volume:
  description: Volume information
  returned: success
  type: dict
#  sample:
#    name: foo
#    rw: 536870927
#    sites:
#      - flags: ""
#        partition: a
#        server: 192.168.122.214
#        type: rw
"""

import json                     # noqa: E402
import os                       # noqa: E402
import pprint                   # noqa: E402
import re                       # noqa: E402
import time                     # noqa: E402
import errno                    # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')
log = Logger(module_name)


class ExtraRights:
    """
    Context manager to add rights temporarily to allow the system
    administrator to mount and unmount volumes.
    """
    def __init__(self, volume, rights, path, name='system:administrators'):
        self.volume = volume
        self.rights = set(rights)
        self.path = path
        self.name = name
        acl = volume.get_acls(self.path)[0]
        self.existing = acl.get(self.name, set(''))
        self.augmented = self.existing | self.rights

    def __enter__(self):
        if self.existing != self.augmented:
            log.info("Adding temporary rights '%s %s' to directory '%s.",
                     self.name, ''.join(self.rights), self.path)
            rights = ''.join(self.augmented)
            self.volume.cmd.fs('setacl', '-dir', self.path, '-acl', self.name,
                               rights)
        return self

    def __exit__(self, *exc):
        if self.existing != self.augmented:
            log.info("Removing temporary rights '%s %s' to directory '%s'",
                     self.name, ''.join(self.rights), self.path)
            rights = ''.join(self.existing)
            if not rights:
                rights = 'none'
            self.volume.cmd.fs('setacl', '-dir', self.path, '-acl', self.name,
                               rights)


class Command(object):
    """
    Run commands with retries.
    """

    def __init__(self, module, results):
        self._commands = {}
        self.module = module
        self.results = results
        self.localauth = module.params['localauth']

    def die(self, msg):
        log.error(msg)
        self.module.fail_json(msg=msg)

    def lookup_command(self, name):
        """
        Lookup an OpenAFS command. First search the installation facts,
        then the PATH.
        """
        if name in self._commands:
            return self._commands[name]
        try:
            with open('/etc/ansible/facts.d/openafs.fact') as f:
                facts = json.load(f)
            cmd = facts['bins'][name]
        except Exception:
            cmd = self.module.get_bin_path(name)
        if not cmd:
            self.die('Unable to locate %s command.' % name)
        self._commands[name] = cmd
        return cmd

    def run_command(self, cmd, *args):
        """
        Run a command.
        """
        cmdargs = [cmd] + list(args)
        cmdline = ' '. join(args)
        rc, out, err = self.module.run_command(cmdargs)
        log.debug('command=%s, rc=%d, out=%s, err=%s', cmdline, rc, out, err)
        if rc != 0:
            self.die('Command failed: %s, rc=%d, out=%s, err=%s' %
                     (cmdline, rc, out, err))
        return out

    def kinit(self, keytab, principal):
        """
        Run the kinit command.
        """
        kinit = self.lookup_command('kinit')
        self.run_command(kinit, '-k', '-t', keytab, principal)

    def aklog(self):
        """
        Run the aklog command.
        """
        aklog = self.lookup_command('aklog')
        self.run_command(aklog, '-d')

    def fs(self, *args):
        """
        Run the fs command and return the stdout.
        """
        fs = self.lookup_command('fs')
        return self.run_command(fs, *args)

    def vos(self, args, done=None, retry=None):
        """
        Run a vos command with retries.
        """
        def _done(rc, out, err):
            return rc == 0

        def _retry(rc, out, err):
            if "server or network not reponding" in err:
                return True
            if "no quorum elected" in err:
                return True
            if "invalid RPC (RX) operation" in err:
                return True  # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True  # May occur during server startup.
            return False

        if done is None:
            done = _done
        if retry is None:
            retry = _retry

        vos = self.lookup_command('vos')
        args.insert(0, vos)
        if self.localauth:
            args.append('-localauth')
        cmdline = ' '.join(args)
        retries = 120
        while True:
            rc, out, err = self.module.run_command(args)
            log.debug('command=%s, rc=%d, out=%s, err=%s',
                      cmdline, rc, out, err)
            if done(rc, out, err):
                return out
            if retries == 0 or not retry(rc, out, err):
                self.die("Command failed: %s, rc=%d, err=%s" %
                         (cmdline, rc, err))
            log.warning("Failed: %s, rc=%d, err=%s; %d retr%s left.",
                        cmdline, rc, err, retries,
                        ('ies' if retries > 1 else 'y'))
            retries -= 1
            time.sleep(5)

    def vos_listvldb(self, name, retry_not_found=True):
        """
        Return the entry of an existing volume.
        """
        log.debug("get_entry(name='%s')", name)
        entry = {
            'sites': []
        }
        vos_fields = {
            'rw': r'RWrite: (\d+)',
            'ro': r'ROnly: (\d+)',
            'bk': r'Backup: (\d+)',
            'rc': r'RClone: (\d+)'
        }

        def done(rc, out, err):
            if rc == 0:
                return True
            if "no such entry" in err:
                if retry_not_found:
                    log.warning("Volume %s not found.", name)
                    return False  # Retry.
                else:
                    return True  # Volume is not present.
            return False

        def retry(rc, out, err):
            if "server or network not reponding" in err:
                return True
            if "no quorum elected" in err:
                return True
            if "invalid RPC (RX) operation" in err:
                return True  # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True  # May occur during server startup.
            if "no such entry" in err:
                if retry_not_found:
                    return True  # Retry not found!
            return False

        out = self.vos(['listvldb', '-name', name, '-noresolve', '-nosort'],
                       done, retry)
        for line in out.splitlines():
            if line == '':
                continue  # Skip blank lines
            m = re.match(r'(\S+)', line)
            if m:
                entry['name'] = m.group(1)
                continue
            for name, pattern in vos_fields.items():
                m = re.search(pattern, line)
                if m:
                    entry[name] = int(m.group(1))
            m = re.search(r'server (\S+) partition (\S+) (RO|RW) Site(.*)',
                          line)
            if m:
                site = {
                    'server': m.group(1),
                    'partition': m.group(2).replace('/vicep', ''),
                    'type': m.group(3).lower(),
                    'flags': m.group(4).replace('--', '').lower().strip()
                }
                entry['sites'].append(site)

        return entry

    def vos_listaddrs(self):
        """
        Retrieve the list of registered server UUIDs from the VLDB.
        """
        log.debug("vos_listaddrs()")

        def done(rc, out, err):
            return rc == 0 and out != ''

        def retry(rc, out, err):
            if "server or network not reponding" in err:
                return True
            if "no quorum elected" in err:
                return True
            if "invalid RPC (RX) operation" in err:
                return True  # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True  # May occur during server startup.
            if out == '':
                return True  # No results; servers not registered yet?
            return False

        out = self.vos(['listaddrs', '-noresolve', '-printuuid'],
                       done=done, retry=retry)
        servers = []
        uuid = None
        addrs = []
        for line in out.splitlines():
            m = re.match(r'UUID: (\S+)', line)
            if m:
                uuid = m.group(1)
                addrs = []
                continue
            m = re.match(r'(\S+)', line)
            if m:
                addrs.append(m.group(1))
                continue
            m = re.match(r'$', line)
            if m:
                # Records are terminated with a blank line.
                servers.append(dict(uuid=uuid, addrs=addrs))
                uuid = None
                addrs = []
        return servers

    def vos_listpart(self, server):
        """
        Retrieve the list of available partitions on the given server.
        """
        log.debug("vos_listpart(server='%s')", server)

        def done(rc, out, err):
            return rc == 0 and 'The partitions on the server are:' in out

        def retry(rc, out, err):
            if "Possible communication failure" in err:
                return True
            if "server or network not reponding" in err:
                return True
            if "invalid RPC (RX) operation" in err:
                return True  # May occur during server startup.
            if "Could not fetch the list of partitions" in err:
                return True
            return False
        out = self.vos(['listpart', '-server', server], done=done, retry=retry)
        parts = re.findall(r'/vicep([a-z]+)', out)
        log.debug('partitions=%s', parts)
        return parts

    def vos_create(self, name, server, partition, quota):
        """
        Ensure a user exists.
        """
        log.debug("vos_create(name='%s', server='%s', partition='%s', "
                  "quota='%d')", name, server, partition, quota)

        def done(rc, out, err):
            if rc == 0:
                log.info('changed: vos create returned 0')
                self.results['changed'] = True
                return True
            if rc == 255 and "already exists" in err:
                log.info("Volume '%s' already exists.", name)
                return True
            return False

        def retry(rc, out, err):
            if "Possible communication failure" in err:
                return True
            if "server or network not reponding" in err:
                return True
            if "no quorum elected" in err:
                return True
            if "invalid RPC (RX) operation" in err:
                return True  # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True  # May occur during server startup.
            if "Could not fetch the list of partitions" in err:
                return True
            return False

        self.vos(['create', '-server', server, '-partition', partition,
                 '-name', name, '-maxquota', str(quota)], done, retry)

    def vos_addsite(self, name, server, partition):
        log.debug("vos_addsite(name='%s', server='%s', partition='%s')",
                  name, server, partition)

        def done(rc, out, err):
            if rc == 0:
                log.info('changed: vos addsite returned 0')
                self.results['changed'] = True
                return True
            if 'RO already exists on partition' in err:
                return True
            return False
        self.vos(['addsite', '-server', server, '-partition', partition,
                 '-id', name], done)

    def vos_release(self, name):
        log.debug("vos_release(name='%s')", name)

        def done(rc, out, err):
            if rc == 0:
                log.info('changed: vos release returned 0')
                self.results['changed'] = True
                return True
            if 'has no replicas - release operation is meaningless!' in err:
                return True
            return False

        self.vos(['release', '-id', name, '-verbose'], done)
        self.fs('checkv')

    def vos_remove(self, name, server=None, partition=None):
        """
        Ensure volume is absent.
        """
        log.debug("vos_remove(name='%s', server='%s', partition='%s')",
                  name, server, partition)

        def done(rc, out, err):
            if rc == 0 and err == '':
                log.info('changed: vos remove returned 0')
                self.results['changed'] = True
                return True
            if "no such entry" in err:
                log.warning("Volume %s not found.", name)
                return True
            if rc == 0 and "Can't find volume name" in err:
                log.warning("Volume %s not found.", name)
                return True
            return False

        def retry(rc, out, err):
            if "server or network not reponding" in err:
                return True
            if "no quorum elected" in err:
                return True
            if "invalid RPC (RX) operation" in err:
                return True  # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True  # May occur during server startup.
            return False

        args = ['remove', '-id', str(name)]
        if server:
            args.extend(['-server', server])
        if partition:
            args.extend(['-partition', partition])
        self.vos(args, done, retry)


class Volume(object):

    def __init__(self, module):
        self._cell = None
        self._afsroot = None
        self._dynroot = None

        self.results = dict(changed=False)
        self.module = module
        self.cmd = Command(module, self.results)

        self.state = module.params['state']
        self.volume = module.params['volume']
        self.server = module.params['server']
        self.partition = module.params['partition']
        self.mount = module.params['mount']
        self.acl = module.params['acl']
        self.quota = module.params['quota']
        self.replicas = module.params['replicas']
        self.auth_user = module.params['auth_user']
        self.auth_keytab = module.params['auth_keytab']

        # Convert k4 to k5 name.
        if '.' in self.auth_user and '/' not in self.auth_user:
            self.auth_user = self.auth_user.replace('.', '/')

        if self.mount and not self.mount.startswith('/'):
            module.fail_json(
                msg='Invalid parameter: mount must be an asolute path; %s' %
                    self.mount)

    def ensure_present(self):
        if not self.cmd.localauth:
            self.login()
        if not self.server:
            servers = self.cmd.vos_listaddrs()
            if not servers:
                self.die('No fileservers found.')
            self.server = servers[0]['addrs'][0]  # Pick the first one found.
        if not self.partition:
            partitions = self.cmd.vos_listpart(self.server)
            if not partitions:
                self.die('No partitions found on server %s.' % self.server)
            self.partition = partitions[0]  # Pick the first one found.
        self.cmd.vos_create(self.volume, self.server, self.partition,
                            self.quota)
        if self.mount:
            self.make_mounts(self.volume, self.mount)
        if self.mount and self.acl:
            self.set_acl(self.volume, self.mount, self.acl)
        if self.replicas:
            for addr, part in self.determine_sites(self.volume, self.replicas):
                self.cmd.vos_addsite(self.volume, addr, part)
        entry = self.cmd.vos_listvldb(self.volume)
        if self.volume != 'root.afs':
            # Defer root.afs release until root.cell is mounted.
            for s in entry['sites']:
                if s['flags'] != '':
                    self.cmd.vos_release(self.volume)
                    entry = self.cmd.vos_listvldb(self.volume)
                    break
        self.results['volume'] = entry

    def ensure_absent(self):
        if not self.cmd.localauth:
            self.login()
        if self.mount:
            self.remove_mounts(self.volume, self.mount)
        entry = self.cmd.vos_listvldb(self.volume, retry_not_found=False)
        if 'ro' in entry:
            ro = entry['ro']
            for s in entry['sites']:
                if s['type'] == 'ro':
                    self.cmd.vos_remove(ro, s['server'], s['partition'])
        self.cmd.vos_remove(self.volume)

    def die(self, msg):
        log.error(msg)
        self.module.fail_json(msg=msg)

    def lookup_directory(self, name):
        """
        Lookup an OpenAFS directory from the local facts file.
        """
        try:
            with open('/etc/ansible/facts.d/openafs.fact') as f:
                facts = json.load(f)
            dir = facts['dirs'][name]
        except Exception:
            self.module.fail_json(msg='Unable to locate %s directory.' % name)
        return dir

    def login(self):
        """
        Get a token for authenicated access.
        """
        log.debug("login()")
        if not os.path.exists(self.auth_keytab):
            self.die('keytab %s not found.' % self.auth_keytab)
        self.cmd.kinit(self.auth_keytab, self.auth_user)
        self.cmd.aklog()

    def lookup_index(self, fileservers, addr):
        for i in fileservers:
            for a in fileservers[i]['addrs']:
                if a == addr:
                    return i
        return None

    def determine_sites(self, name, nreplicas):
        """
        Determine the fileserver addresses and partitions for
        read-only sites.
        """
        log.debug("determine_ro_sites(name='%s', nreplicas=%d)",
                  name, nreplicas)

        # Use a simple integer server index key to reference fileservers.
        fileservers = {}
        for i, entry in enumerate(self.cmd.vos_listaddrs()):
            if not entry['addrs']:
                log.warning("No addresses found for fileserver %d; "
                            "ignoring.", i)
                continue
            fileservers[i] = entry
        log.debug('determine_sites: fileservers=%s',
                  pprint.pformat(fileservers))

        # Convert the ipv4 addresses of the rw and ro sites to the server
        # index.
        entry = self.cmd.vos_listvldb(name)
        rw = None  # rw (index, partition) tuple
        ro = []    # list of (index, partition) tuples for ro sites
        for s in entry['sites']:
            i = self.lookup_index(fileservers, s['server'])
            if s['type'] == 'rw':
                rw = (i, s['partition'])
            elif s['type'] == 'ro':
                ro.append((i, s['partition']))

        log.debug('determine_sites: rw=%s, ro=%s',
                  pprint.pformat(rw), pprint.pformat(ro))

        # Assemble a list of server indexes to matching our goal state. Start
        # with the existing ro sites.
        goal = list(ro)
        all_ = sorted(fileservers.keys())
        taken = [s[0] for s in goal]

        # First, add the read-only clone, if one is not already present.
        if len(goal) < nreplicas and rw:
            clone = rw  # Same server and partition as the rw volume.
            if not clone[0] in taken:
                goal.append(clone)

        # Add remote read-only sites, if needed. Additional read-onlies
        # are added in listaddrs order.
        if len(goal) < nreplicas:
            available = []
            taken = [s[0] for s in goal]
            for i in all_:
                if i not in taken:
                    available.append(i)
            while len(goal) < nreplicas and available:
                goal.append((available.pop(0), None))
        log.debug('determine_sites: goal=%s', pprint.pformat(goal))

        # Finally, get the addresses and partitions to be added. Order is
        # important here, since we want to add the clone first.
        sites = []
        ro_indexes = [s[0] for s in ro]
        for s in goal:
            i, part = s
            if i not in ro_indexes:
                addr = fileservers[i]['addrs'][0]
                if not part:
                    parts = self.cmd.vos_listpart(addr)
                    part = parts[0]
                sites.append((addr, part))
        log.debug('determine_sites: sites=%s', pprint.pformat(sites))
        return sites

    def get_cell_name(self):
        """
        Get the current cell name.
        Assumes this node is a client.
        """
        if self._cell is None:
            out = self.cmd.fs('wscell')
            m = re.search(r"This workstation belongs to cell '(.*)'", out)
            if m:
                self._cell = m.group(1)
                log.info("Cell name is '%s'.", self._cell)
        if not self._cell:
            self.die("Cell name not found.")
        return self._cell

    def get_dynroot_mode(self):
        """
        Returns true if the client dynroot is enabled.

        Stat the root vnode of the root.cell volume of the local cell to
        determine if dynroot mode is enabled on the cache manager.  This check
        assumes the root.cell volume has already been created, which is
        normally done before a client is started, since non-dynroot clients
        will mount the root.cell volume on startup.

        Accesses to /afs/.:mount/<cell>:<volume>/<path> will fail with an
        ENODEV error when dynroot is disabled.  Note that accesses to
        /afs/.:mount/ and /afs/.:mount/<cell>:<volume> will succeed even when
        dynroot is disabled, so be sure to check a vnode in the volume to
        determine when dynroot mode is on.
        """
        if self._dynroot is not None:
            return self._dynroot
        cell = self.get_cell_name()
        path = '/afs/.:mount/{0}:root.cell/.'.format(cell)
        try:
            os.stat(path)
            self._dynroot = True
        except OSError as e:
            if e.errno == errno.ENODEV:
                self._dynroot = False
            else:
                self.die(str(e))

        status = 'enabled' if self._dynroot else 'disabled'
        log.info('dynroot is {0}'.format(status))
        return self._dynroot

    def get_afs_root(self):
        """
        Get the afs root directory from the client cacheinfo file.
        The root directory conventionally '/afs'.
        """
        if self._afsroot is None:
            path = os.path.join(self.lookup_directory('viceetcdir'),
                                'cacheinfo')
            with open(path) as f:
                cacheinfo = f.read()
            m = re.match(r'(.*):(.*):(.*)', cacheinfo)
            if m:
                self._afsroot = m.group(1)
        if not self._afsroot:
            self.die("Failed to parse cacheinfo file '%s'." % path)
        return self._afsroot

    def split_dir(self, path):
        """
        Split a path to get the parent and directory.
        Example:
            split_dir('/afs/example.com/test) -> ('/afs/example.com', 'test')
        """
        components = path.split('/')
        dirname = components.pop(-1)
        return '/'.join(components), dirname

    def get_acls(self, path):
        """
        Get positive and negative acls for a given path.
        Returns a tuple of dictionaries.
        """
        out = self.cmd.fs('listacl', '-path', path)
        acls = {'normal': {}, 'negative': {}}
        for line in out.splitlines():
            if line.startswith('Accces list for'):
                continue
            if line == 'Normal rights:':
                kind = 'normal'
                continue
            if line == 'Negative rights:':
                kind = 'negative'
                continue
            m = re.match(r'  (\S+) (\S+)', line)
            if m:
                name = m.group(1)
                rights = set(m.group(2))
                acls[kind][name] = rights
        return acls['normal'], acls['negative']

    def is_read_only(self, path):
        """
        Check to see if the given path is to a read-only volume.
        """
        out = self.cmd.fs('examine', '-path', path)
        m = re.search(r'Volume status for vid = (\d+) named (\S+)', out)
        if not m:
            self.die("Unable to examine path '%s'." % path)
        name = m.group(2)
        return name.endswith('.readonly') or name.endswith('.backup')

    def make_mounts(self, volume, path, vcell=None, rw=False):
        """
        Make a mount point.
        """
        log.debug("make_mounts(volume='%s, path='%s', vcell='%s')",
                  volume, path, vcell)
        afsroot = self.get_afs_root()
        cell = self.get_cell_name()
        dynroot = self.get_dynroot_mode()
        parent_changed = False

        # The root.afs volume is a special case. In dynroot mode, the rw
        # root.afs vnodes are accessed via the synthetic
        # '/afs/.:mount/<cell>:root.afs' path.
        if volume == 'root.afs' and path == afsroot:
            log.info("Skipping root.afs mount on '%s'." % path)
            return

        # The root.cell volume is a special case in dynroot mode.
        if volume == 'root.cell':
            # Be sure to create a cellular mount point for root.cell.
            if not vcell:
                vcell = cell
            canonical_path = os.path.join(afsroot, vcell)
            canonical_path_rw = os.path.join(afsroot, '.' + vcell)
            if path in (canonical_path, canonical_path_rw):
                # /afs/.:mount/example.com:root.afs/example.com -> root.cell
                if dynroot:
                    path = os.path.join(afsroot,
                                        '.:mount',
                                        ':'.join([vcell, 'root.afs']),
                                        vcell)
                    log.info("Mounting volume '%s' with dynroot path '%s'" %
                             (volume, path))

        # Switch to the read/write path when available
        parent, dirname = self.split_dir(path)
        root_path = os.path.join(afsroot, cell)
        root_path_rw = os.path.join(afsroot, '.' + cell)
        if parent.startswith(root_path):
            parent_rw = parent.replace(root_path, root_path_rw)
            if os.path.exists(parent_rw):
                parent = parent_rw
                path = os.path.join(parent_rw, dirname)
                log.info("Mounting volume '%s' with read/write path '%s'" %
                         (volume, path))

        # Create the regular and read/only mount points if not present.
        path_reg = os.path.join(parent, dirname)
        if not os.path.exists(path_reg):
            log.info("Creating new mount point '%s' for volume '%s'.",
                     path_reg, volume)
            args = ['mkmount', '-dir', path_reg, '-vol', volume]
            if vcell:
                args.extend(['-cell', vcell])
            with ExtraRights(self, 'ia', parent):
                self.cmd.fs(*args)
            log.info('changed: mounted volume %s on path %s.',
                     volume, path_reg)
            self.results['changed'] = True
            self.results['mount'] = path_reg
            parent_changed = True

        # Create a rw mount point if this is root.cell, or requested by caller.
        if volume == 'root.cell' or rw:
            path_rw = os.path.join(parent, '.' + dirname)
            if not os.path.exists(path_rw):
                log.info("Creating new mount point '%s' for volume '%s'.",
                         path_rw, volume)
                args = ['mkmount', '-dir', path_rw, '-vol', volume, '-rw']
                if vcell:
                    args.extend(['-cell', vcell])
                with ExtraRights(self, 'ia', parent):
                    self.cmd.fs(*args)
                log.info('changed: mounted volume %s on path %s with '
                         'read/write flag.', volume, path_rw)
                self.results['changed'] = True
                self.results['mount'] = path_rw
                parent_changed = True

        # Release the parent volume if we changed it.
        if parent_changed:
            out = self.cmd.fs('getfid', '-path', parent)
            m = re.search(r'File .* \((\d+)\.\d+\.\d+\)', out)
            if not m:
                self.die("Failed to find parent volume id for mount path '%s'."
                         % path)
            parent_id = m.group(1)
            log.info("Releasing parent volume '%s'.", parent_id)
            self.cmd.vos_release(parent_id)

    def remove_mounts(self, volume, path):
        """
        Remove regular and read/write mount points.
        """
        log.debug("remove_mounts(volume='%s', path='%s')", volume, path)
        afsroot = self.get_afs_root()
        cell = self.get_cell_name()
        dynroot = self.get_dynroot_mode()

        if not os.path.exists(path):
            log.info("Mount '%s' already absent.", path)
            return

        # Unmounting root.afs is a no-op.
        if volume == 'root.afs':
            log.info("Skipping fs rmmount of root.afs")
            return

        # The root.cell volume is a special case.
        if volume == 'root.cell' and dynroot:
            canonical_path = os.path.join(afsroot, cell)
            canonical_path_rw = os.path.join(afsroot, '.' + cell)
            if path in (canonical_path, canonical_path_rw):
                path = os.path.join(afsroot,
                                    '.:mount',
                                    ':'.join([cell, 'root.afs']),
                                    cell)
                log.info("Unmounting volume '%s' with dynroot path '%s'" %
                         (volume, path))

        # Switch to the read/write path when available
        parent, dirname = self.split_dir(path)
        root_path = os.path.join(afsroot, cell)
        root_path_rw = os.path.join(afsroot, '.' + cell)
        if parent.startswith(root_path):
            parent_rw = parent.replace(root_path, root_path_rw)
            if os.path.exists(parent_rw):
                parent = parent_rw
                log.info("Unmounting volume '%s' with read/write parent "
                         "path '%s'" % (volume, parent))

        # Remove the regular and read/only mount points when present.
        parent_changed = False
        paths = [
            os.path.join(parent, dirname),
            os.path.join(parent, '.' + dirname),
        ]
        for p in paths:
            if os.path.exists(p):
                with ExtraRights(self, 'd', parent):
                    self.cmd.fs('rmmount', '-dir', p)
                log.info('changed: removed mount %s', p)
                self.results['changed'] = True
                parent_changed = True

        # Release the parent volume if we changed it.
        if parent_changed:
            out = self.cmd.fs('getfid', '-path', parent)
            m = re.search(r'File .* \((\d+)\.\d+\.\d+\)', out)
            if not m:
                self.die("Failed to find parent volume id for mount "
                         "path '%s'." % path)
            parent_id = m.group(1)
            log.info("Releasing parent volume '%s'.", parent_id)
            self.cmd.vos_release(parent_id)

    def parse_acl_param(self, acl):
        """
        Convert a list of strings (each containing two words separated by one
        or more spaces) or dictionaries into a list of terms to be passed to fs
        setacl.
        """
        if not isinstance(acl, list):
            self.die('Internal: acl param is not a list')
        terms = []
        for a in acl:
            if isinstance(a, dict):
                for n, r in a.items():
                    terms.extend([n, r])
            else:
                m = re.match(r'\s*(\S+)\s+(\S+)', a)
                if m:
                    terms.extend(list(m.groups()))
                else:
                    self.die("Invalid acl term '%s'." % a)
        log.debug('acl=%s', pprint.pformat(terms))
        return terms

    def set_acl(self, volume, path, acl):
        """
        Set the acl on a path and checks for a change.
        This function assumes the user is a member of system:administors (or
        already has 'a' rights on directory.)
        """
        log.debug("set_acl(volume='%s', path='%s', acl='%s')",
                  volume, path, acl)
        acl = self.parse_acl_param(acl)
        afsroot = self.get_afs_root()  # e.g. /afs
        cell = self.get_cell_name()    # e.g. example.com
        dynroot = self.get_dynroot_mode()

        # The root.afs volume is a special case.
        if volume == 'root.afs' and path == afsroot:
            if dynroot:
                path = os.path.join(afsroot,
                                    '.:mount',
                                    ':'.join([cell, 'root.afs']))
                log.info("Setting '%s' acl with dynroot path '%s'." %
                         (volume, path))
            else:
                # No dynroot: We need to use temporary rw mount point if the
                # root.afs volume has been released. For now, just set the acls
                # before the release.
                if self.is_read_only(path):
                    log.info("Skipping acl change of root.afs on path '%s'.",
                             path)
                    return

        # Switch to the read/write path when available
        root_path = os.path.join(afsroot, cell)
        root_path_rw = os.path.join(afsroot, '.' + cell)
        if path.startswith(root_path):
            path_rw = path.replace(root_path, root_path_rw)
            if os.path.exists(path_rw):
                log.info("Setting acl with rw path '%s'.", path_rw)
                path = path_rw
            else:
                log.warning("path_rw='%s' does not exist.", path_rw)

        log.info("Setting acl '%s' on path '%s'.", ' '.join(acl), path)
        old = self.get_acls(path)
        self.cmd.fs('setacl', '-clear', '-dir', path, '-acl', *acl)
        new = self.get_acls(path)
        self.results['acl'] = new
        if new != old:
            log.info('changed: acl from=%s to=%s',
                     pprint.pformat(old), pprint.pformat(new))
            self.results['changed'] = True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str',
                       choices=['present', 'absent'],
                       default='present'),
            volume=dict(type='str', aliases=['name']),
            server=dict(type='str', default=None),
            partition=dict(type='str', default=None),
            mount=dict(type='str',
                       default=None,
                       aliases=['mountpoint', 'mtpt']),
            acl=dict(type='list', default=[], aliases=['acls', 'rights']),
            quota=dict(type='int', default=0),
            replicas=dict(type='int', default=0),
            localauth=dict(type='bool', default=False),
            auth_user=dict(type='str', default='admin'),
            auth_keytab=dict(type='str', default='admin.keytab'),
        ),
        supports_check_mode=False,
    )
    log.info('Starting %s', module_name)

    v = Volume(module)
    if v.state == 'present':
        v.ensure_present()
    elif v.state == 'absent':
        v.ensure_absent()
    else:
        v.die("Internal error: invalid state %s" % v.state)

    log.debug('Results: %s' % pprint.pformat(v.results))
    log.info('Exiting %s' % module_name)
    module.exit_json(**v.results)


if __name__ == '__main__':
    main()
