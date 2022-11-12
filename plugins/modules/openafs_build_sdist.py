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
module: openafs_build_sdist

short_description: Create OpenAFS source distribution archives from a git repo.

description:
  - Create OpenAFS source and document source distribution archives from
    a git checkout.

requirements:
  - git
  - autoconfig
  - automake
  - libtools
  - tar
  - gzip
  - bzip2
  - md5sum
  - pod2man

options:
  sdist:
    description:
      - The path on the remote node to write the source distribution files.
      - This path will be created if it does not exist.
    type: path
    required: true

  topdir:
    description: git project directory on the remote node.
    type: path
    default: C(openafs)

  tar:
    description: C(tar) program path
    type: path
    default: detected

  git:
    description: C(git) program path
    type: path
    default: detected

  gzip:
    description: C(gzip) program path
    type: path
    default: detected

  bzip2:
    description: C(bzip2) program path
    type: path
    default: detected

  md5sum:
    description: C(md5sum) program path
    type: path
    default: detected

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- import_role:
    name: openafs_devel

- name: Checkout source.
  git:
    repo: "git://git.openafs.org/openafs.git"
    version: "openafs-stable-1_8_8"
    dest: "openafs"

- name: Make source distribution files.
  openafs_build_sdist:
    topdir: "openafs"
    sdist: "openafs/packages"
'''

RETURN = r'''
version:
  description: OpenAFS version
  returned: always
  type: dict

files:
  description: The list of sdist files created on the remote node.
  returned: always
  type: list
