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

  logdir:
    description: >
      Absolute path to the installation logs for troubleshooting.
      If not given, no log files are written.
    type: type

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
from ansible.module_utils.basic import AnsibleModule

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

def copy_tree(src, dst):
    """Copy an entire directory tree.

    Creates destination if needed. Clobbers any existing files/symlinks.

    :arg src: directory to copy from. must already exist
    :arg dst: directory to copy to. created if not already present
    :returns: a list of files/symlinks created
    """
    outputs = []
    if not os.path.isdir(src):
        raise FileError("cannot copy tree '%s': not a directory" % src)
    try:
        names = os.listdir(src)
    except os.error:
        raise FileError("error listing files in '%s'" % src)
    if not os.path.isdir(dst):
        os.makedirs(dst)
    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)
        if os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if os.path.exists(dst_name):
                os.remove(dst_name)
            os.symlink(link_dest, dst_name)
            outputs.append(dst_name)
        elif os.path.isdir(src_name):
            outputs.extend(copy_tree(src_name, dst_name))
        else:
            shutil.copy2(src_name, dst_name)
            outputs.append(dst_name)
    return outputs

def main():
    logger = logging.getLogger(__name__)
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
            logdir=dict(type='path'),
        ),
        supports_check_mode=False
    )
    destdir = module.params['destdir']
    logdir = module.params['logdir']

    if logdir and os.path.isdir(logdir):
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
    files = copy_tree(destdir, '/')
    results['files'] = files
    if files:
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
        logger.info('Running ldconfig to update shared object cache.')
        ldconfig = ['/sbin/ldconfig']
        rc, out, err = module.run_command(ldconfig, check_rc=True)
        results['changed'] = True

    if results['kmods']:
        if platform.system() == 'Linux':
            logger.info('Running depmod to update modprobe dependencies.')
            depmod = ['/sbin/depmod', '-a']
            rc, out, err = module.run_command(depmod, check_rc=True)
            results['changed'] = True


    msg = 'Install completed'
    logger.info(msg)
    results['msg'] = msg
    module.exit_json(**results)

if __name__ == '__main__':
    main()
