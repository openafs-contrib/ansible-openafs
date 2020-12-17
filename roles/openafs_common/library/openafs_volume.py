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
    description: c(present) ensure the volume is present, c(absent) ensure the volume is removed
    type: str
    required: no
    default: c(present)
  volume:
    description: Volume name. Should be the read-write volume name.
    type: str
    required: yes
  server:
    description:
      - The initial volume fileserver location.
      - If provided, should be the hostname or fileserver address.
      - If not provided, the first fileserver address from c(vos listaddrs) will be used.
      - The volume will not be moved if it already exists on a different server.
      - This option is ignored when the state is c(absent).
    type: str
    default: first fileserver entry found in VLDB
  partition:
    description:
      - The initial volume partition id.
      - If provided, should be the partition id; c('a') ..  c('iu').
      - If not provided, the first partition found from c(vos listpart) will be used.
      - The volume will not be moved if it already exists on a different partition.
      - This option is ignored when the state is c(absent).
    type: str
    default: the first partition found on the fileserver
  mount:
    description:
      - The initial mount point path.
      - Should be the fully-qualified path to the mount point to be created.
      - The read/write path variant will be used if it is available.
      - A read/write mount point will also be created for the c(root.cell) volume.
      - The c(i) and c(a) ACL rights will be temporarily assigned to the mount point
        parent directory in order to create the mount point if those rights are missing.
      - The volume containing the parent volume will be released if a mount point was
        created.
      - The volume will be created but not mounted if the c(mount) option is not given.
      - This option is ignored when the state is c(absent).
      - This option may only be used if a client is installed on the remote node.
    type: str
    required: no
  acl:
    description:
      - The access control list to be set in the volumes root directory.
      - The c(acl) option my be specified as a list of strings. Each string
        contains a pair of strings separated by a space. The substring
        names a user or group, the second indicates the access rights.
      - See c(fs setacl) for details.
      - This option may only be used if a client is installed on the remote node.
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
      - The c(replicas) option indicates the minumum number of read-only volumes
        desired.
    type: int
    required: no
    default: 0
  localauth:
    description:
      - Indicates if the c(-localauth) option is to be used for authentication.
      - This option should only be used when running on a server.
      - The c(mount) and c(acl) options may not be used with c(localauth).
    type: bool
    default: no
  auth_user:
    description:
      - The afs user name to be used when c(localauth) is False.
      - The user must be a member of the c(system:administrators) group and
        must be a server superuser, that is, set in the c(UserList) file on
        each server in the cell.
      - This option may only be used if a client is installed on the remote node.
    type: str
    default: admin
  auth_keytab:
    description:
      - The path on the remote host to the keytab file to be used to authenticate.
      - The keytab file must already be present on the remote host.
      - This option may only be used if a client is installed on the remote node.
    type: str
    default: admin.keytab
"""

EXAMPLES = r"""
- name: Create afs root volume
  openafs_volume:
    state: present
    name: root.afs
    mount: /afs
    acl: "system:anyuser read"
    replicas: 3

- name: Create cell root volume
  openafs_volume:
    state: present
    name: root.cell
    mount: /afs/example.com
    acl: "system:anyuser read"
    replicas: 3

- name: Create a volume
  openafs_volume:
    state: present
    name: test
    mount: /afs/example.com/test
    acl:
      - "bob all"
      - "system:anyuser read"
      - "system:authuser write"

- name: Alternate acl format
  openafs_volume:
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
  returned: on success
  type: list of strings
  sample:
    - "system:anyuser":
        - r
        - l
mount:
  description: Mount point path
  returned: on success
  type: str
  sample: "/afs/.example.com/test/foo",
volume:
  description: Volume information
  returned: on success
  type: dictionary
  sample:
    name: foo
    rw: 536870927
    sites:
      - flags: ""
        partition: a
        server: 192.168.122.214
        type: rw
