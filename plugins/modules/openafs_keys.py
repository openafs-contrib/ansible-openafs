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
module: openafs_keys

short_description: Add kerberos service keys with asetkey

description:
  - Import the service keys from a keytab file using the OpenAFS
    C(asetkey) utility.

  - This module uses C(asetkey) rather than the newer C(akeyconvert)
    since C(akeyconvert) is not available on all platforms yet.

  - Before running this module, be sure C(asetkey) is installed

  - The C(asetkey) program requires the server C(CellServDB)
    and C(ThisCell) files to be present.

  - A keytab file containing the service keys must be copied to the server.

options:

  state:
    description: c(present) to ensure keys are present in the keyfile(s)
    required: false
    type: str

  keytab:
    description: path to the keytab file on the remote node
    required: true
    type: path

  cell:
    description: AFS cell name
    required: true
    type: str

  realm:
    description: Kerberos realm name
    required: false
    type: str
    default: uppercase of the cell name

  asetkey:
    description: asetkey program path
    required: false
    type: path
    default: Search the local facts, search the path.

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: Upload service keytab
  become: yes
  copy:
    src: "files/example.keytab"
    dest: "/usr/afs/etc/rxkad.keytab"
    mode: 0600
    owner: root
    group: root

- name: Add service keys
  become: yes
  openafs_contrib.openafs.openafs_keys:
    state: present
    keytab: /usr/afs/etc/rxkad.keytab
    cell: example.com
'''

RETURN = r'''
asetkey:
  description: asetkey path found
  type: path
  returned: success
#  sample: /usr/sbin/asetkey

have_extended_keys:
  description: Indicates if extended keys are supported.
  type: bool
  returned: success
#  sample: true

keys:
  description: keys found in the keytab file
  type: list
  returned: success
#  sample:
#    - enctype: aes256-cts-hmac-sha1-96
#      eno: 18
#      kvno: 3
#      principal: afs/example.com@EXAMPLE.COM
#      realm: EXAMPLE.COM
#      timestamp: 1605734384
#    - enctype: aes128-cts-hmac-sha1-96
#      eno: 17
#      kvno: 3
#      principal: afs/example.com@EXAMPLE.COM
#      realm: EXAMPLE.COM
#      timestamp: 1605734384

imported:
  description: Imported key versions
  type: list
  returned: success
#  sample:
#    - eno: 17
#      kvno: 3
#      type: rxkad_krb5
#    - eno: 18
#      kvno: 3
#      type: rxkad_krb5

service_principal:
  description: kerberos service principal
  type: str
  returned: success
