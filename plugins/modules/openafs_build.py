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
module: openafs_build

short_description: Build OpenAFS binaries from source

description:
  - Build OpenAFS server and client binaries from source code.

  - The source code must be already present in the I(projectdir) directory on
    the host.

  - The M(openafs_build) module will run the OpenAFS C(regen.sh) command to
    generate the C(configure) script, then run C(configure) with the given
    I(configure_options), and then run C(make) with the given I(target).  If a
    I(target) is not specified, one will be determined based on the given
    I(configure_options). The C(regen.sh) execution is skipped when the
    C(configure) file already exists.

  - A complete set of build log files are written on the I(logdir) directory on
    the host for build troubleshooting.

  - Out-of-tree builds are supported by specifying a build directory with the
    I(builddir) option.

  - At the start of the build, when I(clean) is true and a C(.git) directory is
    found in the C(projectdir), C(git clean) is run in the I(projectdir)
    directory to remove artifacts from a previous build. When I(clean) is true
    and a C(.git) directory is not found, then C(make clean) is run to remove
    artifacts from a previous build.  When I(clean) is true and an out-of-tree
    build is being done, all of the files and directories are removed from the
    I(builddir).

  - A check for a loadable kernel module is done after the build completes when
    the I(state) is C(built-module).  Be sure the I(target) and
    I(configure_options) are set to build a kernel module when using the
    C(buildt-module) state.

  - An installation file tree is created in the I(destdir) directory when the
    I(target) starts with C(install) or C(dest). The files in I(destdir) may be
    installed with the M(openafs_install_bdist) module.

  - See the C(openafs_devel) role for tasks to install required build tools and
    libraries on various platforms.

requirements:
  - tools and libraries required to build OpenAFS

options:
  state:
    description:
      - C(built) Run regen.sh, configure, make
      - C(built-module) After build is complete, also verify a kernel module
        was built for the current running kernel version. Be sure the target
        and configure options are set to build a client when this state is in
        use.
    type: str
    default: complete

  projectdir:
    description:
      - The project directory.
      - Source files must have been previously checkout or copied to this path.
    required: true
    type: path

  builddir:
    description:
      - The path for out-of-tree builds.
    default: <projectdir>
    type: path

  logdir:
    description:
      - The path to store build log files.
      - The logdir may be a subdirectory of the C(projectdir).
      - The logdir may not be a subdirectory of the C(builddir) when doing
        an out-of-tree build.
    type: path
    default: <projectdir>/.ansible

  clean:
    description:
      - Run C(git clean) in the I(projectdir) when it contains a C(.git)
        directory, otherwise run C(make clean).
      - Remove the I(builddir) when using an out of tree build, that is
        the I(builddir) is different than the I(projectdir).
      - A I(clean) build should be done to force a complete rebuild.
      - The I(clean) option will remove any new files you added manually
        on the remote node and did not commit when the I(projectdir) is
        a git repository.
    type: bool
    default: false

  version:
    description:
      - Version string to embed in built files.
      - The I(version) will be written to the C(.version) file, overwritting
        the current contents, if any.
    type: str

  make:
    description:
      - The C(make) program to be executed.
    type: path
    default: detect

  target:
    description:
      - The make target to be run. If not specified, the target will
        be determined based on the I(configure_options).
      - The target is set to C(dest) if the I(configure_options) contain
        C(--enable-transarc-paths), or set to C(install) otherwise.
      - The target is set to C(dest_nolibafs) or C(install_nolibafs)
        if the I(configure_options) contains C(--disable-kernel-module).
    type: str
    default: detect based on I(configure_options)

  jobs:
    description:
      - Number of parallel make processes.
      - Set this to 0 to disable parallel make.
    default: the number of CPUs on the system
    type: int

  manpages:
    description:
      - Generate the man-pages from POD files when running C(regen).
    default: true
    type: bool

  destdir:
    description:
      - The destination directory for C(install) and C(dest) targets and
        variants.
      - The tree staged in this directory may be installed with the
        M(openafs_install_bdist) module.
    default: <projectdir>/packages/dest
    type: path

  configure_options:
    description:
      - The C(configure) options as a string, list of strings, or a dictionary
    type: raw

  transarc_paths:
    description:
      - Build binaries which use the legacy Transarc-style paths
      - When True, this option adds the C(--enable-transarc-paths) to the
        I(configure_options).
      - This option has no effect when the C(--enable-transarc-paths) argument
        is already present in the I(configure_options)
    type: bool

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: Build OpenAFS from source
  openafs_contrib.openafs.openafs_build:
    projectdir: ~/src/openafs

