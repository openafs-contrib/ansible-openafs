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
module: openafs_build

short_description: Build OpenAFS binaries from source

description:
  - Build OpenAFS server and client binaries from source code by running
    C(regen.sh), C(configure), and C(make). The source code must be already
    present in the I(srcdir) directory.

  - The M(openafs_build) module will run the OpenAFS C(regen.sh) command to
    generate the C(configure) script when the C(configure) script is not
    already present in the I(srcdir).

  - Unless the I(configure_options) option is specified, the configure command
    line arguments are determined automatically, based on the platform and
    M(openafs_build) options.

  - The C(make) program is run to build the binaries. Unless the I(target)
    options is specified, the make target is determined automatically.

  - A complete set of build log files are written on the I(logdir) directory
    on the host for build troubleshooting.

  - Out-of-tree builds are supported by specifying a build directory with the
    I(builddir) option.

  - C(git clean) is run in the I(srcdir) when I(clean) is true and a
    C(.git) directory is found in the C(srcdir).  When I(clean) is true
    but a C(.git) directory is not found, then C(make clean) is run to remove
    artifacts from a previous build.  When I(clean) is true and an out-of-tree
    build is being done, all of the files and directories are removed from the
    I(builddir).

  - An installation file tree is created in the I(destdir) directory when the
    I(target) starts with C(install) or C(dest). The files in I(destdir) may
    be installed with the M(openafs_install_bdist) module.

  - See the C(openafs_devel) role for tasks to install required build tools
    and libraries on various platforms.

requirements:
  - tools and libraries required to build OpenAFS

options:
  srcdir:
    description:
      - Source files must have been previously checkout or copied to this
        path.
    required: true
    type: path

  builddir:
    description:
      - The path for out-of-tree builds.
    default: <srcdir>
    type: path

  logdir:
    description:
      - The path to store build log files.
      - The logdir may be a subdirectory of the C(srcdir).
      - The logdir may not be a subdirectory of the C(builddir) when doing
        an out-of-tree build.
    type: path
    default: <srcdir>/.ansible

  destdir:
    description:
      - The destination directory for C(install) and C(dest) targets and
        variants.
      - The tree staged in this directory may be installed with the
        M(openafs_install_bdist) module.
    default: <srcdir>/packages/dest
    type: path

  clean:
    description:
      - Run C(git clean) in the I(srcdir) when it contains a C(.git)
        directory, otherwise run C(make clean).
      - Remove the I(builddir) when using an out of tree build, that is
        the I(builddir) is different than the I(srcdir).
      - A I(clean) build should be done to force a complete rebuild.
      - The I(clean) option will remove any new files you added manually
        on the remote node and did not commit when the I(srcdir) is
        a git repository.
    type: bool
    default: false

  make:
    description:
      - The C(make) program to be executed.
    type: path
    default: detect

  jobs:
    description:
      - Number of parallel make processes.
      - Set this to 0 to disable parallel make.
    default: the number of CPUs on the system
    type: int

  build_manpages:
    description: Generate the man pages.
    default: true
    type: bool

  build_userspace:
    description: Build userspace programs and libraries.
    default: true
    type: bool

  build_module:
    description: Build the OpenAFS kernel module.
    default: true
    type: bool

  build_terminal_programs:
    description: Build curses-based terminal programs.
    default: true
    type: bool

  build_bindings:
    description: Build program language bindings with swig.
    default: true
    type: bool

  build_fuse_client:
    description: Build fuse client.
    default: true
    type: bool

  with_version:
    description:
      - Version string to embed in program files.
      - The I(version) will be written to the C(.version) file, overwritting
        the current contents, if any.
    type: str

  with_transarc_paths:
    description: Build binaries which use the legacy Transarc-style paths.
    default: false
    type: bool

  with_debug_symbols:
    description: Include debug symbols and disable optimizations.
    default: true
    type: bool

  with_rxgk:
    description: Include rxgk support.
    default: false
    type: bool

  configure_options:
    description:
      - The explicit C(configure) command arguments. When present, this option
        overrides the C(build_*) and C(with_*) options.
      - May be specified as a string, list of strings, or a dictionary.
      - When specified as a dictionary, the values of the keys
        C(enabled), C(disabled), C(with), and C(without) may be lists.
    type: raw

  configure_environment:
    description:
      - Extra environment variables to be set when running C(configure).
    type: dict

  target:
    description:
      - The make target to be run.
      - The make target will be determined automatically when this option is
        omitted.
    type: str
    default: detect

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: Build OpenAFS from source
  openafs_contrib.openafs.openafs_build:
    srcdir: ~/src/openafs

