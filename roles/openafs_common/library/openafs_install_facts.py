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
module: openafs_install_facts

short_description: Gather and save installation paths as local facts.

description:
  - Gather the paths to installed OpenAFS programs from the
    installed packages and save the installed paths as Ansible
    local facts.

  - Facts are saved in the c(/etc/ansible/facts.d/openafs.fact)
    file on the remote host, which will be read during subsequent
    plays when facts are gathered.

  - The c(openafs.fact) contains a dictionary of installation
    paths called c(paths) and a dictionary of installation
    and configuration directories called c(dirs).

options:
  state:
    description:
      - c(update) Gather information and update the c(openafs.fact) file.
    choices:
      - update

  package_type:
    description: Package manager type
    choices:
      - rpm
      - deb

  factsdir:
    description: Path to the c(openafs.fact) file
    type: path
    default: /etc/ansible/facts.d
'''

EXAMPLES = r'''
'''

import json
import os
import fnmatch
from ansible.module_utils.basic import AnsibleModule

COMMANDS = {
    'rpm': {
        'query_packages': ['/usr/bin/rpm', '--query', '--all'],
        'query_files': ['/usr/bin/rpm', '--query', '--list'],
    },
    'deb': {
        'query_packages': ['/usr/bin/dpkg-query', '--show', '--showformat', '${Package}\\n'],
        'query_files': ['/usr/bin/dpkg-query', '--listfiles'],
    },
}

DIRS = {
    'rpm': {
        'afsbosconfigdir': '/usr/afs/local',
        'afsconfdir': '/usr/afs/etc',
        'afsdbdir': '/usr/afs/db',
        'afslocaldir': '/usr/afs/local',
        'afslogdir': '/usr/afs/logs',
        'afssrvdir': '/usr/afs/bin',
        'viceetcdir': '/usr/vice/etc',
    },
    'deb': {
        'afsbosconfigdir': '/etc/openafs',
        'afsconfdir': '/etc/openafs/server',
        'afsdbdir': '/var/lib/openafs/db',
        'afslocaldir': '/var/lib/openafs/local',
        'afslogdir': '/var/log/openafs',
        'afssrvdir': '/usr/lib/openafs',
        'viceetcdir': '/etc/openafs',
    }
}

NAME_MAP = {
    'rpm': {
    },
    'deb': {
        'pagsh.openafs': 'pagsh',
    }
}

def list_files(module):
    """
    List installed files.
    """
    pkg = module.params['package_type']
    commands = COMMANDS[pkg]
    query_packages = commands['query_packages']
    query_files = commands['query_files']
    packages = []
    rc, out, err = module.run_command(query_packages, check_rc=True)
    for line in out.splitlines():
        line = line.strip()
        if line.startswith('openafs'):
            packages.append(line)
    if packages:
        rc, out, err = module.run_command(query_files + packages, check_rc=True)
        for line in out.splitlines():
            line = line.strip()
            if line and os.path.exists(line):
                yield line

def main():
    results = dict(
        changed=False,
        ansible_facts={'ansible_local':{'openafs':{}}},
    )
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(choices=['gather', 'update'], default='gather'),
                package_type=dict(choices=['rpm', 'deb'], default='rpm'),
                factsdir=dict(type='path', default='/etc/ansible/facts.d'),
            ),
            supports_check_mode=False,
    )

    #
    # Gather current facts.
    #
    factsdir = module.params['factsdir']
    factsfile = os.path.join(factsdir, 'openafs.fact')
    facts = None
    try:
        with open(factsfile) as fp:
            facts = json.load(fp)
    except:
        pass

    #
    # Gather installed commands.
    #
    def exclude(f):
        # Exclude libraries and build artifacts.
        for pattern in ('/*/lib*.so*', '/usr/src/*'):
            if fnmatch.fnmatch(f, pattern):
                return True
        return False

    changed = False
    if not facts:
        facts = {}
    if not 'paths' in facts:
        facts['paths'] = {}
    if not 'dirs' in facts:
        facts['dirs'] = {}
    pkg = module.params['package_type']
    name_map = NAME_MAP[pkg]
    for f in list_files(module):
        name = os.path.basename(f)
        name = name_map.get(name, name)
        if exclude(f):
            continue
        if os.path.isfile(f) and os.access(f, os.X_OK):
            if facts['paths'].get(name) != f:
                facts['paths'][name] = f
                changed = True

    #
    # Add package specific directory paths. Ideally we would query the
    # installed binaries for the paths, but we don't have a good way
    # to do that yet (e.g. -V option), so punt and assume the the paths
    # based on the package type.
    #
    pkg = module.params['package_type']
    dirs = DIRS[pkg]
    for name in dirs:
        path = dirs[name]
        if facts['dirs'].get(name) != path:
            facts['dirs'][name] = path
            changed = True

    #
    # Save facts for the next play.
    #
    state = module.params['state']
    if changed and state == 'update':
        if not os.path.exists(factsdir):
            os.makedirs(factsdir)
            results['changed'] = True
        with open(factsfile, 'w') as fp:
            json.dump(facts, fp, indent=2)
            results['changed'] = True

    #
    # Set local facts for this play.
    #
    results['ansible_facts']['ansible_local']['openafs'] = facts
    module.exit_json(**results)

if __name__ == '__main__':
    main()
