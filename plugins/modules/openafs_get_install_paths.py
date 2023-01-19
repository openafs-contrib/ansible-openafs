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
      - Supported values are C(rpm) and C(apt).
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

from ansible.module_utils.basic import AnsibleModule   # noqa: E402
from ansible.module_utils.facts.system.distribution import DistributionFactCollector  # noqa: E402, E501
from ansible.module_utils.facts.system.pkg_mgr import PkgMgrFactCollector  # noqa: E402, E501

from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')
log = Logger(module_name)


def prefix_keys(prefix, facts):
    """
    Add a namespace prefix to the keys in a dictionary, e.g.,
    change os_family to ansible_os_family.
    """
    new_facts = {}
    for key, value in facts.items():
        if not key.startswith(prefix):
            key = prefix + key
        new_facts[key] = value
    return new_facts


def get_system_pkg_mgr(module):
    """
    Run the Ansible PkgMgrFactCollector to find the ansible_pkg_mgr on this
    system.  The PkgMgrFactCollector depends on the platform distribution
    facts, prefixed with the ansible namespace, e.g. ansible_os_family, not
    os_family.
    """
    dist_collector = DistributionFactCollector()
    dist_facts = prefix_keys('ansible_', dist_collector.collect(module))

    pkg_mgr_collector = PkgMgrFactCollector()
    pkg_mgr_facts = pkg_mgr_collector.collect(module, dist_facts)
    pkg_mgr = pkg_mgr_facts.get('pkg_mgr')
    if not pkg_mgr:
        raise ValueError('Unable to find the system package manager.')

    log.info('pkg_mgr is %s', pkg_mgr)
    return pkg_mgr


def get_pkg_mgr_subclass(cls, module):
    """
    Find a suitable collector subclass for the package manager on this system.
    Lookup the ansible_pkg_mgr if a package manager is not specified by as a
    module parameter.
    """
    pkg_mgr = module.params.get('package_manager_type')
    if not pkg_mgr:
        pkg_mgr = get_system_pkg_mgr(module)

    for subcls in cls.__subclasses__():
        if pkg_mgr in subcls.pkg_mgrs:
            return subcls

    raise NotImplementedError('Unknown package manager: {0}'.format(pkg_mgr))