#  sample: "afs/example.com@EXAMPLE.COM"
'''

import json                     # noqa: E402
import os                       # noqa: E402
import pprint                   # noqa: E402
import re                       # noqa: E402
import struct                   # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')

KEYTAB_MAGIC = 0x0502
KEYTAB_MAGIC_OLD = 0x0501

# See https://www.iana.org/assignments/kerberos-parameters/kerberos-parameters.xhtml       # noqa: E501
ENCTYPES = {
    1: 'des-cbc-crc',
    2: 'des-cbc-md4',
    3: 'des-cbc-md5',
    5: 'des3-cbc-md5',
    7: 'des3-cbc-sha1',
    9: 'dsaWithSHA1-CmsOID',
    10: 'md5WithRSAEncryption-CmsOID',
    11: 'sha1WithRSAEncryption-CmsOID',
    12: 'rc2CBC-EnvOID',
    13: 'rsaEncryption-EnvOID',
    14: 'rsaES-OAEP-ENV-OID',
    15: 'des-ede3-cbc-Env-OID',
    16: 'des3-cbc-sha1-kd',
    17: 'aes128-cts-hmac-sha1-96',
    18: 'aes256-cts-hmac-sha1-96',
    23: 'rc4-hmac',
    24: 'rc4-hmac-exp',
    25: 'camellia128-cts-cmac',
    26: 'camellia256-cts-cmac',
    65: 'subkey-keymaterial',
}
DES_ENCTYPES = (1, 2, 3, 15)


class Keytab:
    """
    Decode keytab files.
    """
    #
    # The following C-like structure definitions illustrate the MIT keytab
    # file format. All values are in network byte order. All text is ASCII.
    #
    #   keytab {
    #       uint16_t file_format_version;                    /* 0x502 */
    #       keytab_entry entries[*];
    #   };
    #   keytab_entry {
    #       int32_t size;
    #       uint16_t num_components;    /* sub 1 if version 0x501 */
    #       counted_octet_string realm;
    #       counted_octet_string components[num_components];
    #       uint32_t name_type;   /* not present if version 0x501 */
    #       uint32_t timestamp;
    #       uint8_t vno8;
    #       keyblock key;
    #       uint32_t vno; /* only present if >= 4 bytes left in entry */
    #   };
    #   counted_octet_string {
    #       uint16_t length;
    #       uint8_t data[length];
    #   };
    #   keyblock {
    #       uint16_t type;
    #       counted_octet_string key;
    #   };

    def __init__(self, filename):
        self.entries = []
        self.name = filename
        self.read(filename)

    def _read_data(self, f, fmt):
        """
        Read one or more data fields.
        """
        size = struct.calcsize(fmt)
        data = f.read(size)
        if len(data) != size:
            raise IOError("Failed to read keytab data.")
        return struct.unpack(fmt, data)  # returns a tuple

    def _read_bytes(self, f):
        """
        Read a byte string.
        """
        length = self._read_data(f, "!H")
        bytes_, = self._read_data(f, "%ds" % length)
        return bytes_

    def _read_string(self, f):
        """
        Read an ascii text string.
        """
        return self._read_bytes(f).decode('ascii')

    def _read_entry(self, f, version):
        """
        Read a keytab entry.
        """
        numc, = self._read_data(f, "!h")
        if version == KEYTAB_MAGIC_OLD:
            numc -= 1
        realm = self._read_string(f)
        components = []
        for _ in range(0, numc):
            components.append(self._read_string(f))
        if version != KEYTAB_MAGIC_OLD:
            self._read_data(f, "!L")  # read past name_type
        timestamp, vno8, eno = self._read_data(f, "!LBH")
        self._read_bytes(f)  # read past key
        principal = "%s@%s" % ('/'.join(components), realm)
        entry = {
            'realm': realm,
            'components': components,
            'principal': principal,
            'timestamp': timestamp,
            'kvno': vno8,
            'eno': eno,
            'enctype': ENCTYPES.get(eno, 'unknown'),
        }
        return entry

    def read(self, path):
        """
        Read a keytab file.
        """
        self.filename = path
        stat = os.stat(path)
        file_size = stat.st_size
        with open(path, 'rb') as f:
            offset = struct.calcsize("!h")
            try:
                version, = self._read_data(f, "!h")
            except IOError:
                version = 0
            if not (version == KEYTAB_MAGIC or version == KEYTAB_MAGIC_OLD):
                raise ValueError("File {0} is not keytab.".format(path))
            while offset < file_size:
                f.seek(offset)
                # record size, not including this field
                size, = self._read_data(f, "!l")
                entry = self._read_entry(f, version)
                self.entries.append(entry)
                # Calculate next record location.
                record_size = struct.calcsize("!l") + size
                offset += record_size
        return

    def find(self, principal):
        """
        Find keytab entries for the given principal.
        """
        entries = []
        for e in self.entries:
            if e['principal'] == principal:
                entries.append(e)
        return entries


def main():
    results = dict(
        changed=False,
        debug=[],
        imported=[],
    )
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(type='str', choices=['present'], default='present'),
                keytab=dict(type='path', required=True),
                cell=dict(type='str', required=True),
                realm=dict(type='str', default=None),
            ),
            supports_check_mode=False,
    )
    log = Logger(module_name)
    log.info('Starting %s', module_name)
    log.info('Parameters: %s', pprint.pformat(module.params))

    keytab = module.params['keytab']
    cell = module.params['cell']
    realm = module.params['realm']
    if not realm:
        realm = cell.upper()

    def lookup_command(name):
        try:
            with open('/etc/ansible/facts.d/openafs.fact') as f:
                facts = json.load(f)
            cmd = facts['bins'][name]
        except Exception:
            cmd = module.get_bin_path(name)
        if not cmd:
            module.fail_json(msg='Unable to locate %s command.' % name)
        return cmd

    asetkey = lookup_command('asetkey')
    log.debug('asetkey=%s', asetkey)

    # Decode the keytab to find the kvnos, enctypes, and principals.
    keytab = Keytab(keytab)
    service_principal = 'afs/%s@%s' % (cell, realm)
    keys = keytab.find(service_principal)
    if not keys:
        # Try old service principal format.
        service_principal = '%s@%s' % (cell, realm)
        keys = keytab.find(service_principal)
    if not keys:
        msg = "Keys not found in keytab %s for cell '%s', realm '%s'." % \
              (keytab.name, cell, realm)
        log.error(msg)
        module.fail_json(msg=msg, keys=keytab.entries)

    results['service_principal'] = service_principal
    results['keys'] = keys

    # Check asetkey usage to determine how to add keys.
    rc, out, err = module.run_command([asetkey])
    usage = err.splitlines()
    if len(usage) == 0 or 'usage' not in usage[0]:
        log.error("Failed to get asetkey usage; rc=%d, out=%s, err=%s",
                  rc, out, err)
        module.fail_json(msg="Failed to get asetkey usage.",
                         asetkey=asetkey, rc=rc, out=out, err=err)
    have_extended_keys = False
    for line in usage:
        if "add <type> <kvno> <subtype> <keyfile> <princ>" in line:
            have_extended_keys = True
    log.debug("have_extended_keys=%s",
              "True" if have_extended_keys else "False")
    results['have_extended_keys'] = have_extended_keys

    # Retrieve the current keys to check for changes.
    rc, before, err = module.run_command([asetkey, 'list'])
    if rc != 0:
        log.error("Failed to list keys; rc=%d, out=%s, err=%s", rc, out, err)
        module.fail_json(msg="Failed to list keys.",
                         asetkey=asetkey, rc=rc, out=out, err=err)

    # Add the keys.
    for e in keys:
        kvno = str(e['kvno'])
        eno = str(e['eno'])
        if have_extended_keys:
            args = [asetkey, 'add', 'rxkad_krb5', kvno, eno, keytab.name,
                    service_principal]
        else:
            # Old versions only support DES. OpenAFS 1.6.5 up to 1.8.0 will
            # read non-DES keys from rxkad.keytab directly, so we just ignore
            # them here and hope for the best.
            if eno not in DES_ENCTYPES:
                continue
            args = [asetkey, 'add', kvno, keytab.name, service_principal]
        rc, out, err = module.run_command(args)
        results['debug'].append(dict(cmd=' '.join(args),
                                rc=rc, out=out, err=err))
        if rc != 0:
            log.error("Failed asetkey add; rc=%d, out=%s, err=%s",
                      rc, out, err)
            module.fail_json(msg="Failed asetkey add",
                             rc=rc, out=out, err=err, keys=keys)

    # Check for changes and return list of key version numbers. Avoid returning
    # the key values!
    rc, after, err = module.run_command([asetkey, 'list'])
    if rc != 0:
        log.error("Failed to list keys; rc=%d, out=%s, err=%s", rc, out, err)
        module.fail_json(msg="Failed to list keys.",
                         asetkey=asetkey, rc=rc, out=out, err=err)
    if before != after:
        results['changed'] = True
    for line in after.splitlines():
        m = re.match(r'^(\w+)+\s+kvno\s+(\d+)\s+enctype\s+(\d+)', line)
        if m:
            results['imported'].append(dict(type=m.group(1), kvno=m.group(2),
                                            eno=m.group(3)))

    log.info('Results: %s', pprint.pformat(results))
    module.exit_json(**results)


if __name__ == '__main__':
    main()
