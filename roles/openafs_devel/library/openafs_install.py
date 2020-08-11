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
module: openafs_install

short_description: Install OpenAFS binaries built from source

description: >
  Install OpenAFS binaries built from source. This module usually needs to be
  run as root.  The paths to installed commands are saved as facts in
  ansible_facts['ansible_local']['openafs']['commands'].  These facts are
  written to the file '/etc/ansible/facts.d/openafs.fact' on the remote machine
  and will be loaded by the setup module on subsequent plays.

options:
  destdir:
    description: >
      Absolute path to the installation file tree to be installed.
      The file tree is usually created by the openafs_build module, and if
      so, the openafs_build results may provide the destdir value.
    type: path
    required: true

  exclude:
    description: >
      List of file patterns to be excluded.
    type: list

  logdir:
    description: >
      Absolute path to the installation logs for troubleshooting.
      If not given, no log files are written.
    type: path

  ldconfig:
    description: >
      ldconfig command to be run to reload ld cache on Linux.
    default: "/sbin/ldconfig"

  depmod:
    description: >
      depmod command to be run to update kernel module dependencies
      on Linux.
    default: "/sbin/modprobe -a"

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: Build OpenAFS from source
  openafs_build:
    projectdir: ~/src/openafs
    target: install
    destdir: /tmp/openafs/dest

