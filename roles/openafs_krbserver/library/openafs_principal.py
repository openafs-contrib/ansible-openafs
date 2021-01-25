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

short_description: Create principals and keytab files.

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
'''

EXAMPLES = r'''
- name: Create an AFS service key
  become: yes
  openafs_principal:
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
  openafs_principal:
    state: rekey
    principal: afs/example.com

# Requires an old version of Kerberos.
- name: Obsolete DES key for testing
  become: yes
  openafs_principal:
    state: present
    service: afs
    principal: afs/broken.com
    enctype: des-cbc-crc:afs3

- name: Create some user principals
  become: yes
  openafs_principal:
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

import logging
import logging.handlers
import os
import pprint

from ansible.module_utils.basic import AnsibleModule

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

def main():
    setup_logging()
    results = dict(
        changed=False,
        debug=[],
    )
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(type='str', choices=['present', 'absent', 'rekey'], default='present'),
                principal=dict(type='str', required=True),
                password=dict(type='str'),
                enctypes=dict(type='list', aliases=['enctype','encryption_type', 'encryption_types', 'keysalts']),
                keytabs=dict(type='path', default='/var/lib/ansible-openafs/keytabs'),
                kadmin=dict(type='path'),
            ),
            supports_check_mode=False,
    )
    log.info('Parameters: %s', pprint.pformat(module.params))
    state = module.params['state']
    principal = module.params['principal']
    password = module.params['password']
    enctypes = module.params['enctypes']
    keytabs = module.params['keytabs']
    kadmin = module.params['kadmin']

    if '@' in principal:
        principal, realm = principal.split('@', 1)
    else:
        realm = None

    keytab = '%s/%s.keytab' % (keytabs, principal.replace('/', '.'))

    if not kadmin:
        kadmin = module.get_bin_path('kadmin.local', required=True)

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
        if not 'Principal does not exist' in err:
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

    if state == 'present':
        metadata = get_principal()
        if not metadata:
            delete_keytab() # Remove stale keytab, if present.
            add_principal()
            metadata = get_principal()
            if not metadata:
                die('Failed to add principal.')
        if not os.path.exists(keytab):
            ktadd()
        results['metadata'] = metadata
        results['keytab'] = keytab
    elif state == 'rekey':
        if get_principal():
            ktadd(rekey=True)
        else:
            delete_keytab() # Remove stale keytab, if present.
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
    else:
        die('Internal error; invalid state: %s' % state)

    log.info('Results: %s', pprint.pformat(results))
    module.exit_json(**results)

if __name__ == '__main__':
    main()
