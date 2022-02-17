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
module: openafs_user

short_description: Create an OpenAFS user

description:
  - Create or remove a user.
  - Optionally create new groups and add the user to groups.
  - Localauth authentication may be used on server nodes, running as root.
  - Keytab based authentication may be used on client nodes.
    This requires a keytab for a user in the system:adminstrators
    group and a member of the UserList on all of the database servers.

options:

  state:
    description:
      - C(present) create user and groups when not present
      - C(absent) remove user when not present
    type: str
    default: present

  user:
    description: The OpenAFS username.
    type: str
    required: true

  id:
    description:
      - The OpenAFS pts id.
      - The next available id will be selected if omitted or 0.
    type: int
    required: false
    default: 0

  groups:
    description:
      - The OpenAFS group names the user is a member.
      - Non-system groups will be created.
    type: list
    required: false
    aliases:
      - group

  localauth:
    description:
      - Indicates if the C(-localauth) option is to be used for authentication.
      - This option should only be used when running on a server.
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
'''

EXAMPLES = r'''
- name: Create users
  openafs_contrib.openafs.openafs_user:
     name: "{{ item }}"
     group: tester
  with_items:
    - alice
    - bob
    - charlie
'''

RETURN = r'''
user:
  description: User information.
  type: dictionary
#  sample:
#    user:
#      id: 5
#      name: tycobb
#      creator: admin
#      owner: "system:administrators"
#      flags: S----
#      groups:
#        - "system:administrators"
#        - tester
'''

import json                     # noqa: E402
import os                       # noqa: E402
import pprint                   # noqa: E402
import re                       # noqa: E402
import time                     # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')


def main():
    results = dict(
        changed=False,
    )
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(type='str',
                           choices=['present', 'absent'],
                           default='present'),
                user=dict(type='str', aliases=['name']),
                id=dict(type='int', default=0),
                groups=dict(type='list', default=[], aliases=['group']),
                localauth=dict(type='bool', default=False),
                auth_user=dict(type='str', default='admin'),
                auth_keytab=dict(type='str', default='admin.keytab'),
            ),
            supports_check_mode=False,
    )
    log = Logger(module_name)
    log.info('Starting %s', module_name)

    state = module.params['state']
    user = module.params['user']
    userid = module.params['id']
    groups = set(module.params['groups'])
    localauth = module.params['localauth']
    auth_user = module.params['auth_user']
    auth_keytab = module.params['auth_keytab']

    # Convert k4 to k5 name.
    if '.' in auth_user and '/' not in auth_user:
        auth_user = auth_user.replace('.', '/')

    def die(msg):
        log.error(msg)
        module.fail_json(msg=msg)

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

    def run_command(args):
        """
        Run a command.
        """
        cmdline = ' '. join(args)
        log.debug('Running: %s', cmdline)
        rc, out, err = module.run_command(args)
        log.debug('Ran: %s, rc=%d, out=%s, err=%s', cmdline, rc, out, err)
        if rc != 0:
            die('Failed: %s, rc=%d, out=%s, err=%s' % (cmdline, rc, out, err))

    def login():
        """
        Get a token for authenicated access.
        """
        kinit = lookup_command('kinit')
        aklog = lookup_command('aklog')
        if not os.path.exists(auth_keytab):
            die('keytab %s not found.' % auth_keytab)
        run_command([kinit, '-k', '-t', auth_keytab, auth_user])
        run_command([aklog, '-d'])

    def run_pts(args, is_done):
        """
        Run a pts command with retries.
        """
        def should_retry(err):
            if "server or network not reponding" in err:
                return True
            if "no quorum elected" in err:
                return True
            if "invalid RPC (RX) operation" in err:
                return True  # May occur during server startup.
            if "Couldn't read/write the database" in err:
                return True  # May occur during server startup.
            if "User or group doesn't exist" in err:
                return True  # Retry not found!
            return False

        pts = lookup_command('pts')
        args.insert(0, pts)
        if localauth:
            args.append('-localauth')
        cmdline = ' '.join(args)
        retries = 120
        while True:
            log.debug('Running: %s', cmdline)
            rc, out, err = module.run_command(args)
            log.debug('Ran: %s, rc=%d, out=%s, err=%s', cmdline, rc, out, err)
            if is_done(rc, out, err):
                return out
            if retries == 0 or not should_retry(err):
                log.error("Failed: %s, rc=%d, err=%s", cmdline, rc, err)
                module.fail_json(
                    dict(msg='Command failed.', cmdline=cmdline, rc=rc,
                         out=out, err=err))
            log.warning("Failed: %s, rc=%d, err=%s; %d retr%s left.",
                        cmdline, rc, err, retries,
                        ('ies' if retries > 1 else 'y'))
            retries -= 1
            time.sleep(2)

    def pts_examine(name):
        """
        Return the entry of an existing user.
        """
        pts_fields = {
            'name': r'Name: ([^,]+),',
            'id': r'id: (\d+),',
            'owner': r'owner: ([^,]+),',
            'creator': r'creator: ([^,]+),',
            'flags': r'flags: (.....),',
            'quota': r'group quota: (\d+|unlimited)\.'
        }

        def is_done(rc, out, err):
            if rc == 0:
                return True
            if rc == 1 and "User or group doesn't exist" in err:
                log.warning("User %s not found.", name)
                return False  # Retry
            return False

        out = run_pts(['examine', '-nameorid', name], is_done)
        entry = {}
        for name, pattern in pts_fields.items():
            m = re.search(pattern, out)
            value = m.group(1) if m else None
            if name == 'id':
                value = int(value)
            elif name == 'quota':
                if value == 'unlimited':
                    continue  # no quota
                value = int(value)
            entry[name] = value
        return entry

    def pts_membership(name):
        """
        Lookup user groups.
        """
        def is_done(rc, out, err):
            return rc == 0
        out = run_pts(['membership', '-nameorid', name], is_done)
        members = set()
        for line in out.splitlines():
            m = re.search(r'^  (\S+)', line)
            if m:
                members.add(m.group(1))
        return list(members)

    def pts_createuser(name, userid):
        """
        Ensure a user exists.
        """
        def is_done(rc, out, err):
            if rc == 0:
                results['changed'] = True
                return True
            if rc == 1 and "Entry for name already exists" in err:
                return True
            if rc == 1 and "Entry for id already exists" in err:
                pattern = r'unable to create user (\S+) with id (\d+)'
                m = re.search(pattern, err)
                if m and m.group(1) == name and int(m.group(2)) == userid:
                    return True
            return False

        cmd = ['createuser', '-name', name]
        if userid:
            cmd.extend(['-id', str(userid)])
        run_pts(cmd, is_done)

    def pts_creategroup(name):
        """
        Ensure a group exists.
        """
        def is_done(rc, out, err):
            if rc == 0:
                results['changed'] = True
                return True
            if rc == 1 and "already exists" in err:
                return True
            return False
        run_pts(['creategroup', '-name', name], is_done)

    def pts_adduser(user, group):
        """
        Ensure user is member of the group.
        """
        def is_done(rc, out, err):
            if rc == 0:
                results['changed'] = True
                return True
            if rc == 1 and "already exists" in err:
                return True
            return False
        run_pts(['adduser', '-user', user, '-group', group], is_done)

    def pts_delete(name):
        """
        Ensure user is absent.
        """
        def is_done(rc, out, err):
            if rc == 0 and err == '':
                results['changed'] = True
                return True
            if rc == 0 and "User or group doesn't exist" in err:
                log.warning("User %s not found.", name)
                return True
            return False
        run_pts(['delete', '-nameorid', name], is_done)

    if not localauth:
        login()

    if state == 'present':
        pts_createuser(user, userid)
        for group in groups:
            if not group.startswith('system:'):
                pts_creategroup(group)
            pts_adduser(user, group)
        results['user'] = pts_examine(user)
        results['user']['groups'] = pts_membership(user)
    elif state == 'absent':
        pts_delete(user)
    else:
        module.fail_json(msg="Internal error: invalid state %s" % state)

    log.debug('Results: %s' % pprint.pformat(results))
    log.info('Exiting %s' % module_name)
    module.exit_json(**results)


if __name__ == '__main__':
    main()
