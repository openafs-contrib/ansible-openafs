#!/usr/bin/python
# Copyright (c) 2020-2022, Sine Nomine Associates
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
    to remote nodes with C(synchronize) or encrypted with C(ansible-vault) then
    downloaded to the controller for distribution in subsequent plays. This

  - If the state is C(present), then a principal is added if it is not
    already present and a keyfile is created. The initial password may
    be specified with the C(password) parameter, otherwise a random key
    is generated and a keytab file will be created.

  - If the state is C(absent), then the principal and keytab files are
    removed if present.

  - Keytabs for the principals created by the module are stored in the
    C(keytabs) directory on the KDC, readable by root. The default path is
    C(/var/lib/ansible-openafs/keytabs).

requirements:
  - The Kerberos realm has been created.
  - C(kadmin.local) is installed and in the PATH.

options:
  state:
    description:
      - C(present) ensure the principal and keytab file exist.
      - C(absent) ensure the principal and keytab file are removed.
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
    default: C(/var/lib/ansible-openafs/keytabs)

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
    password: "{{ initial_password }}"
  with_items:
    - alice
    - bob
    - charlie
'''

RETURN = r'''
attributes:
  description: Principal attributes from C(get_principal)
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
#  sample: "/sbin/kadmin.local"

keytab:
  description: Path of the generated keytab on the remote node.
  type: path
  returned: success
#  sample: "/var/lib/ansible-openafs/keytabs/afs.example.com.keytab"

principal:
  description: principal name
  type: str
  returned: success
#  sample: "afs/example.com"

realm:
  description: realm name
  type: str
  return: when present in the principal parameter
