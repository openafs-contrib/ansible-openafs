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
  - Build OpenAFS server and client binaries from source code by running
    C(regen.sh), C(configure), and C(make). The source code must be already
    present in the I(projectdir) directory.

  - The M(openafs_build) module will run the OpenAFS C(regen.sh) command to
    generate the C(configure) script when the C(configure) script is not
    already present in the I(projectdir).

  - Unless the I(configure_options) option is specified, the configure command
    line arguments are determined automatically, based on the platform and
    M(openafs_build) options.

  - The C(make) program is run to build the binaries. Unless the I(target)
    options is specified, the make target is determined automatically.

  - A complete set of build log files are written on the I(logdir) directory
    on the host for build troubleshooting.

  - Out-of-tree builds are supported by specifying a build directory with the
    I(builddir) option.

  - C(git clean) is run in the I(projectdir) when I(clean) is true and a
    C(.git) directory is found in the C(projectdir).  When I(clean) is true
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
      - Source files must have been previously checkout or copied to this
        path.
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

  destdir:
    description:
      - The destination directory for C(install) and C(dest) targets and
        variants.
      - The tree staged in this directory may be installed with the
        M(openafs_install_bdist) module.
    default: <projectdir>/packages/dest
    type: path

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

  transarc_paths:
    description:
      - Build binaries which use the legacy Transarc-style paths.
      - This option is ignored when the I(configure_options) option is
        specified.
    type: bool

  configure_options:
    description:
      - The C(configure) command arguments.
      - May be specified as a string, list of strings, or a dictionary.
      - When specified as a dictionary, the values of the keys
        C(enabled), C(disabled), C(with), and C(without) may be lists.
    type: raw

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

import glob       # noqa: E402
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
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.common \
    import Logger, chdir, lookup_fact  # noqa: E402
from ansible_collections.openafs_contrib.openafs.plugins.module_utils.o2a \
    import options_to_args  # noqa: E402

module_name = os.path.basename(__file__).replace('.py', '')
log = None
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
            proc = subprocess.Popen(command,
                                    stdout=f.fileno(),
                                    stderr=f.fileno())
            rc = proc.wait()
    if rc != 0:
        log.error('%s failed; rc=%d' % (name, rc))
        module.fail_json(
            msg='%s command failed. See log file "%s".' % (name, logfile),
        )


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


def find_kmods_linux(builddir):
    """
    Search for built kernel modules on Linux.
    """
    pattern = os.path.join(builddir, 'src/libafs/MODLOAD-*/*afs.ko')
    kmods = glob.glob(pattern)
    return kmods


def kmod_check_linux(module, results):
    """
    Verify we built a kernel module that matches the running kernel version.
    """
    log.info('Checking for linux kernel module for %s.' % platform.release())
    modloads = []
    for kmod in results['kmods']:
        pattern = r'/MODLOAD-%s-[A-Z]*/(lib|open)afs\.ko$' % platform.release()
        m = re.search(pattern, kmod)
        if m:
            modloads.append(kmod)
    log.info('Modules found: %s' % ' '.join(modloads))
    if not modloads:
        results['msg'] = 'Loadable linux kernel module not found for %s' \
                         % platform.release()
        log.error(results['msg'])
        module.fail_json(**results)


def find_kmods_solaris(builddir):
    """
    Search for built kernel modules on Solaris.
    """
    kmods = []
    for name in ('libafs.o', 'libafs.nonfs.o'):
        kmod = os.path.join(builddir, 'src/libafs/MODLOAD64', name)
        if os.path.exists(kmod):
            kmods.append(kmod)
    return kmods


def kmod_check_solaris(module, results):
    """
    Verify we built a kernel module.
    """
    log.info('Checking for solaris kernel modules.')
    if not results['kmods']:
        results['msg'] = 'Kernel module not found.'
        log.error(results['msg'])
        module.fail_json(**results)


def determine_configure_options(module):
    """
    Determine configure arguments for this system.

    Automatically determine configure options for this system and build
    options when the explicit configure options are not specified.
    """
    configure_options = module.params['configure_options']
    transarc_paths = module.params['transarc_paths']

    if configure_options is None:
        configure_options = {}
        if transarc_paths:
            configure_options['enable'] = 'transarc_paths'

    return configure_options


def configure_command(module, results):
    """
    Determine configure command line.

    Use the explicitly specified configure_options when specified, otherwise,
    determine the options depeneding on the current system and build
    parameters.
    """
    # Convert structured data to a list of command line arguments.
    configure_options = determine_configure_options(module)
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

    projectdir = module.params['projectdir']
    command = [os.path.join(projectdir, 'configure'), *args]
    results['configure'] = command
    return command


def determine_target(module, results):
    """
    Determine the make target name.

    If a target name is not explicitly specified, determine a suitable top
    level target based on the configure command line used to configure
    the tree.
    """
    # This function must be called after configure, assert otherwise.
    if 'configure' not in results:
        module.fail_json(msg='Internal error: configure not found in results.')

    target = module.params['target']
    configure = results['configure']
    if target is None:
        if '--enable-transarc-paths' in configure:
            target = 'dest'      # legacy mode
        else:
            target = 'install'   # implies "all"
        if '--disable-kernel-module' in configure:
            target += '_nolibafs'
    results['target'] = target
    return target


