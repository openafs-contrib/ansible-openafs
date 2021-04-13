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
module: openafs_store_facts

short_description: Store OpenAFS facts in a json file

description:
  - Store facts in the json formatted c(openafs.fact) file on the remote
    host. This file is located in the c(/etc/ansible/facts.d) directory or the
    path specified by the c(factsdir) parameter. The c(openafs.fact) file is
    read by Ansible when facts are gathered on subsequent plays.

  - The c(openafs.fact) contains a dictionary of facts which can be accessed
    from c(ansible_local.openafs).

options:
  state:
    description:
      - c(update) update the facts
    choices:
      - update

  factsdir:
    description: Path to the c(openafs.fact) file
    type: path
    default: /etc/ansible/facts.d

author:
  - Michael Meffie
'''

EXAMPLES = r'''
'''

import json                     # noqa: E402
import logging                  # noqa: E402
import logging.handlers         # noqa: E402
import os                       # noqa: E402
import pprint                   # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402

log = logging.getLogger('openafs_store_facts')


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
        ansible_facts={'ansible_local': {'openafs': {}}},
    )
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(choices=['set', 'update'], default='update'),
                factsdir=dict(type='path', default='/etc/ansible/facts.d'),
                facts=dict(type='dict', default={}),
            ),
            supports_check_mode=False,
    )
    log.info('Parameters: %s', pprint.pformat(module.params))
    state = module.params['state']
    factsdir = module.params['factsdir']
    factsfile = os.path.join(factsdir, 'openafs.fact')
    tmpdir = '/tmp/ansible-openafs'
    tmpfile = os.path.join(tmpdir, 'openafs.fact')

    try:
        with open(factsfile) as fp:
            facts = json.load(fp)
    except Exception:
        facts = {}

    for key, value in module.params['facts'].items():
        if state == 'set':
            facts[key] = value
        elif state == 'update':
            if key not in facts:
                facts[key] = value
            elif isinstance(facts[key], dict) and isinstance(value, dict):
                facts[key].update(value)
            elif isinstance(facts[key], list) and isinstance(value, list):
                facts[key].append(value)
            else:
                facts[key] = value
        else:
            module.fail_json(msg='Internal error: unknown state %s' % state)

    # Write our facts to a temp file and check for changes.
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    with open(tmpfile, 'w') as fp:
        log.debug("Writing '%s'.", tmpfile)
        json.dump(facts, fp, indent=2)
    old_sha1 = module.sha1(factsfile)  # Returns None if file does not exist.
    new_sha1 = module.sha1(tmpfile)
    log.debug('old_sha1=%s, new_sha1=%s', old_sha1, new_sha1)

    if old_sha1 != new_sha1:
        if not os.path.exists(factsdir):
            os.makedirs(factsdir)
        module.preserved_copy(tmpfile, factsfile)
        log.info("Facts file '%s' changed.", factsfile)
        results['changed'] = True

    # Update local facts in the current play.
    results['ansible_facts']['ansible_local']['openafs'] = facts
    log.info('results=%s', pprint.pformat(results))
    module.exit_json(**results)


if __name__ == '__main__':
    main()
