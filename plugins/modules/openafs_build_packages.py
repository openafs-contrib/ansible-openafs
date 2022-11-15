#!/usr/bin/python
# Copyright (c) 2021-2022, Sine Nomine Associates
# BSD 2-Clause License

ANSIBLE_METADATA = {
    'metadata_version': '1.1.',
    'status': ['preview'],
    'supported_by': 'community',
}

DOCUMENTATION = r'''
---
module: openafs_build_packages

short_description: Build OpenAFS installation packages

description:
- Build OpenAFS installation packages from an OpenAFS source distribution.

- This module supports building RPM packages for RedHat family distributions.
  Other packaging types may be added in the future.

- The source distribution files must be already present in the I(sdist)
  directory on the remote node. The source distribution files may be created
  with the C(openafs_build_sdist) module.

- The M(openafs_build_packages) module will create the rpm workspace
  directories and populate the SPECS and SOURCES directories from the source
  distribution files and the file options, then will build the source and
  binary rpm files with C(rpmbuild).

- The RPM package version and release strings are generated from the OpenAFS
  version string extracted from the C(.version) file in the source archive.

- See the C(openafs_devel) role for tasks to install the required build tools
  and libraries.

requirements:
  - Tools and libraries required to build OpenAFS.
  - The C(kernel-devel) package, when building the kernel module.
  - C(rpmbuild) tool

options:
  build:
    description:
      - Specifies which packages to build.
      - C(all) build source and binary RPMs for userspace and kernel module
      - C(source) build the source RPM only
      - C(userspace) build the source RPM and the userspace RPMs
      - C(modules) build the source RPM and the kmod RPM
    type: str
    default: all

  sdist:
    description:
    - The path on the remote node to the source distribution files directory
      on the remote node.
    - The I(sdist) directory must contain the C(openafs-<version>-src.tar.bz2)
      source archive and the C(openafs-<version>-doc.tar.bz2) documentation
      archive.
    - The I(sdist) directory may also contain the C(ChangeLog) file and the
      C(RELNOTES-<version>) file.
    type: path
    required: true

  spec:
    description:
    - The path on the remote node to a custom C(openafs.spec) file to be used
      to build the rpm files. The C(openafs.spec) file will be extracted from
      the source archive file when the I(spec) option is not provided.
    type: str
    default: None

  relnotes:
    description:
    - The path on the remote node to a custom C(RELNOTES) file to be included
      in the build.
    - The C(RELNOTES-<version>) in the I(sdist) directory will be used when
      the I(relnotes) option is not specified. The C(NEWS) file will be
      extracted from the source archive if the C(RELNOTES-<version>) file is
      not found in the I(sdist) directory.
    type: str
    default: None

  changelog:
    description:
    - The path on the remote node to a custom C(ChangeLog) file to be included
      in the build.
    - The C(ChangeLog) in the I(sdist) directory will be used when the
      C(changelog) option is not specified.  An empty C(ChangeLog) file will be
      created if the  C(ChangeLog) is not found in the I(sdist) directory,
    type: str
    default: None

  csdb:
    description:
    - The path on the remote node to a custom C(CellServDB) file to be incuded
      in the build.
    - The C(CellServDB) file in the I(sdist) directory will be used when the
      I(csdb) option is not specified. The C(CellServDB) file will be extracted
      from the source archive if the C(CellServDB) file is not found in the
      I(sdist) directory.
    type: path
    default: None

  patchdir:
    description:
    - The path on the remote node of the directory containing patch files to
      be applied.
    - Patch names are identified by the C(PatchXX) directives in the spec
      file.
    type: path
    default: I(sdist)

  kernvers:
    description:
    - The kernel version to be used when building the kernel module. By
      default, the kernel version of the running kernel will be used.
    type: str
    default: current kernel version

  topdir:
    description:
      - The top level rpmbuild workspace directory on the remote node.
    type: path
    default: C(~/rpmbuild)

  logdir:
    description:
      - The path to write build log files on the remote node.
    type: path
    default: I(topdir)/C(BUILD)

  tar:
    description:
      - The C(tar) program used to unpack the source archive.
    type: path
    default: C(tar)

  tar_extra_options:
    description:
      - Extra command line options to unpack the source archive.
    type: str
    default: None

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: "Checkout OpenAFS source code."
  git:
    repo: "git@openafs.org/openafs.git"
    version: openafs-devel-1_9_1
    dest: openafs

- name: "Build source distribution."
  openafs_build_sdist:
    topdir: openafs
    sdist: openafs/packages

- name: "Build RPM files."
  openafs_build_packages:
    build: all
    sdist: openafs/packages
  register: build_results
'''