- name: Build OpenAFS binaries for the current system.
  openafs_contrib.openafs.openafs_build:
    srcdir: ~/src/openafs
    clean: yes

- name: Build OpenAFS legacy distribution
  openafs_contrib.openafs.openafs_build:
    srcdir: ~/src/openafs
    clean: yes
    with_transarc_paths: yes

- name: Build OpenAFS server binaries with custom install paths.
  openafs_contrib.openafs.openafs_build:
    srcdir: ~/src/openafs
    clean: yes
    target: install_nolibafs
    destdir: packages/dest
    configure_options:
      prefix: /usr
      bindir: /usr/bin
      libdir: /usr/lib64
      sbindir: /usr/sbin
      disable:
        - strip_binaries
        - kernel_module
      enable:
        - debug
        - redhat_buildsys
        - transarc_paths
      with:
        - krb5: /path/to/krb5.lib
      with_linux_kernel_packaging: true
      with_swig: true
'''

RETURN = r'''
srcdir:
  description: Absolute path to the project directory.
  returned: always
  type: string
  sample: /home/tycobb/projects/myproject

builddir:
  description: Absolute path to the build directory
  returned: always
  type: string
  sample: /home/tycobb/projects/myproject

destdir:
  description: Absolute path to the installation files.
  returned: when destdir is specified
  type: string
  sample: /home/tycobb/projects/myproject/packages/dest

logdir:
  description: Absolute path to the log files. May be used for
               M(openafs_install_bdist).
  return: always
  type: string
  sample: /home/tycobb/projects/myproject/.ansible

logfiles:
  description: Log files written for troubleshooting
  returned: always
  type: list
  sample:
    - /tmp/logs/build.log
    - /tmp/logs/make.out
    - /tmp/logs/make.err

kmods:
  description: The list of kernel modules built, if any.
  returned: success
  type: list
  sample:
    - /home/tycobb/projects/myproject/src/libafs/MODLOAD-5.1.0-SP/openafs.ko
