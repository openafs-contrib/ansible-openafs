#
# Molecule test driver for roles and playbooks.
#
# USAGE
#
#   pytest --co                #  list test cases
#   pytest -v                  #  run tests
#   pytest -v -k '<pattern>'   # to run specific tests
#
# DESCRIPTION
#
#   Run molecule scenarios for the supported platforms.
#
#   Molecule stdout and stderr is written to log files:
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
from pathlib import Path
import pytest

PLATFORMS = [
    'centos7',
    'centos8',
    'fedora34',
    'fedora33',
    'debian11',
    'debian10',
]
ROLE = Path(os.getcwd()).name
LOGDIR = Path('/tmp/ansible-openafs/molecule') / ROLE
BASECONFIGDIR = Path('~/.config/molecule').expanduser()

ANSIBLE_VARS = {
    'ANSIBLE_VERBOSITY': '1',
    'ANSIBLE_STDOUT_CALLBACK': 'debug',
    'ANSIBLE_NOCOLOR': '1',
    'ANSIBLE_FORCE_COLOR': '0',
}


def parameters():
    params = []
    scenarios = [p.parent.name for p in Path().glob('molecule/*/molecule.yml')]
    for p in PLATFORMS:
        for s in scenarios:
            params.append((p, s))
    return params


def set_env_vars(platform):
    for n, v in ANSIBLE_VARS.items():
        os.environ[n] = v
    os.environ['AFS_IMAGE'] = 'generic/%s' % platform


def run(proc, logfile):
     rc = proc.wait()
     assert rc == 0, 'See "%s".' % logfile


@pytest.mark.parametrize('platform,scenario', parameters())
def test_scenario(tmpdir, platform, scenario):
    args = []
    args.append('molecule')
    platform_config = BASECONFIGDIR / 'platforms' / '%s.yml' % platform
    if platform_config.exists():
        args.append('--base-config=%s' % platform_config)
    args.append('test')
    args.append('--scenario-name=%s' % scenario)

    logfile = '%s/%s-%s.log' % (LOGDIR, platform, scenario)
    if not LOGDIR.exists():
        os.makedirs(LOGDIR)

    print('\nWriting output to %s' % logfile)
    with open(logfile, 'w') as f:
        set_env_vars(platform)
        print('Running: %s\n' % ' '.join(args))
        proc = subprocess.Popen(args, stdout=f.fileno(), stderr=subprocess.STDOUT)
        #run(proc, logfile)