RETURN = r'''
version:
  description: OpenAFS and package versions extracted from the source archive.
  returned: always
  type: dict

logfiles:
  description: The build log files written on the remote node.
  returned: always
  type: list

packages:
  description: The list of package files created on the remote node.
  returned: always
  type: list
'''

import glob             # noqa: E402
import os               # noqa: E402
import platform         # noqa: E402
import re               # noqa: E402
import shlex            # noqa: E402
import shutil           # noqa: E402
import subprocess       # noqa: E402

from ansible.module_utils.basic import get_distribution  # noqa: E402
from ansible.module_utils.basic import AnsibleModule     # noqa: E402
from ansible.module_utils.common.sys_info import get_platform_subclass  # noqa: E402, E501

from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import tmpdir  # noqa: E402, E501

# Globals
module_name = os.path.basename(__file__).replace('.py', '')
log = Logger(module_name)


def expand_path(path):
    if path:
        path = os.path.abspath(os.path.expanduser(path))
    return path


class PackageBuilder(object):
    """
    Base class for package builders.  Platform specific subclasses must provide
    implementation.

    This class is created on platforms we do not support packaging building
    yet, and so the module will fail on those platforms.
    """
    def __new__(cls, *args, **kwargs):
        new_cls = get_platform_subclass(PackageBuilder)
        return super(cls, new_cls).__new__(new_cls)

    def __init__(self, module):
        self.module = module
        self.results = dict(
            changed=False,
            platform=platform.system(),
            distribution=get_distribution(),
            builder=self.__class__.__name__,
            logfiles=[],
        )

    def create_workspace(self):
        self.module.fail_json(
            msg='Unsupported platform.',
            module=module_name,
            platform=platform.system(),
            distribution=get_distribution(),
        )

    def build(self):
        self.module.fail_json(
            msg='Unsupported platform.',
            module=module_name,
            platform=platform.system(),
            distribution=get_distribution(),
        )

    def copy(self, src, dst):
        """
        Copy a file.
        """
        if not os.path.exists(src):
            self.module.fail_json(msg='Source file not found.', src=src)
        if src == dst:
            self.module.fail_json(
                msg='Source name is same as destination.', src=src)
        log.info('Copying "%s" to "%s".' % (src, dst))
        shutil.copy(src, dst)

    def untar(self, archive):
        """
        Uncompress a tar archive in the current directory.
        """
        log.info('Unpacking archive "%s".' % archive)
        tar = self.module.params['tar']
        tar_extra_options = \
            shlex.split(self.module.params['tar_extra_options'])
        if not tar:
            tar = self.module.get_bin_path('tar', required=True)
        if archive.endswith('.gz'):
            uncompress = 'z'
        elif archive.endswith('.bz2'):
            uncompress = 'j'
        else:
            raise ValueError('Unsupported compression type: %s' % archive)
        options = ''.join(['x', uncompress, 'f'])
        args = [tar, options] + tar_extra_options + [archive]
        rc, out, err = self.module.run_command(args, check_rc=True)
        log.info('untar: rc=%d out=%s err=%s', rc, out, err)

    def unpack_source(self, sdist):
        """
        Unpack the source archive file and return the version info.
        """
        g = glob.glob('%s/openafs-*-src.tar.bz2' % sdist)
        if len(g) == 0:
            raise ValueError('Source archive not found in path "%s".' % sdist)
        if len(g) > 1:
            raise ValueError(
                'More than one source archive found in path "%s".' % sdist)
        archive = g[0]
        self.untar(archive)
        roots = glob.glob('openafs*')
        if len(roots) != 1:
            raise ValueError('One root directory expected source archive.')
        os.chdir(roots[0])
        version = self.extract_version_info()
        self.results['version'] = version
        return version


