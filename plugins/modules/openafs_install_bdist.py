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
module: openafs_install_bdist

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

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: Build OpenAFS from source
  openafs_contrib.openafs.openafs_build:
    projectdir: ~/src/openafs
    target: install
    path: /tmp/openafs/bdist

- name: Install OpenAFS binaries as root
  become: yes
  openafs_contrib.openafs.openafs_install:
    path: /tmp/openafs/bdist
    exclude: /usr/vice/etc/*
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

import filecmp            # noqa: E402
import fnmatch            # noqa: E402
import glob               # noqa: E402
import json               # noqa: E402
import os                 # noqa: E402
import platform           # noqa: E402
import pprint             # noqa: E402
import shutil             # noqa: E402
import stat               # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import chdir  # noqa: E402, E501
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import execute  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')
log = None

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


def solaris_relocate_64_bit_libs(files):
    """
    The OpenAFS 'make dest' command puts the solaris 64-bit shared libraries in
    /lib, which is incorrect.  Move the 64-bit libraries to the /lib/64
    directory, including the shared library symlinks.
    """
    moved = []
    afslibs = set()
    for f in files:
        dirname = os.path.dirname(f[0])
        basename = os.path.basename(f[0])
        if dirname == '/lib':
            afslibs.add(basename)
    # Expected system directories should be present.
    for libdir in ('/lib', '/lib/64'):
        if not os.path.exists(libdir):
            raise AssertionError('System lib dir not found: %s' % libdir)
    with chdir('/lib'):
        # Find the shared library symlinks.
        links = {}
        for path in glob.glob('*'):
            if os.path.islink(path):
                target = os.readlink(path)
                if target not in links:
                    links[target] = []
                links[target].append(path)
        # Find 64-bit libraries to be moved.
        tomove = []
        todel = []
        for path in afslibs:
            if not os.path.exists(path):
                continue
            if os.path.isdir(path):
                continue
            if os.path.islink(path):
                continue
            output = execute('file %s' % path)
            if '64-bit' in output:
                target = os.path.join('64', path)
                if not os.path.exists(target):
                    tomove.append(path)   # Relocate file.
                elif filecmp.cmp(path, target):
                    todel.append(path)    # Already relocated.
                else:
                    tomove.append(path)   # Relocate updated file.
        # Move 64-bit libraries and associated symlinks.
        for path in tomove:
            for link in links.get(path, []):
                if os.path.exists(link) and os.path.islink(link):
                    os.unlink(link)
            target = os.path.join('64', path)
            if os.path.exists(target):
                os.unlink(target)
            os.rename(path, target)
            with chdir('64'):
                for link in links.get(path, []):
                    if not os.path.exists(link):
                        os.symlink(path, link)
                        moved.append(link)
        # Cleanup duplicate files.
        for path in todel:
            for link in links.get(path, []):
                if os.path.exists(link) and os.path.islink(link):
                    os.unlink(link)
            os.unlink(path)
    return moved


def solaris_driver_path():
    """
    Determine the solaris afs driver path.
    """
    output = execute('isainfo -k')
    if 'amd64' in output:
        driver = '/kernel/drv/amd64/afs'
    elif 'sparcv9' in output:
        driver = 'kernel/drv/sparcv9/afs'
    else:
        driver = '/kernel/drv/afs'
    return driver


def copy_tree(src, dst, exclude=None):
    """Copy an entire directory tree.

    Creates destination if needed. Clobbers any existing files/symlinks.

    :arg src: directory to copy from. must already exist
    :arg dst: directory to copy to. created if not already present
    :arg exclude: list of patterns (glob notation) to exclude
    :returns: a list of tuples of the files/symlinks copied and skipped
    """
    files = []  # list of (<path>, <changed>, <executable>) tuples
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
            files.append((dst_name, False))
        elif os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if os.path.exists(dst_name):
                os.remove(dst_name)
            log.debug("Creating symlink '%s'.", dst_name)
            os.symlink(link_dest, dst_name)
            files.append((dst_name, True))
        else:
            log.debug("Copying '%s' to '%s'.", src_name, dst_name)
            shutil.copy2(src_name, dst_name)
            files.append((dst_name, True))
    return files


def find_destdir(path, sysname=None):
    """
    Search for a legacy dest directory in the binary distribution. The legacy
    dest directory is the old style format created for AFS binary
    distributions. The dest directory contains a 'root.server' directory for
    the server binaries, a 'root.client' directory for the client binaries,
    and a set of common directories.
    """
    log.debug('find_destdir: %s', path)
    if not sysname:
        sysname = '*'
    roots = set(['bin', 'etc', 'include', 'lib', 'man', 'root.server',
                'root.client'])
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
                dst = '/usr/bin'  # Put misc programs in the PATH.
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
    global log
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
            components=dict(type='list',
                            default=['common', 'client', 'server']),
            ldconfig=dict(type='path', default='/sbin/ldconfig'),
            depmod=dict(type='path', default='/sbin/depmod'),
        ),
        supports_check_mode=False
    )
    log = Logger(module_name)
    log.info('Starting %s', module_name)
    log.info('Parameters: %s', pprint.pformat(module.params))

    path = module.params['path']
    exclude = module.params['exclude']
    components = module.params['components']
    ldconfig = module.params['ldconfig']
    depmod = module.params['depmod']

    if not os.path.isdir(path):
        msg = 'Directory not found: %s' % path
        log.error(msg)
        module.fail_json(msg=msg)

    sysname = module.params['sysname']
    destdir = find_destdir(path, sysname)
    if destdir:
        log.info("Installing %s from path '%s'." %
                 (','.join(components), destdir))
        files = install_dest(destdir, components)
        results['dirs'] = TRANSARC_INSTALL_DIRS
    else:
        log.info('Copying files from %s to /' % path)
        files = copy_tree(path, '/', exclude)
        dirs = {}
        filename = os.path.join(path, '.build-info.json')
        if os.path.exists(filename):
            log.info("Reading metadata file '%s'.", filename)
            with open(filename) as f:
                build_info = json.load(f)
            log.info("build_info=%s", pprint.pformat(build_info))
            dirs = build_info.get('dirs', {})
            log.info("dirs=%s", pprint.pformat(dirs))
        results['dirs'] = dirs

    for f in files:
        fn, changed = f
        if changed:
            results['changed'] = True
        try:
            mode = os.stat(fn).st_mode
            if stat.S_ISREG(mode) and (mode & stat.S_IXUSR):
                results['bins'][os.path.basename(fn)] = fn
        except IOError as e:
            log.error('Failed to stat installed file "%s: %s".' % (fn, e))

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
    elif platform.system() == 'SunOS':
        relocated = solaris_relocate_64_bit_libs(files)
        if relocated:
            results['changed'] = True
        results['relocated'] = relocated

        kmod = None
        for f in files:
            if f[0].endswith('libafs64.o'):
                kmod = f[0]
                results['kmods'].append(kmod)
        if kmod:
            driver = solaris_driver_path()
            if not os.path.exists(driver):
                update = True
                log.debug('Driver to be installed.')
            elif filecmp.cmp(kmod, driver, shallow=True):
                update = False
                log.debug('Driver is already up to date.')
            else:
                update = True
                log.debug('Driver to be updated.')
            if update:
                log.info('Copying "%s" to "%s"', kmod, driver)
                shutil.copy2(kmod, driver)
                results['kmods'].append(driver)
                results['changed'] = True

    msg = 'Install completed'
    log.info(msg)
    results['msg'] = msg
    log.info('Results: %s', pprint.pformat(results))
    module.exit_json(**results)


if __name__ == '__main__':
    main()
