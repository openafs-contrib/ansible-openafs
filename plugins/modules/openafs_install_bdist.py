#!/usr/bin/python
# Copyright (c) 2020-2022, Sine Nomine Associates
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
import re                 # noqa: E402
import shutil             # noqa: E402
import stat               # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')
log = Logger(module_name)

TRANSARC_INSTALL_DIRS = {
    'afsbosconfigdir': '/usr/afs/local',
    'afsconfdir': '/usr/afs/etc',
    'afsdbdir': '/usr/afs/db',
    'afslocaldir': '/usr/afs/local',
    'afslogsdir': '/usr/afs/logs',
    'viceetcdir': '/usr/vice/etc',
}


class CopyTreeError(Exception):
    pass


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
        raise CopyTreeError("Cannot copy tree '%s': not a directory." % src)
    try:
        names = os.listdir(src)
    except os.error:
        raise CopyTreeError("Error listing files in '%s'." % src)
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


def get_platform_subclass(cls):
    for subcls in cls.__subclasses__():
        if platform.system() == subcls.platform:
            return subcls
    raise ValueError('Unknown platform: {0}'.format(platform.system))


class BinaryDistInstaller(object):
    """
    Install OpenAFS from a binary distribution.
    """

    def __new__(cls, module):
        new_cls = get_platform_subclass(BinaryDistInstaller)
        return super(cls, new_cls).__new__(new_cls)

    def __init__(self, module):
        self.module = module
        self.changed = False
        self.transarc_dist = None
        self.logfiles = []
        self.kmods = []
        self.bins = {}
        self.dirs = {}

    def install(self):
        """
        Install OpenAFS binaries.
        """
        path = self.module.params['path']
        if not os.path.isdir(path):
            self.module.fail_json(msg='path not found', path=path)

        exclude = self.get_excluded_paths()
        self.transarc_dist = self.detect_transarc_dist(path)
        if self.transarc_dist:
            log.info('Installing files from %s to legacy paths.',
                     self.transarc_dist)
            files = self.install_transarc(self.transarc_dist, exclude)
            self.dirs = TRANSARC_INSTALL_DIRS
            self.collect_bins(files)
        else:
            log.info('Installing files from %s to modern paths.', path)
            files = copy_tree(path, '/', exclude)
            self.collect_dirs(path)
            self.collect_bins(files)

        self.install_shared_libraries(files)
        self.install_kernel_module(files)

        results = dict(
            changed=self.changed,
            platform=self.platform,
            logfiles=self.logfiles,
            kmods=self.kmods,
            bins=self.bins,
            dirs=self.dirs,
        )
        return results

    def install_transarc(self, destdir, exclude):
        """
        Install a Transarc-style distribution to the lecacy paths.
        """
        components = self.module.params['components']
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

    def detect_transarc_dist(self, path, sysname=None):
        """
        Search for a legacy dest directory in the binary distribution. The
        legacy dest directory is the old style format created for AFS binary
        distributions. The dest directory contains a 'root.server' directory
        for the server binaries, a 'root.client' directory for the client
        binaries, and a set of common directories.
        """
        sysname = self.module.params['sysname']
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

    def collect_dirs(self, path):
        """
        Read the build metadata file created by the openafs_build module to
        determine the configure-time generated installation paths.
        """
        dirs = {}
        filename = os.path.join(path, '.build-info.json')
        if os.path.exists(filename):
            log.info("Reading metadata file '%s'.", filename)
            with open(filename) as f:
                build_info = json.load(f)
            log.info("build_info=%s", pprint.pformat(build_info))
            dirs = build_info.get('dirs', {})
        self.dirs = dirs

    def collect_bins(self, files):
        """
        Scan the list of installed files to determine the dictionary
        of program files.
        """
        bins = {}
        for f in files:
            fn, changed = f
            if changed:
                self.changed = True
            if re.match(r'^lib.*\.so[.\d]*$', os.path.basename(fn)):
                continue  # Skip shared libraries.
            try:
                mode = os.stat(fn).st_mode
                if stat.S_ISREG(mode) and (mode & stat.S_IXUSR):
                    bins[os.path.basename(fn)] = fn
            except IOError as e:
                log.error('Failed to stat installed file "%s: %s".' % (fn, e))
        self.bins = bins

    def find_by_suffix(self, files, suffix):
        """Find a list of files by filename suffix."""
        found = []
        for f in files:
            filename, _ = f
            if filename.endswith(suffix):
                found.append(filename)
        return found

    def directories(self, filenames):
        """Find the set of directory names for the given filename paths."""
        dirs = set()
        for filename in filenames:
            dirs.add(os.path.dirname(filename))
        return dirs