class RedHatRpmBuilder(PackageBuilder):
    """
    Package builder for RedHat family distributions.
    """
    platform = 'Linux'
    distribution = 'Redhat'

    def __init__(self, module):
        super(RedHatRpmBuilder, self).__init__(module)
        self.topdir = expand_path(module.params['topdir'])
        self.logdir = expand_path(module.params['logdir'])
        # Set up logging.
        if not self.logdir:
            self.logdir = os.path.join(self.topdir, 'BUILD')
        if not os.path.isdir(self.logdir):
            os.makedirs(self.logdir)
            self.results['changed'] = True

    def create_workspace(self):
        """
        Setup the rpmbuild workspace directory tree.

        Create the rpmbuild SOURCES and SPECS directories and populate them
        with the source and spec files from the source distribution in
        preparation for building the source and binary RPM files.
        """

        sdist = expand_path(self.module.params['sdist'])
        spec = expand_path(self.module.params['spec'])
        relnotes = expand_path(self.module.params['relnotes'])
        changelog = expand_path(self.module.params['changelog'])
        csdb = expand_path(self.module.params['csdb'])
        patchdir = expand_path(self.module.params['patchdir'])

        for name in ('SOURCES', 'SPECS'):
            directory = os.path.join(self.topdir, name)
            if not os.path.exists(directory):
                os.makedirs(directory)

        with tmpdir():
            version = self.unpack_source(sdist)
            if spec:
                if spec.endswith('.in'):
                    self.prepare_spec(spec, version)
                else:
                    self.copy(spec, os.path.join(self.topdir, 'SPECS', 'openafs.spec'))  # noqa: E501
            else:
                self.prepare_spec('src/packaging/RedHat/openafs.spec.in', version)   # noqa: E501
            for source in self.list_sources(version):
                dest = os.path.join(self.topdir, 'SOURCES', source)
                if '-src.tar.' in source:
                    self.copy(os.path.join(sdist, source), dest)
                elif '-doc.tar.' in source:
                    self.copy(os.path.join(sdist, source), dest)
                elif 'RELNOTES' in source:
                    if not relnotes:
                        relnotes = os.path.join(sdist, source)
                    if os.path.exists(relnotes):
                        self.copy(relnotes, dest)
                    else:
                        with open(dest, 'w') as f:
                            f.write('No release notes provided.\n')
                elif 'ChangeLog' in source:
                    if not changelog:
                        changelog = os.path.join(sdist, 'ChangeLog')
                    if os.path.exists(changelog):
                        self.copy(changelog, dest)
                    else:
                        with open(dest, 'w') as f:
                            f.write('No change log provided.\n')
                elif 'CellServDB' in source:
                    if not csdb:
                        csdb = os.path.join(sdist, 'CellServDB')
                        if not os.path.exists(csdb):
                            csdb = 'src/afsd/CellServDB'
                    self.copy(csdb, dest)
                else:
                    self.copy(os.path.join('src/packaging/RedHat', source), dest)   # noqa: E501

            for patch in self.list_patches(version):
                dest = os.path.join(self.topdir, 'SOURCES', patch)
                if patchdir:
                    self.copy(os.path.join(patchdir, patch), dest)
                else:
                    self.copy(os.path.join(sdist, patch), dest)

    def build(self):
        """
        Run rpmbuild to build the source and/or binary rpms.
        """
        build = self.module.params['build'] or 'all'
        kernvers = self.module.params['kernvers']

        rpmbuild = self.module.get_bin_path('rpmbuild', required=True)
        args = [rpmbuild, '--define', '_topdir %s' % self.topdir]
        if build == 'source':
            args.append('-bs')
        elif build == 'all':
            args.append('-ba')
        elif build == 'userspace':
            args.append('-ba')
            args.extend(['--define', 'build_userspace 1'])
            args.extend(['--define', 'build_modules 0'])
        elif build == 'module':
            args.append('-ba')
            args.extend(['--define', 'build_userspace 0'])
            args.extend(['--define', 'build_modules 0'])
        if build != 'source' and kernvers:
            args.extend(['--define', 'kernvers %s' % kernvers])
        args.append(os.path.join(self.topdir, 'SPECS', 'openafs.spec'))
        logfile = os.path.join(self.logdir, 'rpmbuild.log')
        self.results['logfiles'].append(logfile)
        with open(logfile, 'w') as f:
            log.info('Running: %s > %s' % (' '.join(args), logfile))
            proc = subprocess.Popen(args, stdout=f.fileno(), stderr=f.fileno())
            rc = proc.wait()
        log.info('rpmbuild rc=%d', rc)
        if rc != 0:
            self.module.fail_json(msg='rpmbuild failed', logfile=logfile)
        packages = []
        with open(logfile, 'r') as f:
            for line in f.readlines():
                m = re.match(r'Wrote: (.*)', line)
                if m:
                    packages.append(m.group(1).rstrip())
        self.results['package_type'] = 'rpm'
        self.results['packages'] = packages
        self.results['changed'] = True

    def extract_version_info(self):
        """
        Extract the version information from the .version file.
        """
        version = None
        if os.path.exists('.version'):
            with open('.version') as f:
                line = f.read().rstrip()
            log.info('.version contains "%s"', line)
            if line.startswith('openafs-'):
                # Extract version from the git tag name.
                version = re.sub('openafs-[^-]*-', '', line).replace('_', '.')
            elif line.startswith('BP-'):
                # Branch point tags do not contain the version number.
                log.info('.version file has old branch point tag name.')
            else:
                # Use the given version string.
                version = line
        if not version:
            # Unable to lookup version from the .version file, try to extract
            # the version from the source directory name.
            root = os.path.basename(os.path.abspath('.'))
            m = re.match(r'openafs-(.*)', root)
            if m:
                version = m.group(1)
        if not version:
            self.module.fail_json(msg='Unable to determine version.')

        # Determine package version and release from the OpenAFS version.
        m1 = re.match(r'(.*)(pre[0-9]+)', version)              # prerelease
        m2 = re.match(r'(.*)dev', version)                      # development
        m3 = re.match(r'(.*)-([0-9]+)-(g[a-f0-9]+)$', version)  # development
        m4 = re.match(r'(.*)-([a-z]+)([0-9]+)', version)        # custom
        if m1:
            v = m1.group(1)
            r = "0.{0}".format(m1.group(2))
        elif m2:
            v = m2.group(1)
            r = "0.dev"
        elif m3:
            v = m3.group(1)
            r = "{0}.{1}".format(m3.group(2), m3.group(3))
        elif m4:
            v = m4.group(1).replace('-', '')
            r = "1.2.{0}.{1}".format(m4.group(3), m4.group(2))
        else:
            v = version  # standard release
            r = "1"      # increment when repackaging this version
        # '-' are used as delimiters by rpm.
        v = v.replace('-', '_')
        r = r.replace('-', '_')
        package_version = {
            'openafs_version': version,
            'package_version': v,
            'package_release': r,
        }
        return package_version

    def prepare_spec(self, template, version):
        """
        Render the openafs.spec file from the openafs.spec.in template.

        Fill in the application and package version numbers.
        Remove the date extension from the CellServDB source so we can
        use a provided file or one from the tree if not provided.
        """
        v = version
        with open(template, 'r') as fin:
            spec = os.path.join(self.topdir, 'SPECS/openafs.spec')
            with open(spec, 'w') as fout:
                for line in fin.readlines():
                    line = line.replace('@VERSION@', v['openafs_version'])
                    line = line.replace('@PACKAGE_VERSION@', v['openafs_version'])  # noqa: E501
                    line = line.replace('@LINUX_PKGVER@', v['package_version'])
                    line = line.replace('@LINUX_PKGREL@', v['package_release'])
                    line = re.sub(r'^Source([\d]+): .*CellServDB.*',
                                  r'Source\1: CellServDB', line)
                    fout.write(line)

    def list_sources(self, version):
        """
        Extract the source filenames from the spec file.
        """
        sources = []
        spec = os.path.join(self.topdir, 'SPECS', 'openafs.spec')
        with open(spec, 'r') as f:
            for line in f.readlines():
                line = line.rstrip()
                m = re.match(r'Source[\d]+: (.*)', line)
                if m:
                    source = m.group(1).replace(
                        r'%{afsvers}',
                        version['openafs_version'])
                    sources.append(os.path.basename(source))
        return sources

    def list_patches(self, version):
        """
        Extract the patch filenames from the spec file.
        """
        patches = []
        spec = os.path.join(self.topdir, 'SPECS', 'openafs.spec')
        with open(spec, 'r') as f:
            for line in f.readlines():
                line = line.rstrip()
                m = re.match(r'Patch[\d]+: (.*)', line)
                if m:
                    patch = m.group(1).replace(r'%{afsvers}',
                                               version['openafs_version'])
                    patches.append(os.path.basename(patch))
        return patches


