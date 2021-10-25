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

def parameters():
    params = []
    scenarios = [p.parent.name for p in Path().glob('molecule/*/molecule.yml')]
    for p in PLATFORMS:
        for s in scenarios:
            params.append((p, s))
    return params


def run_molecule(cmd, scenario, log, options):
     args = ['molecule']
     for k, v in options.items():
        args.append('--%s=%s' % (k, v))
     args.append(cmd)
     args.append('--scenario-name=%s' % scenario)
     msg = 'Running: %s' % ' '.join(args)
     print(msg)
     log.write('%s\n' % msg)
     proc = subprocess.Popen(args, stdout=log.fileno(), stderr=subprocess.STDOUT)
     rc = proc.wait()
     assert rc == 0, 'See "%s".' % log.name


@pytest.mark.parametrize('platform,scenario', parameters())
def test_scenario(tmpdir, platform, scenario):
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
        os.environ['AFS_IMAGE'] = 'generic/%s' % platform
        run_molecule('test', scenario, log, options)
        run_molecule('reset', scenario, log, options)