"""

import json
import logging
import os
import pprint
import re
import time
from ansible.module_utils.basic import AnsibleModule

log = logging.getLogger(__name__)

# Cached items.
_commands = {}
_cell = None
_afsroot = None
_dynroot = None

def main():
    results = dict(
        changed=False,
    )
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(type='str', choices=['present', 'absent'], default='present'),
                volume=dict(type='str', aliases=['name']),
                server=dict(type='str', default=None),
                partition=dict(type='str', default=None),
                mount=dict(type='str', default=None, aliases=['mountpoint', 'mtpt']),
                acl=dict(type='list', default=[], aliases=['acls', 'rights']),
                quota=dict(type='int', default=0),
                replicas=dict(type='int', default=0),
                localauth=dict(type='bool', default=False),
                auth_user=dict(type='str', default='admin'),
                auth_keytab=dict(type='str', default='admin.keytab'),
            ),
            supports_check_mode=False,
    )
    state = module.params['state']
    volume = module.params['volume']
    server = module.params['server']
    partition = module.params['partition']
    mount = module.params['mount']
    acl = module.params['acl']
    quota = str(module.params['quota'])
    replicas = module.params['replicas']
    localauth = module.params['localauth']
    auth_user = module.params['auth_user']
    auth_keytab = module.params['auth_keytab']

    if mount and not mount.startswith('/'):
        module.fail_json(msg='Invalid parameter: mount must be an asolute path; %s' % mount)

    logfile = '/var/log/ansible-openafs/openafs_volume_%d.log' % os.getuid()
    logging.basicConfig(
        level=logging.DEBUG,
        filename=logfile,
        format='%(asctime)s %(levelname)s %(message)s',
    )
    log.info('Starting openafs_volume')
    log.debug('Parameters: %s' % pprint.pformat(module.params))

    def die(msg):
        log.error(msg)
        module.fail_json(msg=msg, note='See log %s for details.' % logfile)

    def lookup_command(name):
        """
        Lookup an OpenAFS command. First search the installation facts,
        then the PATH.
        """
        global _commands
        if name in _commands:
            return _commands[name]
        try:
            with open('/etc/ansible/facts.d/openafs.fact') as f:
                facts = json.load(f)
            cmd = facts['bins'][name]
        except:
            cmd = module.get_bin_path(name)
        if not cmd:
            die('Unable to locate %s command.' % name)
        _commands[name] = cmd
        return cmd

    def lookup_directory(name):
        """
        Lookup an OpenAFS directory from the local facts file.
        """
        try:
            with open('/etc/ansible/facts.d/openafs.fact') as f:
                facts = json.load(f)
            dir = facts['dirs'][name]
        except:
            module.fail_json(msg='Unable to locate %s directory.' % name)
        return dir

    def run_command(cmd, *args):
        """
        Run a command.
        """
        cmdargs = [cmd] + list(args)
        cmdline = ' '. join(args)
        rc, out, err = module.run_command(cmdargs)
        log.debug('command=%s, rc=%d, out=%s, err=%s', cmdline, rc, out, err)
        if rc != 0:
            die('Command failed: %s, rc=%d, out=%s, err=%s' % (cmdline, rc, out, err))
        return out

    def login():
        """
        Get a token for authenicated access.
        """
        log.debug("login()")
        if not os.path.exists(auth_keytab):
            die('keytab %s not found.' % auth_keytab)
        kinit = lookup_command('kinit')
        aklog = lookup_command('aklog')
        run_command(kinit, '-k', '-t', auth_keytab, auth_user)
        run_command(aklog, '-d')

    def vos(args, done=None, retry=None):
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
                return True # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True # May occur during server startup.
            return False

        if done is None:
            done = _done
        if retry is None:
            retry = _retry

        args.insert(0, lookup_command('vos'))
        if localauth:
            args.append('-localauth')
        cmdline = ' '.join(args)
        retries = 120
        while True:
            rc, out, err = module.run_command(args)
            log.debug('command=%s, rc=%d, out=%s, err=%s', cmdline, rc, out, err)
            if done(rc, out, err):
                return out
            if retries == 0 or not retry(rc, out, err):
                die("Command failed: %s, rc=%d, err=%s" % (cmdline, rc, err))
            log.warning("Failed: %s, rc=%d, err=%s; %d retr%s left.",
                cmdline, rc, err, retries, ('ies' if retries > 1 else 'y'))
            retries -= 1
            time.sleep(5)

    def fs(*args):
        """
        Run the fs command and return the stdout.
        """
        return run_command(lookup_command('fs'), *args)

    def vos_listaddrs():
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
                return True # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True # May occur during server startup.
            if out == '':
                return True # No results; servers not registered yet?
            return False

        out = vos(['listaddrs', '-noresolve', '-printuuid'], done=done, retry=retry)
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
            m = re.match(r'$', line) # Records are terminated with a blank line.
            if m:
                servers.append(dict(uuid=uuid, addrs=addrs))
                uuid = None
                addrs = []
        return servers

    def vos_listpart(server):
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
                return True # May occur during server startup.
            if "Could not fetch the list of partitions" in err:
                return True
            return False
        out = vos(['listpart', '-server', server], done=done, retry=retry)
        parts = re.findall(r'/vicep([a-z]+)', out)
        log.debug('partitions=%s', parts)
        return parts

    def get_entry(name, retry_not_found=True):
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
                    return False # Retry.
                else:
                    return True  # Volume is not present.
            return False

        def retry(rc, out, err):
            if "server or network not reponding" in err:
                return True
            if "no quorum elected" in err:
                return True
            if "invalid RPC (RX) operation" in err:
                return True # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True # May occur during server startup.
            if "no such entry" in err:
                if retry_not_found:
                    return True # Retry not found!
            return False

        out = vos(['listvldb', '-name', name, '-noresolve', '-nosort'], done, retry)
        for line in out.splitlines():
            if line == '':
                continue # Skip blank lines
            m = re.match(r'(\S+)', line)
            if m:
                entry['name'] = m.group(1)
                continue
            for name, pattern in vos_fields.items():
                m = re.search(pattern, line)
                if m:
                    entry[name] = int(m.group(1))
            m = re.search(r'server (\S+) partition (\S+) (RO|RW) Site(.*)', line)
            if m:
                site = {
                    'server': m.group(1),
                    'partition': m.group(2).replace('/vicep', ''),
                    'type': m.group(3).lower(),
                    'flags': m.group(4).replace('--', '').lower().strip()
                }
                entry['sites'].append(site)

        return entry

    def vos_create(name, server, partition, quota):
        """
        Ensure a user exists.
        """
        log.debug("vos_create(name='%s', server='%s', partition='%s', quota='%d')", \
                  name, server, partition, quota)
        def done(rc, out, err):
            if rc == 0:
                log.info('changed: vos create returned 0')
                results['changed'] = True
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
                return True # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True # May occur during server startup.
            if "Could not fetch the list of partitions" in err:
                return True
            return False

        vos(['create', '-server', server, '-partition', partition,
                 '-name', name, '-maxquota', quota], done, retry)

    def lookup_index(fileservers, addr):
        for i in fileservers:
            for a in fileservers[i]['addrs']:
                if a == addr:
                    return i
        return None

    def determine_sites(name, nreplicas):
        """
        Determine the fileserver addresses and partitions for
        read-only sites.
        """
        log.debug("determine_ro_sites(name='%s', nreplicas=%d)", name, nreplicas)

        # Use a simple integer server index key to reference fileservers.
        fileservers = {}
        for i, entry in enumerate(vos_listaddrs()):
            if not entry['addrs']:
                log.warning("No addresses found for fileserver %d; ignoring.", i)
                continue
            fileservers[i] = entry
        log.debug('determine_sites: fileservers=%s', pprint.pformat(fileservers))

        # Convert the ipv4 addresses of the rw and ro sites to the server index.
        entry = get_entry(name)
        rw = None  # rw (index, partition) tuple
        ro = []    # list of (index, partition) tuples for ro sites
        for s in entry['sites']:
            i = lookup_index(fileservers, s['server'])
            if s['type'] == 'rw':
                rw = (i, s['partition'])
            elif s['type'] == 'ro':
                ro.append((i, s['partition']))

        log.debug('determine_sites: rw=%s, ro=%s', pprint.pformat(rw), pprint.pformat(ro))

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
                if not i in taken:
                    available.append(i)
            while len(goal) < nreplicas and available:
                goal.append((available.pop(0), None))
        log.debug('determine_sites: goal=%s', pprint.pformat(goal))

        # Finally, get the addresses and partitions to be added. Order is important
        # here, since we want to add the clone first.
        sites = []
        ro_indexes = [s[0] for s in ro]
        for s in goal:
            i, part = s
            if not i in ro_indexes:
                addr = fileservers[i]['addrs'][0]
                if not part:
                    parts = vos_listpart(addr)
                    part = parts[0]
                sites.append((addr, part))
        log.debug('determine_sites: sites=%s', pprint.pformat(sites))
        return sites

    def vos_addsite(name, server, partition):
        log.debug("vos_addsite(name='%s', server='%s', partition='%s')", name, server, partition)
        def done(rc, out, err):
            if rc == 0:
                log.info('changed: vos addsite returned 0')
                results['changed'] = True
                return True
            if 'RO already exists on partition' in err:
                return True
            return False
        vos(['addsite', '-server', server, '-partition', partition, '-id', name], done)

    def vos_release(name):
        log.debug("vos_release(name='%s')", name)
        def done(rc, out, err):
            if rc == 0:
                log.info('changed: vos release returned 0')
                results['changed'] = True
                return True
            if 'has no replicas - release operation is meaningless!' in err:
                return True
            return False
        vos(['release', '-id', name, '-verbose'], done)
        fs('checkv')

    def vos_remove(name, server=None, partition=None):
        """
        Ensure volume is absent.
        """
        log.debug("vos_remove(name='%s', server='%s', partition='%s')", name, server, partition)
        def done(rc, out, err):
            if rc == 0 and err == '':
                log.info('changed: vos remove returned 0')
                results['changed'] = True
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
                return True # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True # May occur during server startup.
            return False

        args = ['remove', '-id', str(name)]
        if server:
            args.extend(['-server', server])
        if partition:
            args.extend(['-partition', partition])
        vos(args, done, retry)

    def get_cell_name():
        """
        Get the current cell name.
        Assumes this node is a client.
        """
        global _cell # Cached value.
        if _cell is None:
            out = fs('wscell')
            m = re.search(r"This workstation belongs to cell '(.*)'", out)
            if m:
                _cell = m.group(1)
                log.info("Cell name is '%s'.", _cell)
        if not _cell:
            die("Cell name not found.")
        return _cell

    def get_dynroot_mode():
        """
        Returns true if the client dynroot is enabled.

        When the dynamic root (-dynroot, -dynroot-sparse) and the fake stat
        (-fakestat, -fakestat-all) modes are in effect, use the special directory
        named /afs/.:mount to mount the root.cell volume and to set root.afs
        access rights.

        The afsd command arguments are saved as an installation fact to provide
        a portable way to lookup the client startup options.
        """
        global _dynroot # Cached value.
        if _dynroot is None:
            try:
                with open('/etc/ansible/facts.d/openafs.fact') as f:
                    facts = json.load(f)
                options = facts['client_options']
            except Exception as e:
                die('Unable to determine dynroot mode: afsd options not found; %s' % e)
            options = set(options.split(' '))
            dynroot = set(['-dynroot', '-dynroot-sparse'])
            fakestat = set(['-fakestat', '-fakestat-all'])
            _dynroot = (dynroot & options) and (fakestat & options)
        return _dynroot

    def get_afs_root():
        """
        Get the afs root directory from the client cacheinfo file.
        The root directory conventionally '/afs'.
        """
        global _afsroot  # Cached value.
        if _afsroot is None:
            path = os.path.join(lookup_directory('viceetcdir'), 'cacheinfo')
            with open(path) as f:
                cacheinfo = f.read()
            m = re.match(r'(.*):(.*):(.*)', cacheinfo)
            if m:
                _afsroot = m.group(1)
        if not _afsroot:
            die("Failed to parse cacheinfo file '%s'." % path)
        return _afsroot

    def split_dir(path):
        """
        Split a path to get the parent and directory.
        Example:
            split_dir('/afs/example.com/test) -> ('/afs/example.com', 'test')
        """
        components = path.split('/')
        dirname = components.pop(-1)
        return '/'.join(components), dirname

    def get_acls(path):
        """
        Get positive and negative acls for a given path.
        Returns a tuple of dictionaries.
        """
        out = fs('listacl', '-path', path)
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

    class ExtraRights:
        """
        Context manager to add rights temporarily to allow the system administrator
        to mount and unmount volumes.
        """
        def __init__(self, rights, path, name='system:administrators'):
            self.rights = set(rights)
            self.path = path
            self.name = name
            acl = get_acls(self.path)[0]
            self.existing = acl.get(self.name, set(''))
            self.augmented = self.existing | self.rights

        def __enter__(self):
            if self.existing != self.augmented:
                log.info("Adding temporary rights '%s %s' to directory '%s.", self.name, ''.join(self.rights), self.path)
                rights = ''.join(self.augmented)
                fs('setacl', '-dir', self.path, '-acl', self.name, rights)
            return self

        def __exit__(self, *exc):
            if self.existing != self.augmented:
                log.info("Removing temporary rights '%s %s' to directory '%s'", self.name, ''.join(self.rights), self.path)
                rights = ''.join(self.existing)
                if not rights:
                    rights = 'none'
                fs('setacl', '-dir', self.path, '-acl', self.name, rights)

    def is_read_only(path):
        """
        Check to see if the given path is to a read-only volume.
        """
        out = fs('examine', '-path', path)
        m = re.search(r'Volume status for vid = (\d+) named (\S+)', out)
        if not m:
            die("Unable to examine path '%s'." % path)
        name = m.group(2)
        return name.endswith('.readonly') or name.endswith('.backup')

    def make_mounts(volume, path, vcell=None, rw=False):
        """
        Make a mount point.
        """
        log.debug("make_mounts(volume='%s, path='%s', vcell='%s')", volume, path, vcell)
        afsroot = get_afs_root()
        cell = get_cell_name()
        dynroot = get_dynroot_mode()
        parent_changed = False

        # The root.afs volume is a special case. In dynroot mode, the rw root.afs
        # vnodes are accessed via the synthetic '/afs/.:mount/<cell>:root.afs' path.
        if volume == 'root.afs' and path == afsroot:
            log.info("Skipping root.afs mount on '%s'." % path)
            return

        # The root.cell volume is a special case in dynroot mode.
        if volume == 'root.cell':
            if not vcell:
                vcell = cell # Be sure to create a cellular mount point for root.cell.
            canonical_path = os.path.join(afsroot, vcell)           # e.g. /afs/example.com
            canonical_path_rw = os.path.join(afsroot, '.' + vcell)  # e.g. /afs/.example.com
            if path in (canonical_path, canonical_path_rw):
                if dynroot:
                    # e.g., /afs/.:mount/example.com:root.afs/example.com -> root.cell
                    path = os.path.join(afsroot, '.:mount', ':'.join([vcell, 'root.afs']), vcell)
                    log.info("Mounting volume '%s' with dynroot path '%s'" % (volume, path))

        # Switch to the read/write path when available
        parent, dirname = split_dir(path)
        root_path = os.path.join(afsroot, cell)          # e.g., /afs/example.com
        root_path_rw = os.path.join(afsroot, '.' + cell) # e.g, /afs/.example.com
        if parent.startswith(root_path):
            parent_rw = parent.replace(root_path, root_path_rw)
            if os.path.exists(parent_rw):
                parent = parent_rw
                path = os.path.join(parent_rw, dirname)
                log.info("Mounting volume '%s' with read/write path '%s'" % (volume, path))

        # Create the regular and read/only mount points if not present.
        path_reg = os.path.join(parent, dirname)
        if not os.path.exists(path_reg):
            log.info("Creating new mount point '%s' for volume '%s'.", path_reg, volume)
            args = ['mkmount', '-dir', path_reg, '-vol', volume]
            if vcell:
                args.extend(['-cell', vcell])
            with ExtraRights('ia', parent):
                fs(*args)
            log.info('changed: mounted volume %s on path %s.', volume, path_reg)
            results['changed'] = True
            results['mount'] = path_reg
            parent_changed = True

        # Create a rw mount point if this is root.cell, or requested by caller.
        if volume == 'root.cell' or rw:
            path_rw = os.path.join(parent, '.' + dirname)
            if not os.path.exists(path_rw):
                log.info("Creating new mount point '%s' for volume '%s'.", path_rw, volume)
                args = ['mkmount', '-dir', path_rw, '-vol', volume, '-rw']
                if vcell:
                    args.extend(['-cell', vcell])
                with ExtraRights('ia', parent):
                    fs(*args)
                log.info('changed: mounted volume %s on path %s with read/write flag.', volume, path_rw)
                results['changed'] = True
                results['mount'] = path_rw
                parent_changed = True

        # Release the parent volume if we changed it.
        if parent_changed:
            out = fs('getfid', '-path', parent)
            m = re.search(r'File .* \((\d+)\.\d+\.\d+\)', out)
            if not m:
                die("Failed to find parent volume id for mount path '%s'." % path)
            parent_id = m.group(1)
            log.info("Releasing parent volume '%s'.", parent_id)
            vos_release(parent_id)

    def remove_mounts(volume, path):
        """
        Remove regular and read/write mount points.
        """
        log.debug("remove_mounts(volume='%s', path='%s')", volume, path)
        afsroot = get_afs_root()
        cell = get_cell_name()
        dynroot = get_dynroot_mode()

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
                path = os.path.join(afsroot, '.:mount', ':'.join([cell, 'root.afs']), cell)
                log.info("Unmounting volume '%s' with dynroot path '%s'" % (volume, path))

        # Switch to the read/write path when available
        parent, dirname = split_dir(path)
        root_path = os.path.join(afsroot, cell)          # e.g., /afs/example.com
        root_path_rw = os.path.join(afsroot, '.' + cell) # e.g., /afs/.example.com
        if parent.startswith(root_path):
            parent_rw = parent.replace(root_path, root_path_rw)
            if os.path.exists(parent_rw):
                parent = parent_rw
                log.info("Unmounting volume '%s' with read/write parent path '%s'" % (volume, parent))

        # Remove the regular and read/only mount points when present.
        parent_changed = False
        for p in (os.path.join(parent, dirname), os.path.join(parent, '.' + dirname)):
            if os.path.exists(p):
                with ExtraRights('d', parent):
                    fs('rmmount', '-dir', p)
                log.info('changed: removed mount %s', p)
                results['changed'] = True
                parent_changed = True

        # Release the parent volume if we changed it.
        if parent_changed:
            out = fs('getfid', '-path', parent)
            m = re.search(r'File .* \((\d+)\.\d+\.\d+\)', out)
            if not m:
                die("Failed to find parent volume id for mount path '%s'." % path)
            parent_id = m.group(1)
            log.info("Releasing parent volume '%s'.", parent_id)
            vos_release(parent_id)

    def parse_acl_param(acl):
        """
        Convert a list of strings (each containing two words separated by one or more spaces)
        or dictionaries into a list of terms to be passed to fs setacl.
        """
        if not isinstance(acl, list):
            die('Internal: acl param is not a list')
        terms = []
        for a in acl:
            if isinstance(a, dict):
                for n,r in a.items():
                    terms.extend([n, r])
            else:
                m = re.match(r'\s*(\S+)\s+(\S+)', a)
                if m:
                    terms.extend(list(m.groups()))
                else:
                    die("Invalid acl term '%s'." % a)
        log.debug('acl=%s', pprint.pformat(terms))
        return terms

    def set_acl(volume, path, acl):
        """
        Set the acl on a path and checks for a change.
        This function assumes the user is a member of system:administors (or
        already has 'a' rights on directory.)
        """
        log.debug("set_acl(volume='%s', path='%s', acl='%s')", volume, path, acl)
        acl = parse_acl_param(acl)
        afsroot = get_afs_root() # e.g. /afs
        cell = get_cell_name()   # e.g. example.com
        dynroot = get_dynroot_mode()

        # The root.afs volume is a special case.
        if volume == 'root.afs' and path == afsroot:
            if dynroot:
                path = os.path.join(afsroot, '.:mount', ':'.join([cell, 'root.afs']))
                log.info("Setting '%s' acl with dynroot path '%s'." % (volume, path))
            else:
                # No dynroot: We need to use temporary rw mount point if the root.afs volume has
                # been released. For now, just set the acls before the release.
                if is_read_only(path):
                    log.info("Skipping acl change of root.afs on path '%s'.", path)
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
        old = get_acls(path)
        fs('setacl', '-clear', '-dir', path, '-acl', *acl)
        new = get_acls(path)
        results['acl'] = new
        if new != old:
            log.info('changed: acl from=%s to=%s', pprint.pformat(old), pprint.pformat(new))
            results['changed'] = True

    #
    # Ensure volume is present/absent.
    #
    if state == 'present':
        if not localauth:
            login()
        if not server:
            servers = vos_listaddrs()
            if not servers:
                die('No fileservers found.')
            server = servers[0]['addrs'][0] # Pick the first one found.
        if not partition:
            partitions = vos_listpart(server)
            if not partitions:
                die('No partitions found on server %s.' % server)
            partition = partitions[0] # Pick the first one found.
        vos_create(volume, server, partition, quota)
        if mount:
            make_mounts(volume, mount)
        if mount and acl:
            set_acl(volume, mount, acl)
        if replicas:
            for addr, part in determine_sites(volume, replicas):
                vos_addsite(volume, addr, part)
        entry = get_entry(volume)
        if volume != 'root.afs':    # Defer root.afs release until root.cell is mounted.
            for s in entry['sites']:
                if s['flags'] != '':
                    vos_release(volume)
                    entry = get_entry(volume)
                    break
        results['volume'] = entry
    elif state == 'absent':
        if not localauth:
            login()
        if mount:
            remove_mounts(volume, mount)
        entry = get_entry(volume, retry_not_found=False)
        if 'ro' in entry:
            ro = entry['ro']
            for s in entry['sites']:
                if s['type'] == 'ro':
                    vos_remove(ro, s['server'], s['partition'])
        vos_remove(volume)
    else:
        die("Internal error: invalid state %s" % state)

    log.debug('Results: %s' % pprint.pformat(results))
    log.info('Exiting openafs_volume')
    module.exit_json(**results)

if __name__ == '__main__':
    main()