'''

import glob        # noqa: E402
import json        # noqa: E402
import os          # noqa: E402
import platform    # noqa: E402
import re          # noqa: E402
import shlex       # noqa: E402
import shutil      # noqa: E402
import subprocess  # noqa: E402

from multiprocessing import cpu_count  # noqa: E402

from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible.module_utils.six import string_types  # noqa: E402

from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common \
    import Logger, chdir, lookup_fact  # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.o2a \
    import options_to_args  # noqa: E402

module_name = os.path.basename(__file__).replace('.py', '')
log = Logger(module_name)

MAKEFILE_DIRS = r"""
include ./src/config/Makefile.config

all:
	@echo afsbosconfigdir=$(afsbosconfigdir)
	@echo afsconfdir=$(afsconfdir)
	@echo afsdbdir=$(afsdbdir)
	@echo afslocaldir=$(afslocaldir)
	@echo afslogsdir=$(afslogsdir)
	@echo viceetcdir=$(viceetcdir)
"""  # noqa: W191,E101


def copy_tree(src, dst):
    """Copy an entire directory tree.

    Creates destination if needed. Clobbers any existing files/symlinks.

    :arg src: directory to copy from. must already exist
    :arg dst: directory to copy to. created if not already present
    :returns: a list of files/symlinks created
    """
    outputs = []
    if not os.path.isdir(src):
        raise ValueError("cannot copy tree '%s': not a directory" % src)
    try:
        names = os.listdir(src)
    except os.error:
        raise ValueError("error listing files in '%s'" % src)
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


def get_platform_subclass(cls):
    for subcls in cls.__subclasses__():
        if platform.system() == subcls.platform:
            return subcls
    raise ValueError('Unknown platform: {0}'.format(platform.system()))


class Builder(object):

    def __new__(cls, module):
        new_cls = get_platform_subclass(Builder)
        return super(cls, new_cls).__new__(new_cls)

    def __init__(self, module):
        self._stage = 'init'
        self.module = module
        self.logdir = None
        self.logfiles = set()
        self.changed = False
        self.srcdir = None
        self.builddir = None
        self.gitdir = None
        self.destdir = None
        self.version = None
        self.make = None
        self.target = None
        self.transarc_paths = None
        self.sysname = None
        self.configure_args = None
        self.make_args = None
        self.kmods = []
        self.install_dirs = {}

        # Verify srcdir exists.
        self.srcdir = os.path.abspath(self.module.params['srcdir'])
        if not os.path.exists(self.srcdir):
            self.fail('srcdir directory not found: %s' % self.srcdir)
        if not os.path.isdir(self.srcdir):
            self.fail('srcdir is not a directory: %s' % self.srcdir)

        # Set builddir paths for out of tree builds.
        self.builddir = self.module.params['builddir']
        if self.builddir:
            self.builddir = self.abspath(self.srcdir, self.builddir)
        else:
            self.builddir = self.srcdir

        # Set build logging path.
        self.logdir = self.module.params['logdir']
        if not self.logdir:
            self.logdir = os.path.join(self.builddir, '.ansible')

        # Is the srcdir a git repo?
        self.gitdir = os.path.abspath(os.path.join(self.srcdir, '.git'))
        if not (os.path.exists(self.gitdir) and os.path.isdir(self.gitdir)):
            self.gitdir = None

        # Do we have git clean --exclude option? (It is not available on
        # very old git versions, notably on it is not available on RHEL6.)
        self.git = self.module.get_bin_path('git')
        self.have_git_clean_exclude = False
        if self.git:
            args = [self.git, 'clean', '-h']
            rc, out, err = self.module.run_command(args)
            if '--exclude' in out:
                self.have_git_clean_exclude = True

        # Find make if not specified.
        self.make = self.module.params['make']
        if not self.make:
            self.make = self.module.get_bin_path('make', required=True)

        # Setup environment variables.
        self.set_environment_variables()

    def build(self):
        """
        Build OpenAFS binaries.
        """
        self.build_clean()
        self.build_version()
        self.build_regen()
        self.build_configure()
        self.build_make()
        self.log('Build completed.')
        results = {
            'changed': self.changed,
            'logdir': self.logdir,
            'logfiles': sorted(list(self.logfiles)),
            'srcdir': self.srcdir,
            'builddir': self.builddir,
            'configure': ' '.join(self.configure_args),
            'make': ' '.join(self.make_args),
            'kmods': self.kmods,
            'install_dirs': self.install_dirs,
        }
        if self.gitdir:
            results['gitdir'] = self.gitdir
        if self.destdir:
            results['destdir'] = self.destdir
        if self.sysname:
            results['sysname'] = self.sysname
        if self.version:
            results['version'] = self.version
        if self.target:
            results['target'] = self.target
        return results

    def build_clean(self):
        """
        Clean intermediates from the previous build.
        """
        if self._stage != 'init':
            raise AssertionError('sequence error: %s' % self._stage)
        self._stage = 'clean'

        clean = self.module.params['clean']
        if not clean:
            return   # Skip clean

        if self.builddir == self.srcdir:
            # In-tree build; do our best to clean intermediates.
            if self.gitdir and self.have_git_clean_exclude:
                self.run('clean', [self.git, 'clean', '-f', '-d', '-x',
                         '--exclude=.ansible'], self.srcdir)
            else:
                makefile = os.path.join(self.srcdir, 'Makefile')
                if os.path.exists(makefile):
                    self.run('clean', [self.make, 'clean'], self.srcdir)
        else:
            # Out-of-tree build.
            if os.path.exists(self.builddir):
                makefile = os.path.join(self.builddir, 'Makefile')
                if os.path.exists(makefile):
                    self.run('clean', [self.make, 'clean'], self.builddir)
                else:
                    if self.builddir == '/':
                        self.fail('Refusing to remove "/" builddir!')
                    self.log('Removing old build directory %s' % self.builddir)
                    shutil.rmtree(self.builddir)
            # Setup build directory. This must be done after running clean!
            if not os.path.isdir(self.builddir):
                self.log('Creating build directory %s' % self.builddir)
                os.makedirs(self.builddir)

    def build_version(self):
        """
        Create the .version file if the with_version parameter was set.
        Run git-version to get the version string.
        """
        if self._stage != 'clean':
            raise AssertionError('sequence error: %s' % self._stage)
        self._stage = 'version'

        # Optionally write a .version file. This will overwrite the current
        # .version file if one was is already present.
        with_version = self.module.params['with_version']
        if with_version:
            version_file = os.path.join(self.srcdir, '.version')
            self.log('Writing version %s to file %s' %
                     (with_version, version_file))
            with open(version_file, 'w') as f:
                f.write(with_version)

        # Report the version string. This is read from the .version file if
        # present, otherwise it is generated from `git describe`.
        git_version = os.path.join(self.srcdir, 'build-tools', 'git-version')
        output = self.shell([git_version, self.srcdir])
        self.version = output.rstrip()

    def build_regen(self):
        """
        Run regen.sh to generate configure.
        """
        if self._stage != 'version':
            raise AssertionError('sequence error: %s' % self._stage)
        self._stage = 'regen'

        if os.path.exists(os.path.join(self.srcdir, 'configure')):
            self.log('Skipping regen.sh: configure already exists.')
            return
        regen = [os.path.join(self.srcdir, 'regen.sh')]
        if not self.module.params['build_manpages']:
            regen.append('-q')
        self.run('regen', regen, self.srcdir)

    def build_configure(self):
        """
        Run configure to configure the build tree.
        """
        if self._stage != 'regen':
            raise AssertionError('sequence error: %s' % self._stage)
        self._stage = 'configure'

        options = self.module.params['configure_options']
        if options is None:
            options = self.get_configure_options()

        # Convert structured data to a list of command line arguments.
        if not options:
            args = []
        elif isinstance(options, dict):
            args = options_to_args(options)
        elif isinstance(options, list):
            args = options
        elif isinstance(options, tuple):
            args = list(options)
        elif isinstance(options, string_types):
            args = shlex.split(options)
        else:
            self.fail("Invalid configure options type")

        command = [os.path.join(self.srcdir, 'configure')]
        command.extend(args)
        self.configure_args = command
        self.transarc_paths = '--enable-transarc-paths' in command

        configure_environment = self.module.params['configure_environment']
        self.run('configure', self.configure_args, self.builddir,
                 extra_env=configure_environment)

        # Extract info from the configured build tree.
        self.collect_sysname()
        self.collect_install_dirs()

    def build_make(self):
        """
        Run make to perform the build.
        """
        if self._stage != 'configure':
            raise AssertionError('sequence error: %s' % self._stage)
        self._stage = 'make'

        make = [self.make]
        fakeroot = self.module.params['fakeroot']
        if fakeroot:
            make.insert(0, fakeroot)
        jobs = self.module.params['jobs']
        if jobs > 0:
            make.extend(['-j', '%d' % jobs])
        self.target = self.get_target()
        if self.target:
            make.append(self.target)
        path = self.module.params['destdir']
        if path:
            self.destdir = self.abspath(self.builddir, path)
            if not self.target.startswith('dest'):
                make.append('DESTDIR=%s' % self.destdir)

        self.make_args = make
        self.run('make', make, self.builddir)
        self.changed = True

        # make may silently fail to build a kernel module for the running
        # kernel version (or any version). Let's fail early instead of finding
        # out later when we try to start the cache manager.
        self.kmods = self.collect_kernel_modules(self.builddir)
        self.verify_kernel_module()

        # Transarc style post build tasks.
        if self.transarc_paths:
            self.transarc_post_build()

        # Save configured build paths in a meta-data file.
        build_info = {
            'dirs': self.install_dirs,
            'configure': self.configure_args,
            'make': self.make_args,
        }
        filename = os.path.join(self.destdir, '.build-info.json')
        self.log('Writing %s' % filename)
        with open(filename, 'w') as f:
            f.write(json.dumps(build_info, indent=4))

    def log(self, msg):
        """
        Log a message to the build.log file and the syslog.
        """
        log.info(msg)
        if not os.path.isdir(self.logdir):
            os.makedirs(self.logdir)
            self.changed = True
        build_log = os.path.join(self.logdir, 'build.log')
        with open(build_log, 'a') as f:
            f.write('%s\n' % msg)
        self.logfiles.add(build_log)

    def abspath(self, base, rel):
        """
        Get absolute path name relative to a base directory.
        """
        prev = os.getcwd()
        os.chdir(base)
        path = os.path.abspath(rel)
        os.chdir(prev)
        return path

    def fail(self, msg):
        """
        Log and error message and abort.
        """
        log.error(msg)
        self.module.fail_json(msg=msg)

    def shell(self, args, cwd=None):
        """
        Run a command and return the stdout as a string.
        """
        if cwd:
            msg = '[%s] %s' % (cwd, ' '.join(args))
        else:
            msg = '%s' % ' '.join(args)
        self.log(msg)
        rc, out, err = self.module.run_command(args, check_rc=True, cwd=cwd)
        if err:
            log.error(err)
        return out

    def run(self, name, command, cwd, extra_env=None):
        """
        Run a command and write stdout and stderr a tailable file.

        Unlike the standard run_command(), this function pipes the output as
        received to a file that can be followed with tail -f.  This can be
        helpful when troubleshooting builds.
        """
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)

        if not os.path.isdir(self.logdir):
            os.makedirs(self.logdir)
            self.changed = True

        self.log('Running [%s] %s' % (cwd, ' '.join(command)))
        logfile = os.path.join(self.logdir, '%s.log' % name)
        self.logfiles.add(logfile)
        with open(logfile, 'w') as f:
            with chdir(cwd):
                proc = subprocess.Popen(command, env=env, stdout=f.fileno(),
                                        stderr=f.fileno())
                rc = proc.wait()
        if rc != 0:
            self.fail('%s command failed; see "%s".' % (name, logfile))

    def get_configure_options(self):
        """
        Determine configure options based on parameters.
        """
        build_userspace = self.module.params['build_userspace']
        build_module = self.module.params['build_module']
        build_terminal_programs = self.module.params['build_terminal_programs']
        build_bindings = self.module.params['build_bindings']
        build_fuse_client = self.module.params['build_fuse_client']
        with_transarc_paths = self.module.params['with_transarc_paths']
        with_debug_symbols = self.module.params['with_debug_symbols']
        with_rxgk = self.module.params['with_rxgk']

        if not (build_userspace or build_module):
            self.fail("specify build_userspace and/or build_module")

        options = {'enable': [], 'disable': [], 'with': [], 'without': []}
        if build_module:
            options['enable'].append('kernel-module')
            self.kernel_module_configure_options(options)
        else:
            options['disable'].append('kernel-module')
        if not build_terminal_programs:
            options['disable'].append('gtx')
        if not build_bindings:
            options['without'].append('swig')
        if not build_fuse_client:
            options['disable'].append('fuse-client')
        if with_debug_symbols:
            options['enable'].append('debug')
            options['disable'].extend(['optimize', 'strip-binaries'])
            if build_module:
                options['enable'].append('debug-kernel')
                options['disable'].append('optimize-kernel')
        if with_transarc_paths:
            options['enable'].append('transarc-paths')
        if with_rxgk:
            options['enable'].append('rxgk')
        return options

    def get_target(self):
        """
        Determine the make target name.

        Determine the top level make target for the build. First, use the
        explicit target if given. Next interpret the explicit configure options
        if given. Finally, interpret the build options.

        This function may only be used after the configure step, since we may
        check the configure command line arguments to determine the target.

        Historically, the make target depends on the directory path mode
        specified by the configure options.  `make dest` target is used to
        build transarc style paths and `make install` is used to build modern
        style paths (although, hybrid styles are possible).  To make it easier
        to support both modes, by default, just figure out the make target
        based on the configure options.  The caller my specify a explicit
        target (even an empty one) to override.
        """
        target = self.module.params['target']
        if target is not None:
            return target

        if self.configure_args is None:
            raise AssertionError('sequence error: configure_args not found')

        build_userspace = self.module.params['build_userspace']
        build_module = self.module.params['build_module']
        if self.transarc_paths:
            target = 'dest'
        else:
            target = 'install'

        if '--disable-kernel-module' in self.configure_args:
            target += '_nolibafs'
        elif build_module and not build_userspace:
            target += '_only_libafs'

        return target

    def collect_sysname(self):
        """
        Get the afs sysname from the results of configure.
        """
        config_log = os.path.join(self.builddir, 'config.log')
        try:
            with open(config_log) as f:
                for line in f.readlines():
                    m = re.match(r"AFS_SYSNAME='([^']*)'", line)
                    if m:
                        self.sysname = m.group(1)
                        return
        except Exception:
            pass

    def collect_install_dirs(self):
        """
        Extract the configured installation directories.

        Create and run a dummy make file to export the configured symbols.
        """
        makefile_dirs = os.path.join(self.logdir, 'Makefile.dirs')
        with open(makefile_dirs, 'w') as f:
            f.write(MAKEFILE_DIRS)
        output = self.shell([self.make, '-f', makefile_dirs],
                            cwd=self.builddir)
        self.log('Makefile.dirs output')
        for line in output.splitlines():
            line = line.rstrip()
            self.log(line)
            if '=' not in line:
                continue
            name, value = line.split('=', 1)
            value = value.rstrip('/')
            if value.startswith('//'):
                value = value.replace('/', '', 1)
            self.install_dirs[name] = value

    def transarc_post_build(self):
        """
        Post build tasks for transarc-style builds.
        """
        #
        # Copy the transarc-style distribution tree into a DESTDIR file tree
        # for installation.
        #
        if self.target in ('dest', 'dest_nolibafs', 'dest_only_libafs'):
            self.log('Copying transarc-style distribution files to %s' %
                     self.destdir)
            sysname = self.sysname
            if not sysname:
                self.fail('Unable to get destdir; sysname not found.')
            dest = os.path.join(self.builddir, sysname, 'dest')
            if not os.path.isdir(dest):
                self.fail('Missing dest directory: %s' % dest)
            copy_tree(dest, self.destdir)
            self.changed = True

        #
        # Copy security key utilities to a standard location.
        #
        if self.target in ('install', 'install_nolibafs', 'dest',
                           'dest_nolibafs'):
            self.log('Copying security key utilities to %s' % self.destdir)
            for p in ('asetkey', 'akeyconvert'):
                src = os.path.join(self.builddir, 'src', 'aklog', p)
                dst = os.path.join(self.destdir, 'usr', 'sbin')
                if os.path.isfile(src):
                    if not os.path.isdir(dst):
                        os.makedirs(dst)
                    log.debug('shutil.copy2("%s", "%s")' % (src, dst))
                    shutil.copy2(src, dst)
                    self.changed = True


class LinuxBuilder(Builder):
    platform = 'Linux'

    def set_environment_variables(self):
        """
        Set environment variables needed when building on Linux.
        """
        pass

    def kernel_module_configure_options(self, options):
        options['with'].append('linux-kernel-packaging')

    def collect_kernel_modules(self, builddir):
        """
        Search for built kernel modules on Linux.
        """
        pattern = os.path.join(builddir, 'src/libafs/MODLOAD-*/*afs.ko')
        kmods = glob.glob(pattern)
        return kmods

    def verify_kernel_module(self):
        """
        Verify we built a kernel module that matches the running kernel
        version.
        """

        if 'nolibafs' in self.target:
            self.log('Skipping check for kernel module: target is %s' %
                     self.target)
            return

        if '--disable-kernel-module' in self.configure_args:
            self.log('Skipping check for kernel module: configure is %s' %
                     self.configure_args)
            return

        self.log('Checking for linux kernel module for linux '
                 'kernel version %s.' % platform.release())
        modloads = []
        for kmod in self.kmods:
            pattern = \
                r'/MODLOAD-%s-[A-Z]*/(lib|open)afs\.ko$' % platform.release()
            m = re.search(pattern, kmod)
            if m:
                modloads.append(kmod)
        self.log('Modules found: %s' % ' '.join(modloads))
        if not modloads:
            self.fail('Loadable kernel module not found for linux '
                      'kernel version %s' % platform.release())


class SolarisBuilder(Builder):
    platform = 'SunOS'

    def set_environment_variables(self):
        """
        Set environment variables needed when building on Solaris.
        """
        solariscc = lookup_fact('solariscc')
        if solariscc:
            os.environ['SOLARISCC'] = solariscc
        os.environ['UT_NO_USAGE_TRACKING'] = '1'
        os.environ['SUNW_NO_UPDATE_NOTIFY'] = '1'

    def kernel_module_configure_options(self, options):
        pass

    def collect_kernel_modules(self, builddir):
        """
        Search for built kernel modules on Solaris.
        """
        kmods = []
        for name in ('libafs.o', 'libafs.nonfs.o'):
            kmod = os.path.join(builddir, 'src/libafs/MODLOAD64', name)
            if os.path.exists(kmod):
                kmods.append(kmod)
        return kmods

    def verify_kernel_module(self):
        """
        Verify we built a kernel module.
        """
        if 'nolibafs' in self.target:
            self.log('Skipping check for kernel module: target is %s' %
                     self.target)
            return

        if '--disable-kernel-module' in self.configure_args:
            self.log('Skipping check for kernel module: configure is %s' %
                     self.configure_args)
            return

        self.log('Checking for solaris kernel modules.')
        if not self.kmods:
            self.fail('Kernel module not found.')


class FreeBSDBuilder(Builder):
    platform = 'FreeBSD'

    def set_environment_variables(self):
        pass

    def kernel_module_configure_options(self, options):
        pass

    def collect_kernel_modules(self, builddir):
        """
        Search for built kernel module on FreeBSD.
        """
        pattern = os.path.join(builddir, 'src/libafs/MODLOAD/libafs.ko')
        kmods = glob.glob(pattern)
        return kmods

    def verify_kernel_module(self):
        pass


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str'),  # Not used.
            srcdir=dict(type='path', required=True, aliases=['projectdir']),
            builddir=dict(type='path'),
            logdir=dict(type='path'),
            destdir=dict(type='path'),

            # Procesing options
            fakeroot=dict(type='path'),
            make=dict(type='path'),
            clean=dict(type='bool', default=False),
            jobs=dict(type='int', fallback=(cpu_count, [])),

            # Build options.
            with_version=dict(type='str', default=None, aliases=['version']),
            with_transarc_paths=dict(type='bool', default=False,
                                     aliases=['transarc_paths']),
            with_debug_symbols=dict(type='bool', default=True),
            with_rxgk=dict(type='bool', defaults=False),

            # What to build.
            build_manpages=dict(type='bool', default=True,
                                aliases=['manpages']),
            build_userspace=dict(type='bool', default=True),
            build_module=dict(type='bool', default=True),
            build_terminal_programs=dict(type='bool', default=True),
            build_fuse_client=dict(type='bool', default=True),
            build_bindings=dict(type='bool', default=True),

            # Explicit configure and target options.
            configure_options=dict(type='raw', default=None),
            configure_environment=dict(type='dict', default=None),
            target=dict(type='str', default=None),
        ),
        supports_check_mode=False,
    )

    builder = Builder(module)
    results = builder.build()

    module.exit_json(**results)


if __name__ == '__main__':
    main()