- name: Install OpenAFS binaries as root
  become: yes
  openafs_install:
    destdir: /tmp/openafs/dest
    exclude: /usr/vice/etc/*
    logdir: /tmp/openafs/logs
'''

RETURN = r'''
msg:
  description: Informational message.
  returned: always
  type: string
  sample: Install completed

files:
  description: Files installed
  returned: success
  type: list
  sample:
    - /usr/bin/pts
    - /usr/sbin/vos

excluded:
  description: Files excluded from the installation
  returned: success
  type: list
  sample:
    - /usr/vice/etc/afs.conf

logfiles:
  description: Log files written for troubleshooting
  returned: always
  type: list
  sample:
    - /tmp/logs/install.log
'''

import filecmp
import fnmatch
import json
import logging
import os
import platform
import pprint
import shlex
import shutil
from ansible.module_utils.basic import AnsibleModule

logger = logging.getLogger(__name__)

class FileError(Exception):
    pass

def copy_tree(src, dst, exclude=None):
    """Copy an entire directory tree.

    Creates destination if needed. Clobbers any existing files/symlinks.

    :arg src: directory to copy from. must already exist
    :arg dst: directory to copy to. created if not already present
    :arg exclude: list of patterns (glob notation) to exclude
    :returns: a list of tuples of the files/symlinks copied and skipped
    """
    files = [] # list of (<path>, <changed>, <executable>) tuples
    if exclude is None:
        exclude = []

    def is_exclusion(dst):
        for pattern in exclude:
            if fnmatch.fnmatch(dst, pattern):
                return True
        return False

    def is_same(src, dst):
        if os.path.exists(src) and os.path.exists(dst):
            return filecmp.cmp(src, dst, shallow=True)
        return False

    def is_executable(src):
        return os.path.exists(src) and os.path.isfile(src) and os.access(src, os.X_OK)

    if not os.path.isdir(src):
        raise FileError("Cannot copy tree '%s': not a directory." % src)
    try:
        names = os.listdir(src)
    except os.error:
        raise FileError("Error listing files in '%s'." % src)
    if not os.path.isdir(dst):
        os.makedirs(dst)
    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)
        if is_exclusion(dst_name):
            logger.info("Excluding '%s'.", dst_name)
        elif os.path.isdir(src_name):
            files.extend(copy_tree(src_name, dst_name, exclude))
        elif is_same(src_name, dst_name):
            logger.info("Skipping '%s'; unchanged.", dst_name)
            files.append((dst_name, False, is_executable(src_name)))
        elif os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if os.path.exists(dst_name):
                os.remove(dst_name)
            logger.debug("Creating symlink '%s'.", dst_name)
            os.symlink(link_dest, dst_name)
            files.append((dst_name, True, False))
        else:
            logger.debug("Copying '%s' to '%s'.", src_name, dst_name)
            shutil.copy2(src_name, dst_name)
            files.append((dst_name, True, is_executable(src_name)))
    return files

def main():
    results = dict(
        changed=False,
        msg='',
        files=[],
        kmods=[],
        logfiles=[],
        ansible_facts={'ansible_local':{'openafs':{'commands':{}, 'dirs':{}}}},
    )
    module = AnsibleModule(
        argument_spec=dict(
            destdir=dict(type='path', required=True),
            dirs=dict(type='dict', default={}),
            exclude=dict(type='list', default=[]),
            logdir=dict(type='path'),
            factsdir=dict(type='path', default='/etc/ansible/facts.d'),
            ldconfig=dict(default='/sbin/ldconfig'),
            depmod=dict(default='/sbin/depmod -a'),
        ),
        supports_check_mode=False
    )
    destdir = module.params['destdir']
    exclude = module.params['exclude']
    logdir = module.params['logdir']
    ldconfig = shlex.split(module.params['ldconfig'])
    depmod = shlex.split(module.params['depmod'])

    if logdir and not os.path.exists(logdir):
        os.makedirs(logdir)

    if logdir:
        install_log = os.path.join(logdir, 'install.log')
        logging.basicConfig(
            level=logging.INFO,
            filename=install_log,
            format='%(asctime)s %(levelname)s %(message)s',
        )
        results['logfiles'].append(install_log)

    logger.info('Starting install')
    logger.debug('Parameters: %s' % pprint.pformat(module.params))

    if not os.path.isdir(destdir):
        msg = 'destdir directory not found: %s' % destdir
        logger.error(msg)
        module.fail_json(msg=msg)

    #
    # Install files.
    #
    logger.info('Copying files from %s to /' % destdir)
    files = copy_tree(destdir, '/', exclude)
    for f in files:
        results['files'].append(f[0])
        if f[1]:
            results['changed'] = True

    #
    # Log all installed files (even ones we skipped this time).
    #
    if logdir:
        install_list = os.path.join(logdir, 'install.list')
        with open(install_list, 'w') as log:
            for f in files:
                log.write('%s\n' % f[0])
        results['logfiles'].append(install_list)

    #
    # Save the command paths in the local facts. This will
    # read by setup in subsequent plays.
    #
    facts = None
    factsdir = module.params['factsdir'] 
    factsfile = os.path.join(factsdir, 'openafs.fact')
    try:
        with open(os.path.join(factsfile)) as fp:
            facts = json.load(fp)
            logger.debug('Read facts from %s: %s', factsfile, pprint.pformat(facts))
    except:
        pass

    if not facts:
        facts = {}
    if not 'commands' in facts:
        facts['commands'] = {}
    if not 'dirs' in facts:
        facts['dirs'] = {} 

    for f in files:
        if f[2]:
            command = os.path.basename(f[0])
            facts['commands'][command] = f[0]
            results['ansible_facts']['ansible_local']['openafs']['commands'][command] = f[0]
    
    dirs = module.params['dirs']
    for d in dirs:
        facts['dirs'][d] = dirs[d]
        results['ansible_facts']['ansible_local']['openafs']['dirs'][d] = dirs[d]

    if not os.path.exists(factsdir):
        os.makedirs(factsdir)
    with open(factsfile, 'w') as fp:
        json.dump(facts, fp, indent=2)
        logger.debug('Wrote facts to file %s: %s', factsfile, pprint.pformat(facts))

    #
    # Linux specific post-install commands.
    #
    if platform.system() == 'Linux':
        logger.info('Updating shared object cache.')
        module.run_command(ldconfig, check_rc=True)

        have_kmod = False
        for f in files:
            if f[0].endswith('.ko'):
                have_kmod = True
                results['kmods'].append(f[0])
        if have_kmod:
            logger.info('Updating kernel modules dependencies.')
            module.run_command(depmod, check_rc=True)

    #
    # Done.
    #
    msg = 'Install completed'
    logger.info(msg)
    results['msg'] = msg
    module.exit_json(**results)

if __name__ == '__main__':
    main()