- name: Build OpenAFS server binaries for RHEL
  openafs_contrib.openafs.openafs_build:
    state: built
    projectdir: ~/src/openafs
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
  register: build_results
  when: ansible_os_family == 'RedHat'

- name: Build OpenAFS legacy distribution
  openafs_contrib.openafs.openafs_build:
    state: built-module
    projectdir: ~/src/openafs
    clean: yes
    configure_options:
      enable:
        - debug
        - transarc_paths
        - kernel_module
      with:
        - linux_kernel_packaging

- name: Example configure options specified as a string
  openafs_contrib.openafs.openafs_build:
    state: built-module
    projectdir: ~/src/openafs
    configure_options: "--enable-debug --enable-transarc-paths"
'''

RETURN = r'''
msg:
  description: Informational message.
  returned: always
  type: string
  sample: Build completed

projectdir:
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

import contextlib  # noqa: E402
import glob       # noqa: E402
import logging    # noqa: E402
import os         # noqa: E402
import platform   # noqa: E402
import pprint     # noqa: E402
import re         # noqa: E402
import shlex      # noqa: E402
import shutil     # noqa: E402
import subprocess  # noqa: E402
import json       # noqa: E402
from multiprocessing import cpu_count  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402
from ansible.module_utils.six import string_types  # noqa: E402

log = logging.getLogger('openafs_build')
module = None

MAKEFILE_PATHS = r"""
include ./src/config/Makefile.config
short:
	@echo afsbosconfigdir=$(afsbosconfigdir)
	@echo afsconfdir=$(afsconfdir)
	@echo afsdbdir=$(afsdbdir)
	@echo afslocaldir=$(afslocaldir)
	@echo afslogsdir=$(afslogsdir)
	@echo viceetcdir=$(viceetcdir)

long:
	@echo afsbackupdir=$(afsbackupdir)
	@echo afsbosconfigdir=$(afsbosconfigdir)
	@echo afsconfdir=$(afsconfdir)
	@echo afsdbdir=$(afsdbdir)
	@echo afslocaldir=$(afslocaldir)
	@echo afslogsdir=$(afslogsdir)
	@echo afssrvbindir=$(afssrvbindir)
	@echo afskerneldir=$(afskerneldir)
	@echo afssrvlibexecdir=$(afssrvlibexecdir)
	@echo afssrvsbindir=$(afssrvsbindir)
	@echo afsdatadir=$(afsdatadir)
	@echo bindir=$(bindir)
	@echo exec_prefix=$(exec_prefix)
	@echo datarootdir=$(datarootdir)
	@echo datadir=$(datadir)
	@echo includedir=$(includedir)
	@echo libdir=$(libdir)
	@echo libexecdir=$(libexecdir)
	@echo localstatedir=$(localstatedir)
	@echo mandir=$(mandir)
	@echo prefix=$(prefix)
	@echo sbindir=$(sbindir)
	@echo sysconfdir=$(sysconfdir)
	@echo viceetcdir=$(viceetcdir)
"""  # noqa: W191,E101


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


def abspath(base, rel):
    """ Get absolute path name relative to a base directory. """
    prev = os.getcwd()
    os.chdir(base)
    path = os.path.abspath(rel)
    os.chdir(prev)
    return path


def tail(s, n=256):
    """ Get the last n chars of a string. """
    if len(s) <= n:
        return s
    else:
        return s[-n:]


@contextlib.contextmanager
def chdir(path):
    prev = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)