class LinuxBinaryDistInstaller(BinaryDistInstaller):
    platform = 'Linux'

    def get_excluded_paths(self):
        return self.module.params['exclude']

    def install_shared_libraries(self, files):
        if self.changed:
            log.info('Updating shared object cache.')
            libdirs = self.directories(self.find_by_suffix(files, '.so'))
            if libdirs and os.path.exists('/etc/ld.so.conf.d'):
                with open('/etc/ld.so.conf.d/openafs.conf', 'w') as f:
                    for libdir in libdirs:
                        f.write('%s\n' % libdir)
            ldconfig = self.module.params['ldconfig']
            self.module.run_command([ldconfig], check_rc=True)

    def install_kernel_module(self, files):
        self.kmods = self.find_by_suffix(files, '.ko')
        if self.changed and self.kmods:
            log.info('Updating module dependencies.')
            depmod = self.module.params['depmod']
            self.module.run_command([depmod, '-a'], check_rc=True)


class SolarisBinaryDistInstaller(BinaryDistInstaller):
    platform = 'SunOS'

    def get_excluded_paths(self):
        return self.module.params['exclude']

    def install_shared_libraries(self, files):
        if self.changed:
            libdirs = self.directories(self.find_by_suffix(files, '.so'))
            for libdir in libdirs:
                log.info('Configuring runtime link path: %s', libdir)
                self.module.run_command(['crle', '-64', '-u', '-l',
                                        libdir], check_rc=True)

    def install_kernel_module(self, files):
        self.kmods = self.find_by_suffix(files, 'libafs64.o')
        if self.kmods:
            kmod = self.kmods[0]
        else:
            kmod = None
        if kmod:
            driver = self._driver_path()
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
                self.kmods.append(driver)
                self.changed = True

    def _driver_path(self):
        """
        Determine the Solaris afs driver path.
        """
        rc, out, err = self.module.run_command(['isainfo', '-k'],
                                               check_rc=True)
        if 'amd64' in out:
            driver = '/kernel/drv/amd64/afs'
        elif 'sparcv9' in out:
            driver = 'kernel/drv/sparcv9/afs'
        else:
            driver = '/kernel/drv/afs'
        return driver


class FreeBSDBinaryDistInstaller(BinaryDistInstaller):
    platform = 'FreeBSD'

    def get_excluded_paths(self):
        exclude = self.module.params['exclude']
        if exclude is None:
            exclude = []
        if '/bin/libafs.ko' not in exclude:
            exclude.append('/bin/libafs.ko')  # Obsolete module path.
        return exclude

    def install_shared_libraries(self, files):
        pass

    def install_kernel_module(self, files):
        if self.transarc_dist:
            src = os.path.join(self.transarc_dist, 'root.client/bin/libafs.ko')
            dst = '/boot/modules'
            if not os.path.isdir(dst):
                os.makedirs(dst)
            log.info("Copying '%s' to '%s'.", src, dst)
            shutil.copy2(src, dst)
            os.chmod(os.path.join(dst, 'libafs.ko'),
                     stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP |
                     stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


def main():
    log.info('Starting %s', module_name)
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

    installer = BinaryDistInstaller(module)
    results = installer.install()
    log.info('Results: %s', pprint.pformat(results))
    module.exit_json(**results)


if __name__ == '__main__':
    main()