class InstallationFactCollector(object):
    """
    Query the package manager to find the file paths of the currently installed
    OpenAFS packages.   First lookup the installed package names, then lookup
    the files for each package.  Package manager specific tasks are handled by
    subclasses.
    """

    def __new__(cls, module):
        new_cls = get_pkg_mgr_subclass(InstallationFactCollector, module)
        return super(cls, new_cls).__new__(new_cls)

    def __init__(self, module):
        self.module = module

    def collect(self):
        """
        Collect information about the OpenAFS installation on this system.
        """
        packages = self.collect_package_names()
        paths = self.collect_all_paths(packages)
        bins = self.collect_bins(paths)
        manpages = self.collect_manpages(paths)
        dirs = self.collect_dirs(manpages)
        cacheinfo = self.collect_cacheinfo(dirs)

        facts = {
            'packages': sorted(list(packages)),
            'paths': sorted(list(paths)),
            'bins': bins,
            'manpages': manpages,
            'dirs': dirs,
            'cacheinfo': cacheinfo,
        }
        return facts

    def collect_all_paths(self, packages):
        """
        Find all the paths for one or more installed packages.
        """
        paths = set()
        for package in packages:
            paths.update(self.collect_paths(package))
        return paths

    def collect_bins(self, paths):
        """
        Find the installed program files.
        """
        canonical_name = {
            'pagsh.openafs': 'pagsh',
        }
        bins = {}
        for path in paths:
            if self.is_bin(path):
                basename = os.path.basename(path)
                name = canonical_name.get(basename, basename)
                bins[name] = path
        return bins

    def collect_manpages(self, paths):
        """
        Find the installed man pages.
        """
        manpages = {}
        for path in paths:
            m = re.search(r'\.\d\.gz$', path)
            if m:
                name = re.sub(r'\.\d\.gz$', '', os.path.basename(path))
                manpages[name] = path
        return manpages

    def collect_dirs(self, manpages):
        """
        Find the configuration directories.

        This is a hacky workaround to find the OpenAFS configuration
        directories, since that is a build time option, but we currently do not
        have a way to query the binaries to show the embedded configuration
        directories.  For now, try to find them in the man pages, which
        fortunately do not change often.
        """
        dirs = {}

        path = manpages.get('bosserver')
        if path:
            regex = r'create a file named (\S+)/BosConfig\.new'
            dirs['afsbosconfigdir'] = self.search_page(path, regex)

        path = manpages.get('KeyFile')
        if path:
            regex = r'The file must reside in the (\S+) directory'
            dirs['afsconfdir'] = self.search_page(path, regex)

        path = manpages.get('vldb.DB0')
        if path:
            regex = r'reside in the (\S+) directory'
            dirs['afsdbdir'] = self.search_page(path, regex)

        path = manpages.get('NetInfo')
        if path:
            regex = r'The server NetInfo file, if present in the (\S+) directory'  # noqa: E501
            dirs['afslocaldir'] = self.search_page(path, regex)

        path = manpages.get('FileLog')
        if path:
            regex = r'file does not already exist in the (\S+) directory'
            dirs['afslogsdir'] = self.search_page(path, regex)

        path = manpages.get('fileserver')
        if path:
            regex = r'its binary file is located in the (\S+) directory'
            dirs['afssrvbindir'] = self.search_page(path, regex)

        path = manpages.get('cacheinfo')
        if path:
            regex = r'must reside in the (\S+) directory'
            dirs['viceetcdir'] = self.search_page(path, regex)

        return dirs

    def collect_cacheinfo(self, dirs):
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

    def search_page(self, path, pattern):
        """
        Search an OpenAFS man page for a directory.
        """
        # Note: Avoiding a context manager here to support ancient versions
        #       of Python found on RHEL/CentOS 6.
        z = gzip.open(path)
        content = z.read().decode()
        z.close()
        content = re.sub(r'\\&', '', content)
        content = re.sub(r'\\f.', '', content)
        content = re.sub(r'\s+', ' ', content)
        m = re.search(pattern, content)
        if not m:
            raise ValueError('Failed to find directory in %s.' % path)
        return m.group(1)

    def is_bin(self, path):
        """
        Return true if path is an program file.
        """
        if re.search(r'\.so(\.\d+){0,3}$', path):
            return False   # Skip shared object files.
        if not self.is_x(path):
            return False   # Skip non-executable files.
        return True

    def is_x(self, path):
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


class RpmInstallationFactCollector(InstallationFactCollector):
    """
    RPM package manager specific collection methods.
    """
    pkg_mgrs = ['rpm', 'dnf', 'yum', 'zypper']

    def __init__(self, module):
        super(RpmInstallationFactCollector, self).__init__(module)
        self.rpm = module.get_bin_path('rpm', required=True)

    def collect_package_names(self):
        """
        Find the names of the OpenAFS packages installed on this system.
        """
        args = [self.rpm, '--query', '--all', 'name=openafs*']
        rc, out, err = self.module.run_command(args)
        if rc != 0:
            log.error('rpm query failed', err)
            self.module.fail_json(msg='rpm query failed', rc=rc, err=err)
        return set(out.splitlines())

    def collect_paths(self, package):
        """
        Find the paths of the files and directories installed by a package.
        """
        args = [self.rpm, '--query', '--list', package]
        rc, out, err = self.module.run_command(args)
        if rc != 0:
            log.error('rpm query failed', err)
            self.module.fail_json(msg='rpm query failed', rc=rc, err=err)
        paths = set()
        for path in out.splitlines():
            if '.build-id' not in path:  # Omit build meta data files.
                paths.add(path)
        return paths


