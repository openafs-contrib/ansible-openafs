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
module: openafs_principal

short_description: Create principals and keytab files

description:
  - Create a kerberos principal on a primary KDC using C(kadmin.local) and
    export the keys to a keytab file on the KDC. The keytab may be transfered
    to remote nodes with C(syncrhonize) or encrypted with C(ansible-vault) then
    downloaded to the controller for distribution in subsequent plays. This

  - If the state is C(present), then a principal is added if it is not
    already present and a keyfile is created. The initial password may
    be specified with the C(password) parameter, otherwise a random key
    is generated. The key is not randomized when the keytab is generated.

  - If the state is C(absent), then the principal and keytab files are
    removed if present.

  - If the state is C(rekey), and the princical already exists, then new keys
    are generated with the given C(enctypes) and are added to the existing
    keytab file. The updated keytab file must be redistributed servers to avoid
    authentication failures. If the state is C(rekey) and the principal is not
    present, a principal is created and a keytab is generated as if the state
    is C(present).

  - Keytabs for the principals created by the module are stored in the
    C(keytabs) directory on the KDC, readable by root. The default path is
    C(/var/lib/ansible-openafs/keytabs).

  - Currently, this module does not check the keytabs to verify if the key
    versions numbers are in sync with the database. If the principal's password
    is changed manually, remove the keytab file on the kdc before running
    with the C(present) state to generate a new keytab.

requirements:
  - The Kerberos realm has been created.
  - C(kadmin.local) is installed and in the PATH.

options:
  state:
    description:
      - C(present) ensure the principal and keytab file exist.
      - C(absent) ensure the principal and keytab file are removed.
      - C(rekey) generate new keys and add them to the keytab file.
    type: str
    required: false
    default: present

  principal:
    description:
      - Kerberos principal name.
      - The name should be provided without the REALM component.
      - Old kerberos 4 '.' separators are automatically converted to modern '/'
        separators.
    type: str
    required: true

  enctypes:
    description:
      - Kerberos encryption and salt types.
      - See C(kadmin) documenation for possible values.
    type: list
    required: false
    default: See C(kadmin)
    aliases:
      - enctype
      - encryption_type
      - encryption_types
      - keysalts

  rekey:
    description: Generate new key versions.
    type: bool
    required: false
    default: false

  acl:
    description: Administrative permissions
    type: str
    required: false
    default: None

  keytab_name:
    description: Alternative keytab name.
    type: str
    requried: false
    default: principal name with '/' characters replaced by '.' characters.

  keytabs:
    desciption: Keytab storage directory on the KDC
    type: path
    required: false
    default: /var/lib/ansible-openafs/keytabs

  kadmin:
    desciption: Path to the C(kadmin.local) command
    type: path
    required: false
    default: search PATH

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: Create an AFS service key
  become: yes
  openafs_contrib.openafs.openafs_principal:
    principal: afs/example.com
    encryption_types:
      - aes128-cts:normal
      - aes256-cts:normal
  register: service_key

- name: Download the keytab to controller for distribution
  become: yes
  fetch:
    flat: yes
    src: "{{ service_key.keytab }}"
    dest: "rxkad.keytab"

- name: Generate new keys
  become: yes
  openafs_contrib.openafs.openafs_principal:
    state: rekey
    principal: afs/example.com

# Requires an old version of Kerberos.
- name: Obsolete DES key for testing
  become: yes
  openafs_contrib.openafs.openafs_principal:
    state: present
    service: afs
    principal: afs/broken.com
    enctype: des-cbc-crc:afs3

- name: Create some user principals
  become: yes
  openafs_contrib.openafs.openafs_principal:
    state: present
    principal: "{{ item }}"
    password: "{{ initial_password }}
  with_items:
    - alice
    - bob
    - charlie
'''

RETURN = r'''
metadata:
  description: Principal metadata from C(get_principal)
  type: list
  returned: success

debug:
  description: kadmin commands executed and output
  type: list
  returned: always

kadmin:
  description: kadmin executable path
  type: path
  returned: always
  sample: "/sbin/kadmin.local"

