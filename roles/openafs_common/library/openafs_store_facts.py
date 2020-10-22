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

short_description: Store OpenAFS facts in a json file.

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
'''

EXAMPLES = r'''
'''

import json
import os

from ansible.module_utils.basic import AnsibleModule

def main():
    results = dict(
        changed=False,
        ansible_facts={'ansible_local':{'openafs':{}}},
    )
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(choices=['set', 'update'], default='update'),
                factsdir=dict(type='path', default='/etc/ansible/facts.d'),
                facts=dict(type='dict', default={}),
            ),
            supports_check_mode=False,
    )

    state = module.params['state']
    factsdir = module.params['factsdir']
    factsfile = os.path.join(factsdir, 'openafs.fact')

    try:
        with open(factsfile) as fp:
            facts = json.load(fp)
    except:
        facts = {}

    # If a existing fact dictionary with the new keys, if a dictionary
    # was given. Otherwise just set the new fact with the given value.
    for key, value in module.params['facts'].items():
        if state == 'set':
            facts[key] = value
        else:
            if not key in facts:
               facts[key] = value
            elif isinstance(facts[key], dict) and isinstance(value, dict):
                facts[key].update(value)
            elif isinstance(facts[key], list) and isinstance(value, list):
                facts[key].append(value)
            else:
                facts[key] = value

    if not os.path.exists(factsdir):
        os.makedirs(factsdir)
    with open(factsfile, 'w') as fp:
        json.dump(facts, fp, indent=2)
    results['changed'] = True

    # Update current facts.
    results['ansible_facts']['ansible_local']['openafs'] = facts
    module.exit_json(**results)

if __name__ == '__main__':
    main()
