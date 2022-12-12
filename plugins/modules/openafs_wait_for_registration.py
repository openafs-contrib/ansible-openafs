#!/usr/bin/python
# Copyright (c) 2020, Sine Nomine Associates
# BSD 2-Clause License

ANSIBLE_METADATA = {
    'metadata_version': '1.1.',
    'status': ['preview'],
    'supported_by': 'community',
}

DOCUMENTATION = r'''
---
module: openafs_wait_for_registration

short_description: Wait for the fileserver VLDB registration

description: Wait for the fileserver VLDB registration to be completed.

options:
  timeout:
    description: Maximum time to wait in seconds.
    type: int
    default: 600

  delay:
    description: Number of seconds to delay before waiting.
    type: int
    default: 0

  sleep:
    description: Number of seconds to wait between retries.
    type: int
    default: 20

  signal:
    description:
      - If true, issue a XCPU signal to the fileserver to force it to resend
        the VLDB registration after C(sleep) seconds has expired.

      - By default, the fileserver will retry the VLDB registration every 5
        minutes untill the registration succeeds. This option can be used to
        force the retry to happen sooner. As a side-effect, XCPU signal will
        trigger a dump of the fileserver hosts and callback tables, so this
        option must be used with caution.

    type: bool
    default: True

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: Wait for fileserver registration
  openafs_contrib.openafs.openafs_wait_for_registration:
    sleep: 10
    timeout: 600
    signal: no
  when:
    - afs_is_fileserver
'''

import json                     # noqa: E402
import os                       # noqa: E402
import pprint                   # noqa: E402
import re                       # noqa: E402
import socket                   # noqa: E402
import struct                   # noqa: E402
import time                     # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')


def quad_dotted(unpacked_address):
    packed_address = struct.pack('!I', unpacked_address)
    return socket.inet_ntoa(packed_address)


class UUID:
    """
    UUID encoder/decoder.
    """
    _s = struct.Struct('!I H H B B 6B')
    size = _s.size

    def __init__(self, time_low=0, time_mid=0, time_hi=0, clock_hi=0,
                 clock_low=0, node=None):
        self.time_low = time_low
        self.time_mid = time_mid
        self.time_hi = time_hi
        self.clock_hi = clock_hi
        self.clock_low = clock_low
        if node is None:
            self.node = (0, 0, 0, 0, 0, 0)
        else:
            self.node = node

    @classmethod
    def decode(cls, data):
        """
        Create a uuid from packed bytes.

        Args:
            data (bytes): packed uuid bytes
        Returns:
            new UUID object
        """
        vals = cls._s.unpack(data)
        time_low = vals[0]
        time_mid = vals[1]
        time_hi = vals[2]
        clock_hi = vals[3]
        clock_low = vals[4]
        node = vals[5:11]
        return UUID(time_low, time_mid, time_hi, clock_hi, clock_low, node)

    def encode(self):
        """
        Return uuid as packed bytes.

        Returns:
            bytes: packed uuid data
        """
        data = self._s.pack(
            self.time_low,
            self.time_mid,
            self.time_hi,
            self.clock_hi,
            self.clock_low,
            *self.node)
        return data

    @classmethod
    def parse(cls, uuid_str):
        """
        Parse uuid string representation.

        Note: Accepts standard UUID 5-group format 8-4-4-4-12 and OpenAFS
        6-group UUID format 8-4-4-2-2-12.

        Args:
            uuid_str (str): string reprentation of UUID
        Returns:
            new UUID object
        Raises:
            ValueError: uuid_str is not formatted as a uuid string
        """
        r = r'^([0-9a-fA-F]{8})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-'\
            '([0-9a-fA-F]{2})-?([0-9a-fA-F]{2})-([0-9a-fA-F]{12})$'
        m = re.search(r, uuid_str)
        if not m:
            raise ValueError('Not a UUID string: {0}'.format(uuid_str))
        g = m.groups()
        time_low = int(g[0], base=16)
        time_mid = int(g[1], base=16)
        time_hi = int(g[2], base=16)
        clock_hi = int(g[3], base=16)
        clock_low = int(g[4], base=16)
        node = tuple([int(g[5][i:i+2], base=16) for i in range(0, 12, 2)])
        return UUID(time_low, time_mid, time_hi, clock_hi, clock_low, node)

    def __eq__(self, other):
        return \
            self.time_low == other.time_low and \
            self.time_mid == other.time_mid and \
            self.time_hi == other.time_hi and \
            self.clock_hi == other.clock_hi and \
            self.clock_low == other.clock_low and \
            self.node == other.node

    def __ne__(self, other):
        return \
            self.time_low != other.time_low or \
            self.time_mid != other.time_mid or \
            self.time_hi != other.time_hi or \
            self.clock_hi != other.clock_hi or \
            self.clock_low != other.clock_low or \
            self.node != other.node

    def __hash__(self):
        return hash((self.time_low, self.time_mid, self.time_hi, self.clock_hi,
                    self.clock_low, self.node))

    def __str__(self):
        """
        Return string representation of the UUID.
        """
        sep = ''
        return "{0:08x}-{1:04x}-{2:04x}-{3:02x}{4}{5:02x}-"\
               "{6:02x}{7:02x}{8:02x}{9:02x}{10:02x}{11:02x}"\
            .format(self.time_low, self.time_mid, self.time_hi,
                    self.clock_hi, sep, self.clock_low, *self.node)

    def __repr__(self):
        return \
            "<UUID:"\
            " time_low={s.time_low}"\
            " time_mid={s.time_mid}"\
            " time_hi={s.time_hi}"\
            " clock_hi={s.clock_hi}"\
            " clock_low={s.clock_low}"\
            " node={s.node}"\
            ">".format(s=self)


