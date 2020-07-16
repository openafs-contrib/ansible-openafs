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
  Install OpenAFS binaries built from source. This module usually
  needs to be run as root.

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

commands:
  description: Command paths
  returned: success
  type: dict
  sample:
    vos: /usr/sbin/vos
    pts: /usr/bin/pts

logfiles:
  description: Log files written for troubleshooting
  returned: always
  type: list
  sample:
    - /tmp/logs/install.log
'''

import logging
import os
import platform
import pprint
import shutil
import fnmatch
import filecmp
from ansible.module_utils.basic import AnsibleModule

logger = logging.getLogger(__name__)

COMMANDS = {
    'akeyconvert',
    'aklog',
    'asetkey',
    'bos',
    'bosserver',
    'dafileserver',
    'davolserver',
    'fileserver',
    'fs',
    'pts',
    'ptserver',
    'upclient',
    'upserver',
    'vlserver',
    'volserver',
    'vos',
}

class FileError(Exception):
    pass

def copy_tree(src, dst, exclude=None):
    """Copy an entire directory tree.

    Creates destination if needed. Clobbers any existing files/symlinks.

    :arg src: directory to copy from. must already exist
    :arg dst: directory to copy to. created if not already present
    :arg exclude: list of patterns (glob notation) to exclude
    :returns: a list of files/symlinks created
    """
    copied = []
    skipped = []
    if exclude is None:
        exclude = []
    def is_exclusion(fn):
        for pattern in exclude:
            if fnmatch.fnmatch(fn, pattern):
                return True
        return False
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
            c, s = copy_tree(src_name, dst_name, exclude)
            copied.extend(c)
            skipped.extend(s)
        elif filecmp.cmp(src_name, dst_name, shallow=True):
            logger.info("Skipping '%s'; already copied.", dst_name)
            skipped.append(dst_name)
        elif os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if os.path.exists(dst_name):
                os.remove(dst_name)
            logger.debug("Creating symlink '%s'.", dst_name)
            os.symlink(link_dest, dst_name)
            copied.append(dst_name)
        else:
            logger.debug("Copying '%s' to '%s'.", src_name, dst_name)
            shutil.copy2(src_name, dst_name)
            copied.append(dst_name)
    return (copied, skipped)

def main():
    results = dict(
        changed=False,
        msg='',
        ansible_facts={},
        files=[],
        kmods=[],
        logfiles=[],
    )
    module = AnsibleModule(
        argument_spec=dict(
            destdir=dict(type='path', required=True),
            exclude=dict(type='list', default=[]),
            logdir=dict(type='path'),
        ),
        supports_check_mode=False
    )
    destdir = module.params['destdir']
    exclude = module.params['exclude']
    logdir = module.params['logdir']

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

    logger.info('Copying files from %s to /' % destdir)
    copied, skipped = copy_tree(destdir, '/', exclude)
    files = copied + skipped
    results['files'] = files
    if copied:
        results['changed'] = True

    for file_ in files:
        command = os.path.basename(file_)
        if command in COMMANDS:
            results['ansible_facts']['afs_' + command] = file_

    if platform.system() == 'Linux':
        for file_ in files:
            if file_.endswith('.ko'):
                results['kmods'].append(file_)

    if logdir:
        install_list = os.path.join(logdir, 'install.list')
        with open(install_list, 'w') as log:
            for file_ in files:
                log.write('%s\n' % file_)
        results['logfiles'].append(install_list)

    if platform.system() == 'Linux':
        if copied:
            logger.info('Running ldconfig to update shared object cache.')
            ldconfig = ['/sbin/ldconfig']
            rc, out, err = module.run_command(ldconfig, check_rc=True)
            if results['kmods']:
                logger.info('Running depmod to update modprobe dependencies.')
                depmod = ['/sbin/depmod', '-a']
                rc, out, err = module.run_command(depmod, check_rc=True)

    msg = 'Install completed'
    logger.info(msg)
    results['msg'] = msg
    module.exit_json(**results)

if __name__ == '__main__':
    main()
