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
module: openafs_get_install_paths

short_description: Detect installation paths from package installation.

description:

  - Detect the paths of installed OpenAFS programs and detect configuration
    directories from installed man pages.

  - Supports rpm and deb packaging.

options:
  package_mgr_type:
    description:
      - The package manager type on the node.
      - Supported values are C(rpm) and C(deb).
    default: autodetect

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: Get installation paths
  openafs_contrib.openafs.openafs_get_install_paths:
  register: results

- debug:
    msg: >
      Bins are {{ results.bins }}
      Dirs are {{ results.dirs }}
'''

import errno                # noqa: E402
import gzip                 # noqa: E402
import os                   # noqa: E402
import re                   # noqa: E402
import stat                 # noqa: E402
import subprocess           # noqa: E402

from ansible.module_utils.basic import AnsibleModule   # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')
log = None

canonical_name = {
    'pagsh.openafs': 'pagsh',
}


class PkgMgr:
    """
    Lookup installed files.
    """
    def parse_package(self, line):
        return line.rstrip()

    def parse_file(self, line):
        return line.rstrip()

    def list_packages(self, pattern):
        """
        Find installed packages matching a name pattern.
        """
        packages = []
        args = self.query_packages_command(pattern)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in proc.stdout:
            package = self.parse_package(line.decode())
            if package:
                packages.append(package)
        rc = proc.wait()
        if rc != 0:
            raise Exception('Failed to run command: %s, code=%d' %
                            (' '.join(args), rc))
        return packages

    def list_files(self, package):
        """
        List installed files for a given package name.
        """
        files = []
        args = self.query_files_command(package)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in proc.stdout:
            file_ = self.parse_file(line.decode())
            if file_:
                files.append(file_)
        rc = proc.wait()
        if rc != 0:
            raise Exception('Failed to run command: %s, code=%d' %
                            (' '.join(args), rc))
        return files


class RpmPkgMgr(PkgMgr):
    """
    rpm specific bits to lookup installed files.
    """
    def __init__(self, rpm):
        self.rpm = rpm

    def query_packages_command(self, pattern):
        return [self.rpm, '--query', '--all', 'name=%s' % pattern]

    def query_files_command(self, package):
        return [self.rpm, '--query', '--list', package]


class DebPkgMgr(PkgMgr):
    """
    dpkg specific bits to lookup installed files.
    """
    def __init__(self, dpkg_query):
        self.dpkg_query = dpkg_query

    def parse_package(self, line):
        """
        Parse a dpkg-query output line to find installed packages.
        """
        package, _, _, status = line.rstrip().split()
        if status == 'installed':
            return package
        else:
            return None

    def query_packages_command(self, pattern):
        return [self.dpkg_query, '--no-pager', '--show', '--showformat',
                '${Package} ${Status}\\n', pattern]

    def query_files_command(self, package):
        return [self.dpkg_query, '--no-pager', '--listfiles', package]


def is_x(path):
    """
    Return true when the path is an executable file.
    """
    try:
        mode = os.stat(path).st_mode
    except OSError as e:  # OSError works in both PY2 and PY3.
        if e.errno == errno.ENOENT:
            return False
        if e.errno == errno.EACCES:
            return False
        raise e
    return stat.S_ISREG(mode) and (mode & 0o100 != 0)


def is_bin(path):
    """
    Return true if path is an program file.
    """
    if '.build-id' in path:
        return False   # Skip build-id files.
    if re.search(r'\.so(\.\d+){0,3}$', path):
        return False   # Skip shared object files.
    if not is_x(path):
        return False   # Skip non-executable files.
    return True


def search_page(path, pattern):
    """
    Search an OpenAFS man page for a given token.

    """
    with gzip.open(path) as z:
        content = z.read().decode()
    content = re.sub(r'\\&', '', content)
    content = re.sub(r'\\f.', '', content)
    content = re.sub(r'\s+', ' ', content)
    m = re.search(pattern, content)
    if not m:
        raise Exception('Failed to find directory in %s.' % path)
    return m.group(1)


def find_bins(files):
    """
    Find the installed program files.
    """
    bins = {}
    for path in files:
        if is_bin(path):
            basename = os.path.basename(path)
            name = canonical_name.get(basename, basename)
            bins[name] = path
    return bins


def find_manpages(files):
    """
    Find the installed man pages.
    """
    manpages = {}
    for path in files:
        m = re.search(r'\.\d\.gz$', path)
        if m:
            name = re.sub(r'\.\d\.gz$', '', os.path.basename(path))
            manpages[name] = path
    return manpages


def find_dirs(files):
    """
    Detect the configuration directories.

    This is a hacky workaround to find the OpenAFS configuration directories,
    since that is a build time option, but we currently do not have a way to
    query the binaries to show the embedded configuration directories.  For
    now, try to find them in the man pages, which fortunately do not change
    often.
    """
    dirs = {}
    manpages = find_manpages(files)

    path = manpages.get('bosserver')
    if path:
        regex = r'create a file named (\S+)/BosConfig\.new'
        dirs['afsbosconfigdir'] = search_page(path, regex)

    path = manpages.get('KeyFile')
    if path:
        regex = r'The file must reside in the (\S+) directory'
        dirs['afsconfdir'] = search_page(path, regex)

    path = manpages.get('vldb.DB0')
    if path:
        regex = r'reside in the (\S+) directory'
        dirs['afsdbdir'] = search_page(path, regex)

    path = manpages.get('NetInfo')
    if path:
        regex = r'The server NetInfo file, if present in the (\S+) directory'
        dirs['afslocaldir'] = search_page(path, regex)

    path = manpages.get('FileLog')
    if path:
        regex = r'file does not already exist in the (\S+) directory'
        dirs['afslogdir'] = search_page(path, regex)

    path = manpages.get('fileserver')
    if path:
        regex = r'its binary file is located in the (\S+) directory'
        dirs['afssrvdir'] = search_page(path, regex)

    path = manpages.get('cacheinfo')
    if path:
        regex = r'must reside in the (\S+) directory'
        dirs['viceetcdir'] = search_page(path, regex)
    return dirs


def find_cacheinfo(dirs):
    """
    Find the cache manager configuration parameters.
    """
    viceetcdir = dirs.get('viceetcdir')
    if not viceetcdir:
        return None
    ci = os.path.join(viceetcdir, 'cacheinfo')
    if not os.path.exists(ci):
        log.warning('cacheinfo file not found: %s', ci)
        return None
    with open(ci) as f:
        contents = f.read().rstrip()
    try:
        mount, cachedir, size = contents.split(':')
        cacheinfo = {
            'mountpoint': mount,
            'cachedir': cachedir,
            'cachesize': int(size)
        }
    except ValueError as e:
        log.error('Failed to parse cacheinfo %s file: %s', ci, e)
        cacheinfo = None
    return cacheinfo


def find_afsd_args(files):
    """
    Detect the installed AFSD_ARGS envirnonment variable used
    in the openafs-client systemd unit file.
    """
    unitfile = None
    for path in files:
        if path.endswith('openafs-client.service'):
            unitfile = path
    if unitfile is None:
        return None
    with open(unitfile) as f:
        contents = f.readlines()
    envfile = None
    for line in contents:
        if line.startswith('EnvironmentFile=/'):
            fields = line.rstrip().split('=', 1)
            if len(fields) == 2:
                envfile = fields[1].strip()
    if envfile is None:
        return None
    with open(envfile) as f:
        contents = f.readlines()
    afsd_args = None
    for line in contents:
        if line.startswith('AFSD_ARGS'):
            fields = line.rstrip().split('=', 1)
            if len(fields) == 2:
                afsd_args = fields[1].lstrip('"').rstrip('"')
    return afsd_args


def main():
    global log
    results = dict(
        changed=False,
        bins={},
        dirs={},
    )
    module = AnsibleModule(
        argument_spec=dict(
            package_manager_type=dict(type='str', default=None),
        ),
        supports_check_mode=False,
    )
    log = Logger(module_name)
    log.info('Starting %s', module_name)

    def die(msg):
        log.error('Failed: %s' % msg)
        module.fail_json(msg=msg)

    package_manager_type = module.params['package_manager_type']
    rpm = module.get_bin_path('rpm')
    dpkg_query = module.get_bin_path('dpkg-query')

    if package_manager_type is None:
        if rpm and dpkg_query:
            die('Unable to determine package manager; rpm and dpkg found.')
        elif rpm:
            log.info('Detected rpm package manager.')
            pm = RpmPkgMgr(rpm)
        elif dpkg_query:
            log.info('Detected dpkg package manager.')
            pm = DebPkgMgr(dpkg_query)
        else:
            die('Unable to determine package manager.')
    elif package_manager_type in ('rpm', 'yum', 'dnf', 'zypper'):
        if not rpm:
            die('rpm command not found.')
        pm = RpmPkgMgr(rpm)
    elif package_manager_type in ('apt', 'deb', 'dpkg'):
        if not dpkg_query:
            die('dpkg_query command not found.')
        pm = DebPkgMgr(dpkg_query)
    else:
        die('Invalid package_manager_type value: %s' % package_manager_type)

    files = []
    packages = pm.list_packages('openafs*')
    for package in packages:
        files.extend(pm.list_files(package))

    results['bins'] = find_bins(files)
    results['dirs'] = find_dirs(files)
    cacheinfo = find_cacheinfo(results['dirs'])
    if cacheinfo:
        results['cacheinfo'] = cacheinfo
    afsd_args = find_afsd_args(files)
    if afsd_args:
        results['afsd_args'] = afsd_args

    log.debug('Results: %s', results)
    module.exit_json(**results)


if __name__ == '__main__':
    main()