class Sysid:
    MAGIC = 0x88aabbcc
    VERSION = 1

    def __init__(self, filename=None):
        self.magic = self.MAGIC
        self.version = self.VERSION
        self.uuid = UUID()
        self.addrs = []
        if filename:
            with open(filename, 'rb') as f:
                data = f.read()
            self.decode(data)

    def decode(self, data):
        """Decode the packed binary sysid data.

        Args:
            data (bytes): packed sysid data

        Returns:
            Sysid: self
        """
        magic, version = struct.unpack('=I I', data[0:8])
        if magic != self.MAGIC:
            raise ValueError('Bad magic value: 0x%0x' % magic)
        if version != self.VERSION:
            raise ValueError('Bad version value: %d' % version)
        uuid = UUID.decode(data[8:24])
        num_addrs, = struct.unpack('=I', data[24:28])
        if not 0 <= num_addrs <= 255:
            raise ValueError('Bad number of addresses: 0x%s' %
                             data[24:28].hex())
        expected = 28 + (4 * num_addrs)
        if len(data) != expected:
            raise ValueError('Bad data length: expected=%d, found=%d' %
                             (expected, len(data)))
        unpacked_addrs = struct.unpack('!{0}I'.format(num_addrs), data[28:])
        self.magic = magic
        self.version = version
        self.uuid = uuid
        self.addrs = [quad_dotted(ua) for ua in unpacked_addrs]
        return self

    def __repr__(self):
        return \
            "<Sysid:"\
            " magic={self.magic}"\
            " version={self.version}"\
            " uuid={self.uuid}"\
            " addrs={self.addrs}"\
            ">".format(self=self)


