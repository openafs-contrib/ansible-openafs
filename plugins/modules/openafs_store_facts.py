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
import os                       # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')


def flatten(prefix, value):
    """
    Flatten the data tree in sorted order.
    """
    if isinstance(value, dict):
        for k in sorted(value.keys()):
            for element in flatten(prefix + str(k), value[k]):
                yield element
    elif isinstance(value, (list, tuple)):
        for v in sorted(value):
            for element in flatten(prefix, v):
                yield element
    else:
        yield prefix + str(value)


def signature(facts):
    text = '\n'.join(flatten('', facts))
    return text


def main():
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
    log = Logger(module_name)
    log.info('Starting %s', module_name)

    state = module.params['state']
    factsdir = module.params['factsdir']
    factsfile = os.path.join(factsdir, 'openafs.fact')

    try:
        with open(factsfile) as fp:
            facts = json.load(fp)
    except Exception:
        facts = {}
    signature_before = signature(facts)

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

    if not os.path.exists(factsdir):
        os.makedirs(factsdir)
    with open(factsfile, 'w') as fp:
        json.dump(facts, fp, indent=2)

    with open(factsfile) as fp:
        facts = json.load(fp)
    signature_after = signature(facts)
    if signature_before != signature_after:
        log.info("Facts file '%s' changed.", factsfile)
        results['changed'] = True

    # Update local facts in the current play.
    results['ansible_facts']['ansible_local']['openafs'] = facts
    log.debug('results={0}'.format(results))
    module.exit_json(**results)


if __name__ == '__main__':
    main()