def run_command(name, command, cwd, logdir, results):
    """Run a command and log the stdout and stderr to a file.

    :arg command: command argument list
    :arg cwd: current directory to run the command
    :arg logdir: where to place stdout and stderr logs
    :arg results: the module results dictionary
    """
    logfile = os.path.join(logdir, '%s.log' % name)
    results['logfiles'].append(logfile)
    with open(logfile, 'w') as f:
        with chdir(cwd):
            log.info('[%s] %s' % (cwd, ' '.join(command)))
            proc = subprocess.Popen(command, stdout=f.fileno(), stderr=f.fileno())
            rc = proc.wait()
    if rc != 0:
        log.error('%s failed; rc=%d' % (name, rc))
        module.fail_json(
            msg='%s command failed. See log file "%s".' % (name, logfile),
        )


def _od2a(options, prefix=None):
    args = []
    for k, v in options.items():
        if prefix:
            args.append(_o2a(k, v, prefix=prefix))
        elif k in ('enable', 'disable', 'with', 'without'):
            if isinstance(v, dict):
                args.extend(_od2a(v, prefix=k))
            elif isinstance(v, list):
                args.extend(_ol2a(v, prefix=k))
            else:
                args.append(_o2a(v, prefix=k))
        else:
            args.append(_o2a(k, v))
    return args


def _ol2a(options, prefix=None):
    args = []
    for v in options:
        if isinstance(v, dict):
            args.extend(_od2a(v, prefix=prefix))
        else:
            args.append(_o2a(v, prefix=prefix))
    return args


def _o2a(name, value=None, prefix=None):
    if prefix:
        name = '%s-%s' % (prefix, name)
    if not value:
        arg = '--%s' % name
    elif isinstance(value, (dict, list)):
        raise ValueError('Unexpected dict or list: %s' % name)
    elif value is True:
        arg = '--%s' % (name)
    else:
        arg = '--%s=%s' % (name, value)
    return arg


def options_to_args(options):
    """ Convert option dictionary to a list of command line arguments.

    Special handling for the enable, disable, with, without keys. Treat
    these keys (at just the top-level) as a tree of options so we can make
    the yaml look nicer.
    """
    args = []
    if isinstance(options, dict):
        args.extend(_od2a(options))
    elif isinstance(options, list):
        args.extend(_ol2a(options))
    else:
        args.append(_o2a(options))
    return args


def configured_sysname(builddir):
    """ Get the afs sysname from the results of configure.

    :arg builddir: the location of the configure log
    :returns: the afs sysname value or None if not found
    """
    config_log = os.path.join(builddir, 'config.log')
    try:
        with open(config_log) as f:
            for line in f.readlines():
                m = re.match(r"AFS_SYSNAME='([^']*)'", line)
                if m:
                    return m.group(1)
    except Exception:
        pass
    return ''