'''

import glob                    # noqa: E402
import os                      # noqa: E402
import platform                # noqa: E402
import re                      # noqa: E402
import shutil                  # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import Logger  # noqa: E402, E501
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import chdir  # noqa: E402, E501
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common import tmpdir  # noqa: E402, E501

module_name = os.path.basename(__file__).replace('.py', '')
log = Logger(module_name)

COMPRESSIONS = [
    # suffix, command
    ('gz',  'gzip'),
    ('bz2', 'bzip2'),
]


def get_platform_subclass(cls):
    for subcls in cls.__subclasses__():
        if platform.system() == subcls.platform:
            return subcls
    return cls


class SourceDistBuilder(object):
    """
    Create OpenAFS source distribution tar files from a git checkout.
    """
    def __new__(cls, module):
        new_cls = get_platform_subclass(SourceDistBuilder)
        return super(cls, new_cls).__new__(new_cls)

    def __init__(self, module):
        self.module = module
        self.results = dict(files=[], commands=[])
        # paths
        self.sdist = self.get_path('sdist')
        self.topdir = self.get_path('topdir')
        # required bin paths
        self.git = self.get_bin_path('git', required=True)
        self.tar = self.get_bin_path('tar', required=True)
        # add available compression programs
        self.compressors = []
        for suffix, command in COMPRESSIONS:
            path = self.get_bin_path(command)
            if path:
                self.compressors.append(Compressor(self, suffix, path))

    def build(self):
        """
        Create OpenAFS source distribution files.
        """
        sdist = self.sdist
        topdir = self.topdir
        git = self.git
        tar = self.tar

        # Create output directory if not present.
        if not os.path.exists(sdist):
            os.makedirs(sdist)

        # Get the version and change log.
        with chdir(topdir):
            version = self.extract_version_string()
            changelog = '%(sdist)s/ChangeLog' % locals()
            self.shell('%(git)s log >%(changelog)s' % locals())
            self.results['files'].append(changelog)

        # Make source archives.
        with tmpdir():
            # Extract source tree into temp dir.
            self.shell('(cd %(topdir)s &&'
                       ' %(git)s archive'
                       '  --format=tar'
                       '  --prefix=openafs-%(version)s/  HEAD) |'
                       ' %(tar)s xf -' % locals())

            # Generate configure, makefiles, and documents in temp dir.
            with chdir('openafs-%(version)s' % locals()):
                with open('.version', 'w') as f:
                    f.write(version + '\n')
                self.shell('./regen.sh')

            # Create documentation and source archives.
            self.shell('%(tar)s cf'
                       ' openafs-%(version)s-doc.tar'
                       ' openafs-%(version)s/doc' % locals())
            shutil.rmtree('openafs-%(version)s/doc' % locals())
            self.shell('%(tar)s cf '
                       ' openafs-%(version)s-src.tar'
                       ' openafs-%(version)s' % locals())

            # Create compressed archives in destination directory.
            for archive in glob.glob('*.tar'):
                for c in self.compressors:
                    c.compress(archive, sdist)

        self.results['changed'] = True

    def shell(self, command):
        log.info('Running: %s', command)
        rc, out, err = self.module.run_command(
            command, check_rc=True, use_unsafe_shell=True)
        self.results['commands'].append(command)
        return out

    def get_path(self, name):
        """
        Expand optional path to absolute path.
        """
        path = self.module.params[name]
        if path:
            path = os.path.abspath(os.path.expanduser(path))
        return path

    def get_bin_path(self, name, required=False):
        """
        Lookup a binary path.
        """
        bin_path = self.module.params.get(name, None)
        if not bin_path:
            bin_name = self.get_bin_name(name)
            bin_path = self.module.get_bin_path(bin_name, required)
        return bin_path

    def get_bin_name(self, name):
        """
        Lookup a binary name from the parameter name.  Subclasses may
        override to provide platform specific program names.
        """
        return name

    def extract_version_string(self):
        """
        Find the OpenAFS version string from the .version file
        or the output of 'git describe'.
        """
        if os.path.exists('.version'):
            with open('.version') as f:
                output = f.read().rstrip()
            if output.startswith('openafs-'):
                version = re.sub('openafs-[^-]*-', '', output).replace('_', '.')     # noqa: E501
            elif output.startswith('BP-'):
                version = re.sub('BP-openafs-[^-]*-', '', output).replace('_', '.')  # noqa: E501
            else:
                version = output  # Use the given version string.
        else:
            git = self.get_bin_path('git')
            cmd = ' '.join([git, 'describe', '--abbrev=4', 'HEAD'])
            output = self.shell(cmd).rstrip()
            version = re.sub(r'^openafs-[^-]*-', '', output).replace('_', '.')
        log.info('version is %s' % version)
        self.results['version'] = version
        return version


class Compressor(object):

    def __init__(self, builder, suffix, command):
        self.builder = builder
        self.suffix = suffix
        self.command = command
        self.md5sum = builder.get_bin_path('md5sum')

    def compress(self, filename, destdir):
        """
        Create a compressed archive and also create an md5 checksum file
        if the md5sum program is available.
        """
        builder = self.builder
        suffix = self.suffix
        command = self.command

        output = '%(destdir)s/%(filename)s.%(suffix)s' % locals()
        builder.shell('%(command)s < %(filename)s > %(output)s' % locals())
        builder.results['files'].append(output)

        md5sum = self.md5sum
        if md5sum:
            output_md5 = '%(output)s.md5' % locals()
            builder.shell('%(md5sum)s %(output)s > %(output_md5)s' % locals())
            builder.results['files'].append(output_md5)


class SolarisSourceDistBuilder(SourceDistBuilder):
    platform = 'SunOS'

    def get_bin_name(self, name):
        # Use GNU tar on Solaris.
        if name == 'tar':
            return 'gtar'
        else:
            return name


def main():
    module = AnsibleModule(
        argument_spec=dict(
            sdist=dict(type='path', required=True),
            topdir=dict(type='path', default='openafs'),
            # bin paths
            git=dict(type='path', default=None),
            tar=dict(type='path', default=None),
            gzip=dict(type='path', default=None),
            bzip2=dict(type='path', default=None),
            md5sum=dict(type='path', default=None),
        ),
        supports_check_mode=False,
    )
    log.info('Starting %s', module_name)

    builder = SourceDistBuilder(module)
    builder.build()
    module.exit_json(**builder.results)


if __name__ == '__main__':
    main()