class CentOSRpmBuilder(RedHatRpmBuilder):
    platform = 'Linux'
    distribution = 'Centos'


class FedoraRpmBuilder(RedHatRpmBuilder):
    platform = 'Linux'
    distribution = 'Fedora'


class AlmaRpmBuilder(RedHatRpmBuilder):
    platform = 'Linux'
    distribution = 'Almalinux'


class RockyRpmBuilder(RedHatRpmBuilder):
    platform = 'Linux'
    distribution = 'Rocky'


class OracleRpmBuilder(RedHatRpmBuilder):
    platform = 'Linux'
    distribution = 'Oracle'


def main():
    module = AnsibleModule(
        argument_spec=dict(
            build=dict(choices=['all', 'source', 'userspace', 'modules'],
                       default='all'),
            sdist=dict(type='path', required=True),
            spec=dict(type='str', default=None),
            relnotes=dict(type='str', default=None),
            changelog=dict(type='str', default=None),
            csdb=dict(type='path', default=None),
            patchdir=dict(type='path', default=None),
            kernvers=dict(default=None),
            topdir=dict(type='path', default='~/rpmbuild'),
            logdir=dict(type='path', default=None),
            tar=dict(type='path', default=None),
            tar_extra_options=dict(type='str', default=''),
        ),
        supports_check_mode=False,
    )
    log.info('Starting %s', module_name)

    builder = PackageBuilder(module)
    builder.create_workspace()
    builder.build()
    results = builder.results

    module.exit_json(**results)


if __name__ == '__main__':
    main()