def main():
    results = dict(
        changed=False,
        msg='',
        projectdir=None,
        logfiles=[],
        sysname='',
        kmods=[],
        install_dirs={},
    )
    global module
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=['built', 'built-module'], default='built'),
            projectdir=dict(type='path', required=True),
            builddir=dict(type='path'),
            logdir=dict(type='path'),
            clean=dict(type='bool', default=False),
            version=dict(type='str'),
            make=dict(type='path'),
            target=dict(type='str', default=None),
            jobs=dict(type='int', default=cpu_count()),
            manpages=dict(type='bool', default=True),
            destdir=dict(type='path'),
            configure_options=dict(type='raw', default=''),
            transarc_paths=dict(type='bool', default=False)
        ),
        supports_check_mode=False,
    )

    state = module.params['state']
    projectdir = module.params['projectdir']
    builddir = module.params['builddir']
    logdir = module.params['logdir']
    clean = module.params['clean']
    version = module.params['version']
    make = module.params['make']
    target = module.params['target']
    jobs = module.params['jobs']
    manpages = module.params['manpages']
    destdir = module.params['destdir']
    configure_options = module.params['configure_options']
    transarc_paths = module.params['transarc_paths']

    if not (os.path.exists(projectdir) and os.path.isdir(projectdir)):
        module.fail_json(msg='projectdir directory not found: %s' % projectdir)
    results['projectdir'] = os.path.abspath(projectdir)

    # Find `make` if not specified.
    if not make:
        make = module.get_bin_path('make', required=True)

    #
    # Setup logging
    #
    if not logdir:
        logdir = os.path.join(projectdir, '.ansible')
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
        results['changed'] = True
    results['logdir'] = logdir
    build_log = os.path.join(logdir, 'build.log')
    logging.basicConfig(
        level=logging.INFO,
        filename=build_log,
        format='%(asctime)s %(levelname)s %(message)s',
    )
    results['logfiles'].append(build_log)

    log.info('Starting build')
    log.info('Parameters: %s', pprint.pformat(module.params))

    #
    # Setup paths.
    #
    if builddir:
        builddir = abspath(projectdir, builddir)
    else:
        builddir = projectdir
    results['builddir'] = builddir
    log.debug("builddir='%s'", builddir)

    gitdir = os.path.abspath(os.path.join(projectdir, '.git'))
    if not (os.path.exists(gitdir) and os.path.isdir(gitdir)):
        gitdir = None
    log.debug("gitdir='%s'.", gitdir)

    #
    # Clean previous build.
    #
    if clean and gitdir:
        clean_command = [
            module.get_bin_path('git', required=True),
            'clean', '-f', '-d', '-x', '--exclude=.ansible',
        ]
        log.info('Running git clean.')
        run_command('clean', clean_command, projectdir, logdir, results)

    #
    # Clean out of tree build files.
    #
    if clean and builddir != projectdir and os.path.exists(builddir):
        if builddir == '/':
            module.fail_json(msg='Refusing to remove "/" builddir!')
        log.info('Removing old build directory %s' % builddir)
        shutil.rmtree(builddir)

    #
    # Setup build directory. (This must be done after the clean step.)
    #
    if not os.path.isdir(builddir):
        log.info('Creating build directory %s' % builddir)
        os.makedirs(builddir)
    if destdir:
        destdir = abspath(builddir, destdir)  # makefiles need the full path
        results['destdir'] = destdir

    #
    # Set the version string, if supplied.
    #
    if version:
        version_file = os.path.join(projectdir, '.version')
        log.info('Writing version %s to file %s' % (version, version_file))
        with open(version_file, 'w') as f:
            f.write(version)

    #
    # Report the version string. This is read from the .version file if
    # present, otherwise it is generated from `git describe`.
    #
    cwd = os.path.join(builddir, 'build-tools')
    rc, out, err = module.run_command(['./git-version', builddir], cwd=cwd)
    if rc != 0:
        log.info('Unable to determine version string.')
    else:
        results['version'] = out

    #
    # Run autoconf.
    #
    if os.path.exists(os.path.join(projectdir, 'configure')):
        log.info('Skipping regen.sh: configure found.')
    else:
        regen_command = [os.path.join(projectdir, 'regen.sh')]
        if not manpages:
            regen_command.append('-q')
        run_command('regen', regen_command, projectdir, logdir, results)

    #
    # Run configure.
    #
    if not configure_options:
        args = []
    elif isinstance(configure_options, dict):
        args = options_to_args(configure_options)
    elif isinstance(configure_options, list):
        args = configure_options
    elif isinstance(configure_options, tuple):
        args = list(configure_options)
    elif isinstance(configure_options, string_types):
        args = shlex.split(configure_options)
    else:
        module.fail_json(msg="Invalid configure_options type.")

    # Optionally add transarc style paths. The configure options
    # take precedence over the transarc_paths parameter.
    if '--enable-transarc-paths' not in args:
        if transarc_paths:
            args.append('--enable-transarc-paths')

    #
    # Historically, the make target depends on the directory path mode
    # specified by the configure options.  The 'dest' target is used to
    # build transarc style paths and make install is used to build modern
    # style paths (although, hybrid styles are possible).  To make it
    # easier to support both modes, by default, just figure out the make
    # target based on the configure options given.  The caller my specify
    # a explicit target (even an empty one) to override this feature.
    #
    if target is None:
        if '--enable-transarc-paths' in args:
            target = 'dest'
        else:
            target = 'install'
        if '--disable-kernel-module' in args:
            target += '_nolibafs'
        log.info('Using target "%s"', target)
    results['target'] = target

    configure_command = [os.path.join(projectdir, 'configure')]
    configure_command.extend(args)
    run_command('configure', configure_command, builddir, logdir, results)
    results['sysname'] = configured_sysname(builddir)
    log.info("configured sysname is '%s'.", results['sysname'])

    #
    # Get installation directories.
    #
    with open(os.path.join(builddir, '.Makefile.dirs'), 'w') as f:
        f.write(MAKEFILE_PATHS)
    rc, out, err = module.run_command([make, '-f', '.Makefile.dirs'],
                                      cwd=builddir)
    if rc != 0:
        module.fail_json(
            msg='Failed to find installation directories: %s' % err)
    for line in out.splitlines():
        line = line.rstrip()
        if '=' in line:
            name, value = line.split('=', 1)
            if value.startswith('//'):
                # Cleanup leading double slashes.
                value = value.replace('//', '/', 1)
            results['install_dirs'][name] = value

    #
    # Run make clean if we did not run git clean.
    #
    if clean and not gitdir:
        make_command = [make, 'clean']
        run_command('make', make_command, builddir, logdir, results)

    #
    # Run make.
    #
    make_command = [make]
    if jobs > 0:
        make_command.extend(['-j', '%d' % jobs])
    if target:
        make_command.append(target)
    if destdir and not target.startswith('dest'):
        make_command.append('DESTDIR=%s' % destdir)
    run_command('make', make_command, builddir, logdir, results)

    #
    # `make` may silently fail to build a kernel module for the running kernel
    # version (or any version). Let's fail early instead of finding out later
    # when we try to start the cache manager.
    #
    kmod_pattern = \
        os.path.join(builddir, 'src', 'libafs', 'MODLOAD-*', '*afs.ko')
    results['kmods'] = glob.glob(kmod_pattern)
    if state == 'built-module':
        log.info('Checking for kernel module for %s.' % platform.release())
        modloads = []
        for kmod in results['kmods']:
            pattern = \
                r'/MODLOAD-%s-[A-Z]*/(lib|open)afs\.ko$' % platform.release()
            m = re.search(pattern, kmod)
            if m:
                modloads.append(kmod)
        log.info('Modules found: %s' % ' '.join(modloads))
        if not modloads:
            results['msg'] = \
                'Loadable kernel module not found for %s' % platform.release()
            log.error(results['msg'])
            module.fail_json(**results)

    #
    # Copy the transarc-style distribution tree into a DESTDIR file tree
    # for installation.
    #
    if destdir and target in ('dest', 'dest_nolibafs', 'dest_only_libafs'):
        log.info('Copying transarc-style distribution files to %s' % destdir)
        sysname = configured_sysname(builddir)
        if not sysname:
            module.fail_json(msg='Unable to get destdir; sysname not found.')
        dest = os.path.join(builddir, sysname, 'dest')
        if not os.path.isdir(dest):
            module.fail_json(msg='Missing dest directory: %s' % dest)
        copy_tree(dest, destdir)
        results['changed'] = True

    #
    # Copy security key utilities to a standard location.
    #
    install_targets = \
        ['install', 'install_nolibafs', 'dest', 'dest_nolibafs']
    if destdir and target in install_targets:
        log.info('Copying security key utilities to %s' % destdir)
        for p in ('asetkey', 'akeyconvert'):
            src = os.path.join(builddir, 'src', 'aklog', p)
            dst = os.path.join(destdir, 'usr', 'sbin')
            if os.path.isfile(src):
                if not os.path.isdir(dst):
                    os.makedirs(dst)
                log.debug('shutil.copy2("%s", "%s")' % (src, dst))
                shutil.copy2(src, dst)
                results['changed'] = True

    #
    # Save configured build paths in a meta-data file for installation.
    #
    if destdir and target in ('install', 'install_nolibafs'):
        filename = os.path.join(destdir, '.build-info.json')
        build_info = {
          'dirs': results['install_dirs']
        }
        with open(filename, 'w') as f:
            f.write(json.dumps(build_info, indent=4))

    log.debug('Results: %s' % pprint.pformat(results))
    results['msg'] = 'Build completed'
    log.info(results['msg'])

    #
    # Save results.
    #
    with open(os.path.join(logdir, 'results.json'), 'w') as f:
        f.write(json.dumps(results, indent=4))

    module.exit_json(**results)


if __name__ == '__main__':
    main()