def main():
    results = dict(
        changed=False,
    )
    module = AnsibleModule(
            argument_spec=dict(
                timeout=dict(type='int', default=600),
                delay=dict(type='int', default=0),
                sleep=dict(type='int', default=20),
                signal=dict(type='bool', default=True)
            ),
            supports_check_mode=False,
    )
    log = Logger(module_name)
    log.info('Starting %s', module_name)

    timeout = module.params['timeout']
    delay = module.params['delay']
    sleep = module.params['sleep']
    signal = module.params['signal']

    if delay < 0:
        log.warning('Ignoring negative delay parameter.')
        delay = 0
    if sleep < 1:
        log.warning('Ignoring out of range sleep parameter.')
        sleep = 1

    def lookup_command(name):
        """
        Lookup an OpenAFS command from local facts file. Try the PATH
        if not found in the local facts.
        """
        try:
            with open('/etc/ansible/facts.d/openafs.fact') as f:
                facts = json.load(f)
            cmd = facts['bins'][name]
        except Exception as e:
            log.warning("Unable to load facts: %s", e)
            cmd = module.get_bin_path(name)
        if not cmd:
            module.fail_json(msg='Unable to locate %s command.' % name)
        return cmd

    def lookup_directory(name):
        """
        Lookup an OpenAFS directory from the local facts file.
        """
        try:
            with open('/etc/ansible/facts.d/openafs.fact') as f:
                facts = json.load(f)
            dir = facts['dirs'][name]
        except Exception as e:
            log.warning("Unable to load facts: %s", e)
            module.fail_json(msg='Unable to locate %s directory.' % name)
        return dir

    def run_command(args, done=None, retry=None):
        """
        Run an afs command with retries.
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
            if "no such entry" in err:
                return True  # Retry not found!
            return False

        if done is None:
            done = _done
        if retry is None:
            retry = _retry

        args.append('-localauth')
        cmdline = ' '.join(args)
        retries = 120
        while True:
            log.debug('Running: %s', cmdline)
            rc, out, err = module.run_command(args)
            log.debug('Ran: %s, rc=%d, out=%s, err=%s', cmdline, rc, out, err)
            if done(rc, out, err):
                return out
            if retries == 0 or not retry(rc, out, err):
                log.error("Failed: %s, rc=%d, err=%s", cmdline, rc, err)
                module.fail_json(
                    dict(msg='Command failed.', cmdline=cmdline, rc=rc,
                         out=out, err=err))
            log.warning("Failed: %s, rc=%d, err=%s; %d retr%s left.",
                        cmdline, rc, err, retries,
                        ('ies' if retries > 1 else 'y'))
            retries -= 1
            time.sleep(5)

    def vos_listaddrs():
        """
        Retrieve the server uuid and addreses from the VLDB.
        """
        def done(rc, out, err):
            return rc == 0

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

        vos = lookup_command('vos')
        out = run_command([vos, 'listaddrs', '-noresolve', '-printuuid'],
                          done=done, retry=retry)
        servers = []
        uuid = None
        addrs = []
        for line in out.splitlines():
            m = re.match(r'UUID: (\S+)', line)
            if m:
                uuid = UUID.parse(m.group(1))
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
        log.debug("servers=%s", servers)
        return servers

    def lookup_uuid():
        """
        Retreive the fileserver UUID value from the sysid file created
        by the fileserver process.
        """
        path = os.path.join(lookup_directory('afslocaldir'), 'sysid')
        if not os.path.exists(path):
            # The sysid file is created by the filserver process.
            log.info("Waiting for sysid file '%s'.", path)
            return None
        log.debug("Reading sysid file '%s'.", path)
        sysid = Sysid(path)
        log.debug('sysid=%s', sysid)
        return sysid.uuid

    def lookup_bnode():
        """
        Lookup the active fileserver bnode name; 'fs', 'dafs', or None.
        """
        path = os.path.join(lookup_directory('afsbosconfigdir'), 'BosConfig')
        log.debug("Reading BosConfig file '%s'.", path)
        with open(path) as f:
            bosconfig = f.read()
        bnodes = re.findall(r'bnode (fs|dafs) \S+ 1', bosconfig)
        if len(bnodes) == 0:
            log.warning('No active fileserver bnodes found in BosConfig.')
            return None
        if len(bnodes) > 1:
            log.warning('Too many fileserver bnodes found in BosConfig.')
            return None
        bnode = bnodes[0]
        log.debug('fileserver bnode is %s', bnode)
        return bnode

    def lookup_pid():
        """
        Lookup the fileserver process pid or return None if not found.
        """
        bnode = lookup_bnode()
        if not bnode:
            return None
        path = os.path.join(lookup_directory('afslocaldir'),
                            '%s.file.pid' % bnode)
        try:
            log.debug("Reading pid file '%s'.", path)
            with open(path) as f:
                pid = int(f.read())
        except IOError as e:
            log.warning("Unable to read pid file '%s'; %s", path, e)
            return None
        except ValueError as e:
            log.warning("Unable to convert pid file '%s' contents to int; %s",
                        path, e)
            return None
        log.debug('fileserver pid is %d', pid)
        return pid

    #
    # Wait for VLDB registration. We check for our uuid in the VLDB, and if not
    # present, send a signal to the fileserver to expedite the registration.
    # The fileserver will retry to register every 5 minutes as well.
    #
    if delay:
        time.sleep(delay)
    now = int(time.time())
    expires = now + timeout
    retries = 0
    while True:
        uuid = lookup_uuid()
        if uuid:
            servers = vos_listaddrs()
            registered_uuids = [s['uuid'] for s in servers]
            if uuid in registered_uuids:
                results['uuid'] = str(uuid)
                log.info('Fileserver uuid %s is registered.', uuid)
                break
        if signal and retries > 0:
            pid = lookup_pid()
            if pid:
                log.info('Running: kill -XCPU %d', pid)
                module.run_command(['kill', '-XCPU', '%d' % pid])
        now = int(time.time())
        if now > expires:
            log.error('Timeout expired.')
            module.fail_json(msg='Timeout expired')
        log.info('Will retry in %d seconds.' % sleep)
        time.sleep(sleep)
        retries += 1

    results['retries'] = retries
    log.info('Results: %s', pprint.pformat(results))
    module.exit_json(**results)


if __name__ == '__main__':
    main()