def make_command(module, results):
    """
    Determine make command line.

    Historically, the make target depends on the directory path mode
    specified by the configure options.  The 'dest' target is used to build
    transarc style paths and make install is used to build modern style paths
    (although, hybrid styles are possible).  To make it easier to support
    both modes, by default, just figure out the make target based on the
    configure options given.  The caller my specify a explicit target (even
    an empty one) to override this feature.
    """
    make = module.params['make']
    if not make:
        make = module.get_bin_path('make', required=True)
    jobs = module.params['jobs']
    destdir = module.params['destdir']
    if destdir:
        destdir = abspath(results['builddir'], destdir)
        results['destdir'] = destdir

    command = [make]
    if jobs > 0:
        command.extend(['-j', '%d' % jobs])
    target = determine_target(module, results)
    if target:
        command.append(target)
    if destdir and not target.startswith('dest'):
        command.append('DESTDIR=%s' % destdir)

    results['make'] = command
    return command


def main():
    global log
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
            configure_options=dict(type='raw', default=None),
            transarc_paths=dict(type='bool', default=False)
        ),
        supports_check_mode=False,
    )
    log = Logger(module_name)
    log.info('Starting %s', module_name)
    log.info('Parameters: %s', pprint.pformat(module.params))

    state = module.params['state']
    projectdir = module.params['projectdir']
    builddir = module.params['builddir']
    logdir = module.params['logdir']
    clean = module.params['clean']
    version = module.params['version']
    make = module.params['make']
    manpages = module.params['manpages']

    if not (os.path.exists(projectdir) and os.path.isdir(projectdir)):
        module.fail_json(msg='projectdir directory not found: %s' % projectdir)
    results['projectdir'] = os.path.abspath(projectdir)

    # Find `make` if not specified.
    if not make:
        make = module.get_bin_path('make', required=True)

    #
    # Setup build logging.
    #
    if not logdir:
        logdir = os.path.join(projectdir, '.ansible')
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
        results['changed'] = True
    results['logdir'] = logdir

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
    # Setup environment.
    #
    solariscc = lookup_fact('solariscc')
    if solariscc:
        os.environ['SOLARISCC'] = solariscc
        os.environ['UT_NO_USAGE_TRACKING'] = '1'
        os.environ['SUNW_NO_UPDATE_NOTIFY'] = '1'

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
    run_command('configure', configure_command(module, results), builddir,
                logdir, results)
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
        run_command('make', [make, 'clean'], builddir, logdir, results)

    #
    # Run make.
    #
    run_command('make', make_command(module, results), builddir, logdir,
                results)

    #
    # `make` may silently fail to build a kernel module for the running kernel
    # version (or any version). Let's fail early instead of finding out later
    # when we try to start the cache manager.
    #
    if platform.system() == 'Linux':
        results['kmods'] = find_kmods_linux(builddir)
    elif platform.system() == 'SunOS':
        results['kmods'] = find_kmods_solaris(builddir)
    else:
        log.warning('Unable to find kernel modules; unknown platform %s'
                    % platform.system())
    if state == 'built-module':
        if platform.system() == 'Linux':
            kmod_check_linux(module, results)
        elif platform.system() == 'SunOS':
            kmod_check_solaris(module, results)
        else:
            results['msg'] = 'Unable to verify kernel module; '\
                             'unknown platform %s' % platform.system()
            log.error(results['msg'])
            module.fail_json(**results)

    #
    # Copy the transarc-style distribution tree into a DESTDIR file tree
    # for installation.
    #
    if 'destdir' in results and 'target' in results and \
            results['target'] in ('dest', 'dest_nolibafs', 'dest_only_libafs'):
        log.info('Copying transarc-style distribution files to %s' %
                 results['destdir'])
        sysname = configured_sysname(builddir)
        if not sysname:
            module.fail_json(msg='Unable to get destdir; sysname not found.')
        dest = os.path.join(builddir, sysname, 'dest')
        if not os.path.isdir(dest):
            module.fail_json(msg='Missing dest directory: %s' % dest)
        copy_tree(dest, results['destdir'])
        results['changed'] = True

    #
    # Copy security key utilities to a standard location.
    #
    if 'destdir' in results and 'target' in results and \
            results['target'] in ('install', 'install_nolibafs',
                                  'dest', 'dest_nolibafs'):
        log.info('Copying security key utilities to %s' % results['destdir'])
        for p in ('asetkey', 'akeyconvert'):
            src = os.path.join(builddir, 'src', 'aklog', p)
            dst = os.path.join(results['destdir'], 'usr', 'sbin')
            if os.path.isfile(src):
                if not os.path.isdir(dst):
                    os.makedirs(dst)
                log.debug('shutil.copy2("%s", "%s")' % (src, dst))
                shutil.copy2(src, dst)
                results['changed'] = True

    #
    # Save configured build paths in a meta-data file for installation.
    #
    if 'destdir' in results and 'target' in results and \
            results['target'] in ('install', 'install_nolibafs'):
        filename = os.path.join(results['destdir'], '.build-info.json')
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
