#!/usr/bin/python
# Copyright (c) 2020, Sine Nomine Associates
# BSD 2-Clause License

ANSIBLE_METADATA = {
    'metadata_version': '1.1.',
    'status': ['preview'],
    'supported_by': 'community',
}

DOCUMENTATION = r'''
'''

EXAMPLES = r'''
'''

import json
import logging
import os
import pprint
import fnmatch
from ansible.module_utils.basic import AnsibleModule

logger = logging.getLogger(__name__)

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'error': logging.ERROR,
}

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
    pkg = module.params['pkg']
    query_packages = COMMANDS[pkg]['query_packages']
    query_files = COMMANDS[pkg]['query_files']
    packages = []
    logger.info('Running: %s', ' '.join(query_packages))
    rc, out, err = module.run_command(query_packages, check_rc=True)
    for line in out.splitlines():
        line = line.strip()
        if line.startswith('openafs'):
            packages.append(line)
    if packages:
        logger.info('Running: %s', ' '.join(query_files + packages))
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
                pkg=dict(choices=['rpm', 'deb']),
                factsdir=dict(type='path', default='/etc/ansible/facts.d'),
                logdir=dict(type='path', default='/var/tmp/ansible'),
                loglevel=dict(choices=['debug', 'info'], default='info'),
            ),
            supports_check_mode=False,
    )

    logdir = module.params['logdir']
    loglevel = module.params['loglevel']
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    logfile = os.path.join(logdir, 'openafs_gather_facts.log')
    logging.basicConfig(
        level=LEVELS[loglevel],
        filename=logfile,
        format='%(asctime)s %(levelname)s %(message)s',
    )
    results['logfile'] = logfile
    logger.info('Starting openafs_gather_facts module.')
    logger.debug('parameters: %s', pprint.pformat(module.params))

    #
    # Gather current facts.
    #
    factsdir = module.params['factsdir']
    factsfile = os.path.join(factsdir, 'openafs.fact')
    facts = None
    try:
        with open(factsfile) as fp:
            facts = json.load(fp)
            logger.debug('Read facts from %s: %s', factsfile, pprint.pformat(facts))
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
    if not 'commands' in facts:
        facts['commands'] = {}
    if not 'dirs' in facts:
        facts['dirs'] = {}
    pkg = module.params['pkg']
    name_map = NAME_MAP[pkg]
    for f in list_files(module):
        name = os.path.basename(f)
        name = name_map.get(name, name)
        logger.debug('name=%s, f=%s', name, f)
        if exclude(f):
            continue
        if os.path.isfile(f) and os.access(f, os.X_OK):
            if facts['commands'].get(name) != f:
                facts['commands'][name] = f
                changed = True

    #
    # Add package specific directory paths. Ideally we would query the
    # installed binaries for the paths, but we don't have a good way
    # to do that yet (e.g. -V option), so punt and assume the the paths
    # based on the package type.
    #
    pkg = module.params['pkg']
    for name in DIRS[pkg]:
        path = DIRS[pkg][name]
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
            logger.debug('Wrote facts to %s: %s', factsfile, pprint.pformat(facts))

    #
    # Set local facts for this play.
    #
    results['ansible_facts']['ansible_local']['openafs'] = facts
    module.exit_json(**results)

if __name__ == '__main__':
    main()