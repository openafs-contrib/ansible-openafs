#
# Molecule test driver for roles and playbooks.
#
# USAGE
#
#   cd roles/<name>            # must run in the role directory
#   pytest --co                # to list test cases
#   pytest -v                  # to  run tests
#   pytest -v -k '<pattern>'   # to run specific tests
#
# DESCRIPTION
#
#   Run molecule scenarios for the supported platforms.
#
#   Molecule stdout and stderr are written to log files:
#
#       /tmp/ansible-openafs/molecule/<role-or-playbook>/<platform>-<scenario>.log
#
#   Setup the driver name and options in the site-local base config files.
#
# FILES
#
#   ~/.config/molecule/config.yml            default base config
#   ~/.config/molecule/platforms/<name>.yml  platform specific base config
#
import os
import subprocess
import sys
import fnmatch
from pathlib import Path
import yaml
import pytest

PLATFORMS = [
    'alma8',
    'centos7',
    'centos8',
    'debian10',
    'debian11',
    'fedora34',
    'fedora35',
    'opensuse15',
    'rocky8',
    'solaris114',
    'ubuntu20',
    'ubuntu22',
]
ROLE = Path(os.getcwd()).name
LOGDIR = Path('/tmp/ansible-openafs/molecule') / ROLE
BASECONFIGDIR = Path('~/.config/molecule').expanduser()

def image_name(platform):
    """
    Site dependent platform to image name lookup.
    """
    platforms_yml = BASECONFIGDIR / 'platforms.yml'
    try:
        with open(platforms_yml) as f:
            p2i = yaml.safe_load(f)['platforms']
        image_name = p2i[platform]
    except:
        image_name = platform
    return image_name

def read_skip_list():
    """
    Read the pytest.skip file.

    The pytest.skip file can be used to skip platform/scenario test
    combinations. Each line of the file contains a file glob pattern of tests
    to exclude. Lines starting with ! indicate tests to include (to override
    the exclusions). Blank lines and lines starting with '#' are ignored.
    """
    exclude = []
    include = []
    if os.path.exists('pytest.skip'):
        with open('pytest.skip') as f:
            for line in f.readlines():
                line = line.strip()
                if line == '' or line.startswith('#'):
                    continue  # Skip blank lines and comments.
                if line.startswith('!'):
                    include.append(line.replace('!', '', 1))
                else:
                    exclude.append(line)
    return set(exclude), set(include)


def in_list(patterns, name):
    """
    Return true if name matches at least one pattern in the list.
    """
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def parameters():
    """
    Generate the platform-scenario test cases.
    """
    exclude, include = read_skip_list()
    number = 0
    params = []
    scenarios = [p.parent.name for p in Path().glob('molecule/*/molecule.yml')]
    for p in PLATFORMS:
        for s in scenarios:
            name = '%s-%s' % (p, s)
            if in_list(exclude, name) and not in_list(include, name):
                continue
            params.append((number, p, s))
            number += 1
    return params


def run_molecule(cmd, scenario, log, options):
    """
    Run molecule test
    """
    args = ['molecule']
    for k, v in options.items():
        args.append('--%s=%s' % (k, v))
    args.append(cmd)
    args.append('--scenario-name=%s' % scenario)
    msg = 'Running: %s' % ' '.join(args)
    print(msg)
    log.write('%s\n' % msg)
    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    for line in proc.stdout:
        line = line.decode('utf-8')
        sys.stdout.write(line)
        log.write(line)
    rc = proc.wait()
    assert rc == 0, 'See "%s".' % log.name


@pytest.mark.parametrize('number,platform,scenario', parameters())
def test_scenario(number, platform, scenario):
    logfile = '%s/%s-%s.log' % (LOGDIR, platform, scenario)
    if not os.path.exists(os.path.dirname(logfile)):
        os.makedirs(os.path.dirname(logfile))
    with open(logfile, 'w') as log:
        print('\nWriting output to %s' % log.name)
        options = {}
        base_config = BASECONFIGDIR / 'platforms' / ('%s.yml' % platform)
        if base_config.exists():
            options['base-config'] = base_config
        os.environ['ANSIBLE_VERBOSITY'] = '1'
        os.environ['ANSIBLE_STDOUT_CALLBACK'] = 'debug'
        os.environ['ANSIBLE_NOCOLOR'] = '1'
        os.environ['ANSIBLE_FORCE_COLOR'] = '0'
        os.environ['AFS_IMAGE'] = image_name(platform)
        os.environ['AFS_TESTID'] = '-%d-%d' % (os.getpid(), number)
        print('AFS_IMAGE=%s' % os.environ['AFS_IMAGE'])
        print('AFS_TESTID=%s' % os.environ['AFS_TESTID'])
        run_molecule('reset', scenario, log, options)
        run_molecule('test', scenario, log, options)
