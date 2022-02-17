#!/usr/bin/python
# Copyright (c) 2021, Sine Nomine Associates
# BSD 2-Clause License

ANSIBLE_METADATA = {
    'metadata_version': '1.1.',
    'status': ['preview'],
    'supported_by': 'community',
}

DOCUMENTATION = r"""
---
module: openafs_selinux_module

short_description: Create and install an selinux module from input files

description: Build the selinux module from the given input files.

options:

  state:
    description: c(present) is currently the only supported state.

  name:
    description: name of the selinux module
    default: openafs

  path:
    description:
      - Path to the Type Enforcement (te) and File Context (fc) input files and
        the destination path of the output pp and mod files.
    default: /var/lib/ansible-openafs/selinux

author:
  - Michael Meffie
"""

EXAMPLES = r"""
- name: Copy the SELinux module definitions for openafs server
  become: yes
  template:
    dest: "/var/lib/ansible-openafs/selinux/{{ item }}"
    src: "{{ role_path }}/templates/{{ item }}.j2"
  with_items:
    - openafs.te
    - openafs.fc

- name: Build SELinux module for openafs server
  become: yes
  openafs_contrib.openafs.openafs_selinux_module:
    name: openafs
    path: /var/lib/ansible-openafs/selinux
"""

RETURN = r"""
module:
  description: Path to the module
  returned: success
  type: str
#  sample: "/var/lib/ansible-openafs/selinux/openafs.mod"

version:
  description: Module version
  returned: success
  type: str
"""

import os                       # noqa: E402
import pprint                   # noqa: E402
import re                       # noqa: E402

from ansible.module_utils.basic import AnsibleModule   # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')


def main():
    results = dict(
        changed=False,
    )
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(type='str', choices=['present'], default='present'),
                name=dict(type='str', default='openafs'),
                path=dict(type='path', default='/var/lib/ansible-openafs'),
            ),
            supports_check_mode=False,
    )
    log = Logger(module_name)
    log.info('Starting %s', module_name)

    name = module.params['name']
    path = module.params['path']

    def die(msg):
        log.error(msg)
        module.fail_json(msg=msg)

    def run_command(cmd, *args):
        cmdargs = [module.get_bin_path(cmd, required=True)] + list(args)
        cmdline = ' '.join(cmdargs)
        log.info("Running: %s", cmdline)
        rc, out, err = module.run_command(cmdargs)
        if rc != 0:
            die("Command failed: %s, rc=%d, err=%s" % (cmdline, rc, err))
        return out

    def checkmodule(*args):
        return run_command('checkmodule', *args)

    def semodule_package(*args):
        return run_command('semodule_package', *args)

    def semodule(*args):
        return run_command('semodule', *args)

    if not name:
        die("Module name is required.")

    te = os.path.join(path, '%s.te' % name)
    fc = os.path.join(path, '%s.fc' % name)
    for f in (te, fc):
        if not os.path.exists(f):
            die("Input file '%s' not found." % f)

    current_version = None
    target_version = None

    out = semodule('-lstandard')
    for line in out.splitlines():
        m = re.match(r'\s*(\S+)\s+(\S+)\s*', line)
        if m and m.group(1) == name:
            current_version = m.group(2)
            break

    if not current_version:
        log.info("%s module is not installed.", name)
    else:
        log.info("%s module version is '%s'.", name, current_version)
        try:
            with open(te) as f:
                for line in f.readlines():
                    m = re.match(r'\s*module\s+(\S+)\s+(\S+)\s*;', line)
                    if m and m.group(1) == name:
                        target_version = m.group(2)
                        break
        except Exception as e:
            die("Failed to read te file: %s" % str(e))
        if not target_version:
            die("SELinux module version number not found in file '%s'." % te)
        log.info("%s module target version is '%s'.", name, target_version)

    if not current_version or (current_version != target_version):
        mod = os.path.join(path, '%s.mod' % name)
        pp = os.path.join(path, '%s.pp' % name)
        checkmodule('-M', '-m', '-o', mod, te)
        semodule_package('-o', pp, '-m', mod, '-f', fc)
        semodule('-i', pp)
        results['changed'] = True

    log.info('Results: %s', pprint.pformat(results))
    module.exit_json(**results)


if __name__ == '__main__':
    main()
