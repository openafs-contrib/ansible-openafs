#
# Molecule test driver for roles.
#
# Usage:
#
#   cd roles/<role>
#   pytest -v
#
# Molecule stdout and stderr is written to log files:
#
#   /tmp/ansible-openafs/molecule/<role>/<platform>-<scenario>.log
#
# Use the --co option to list test cases:
#
#   cd roles/<role>
#   pytest --co
#
# Use the '-k' option to run test cases matching a pattern.
#
#   cd roles/<role>
#   pytest -k 'debian and bdist' -s -v
#

import os
import subprocess
from pathlib import Path
import pytest

PLATFORMS = ['centos7', 'centos8', 'fedora34', 'debian10']
ROLE = Path(os.getcwd()).name
LOGDIR = Path('/tmp') / 'ansible-openafs' / 'molecule' / ROLE

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

@pytest.mark.parametrize('platform,scenario', parameters())
def test_scenario(tmpdir, platform, scenario):
    args = [
        'molecule',
        'test',
        '--scenario-name=%s' % scenario,
    ]
    driver = os.getenv('MOLECULE_DRIVER')
    if driver:
        args.append('--driver-name=%s' % driver)
    logfile = '%s/%s-%s.log' % (LOGDIR, platform, scenario)
    if not LOGDIR.exists():
        os.makedirs(LOGDIR)
    print('Writing output to %s' % logfile)
    with open(logfile, 'w') as f:
        set_env_vars(platform)
        f.write('\nRunning: %s\n' % ' '.join(args))
        proc = subprocess.Popen(args, stdout=f.fileno(), stderr=subprocess.STDOUT)
        rc = proc.wait()
        assert rc == 0, 'See "%s".' % logfile
