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
  Install OpenAFS binaries built from source code. This module
  will copy the files in a binary distribution tree to the
  system directories. Run this module as root. The paths to
  the installed commands are saved as Ansible local facts.

options:
  path:
    description: >
      Absolute path to the installation file tree to be installed.
    type: path
    required: true

  exclude:
    description: >
      List of file patterns to be excluded.
    type: list

  log_dir:
    description: >
      Absolute path to the installation logs for troubleshooting.
    type: path
    default: /var/log/ansible-openafs

  log_level:
    description: >
      Logging level name.
    type: str

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: Build OpenAFS from source
  openafs_build:
    projectdir: ~/src/openafs
    target: install
    path: /tmp/openafs/bdist

- name: Install OpenAFS binaries as root
  become: yes
  openafs_install:
    path: /tmp/openafs/bdist
    exclude: /usr/vice/etc/*
    log_dir: /tmp/openafs/logs
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

import filecmp
import fnmatch
import glob
import logging
import os
import platform
import pprint
import re
import shutil
from ansible.module_utils.basic import AnsibleModule

log = logging.getLogger(__name__)

LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

TRANSARC_INSTALL_DIRS = {
    'afsbosconfigdir': '/usr/afs/local',
    'afsconfdir': '/usr/afs/etc',
    'afsdbdir': '/usr/afs/db',
    'afslocaldir': '/usr/afs/local',
    'afslogdir': '/usr/afs/logs',
    'afssrvdir': '/usr/afs/bin',
    'viceetcdir': '/usr/vice/etc',
}

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
    files = [] # list of (<path>, <changed>, <executable>) tubles
    if exclude is None:
        exclude = []

    def is_exclusion(fn):
        for pattern in exclude:
            if fnmatch.fnmatch(fn, pattern):
                return True
        return False

    def is_same(src, dst):
        if os.path.exists(src) and os.path.exists(dst):
            return filecmp.cmp(src, dst, shallow=True)
        return False

    def is_executable(fn):
        return os.path.exists(fn) and os.path.isfile(fn) and os.access(fn, os.X_OK)

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
            log.info("Excluding '%s'.", dst_name)
        elif os.path.isdir(src_name):
            files.extend(copy_tree(src_name, dst_name, exclude))
        elif is_same(src_name, dst_name):
            log.info("Skipping '%s'; unchanged.", dst_name)
            files.append((dst_name, False, is_executable(src_name)))
        elif os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if os.path.exists(dst_name):
                os.remove(dst_name)
            log.debug("Creating symlink '%s'.", dst_name)
            os.symlink(link_dest, dst_name)
            files.append((dst_name, True, False))
        else:
            log.debug("Copying '%s' to '%s'.", src_name, dst_name)
            shutil.copy2(src_name, dst_name)
            files.append((dst_name, True, is_executable(src_name)))
    return files

def find_destdir(path, sysname=None):
    """
    Search for a legacy dest directory in the binary distribution. The legacy
    dest directory is the old style format created for AFS binary
    distibutions. The dest directory contains a 'root.server' directory for
    the server binaries, a 'root.client' directory for the client binaries,
    and a set of common directories.
    """
    log.debug('find_destdir: %s', path)
    if not sysname:
        sysname = '*'
    roots = set(['bin', 'etc', 'include', 'lib', 'man', 'root.server', 'root.client'])
    for pattern in ('/%s/dest' % sysname, '/dest', '/'):
        dirs = set(glob.glob(path + pattern))
        log.debug('dirs=%s', dirs)
        for destdir in dirs:
            subdirs = set(map(os.path.basename, glob.glob(destdir + '/*')))
            log.debug('subirs %s', subdirs)
            if roots.issubset(subdirs):
                return destdir
    return None

def install_dest(destdir, components, exclude=None):
    """
    Install Transarc-style distribution files.
    """
    log.debug('install_dest: %s', destdir)
    files = []
    if 'common' in components:
        for d in ('bin', 'etc', 'include', 'lib', 'man'):
            src = '%s/%s' % (destdir, d)
            if d == 'etc':
                dst = '/usr/bin' # Put misc programs in the PATH.
            else:
                dst = '/%s' % d
            files.extend(copy_tree(src, dst, exclude))
    if 'server' in components:
        src = '%s/%s' % (destdir, 'root.server')
        dst = '/'
        files.extend(copy_tree(src, dst, exclude))
    if 'client' in components:
        src = '%s/%s' % (destdir, 'root.client')
        dst = '/'
        files.extend(copy_tree(src, dst, exclude))
    return files

def main():
    results = dict(
        changed=False,
        msg='',
        ansible_facts={},
        logfiles=[],
        kmods=[],
        bins={},
        dirs={},
    )
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True, aliases=['destdir']),
            exclude=dict(type='list', default=[]),
            sysname=dict(type='str', default=None),
            components=dict(type='list', default=['common', 'client', 'server']),
            log_dir=dict(type='path', default='/var/log/ansible-openafs'),
            log_level=dict(type='str', choices=LOG_LEVELS.keys(), default='info'),
            ldconfig=dict(type='path', default='/sbin/ldconfig'),
            depmod=dict(type='path', default='/sbin/depmod'),
        ),
        supports_check_mode=False
    )
    path = module.params['path']
    exclude = module.params['exclude']
    components = module.params['components']
    log_dir = module.params['log_dir']
    log_level = module.params['log_level']
    ldconfig = module.params['ldconfig']
    depmod = module.params['depmod']

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    install_log = os.path.join(log_dir, 'openafs_install_bdist.log')
    results['logfiles'].append(install_log)
    logging.basicConfig(
        level=LOG_LEVELS[log_level],
        filename=install_log,
        format='%(asctime)s %(levelname)s %(message)s',
    )

    log.info('Starting openafs_install_bdist')
    log.debug('Parameters: %s' % pprint.pformat(module.params))

    if not os.path.isdir(path):
        msg = 'Directory not found: %s' % path
        log.error(msg)
        module.fail_json(msg=msg)

    sysname = module.params['sysname']
    destdir = find_destdir(path, sysname)
    if destdir:
        log.info("Installing %s from path '%s'." % (','.join(components), destdir))
        files = install_dest(destdir, components)
        dirs = TRANSARC_INSTALL_DIRS
    else:
        log.info('Copying files from %s to /' % path)
        files = copy_tree(path, '/', exclude)
        dirs = {}
        for f in files:
            m = re.search(r'README\.(.*dir)$', f[0])
            if m:
                dirs[m.group(1)] = os.path.dirname(f[0])

    for f in files:
        if f[1]:
            results['changed'] = True

    bins = {}
    for f in files:
        if f[2]:
            name = os.path.basename(f[0])
            bins[name] = f[0]
    results['bins'] = bins
    results['dirs'] = dirs

    if platform.system() == 'Linux':
        for f in files:
            if f[0].endswith('.ko'):
                results['kmods'].append(f[0])

        if results['changed']:
            log.info('Updating shared object cache.')
            bins = set()
            for f in files:
                if f[0].endswith('.so'):
                    bins.add(os.path.dirname(f[0]))
            if bins and os.path.exists('/etc/ld.so.conf.d'):
                with open('/etc/ld.so.conf.d/openafs.conf', 'w') as f:
                    for p in bins:
                        f.write('%s\n' % p)
            module.run_command([ldconfig], check_rc=True)

        if results['changed']:
            if results['kmods']:
                log.info('Updating module dependencies.')
                module.run_command([depmod, '-a'], check_rc=True)

    msg = 'Install completed'
    log.info(msg)
    results['msg'] = msg
    log.info('results=%s', pprint.pformat(results))
    module.exit_json(**results)

if __name__ == '__main__':
    main()