class DebianInstallationFactCollector(InstallationFactCollector):
    """
    Debian package manager specific collection methods.
    """
    pkg_mgrs = ['apt', 'apt-get', 'dpkg']

    def __init__(self, module):
        super(DebianInstallationFactCollector, self).__init__(module)
        self.dpkg_query = module.get_bin_path('dpkg-query', required=True)

    def collect_package_names(self):
        """
        Find the names of the OpenAFS packages installed on this system.
        """
        args = [self.dpkg_query, '--no-pager', '--show', '--showformat',
                '${Package} ${Status}\\n', 'openafs*']
        rc, out, err = self.module.run_command(args)
        if rc != 0:
            log.error('dpkg-query failed', err)
            self.module.fail_json(msg='dpkg-query failed', rc=rc, err=err)
        packages = set()
        for line in out.splitlines():
            package, _, _, status = line.rstrip().split()
            if status == 'installed':
                packages.add(package)
        return packages

    def collect_paths(self, package):
        """
        Find the paths of the files and directories installed by a package.
        """
        args = [self.dpkg_query, '--no-pager', '--listfiles', package]
        rc, out, err = self.module.run_command(args)
        if rc != 0:
            log.error('dpkg-query failed', err)
            self.module.fail_json(msg='dpkg-query failed', rc=rc, err=err)
        paths = set()
        for path in out.splitlines():
            if path != '/.':      # Omit root directory
                paths.add(path)
        return set(paths)


class SolarisInstallationFactCollector(InstallationFactCollector):
    """
    Solaris package manager specific collection methods.
    """
    pkg_mgrs = ['pkg5']  # aka IPS

    def __init__(self, module):
        super(SolarisInstallationFactCollector, self).__init__(module)
        self.pkg = module.get_bin_path('pkg', required=True)

    def collect_package_names(self):
        """
        Find the names of the OpenAFS packages installed on this system.
        """
        args = [self.pkg, 'list', '-H', '*openafs*']
        rc, out, err = self.module.run_command(args)
        if rc != 0:
            if 'no packages matching' in err:
                return set()
            log.error('pkg list failed', err)
            self.module.fail_json(msg='pkg list failed', rc=rc, err=err)
        packages = set()
        for line in out.splitlines():
            words = line.rstrip().split()
            if len(words) > 0:
                packages.add(words[0])
        return packages

    def collect_paths(self, package):
        """
        Find the paths of the files and directories installed by a package.
        """
        args = [self.pkg, 'contents', '-H', package]
        rc, out, err = self.module.run_command(args)
        if rc != 0:
            log.error('pkg contents failed', err)
            self.module.fail_json(msg='pkg contents failed', rc=rc, err=err)
        paths = set()
        for path in out.splitlines():
            if not path.startswith('/'):
                path = '/%s' % path
            paths.add(path)
        return paths

    def collect_manpages(self, paths):
        """
        Find the installed man pages.
        """
        manpages = {}
        for path in paths:
            m = re.search(r'man/man\d/.*\.\d$', path)
            if m:
                name = re.sub(r'\.\d$', '', os.path.basename(path))
                manpages[name] = path
        return manpages

    def search_page(self, path, pattern):
        """
        Search an OpenAFS man page for a directory.
        """
        with open(path) as f:
            content = f.read()
        content = re.sub(r'\\&', '', content)
        content = re.sub(r'\\f.', '', content)
        content = re.sub(r'\s+', ' ', content)
        m = re.search(pattern, content)
        if not m:
            raise ValueError('Failed to find directory in %s.' % path)
        return m.group(1)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            package_manager_type=dict(type='str', default=None),
        ),
        supports_check_mode=False,
    )
    log.info('Starting %s', module_name)

    collector = InstallationFactCollector(module)
    results = collector.collect()
    results['changed'] = False

    log.debug('Results: %s', results)
    module.exit_json(**results)


if __name__ == '__main__':
    main()
