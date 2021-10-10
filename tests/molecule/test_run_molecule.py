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
from pathlib import Path
import pytest

PLATFORMS = ['centos7', 'centos8', 'debian10']
ANSIBLE_VARS = {
    'ANSIBLE_VERBOSITY': '1',
    'ANSIBLE_STDOUT_CALLBACK': 'debug',
    'ANSIBLE_NOCOLOR': '1',
    'ANSIBLE_FORCE_COLOR': '0',
}
ROLE = Path(os.getcwd()).name
LOGDIR = Path('/tmp') / 'ansible-openafs' / 'molecule' / ROLE

def parameters():
    params = []
    scenarios = [p.parent.name for p in Path().glob('molecule/*/molecule.yml')]
    for p in PLATFORMS:
        for s in scenarios:
            params.append((p, s))
    return params

def info(logfile, msg):
    print(msg)
    with open(logfile, 'a') as f:
        f.write('PYTEST: %s\n' % msg)

def run(cmd, logfile):
    info(logfile, '\nrunning: %s' % cmd)
    rc = os.system(cmd)
    info(logfile, 'exit code %d' % rc)
    assert rc == 0, 'See %s for details.' % logfile

@pytest.mark.parametrize('platform,scenario', parameters())
def test_scenario(tmpdir, platform, scenario):
    for n, v in ANSIBLE_VARS.items():
        if n not in os.environ:
            os.environ[n] = v
    if not LOGDIR.exists():
        os.makedirs(LOGDIR)
    logfile = '%s/%s-%s.log' % (LOGDIR, platform, scenario)
    image = 'generic/%s' % platform
    args = [
        'AFS_IMAGE=%s' % image,
        'molecule',
        'test',
        '--scenario-name=%s' % scenario,
    ]
    driver = os.getenv('MOLECULE_DRIVER')
    if driver:
        args.append('--driver-name=%s' % driver)
    args.append('>%s 2>&1' % logfile)
    cmd = ' '.join(args)
    run(cmd, logfile)
