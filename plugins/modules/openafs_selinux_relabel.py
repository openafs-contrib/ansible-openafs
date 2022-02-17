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
module: openafs_selinux_relabel

short_description: Relabel selinux context for server files

description:
  - Relabel the server directories after the files have been installed
    and the configuration files updated.
  - Relabel the partition directories and the AlwaysAttach file, when present.
  - Safe the list of directories relabelled in the openafs local facts file
    to avoid running restorecon on subsequent plays.

options: {}

author:
  - Michael Meffie
"""

EXAMPLES = r"""
- name: Relabel
  become: yes
  openafs_contrib.openafs.openafs_selinux_relabel:
"""

RETURN = r"""
"""

import glob                     # noqa: E402
import json                     # noqa: E402
import os                       # noqa: E402
import pprint                   # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')


# Note: The bosserver creates the /usr/vice/etc directory if it does not
# exist in order to create a symlink to the server configuration. Be sure
# to set the selinux context on /usr/vice before the bosserver starts.
top_dirs = ['/usr/afs', '/usr/vice']


def main():
    results = dict(
        changed=False,
    )
    module = AnsibleModule(
            argument_spec=dict(
            ),
            supports_check_mode=False,
    )
    log = Logger(module_name)
    log.info('Starting %s', module_name)

    def restorecon(*args):
        restorecon = module.get_bin_path('restorecon', required=True)
        cmdargs = [restorecon] + list(args)
        cmdline = ' '.join(cmdargs)
        log.info("Running: %s", cmdline)
        rc, out, err = module.run_command(cmdargs)
        if rc != 0:
            log.error("Command failed: %s, rc=%d, err=%s", cmdline, rc, err)
            module.fail_json(msg="Command failed", cmd=cmdline,
                             out=out, err=err)

    factsfile = '/etc/ansible/facts.d/openafs.fact'
    try:
        with open(factsfile) as fp:
            facts = json.load(fp)
    except Exception:
        facts = {}

    changed = []
    relabelled = facts.get('relabelled', [])

    for path in top_dirs:
        if not os.path.exists(path):
            os.makedirs(path)
        if path not in relabelled:
            restorecon('-i', '-r', path)
            changed.append(path)

    for path in glob.glob('/vicep*'):
        if path not in relabelled:
            restorecon('-i', path)
            changed.append(path)

    for path in glob.glob('/vicep*/AlwaysAttach'):
        if path not in relabelled:
            restorecon(path)
            changed.append(path)

    if changed:
        facts['relabelled'] = sorted(set(relabelled) | set(changed))
        if not os.path.exists(os.path.dirname(factsfile)):
            os.makedirs(os.path.dirname(factsfile))
        with open(factsfile, 'w') as fp:
            json.dump(facts, fp, indent=2)
        results['changed'] = True

    log.info('Results: %s', pprint.pformat(results))
    module.exit_json(**results)


if __name__ == '__main__':
    main()