keytab:
  description: Path of the generated keytab on the remote node.
  type: path
  returned: success
  sample: "/var/lib/ansible-openafs/keytabs/afs.example.com.keytab"

principal:
  description: principal name
  type: str
  returned: success
  sample: "afs/example.com"

realm:
  description: realm name
  type: str
  return: when present in the principal parameter
  sample: EXAMPLE.COM
'''

import json                     # noqa: E402
import logging                  # noqa: E402
import logging.handlers         # noqa: E402
import os                       # noqa: E402
import pprint                   # noqa: E402
import re                       # noqa: E402

from ansible.module_utils.basic import AnsibleModule   # noqa: E402

log = logging.getLogger('openafs_principal')


def setup_logging():
    level = logging.INFO
    fmt = '%(levelname)s %(name)s %(message)s'
    address = '/dev/log'
    if not os.path.exists(address):
        address = ('localhost', 514)
    facility = logging.handlers.SysLogHandler.LOG_USER
    formatter = logging.Formatter(fmt)
    handler = logging.handlers.SysLogHandler(address, facility)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)


def load_facts():
    try:
        with open('/etc/ansible/facts.d/openafs.fact') as f:
            facts = json.load(f)
        krbserver = facts.get('krbserver', {})
    except Exception as e:
        log.warn('Unable to load krbserver facts: %s' % (str(e)))
        krbserver = {}
    log.debug('krbserver facts: %s' % (pprint.pformat(krbserver)))
    return krbserver


def main():
    setup_logging()
    results = dict(
        changed=False,
        debug=[],
    )
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(type='str',
                           choices=['present', 'absent', 'rekey'],
                           default='present'),
                principal=dict(type='str', required=True),
                password=dict(type='str', no_log=True),
                enctypes=dict(type='list',
                              aliases=['enctype', 'encryption_type',
                                       'encryption_types', 'keysalts']),
                acl=dict(type='str'),
                keytab_name=dict(type='str'),
                keytabs=dict(type='path',
                             default='/var/lib/ansible-openafs/keytabs'),
                kadmin=dict(type='path'),
            ),
            supports_check_mode=False,
    )
    log.info('Parameters: %s', pprint.pformat(module.params))
    state = module.params['state']
    principal = module.params['principal']
    password = module.params['password']
    enctypes = module.params['enctypes']
    acl = module.params['acl']
    keytab_name = module.params['keytab_name']
    keytabs = module.params['keytabs']
    kadmin = module.params['kadmin']

    if '@' in principal:
        principal, realm = principal.split('@', 1)
    else:
        realm = None

    # Convert k4 to k5 name.
    if '.' in principal and '/' not in principal:
        principal = principal.replace('.', '/')

    if not keytab_name:
        keytab_name = principal.replace('/', '.')
    if not keytab_name.endswith('.keytab'):
        keytab_name += '.keytab'
    keytab = '%s/%s' % (keytabs, keytab_name)

    if not kadmin:
        kadmin = module.get_bin_path('kadmin.local', required=True)

    facts = load_facts()  # Read our installation facts.

    results['principal'] = principal
    results['kadmin'] = kadmin
    if realm:
        results['realm'] = realm

    def die(msg):
        results['msg'] = msg
        module.fail_json(**results)

    def run(*cmd):
        query = ' '.join(cmd)
        args = [kadmin]
        if realm:
            args.extend(['-r', realm])
        args.extend(['-q', query])
        rc, out, err = module.run_command(args)
        results['debug'].append(dict(cmd=args, rc=rc, out=out, err=err))
        if rc != 0:
            die('%s failed' % cmd[0])
        return out, err

    def delete_keytab():
        if os.path.exists(keytab):
            os.remove(keytab)
            results['debug'].append(dict(cmd='rm %s' % keytab))

    def get_principal():
        metadata = None
        out, err = run('get_principal', principal)
        if 'Principal does not exist' not in err:
            metadata = out.splitlines()
        return metadata

    def add_principal():
        args = []
        if password:
            args.extend(['-pw', password])
        else:
            args.append('-randkey')
        if enctypes:
            args.extend(['-e', '"%s"' % ','.join(enctypes)])
        args.append(principal)
        run('add_principal', *args)
        results['changed'] = True

    def delete_principal():
        run('delete_principal', '-force', principal)
        results['changed'] = True

    def ktadd(rekey=False):
        if not os.path.exists(keytabs):
            os.makedirs(keytabs)
        args = ['-keytab', keytab]
        if rekey:
            if enctypes:
                args.extend(['-e', '"%s"' % ','.join(enctypes)])
        else:
            args.append('-norandkey')
        args.append(principal)
        run('ktadd', *args)
        if not os.path.exists(keytab):
            die('Failed to create keytab; file not found.')
        results['changed'] = True

    def read_acl_file():
        """
        Slurp acl file into a list of lines.
        """
        kadm5_acl = facts.get('kadm5_acl', None)
        if not kadm5_acl:
            die('Unable to read kadm5.acl; path not found in local facts.')
        log.info('Reading %s', kadm5_acl)
        with open(kadm5_acl) as fh:
            lines = fh.readlines()
        return lines

    def write_acl_file(lines):
        kadm5_acl = facts.get('kadm5_acl', None)
        if not kadm5_acl:
            die('Unable to write kadm5.acl; path not found in local facts.')
        log.info('Updating %s', kadm5_acl)
        with open(kadm5_acl, 'w') as fh:
            for line in lines:
                fh.write(line)
        results['changed'] = True

    def add_acl(principal, permissions):
        """
        Add permissions for a principal to the ACL file.
        """
        found = False
        output = []
        for line in read_acl_file():
            m = re.match(r'^\s*#', line)
            if m:
                output.append(line)
                continue
            m = re.match(r'^\s*$', line)
            if m:
                output.append(line)
                continue
            m = re.match(r'^\s*(\S+)\s+(\S+)', line)
            if m:
                # Note: To keep this simple, we don't bother with the wildcard
                #       matching.
                if m.group(1) == principal and m.group(2) == permissions:
                    # Already present.
                    log.debug("Permissions '%s' for principal '%s' already "
                              "present in acl file.", permissions, principal)
                    return
                if m.group(1) == principal:
                    # Update in place.
                    found = True
                    line = '%s %s\n' % (principal, permissions)
                    log.info("Updating line in acl file: '%s'" % (line))
                    output.append(line)
                    continue
            output.append(line)
        if not found:
            line = '%s %s\n' % (principal, permissions)
            log.info("Adding line to acl file: '%s'" % (line))
            output.append(line)
        write_acl_file(output)

    def remove_acl(principal):
        """
        Remove the permissions for a principal.
        """
        found = False
        output = []
        for line in read_acl_file():
            m = re.match(r'^\s*#', line)
            if m:
                output.append(line)
                continue
            m = re.match(r'^\s*$', line)
            if m:
                output.append(line)
                continue
            m = re.match(r'^\s*(\S+)\s+(\S+)', line)
            if m:
                if m.group(1) == principal:
                    found = True   # remove this line
                    log.info("Removing line from acl file: '%s'" % (line))
                    continue
            output.append(line)
        if found:
            write_acl_file(output)

    if state == 'present':
        metadata = get_principal()
        if not metadata:
            delete_keytab()  # Remove stale keytab, if present.
            add_principal()
            metadata = get_principal()
            if not metadata:
                die('Failed to add principal.')
        if acl:
            add_acl(principal, acl)
        if not os.path.exists(keytab):
            ktadd()
        results['metadata'] = metadata
        results['keytab'] = keytab
    elif state == 'rekey':
        if get_principal():
            ktadd(rekey=True)
        else:
            delete_keytab()  # Remove stale keytab, if present.
            add_principal()
            ktadd()
        metadata = get_principal()
        if not metadata:
            die('Failed to add principal.')
        results['metadata'] = metadata
        results['keytab'] = keytab
    elif state == 'absent':
        delete_keytab()
        if get_principal():
            delete_principal()
        if get_principal():
            die('Failed to delete principal.')
        remove_acl(principal)
    else:
        die('Internal error; invalid state: %s' % state)

    log.info('Results: %s', pprint.pformat(results))
    module.exit_json(**results)


if __name__ == '__main__':
    main()