#  sample: EXAMPLE.COM
'''

import os        # noqa: E402
import re        # noqa: E402
import platform  # noqa: E402

from ansible.module_utils.basic import AnsibleModule   # noqa: E402
from ansible.module_utils.common.sys_info import (     # noqa: E402
    get_distribution,
    get_platform_subclass,
)
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.kerberos import Keytab  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')
log = Logger(module_name)


class KerberosAdmin(object):
    extra_path = None

    def __new__(cls, *args, **kwargs):
        new_cls = get_platform_subclass(KerberosAdmin)
        return super(cls, new_cls).__new__(new_cls)

    def __init__(self, module):
        self.module = module
        self.kadmin = module.params['kadmin']
        self.realm = module.params['realm']
        self.keytabs = module.params['keytabs']
        self.changed = False
        self.debug = []

    def _not_implemented(self):
        myname = self.__class__.__name__
        if myname != 'KerberosAdmin':
            raise NotImplementedError('class %s' % myname)
        else:
            self.module.fail_json(msg='Unknown platform.',
                                  module=module_name,
                                  platform=platform.system(),
                                  distribution=get_distribution())

    # -------------------------------------------------------------------------
    # Abstract methods: Must be implemented by subclasses.
    #
    def kadmin_args(self, command):
        self._not_implemented()

    def get_principal(self, principal):
        self._not_implemented()

    def add_principal(self, principal, password=None):
        self._not_implemented()

    def delete_principal(self, principal):
        self._not_implemented()

    def write_keytab(self, keytab, principal):
        self._not_implemented()

    def update_acl(self, principal, acl):
        self._not_implemented()

    def clear_acl(self, principal):
        self._not_implemented()

    # -------------------------------------------------------------------------
    # Main methods
    #
    def ensure_present(self):
        """
        Ensure the principal exists and return the attributes.
        Create a keytab if a password was not specfied.
        """
        principal = self.normalize(self.module.params['principal'])
        password = self.module.params['password']
        acl = self.module.params['acl']
        keytab = None

        attributes = self.get_principal(principal)
        if not attributes:
            self.add_principal(principal, password)
            attributes = self.get_principal(principal)
            if not attributes:
                self.fail('Failed to add principal "%s".' % principal)

        principal = attributes['principal']  # fully qualified
        kvno = attributes['kvno']

        if not password:
            keytab = self.ensure_present_keytab(principal, kvno)

        if acl:
            self.update_acl(principal, acl)

        results = {
            'changed': self.changed,
            'attributes': attributes,
            'kvno': kvno,
            'debug': self.debug,
        }
        if keytab:
            results['keytab'] = keytab
        return results

    def ensure_present_keytab(self, principal, kvno):
        """
        Ensure a current keytab exists for the given principal.
        """
        keytab = self.get_keytab_filename(principal)
        if os.path.exists(keytab):
            if self.is_keytab_current(keytab, principal, kvno):
                self.debug.append(
                    dict(msg='Existing keytab is current.',
                         keytab=keytab, kvno=kvno, principal=principal))
                return keytab
            # Remove old version.
            self.debug.append(dict(cmd='rm %s' % keytab))
            os.remove(keytab)
            self.changed = True

        keytab_dir = os.path.dirname(keytab)
        if not os.path.exists(keytab_dir):
            self.debug.append(dict(cmd='mkdir -p %s' % keytab_dir))
            os.makedirs(keytab_dir)
            self.changed = True

        self.write_keytab(keytab, principal)
        return keytab

    def ensure_absent(self):
        """
        Ensure the principal and keytab does not exist.
        """
        principal = self.normalize(self.module.params['principal'])

        if self.get_principal(principal):
            self.delete_principal(principal)
        if self.get_principal(principal):
            self.fail('Failed to delete principal "%s".' % principal)

        self.clear_acl(principal)

        keytab = self.get_keytab_filename(principal)
        if os.path.exists(keytab):
            os.remove(keytab)
            self.changed = True
            self.debug.append(dict(cmd='rm %s' % keytab))

        results = {
            'changed': self.changed,
            'debug': self.debug,
        }
        return results

    def run(self, command, check_rc=True):
        args = self.kadmin_args(command)
        rc, out, err = self.module.run_command(args, check_rc)
        self.debug.append(dict(cmd=' '.join(args), rc=rc,
                          out=out.splitlines(), err=err.splitlines()))
        return out, err

    def fail(self, msg):
        """
        Log and error and abort.
        """
        log.error(msg)
        self.module.fail_json(msg=msg, debug=self.debug)

    def normalize(self, principal):
        """
        Convert k4 formatted principals to k5 format.
        k4 format is still used for AFS identities.
        """
        if re.search(r'[^a-zA-Z0-9_\-\./@]', principal):
            self.fail('Illegal character found in principal "%s".' % principal)
        primary, instance, realm = self.get_principal_components(principal)
        tokens = [primary]
        if instance:
            tokens.append('/')
            tokens.append(instance)
        if realm:
            tokens.append('@')
            tokens.append(realm)
        return ''.join(tokens)

    def get_principal_components(self, principal):
        """
        Split the principal names into components.
        """
        if '@' in principal:
            name, realm = principal.split('@', 1)
        else:
            name = principal
            realm = None

        if '/' not in name and '.' in name:  # k4 style separator
            primary, instance = name.split('.', 1)
        elif '/' in name:  # k5 style separator
            primary, instance = name.split('/', 1)
        else:
            primary = name
            instance = None
        return primary, instance, realm

    def get_keytab_filename(self, principal):
        """
        Determine the keytab file name from the principal name.
        """
        keytab_name = self.module.params['keytab_name']
        if not keytab_name:
            # Format a file name in the form "<primary>[.<instance>].keytab".
            # The realm name is not included to retain compatibility with older
            # versions of this module.
            primary, instance, realm = self.get_principal_components(principal)
            tokens = [primary]
            if instance:
                tokens.append('.')
                tokens.append(instance)
            tokens.append('.keytab')
            keytab_name = ''.join(tokens)
        return os.path.join(self.keytabs, keytab_name)

    def is_keytab_current(self, keytab, principal, kvno):
        """
        Check the kvno of this keytab to see if it already matches the one in
        use by the principal.
        """
        kt = Keytab(keytab)
        kt_kvno = kt.get_kvno(principal)
        self.debug.append(dict(msg='checking keytab', principal=principal,
                          keytab=keytab, kvno=kvno, kt_kvno=kt_kvno))
        if kt_kvno is None:
            log.error('Unable to get keytab %s kvno.' % keytab)
        elif kvno is None:
            log.error('Unable to get principal %s kvno.' % principal)
        elif kt_kvno == kvno:
            return True   # Valid
        return False


class MITKerberosAdmin(KerberosAdmin):
    platform = None
    distribution = None

    def __init__(self, module):
        super(MITKerberosAdmin, self).__init__(module)
        self.enctypes = module.params['enctypes']
        if not self.kadmin:
            self.kadmin = module.get_bin_path('kadmin.local', required=True,
                                              opt_dirs=self.extra_path)
        if not self.keytabs:
            self.keytabs = '/var/lib/ansible-openafs/keytabs'  # use kdb dir?

    def kadmin_args(self, command):
        """
        Assemble kadmin command arguments.
        """
        args = [self.kadmin]
        if self.realm:
            args.extend(['-r', self.realm])
        query = ' '.join(command)
        args.extend(['-q', query])
        return args

    def get_principal(self, principal):
        """
        Lookup a principal in the kerberos database and return the attributes
        as a dict.
        """
        out, err = self.run(['get_principal', principal])
        if 'Principal does not exist' in err:
            return None
        attributes = {}
        keys = []
        kvnos = set()
        for line in out.splitlines():
            if ':' not in line:
                continue   # Skip info lines
            name, value = line.split(':', 1)
            name = name.strip().replace(' ', '_').lower()
            value = value.strip()
            if value in ('[never]', '[none]'):
                value = None
            if name == 'key':
                keys.append(value)
                m = re.search(r'vno (\d+)', value)
                if m:
                    kvnos.add(int(m.group(1)))
            else:
                attributes[name] = value
        attributes['keys'] = keys
        attributes['kvno'] = max(kvnos)
        return attributes

    def add_principal(self, principal, password=None):
        """
        Add a principal to the kerberos database.
        """
        command = ['add_principal']
        if password:
            command.extend(['-pw', password])
        else:
            command.append('-randkey')
        if self.enctypes:
            command.extend(['-e', '"%s"' % ','.join(self.enctypes)])
        command.append(principal)
        self.run(command)
        self.changed = True

    def delete_principal(self, principal):
        """
        Delete a principal in the kerberos database.
        """
        self.run(['delete_principal', '-force', principal])
        self.changed = True

    def write_keytab(self, keytab, principal):
        """
        Write the principal's keys to a keytab file.
        """
        command = ['ktadd', '-keytab', keytab]
        if self.enctypes:
            command.extend(['-e', '"%s"' % ','.join(self.enctypes)])
        command.append(principal)
        self.run(command)
        if not os.path.exists(keytab):
            self.fail('Failed to create keytab; file not found.')
        self.changed = True

    def update_acl(self, principal, acl):
        """
        Update an entry in the ACL file.
        """
        found = False
        output = []
        for line in self.read_acl_file():
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
                # Wildcard matching is not supported to keep this simple.
                if m.group(1) == principal and m.group(2) == acl:
                    log.debug("Permissions '%s' for principal '%s' already "
                              "present in acl file.", acl, principal)
                    return
                if m.group(1) == principal:
                    # Update in place.
                    found = True
                    line = '%s %s\n' % (principal, acl)
                    log.info("Updating line in acl file: '%s'" % (line))
                    output.append(line)
                    continue
            output.append(line)
        if not found:
            line = '%s %s\n' % (principal, acl)
            log.info("Adding line to acl file: '%s'" % (line))
            output.append(line)
        self.write_acl_file(output)

    def clear_acl(self, principal):
        """
        Remove the acl entry for the given principal.
        """
        found = False
        output = []
        for line in self.read_acl_file():
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
            self.write_acl_file(output)

    def read_acl_file(self):
        """
        Slurp acl file into a list of lines.
        """
        log.info('Reading %s', self.kadm5_acl)
        with open(self.kadm5_acl) as fh:
            lines = fh.readlines()
        return lines

    def write_acl_file(self, lines):
        log.info('Updating %s', self.kadm5_acl)
        with open(self.kadm5_acl, 'w') as fh:
            for line in lines:
                fh.write(line)
                self.changed = True


class HeimdalKerberosAdmin(KerberosAdmin):
    platform = None
    distribution = None

    def __init__(self, module):
        super(HeimdalKerberosAdmin, self).__init__(module)
        self.enctypes = module.params['enctypes']
        if not self.kadmin:
            self.kadmin = module.get_bin_path('kadmin', required=True,
                                              opt_dirs=self.extra_path)
        if not self.keytabs:
            self.keytabs = '/var/lib/ansible-openafs/keytabs'  # use kdb dir?

    def kadmin_args(self, command):
        """
        Assemble kadmin command arguments.
        """
        args = [self.kadmin, '--local']
        if self.realm:
            args.extend(['-r', self.realm])
        args.extend(command)
        return args

    def get_principal(self, principal):
        """
        Lookup a principal in the kerberos database and return the attributes
        as a dict.
        """
        out, err = self.run(['get_entry', principal], check_rc=False)
        if 'Principal does not exist' in err:
            return None
        attributes = {}
        for line in out.splitlines():
            if ':' not in line:
                continue   # Skip info lines
            name, value = line.split(':', 1)
            name = name.strip().replace(' ', '_').lower()
            value = value.strip()
            if value in ('[never]', '[none]'):
                value = None
            if name == 'kvno':
                value = int(value)
            attributes[name] = value
        return attributes

    def add_principal(self, principal, password=None):
        """
        Add a principal to the kerberos database.
        """
        command = ['add']
        if password:
            command.extend(['-p', password])
        else:
            command.append('--random-password')
        command.append('--use-default')
        command.append(principal)
        self.run(command)
        self.changed = True

    def delete_principal(self, principal):
        self.run(['delete', principal])
        self.changed = True

    def write_keytab(self, keytab, principal):
        """
        Write the principal's keys to a keytab file.
        """
        self.run(['ext_keytab', '-k', keytab, principal])
        if not os.path.exists(keytab):
            self.fail('Failed to create keytab; file not found.')
        self.changed = True
        return keytab

    def update_acl(self, principal, acl):
        pass  # Not implemented

    def clear_acl(self, principal):
        pass  # Not implemented


class RedHatMITKerberosAdmin(MITKerberosAdmin):
    platform = 'Linux'
    distribution = 'Redhat'
    kadm5_acl = '/var/kerberos/krb5kdc/kadm5.acl'


class CentOSMITKerberosAdmin(MITKerberosAdmin):
    platform = 'Linux'
    distribution = 'Centos'
    kadm5_acl = '/var/kerberos/krb5kdc/kadm5.acl'


class FedoraMITKerberosAdmin(MITKerberosAdmin):
    platform = 'Linux'
    distribution = 'Fedora'
    kadm5_acl = '/var/kerberos/krb5kdc/kadm5.acl'


class AlmaMITKerberosAdmin(MITKerberosAdmin):
    platform = 'Linux'
    distribution = 'Almalinux'
    kadm5_acl = '/var/kerberos/krb5kdc/kadm5.acl'


class RockyMITKerberosAdmin(MITKerberosAdmin):
    platform = 'Linux'
    distribution = 'Rocky'
    kadm5_acl = '/var/kerberos/krb5kdc/kadm5.acl'


class OracleMITKerberosAdmin(MITKerberosAdmin):
    platform = 'Linux'
    distribution = 'Oracle'
    kadm5_acl = '/var/kerberos/krb5kdc/kadm5.acl'


class OpensuseMITKerberosAdmin(MITKerberosAdmin):
    platform = 'Linux'
    distribution = 'Opensuse'
    kadm5_acl = '/var/lib/kerberos/krb5kdc/kadm5.acl'
    extra_path = ['/usr/lib/mit/sbin']


class OpensuseLeapMITKerberosAdmin(MITKerberosAdmin):
    platform = 'Linux'
    distribution = 'Opensuse-leap'
    kadm5_acl = '/var/lib/kerberos/krb5kdc/kadm5.acl'
    extra_path = ['/usr/lib/mit/sbin']


class DebianMITKerberosAdmin(MITKerberosAdmin):
    platform = 'Linux'
    distribution = 'Debian'
    kadm5_acl = '/etc/krb5kdc/kadm5.acl'


class UbuntuMITKerberosAdmin(MITKerberosAdmin):
    platform = 'Linux'
    distribution = 'Ubuntu'
    kadm5_acl = '/etc/krb5kdc/kadm5.acl'


class SolarisMITKerberosAdmin(MITKerberosAdmin):
    platform = 'SunOS'
    kadm5_acl = '/etc/krb5/kadm5.acl'


class FreeBSDHeimdalKerberosAdmin(HeimdalKerberosAdmin):
    platform = 'FreeBSD'
    distribution = 'Freebsd'


def main():
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(type='str',
                           choices=['present', 'absent'],
                           default='present'),
                principal=dict(type='str', required=True),
                realm=dict(type='str'),
                password=dict(type='str', no_log=True),
                enctypes=dict(type='list',
                              aliases=['enctype', 'encryption_type',
                                       'encryption_types', 'keysalts']),
                acl=dict(type='str'),
                keytab_name=dict(type='str'),
                keytabs=dict(type='path'),
                kadmin=dict(type='path'),
            ),
            supports_check_mode=False,
    )
    log.info('Starting %s', module_name)

    kadmin = KerberosAdmin(module)
    state = module.params['state']
    if state == 'present':
        results = kadmin.ensure_present()
    elif state == 'absent':
        results = kadmin.ensure_absent()
    else:
        raise ValueError('Invalid state %s ' % state)
    module.exit_json(**results)


if __name__ == '__main__':
    main()
