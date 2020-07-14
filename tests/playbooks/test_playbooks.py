import logging
import os
import pytest
import sh
from .vm import Guest

log = logging.getLogger(__name__)
env = os.environ.copy()
env['ANSIBLE_NOCOLOR'] = 'yes'

ansible = sh.Command('ansible')
ansible_playbook = sh.Command('ansible-playbook')

# Single host fixture.
@pytest.fixture(params=['centos7', 'centos8', 'debian10'])
def guest(request):
    template = 'base-%s' % request.param
    with Guest('afs01', template, update_resolver=True) as g:
        for line in ansible('all', i='hosts/single', m='wait_for_connection',
                            _cwd='../playbooks', _env=env, _iter=True):
            log.info('wait_for_connection: %s' % line.rstrip())
        yield(g)

def invfn(val):
    return '%s-%s' % (val[0].replace('hosts/', ''), val[2])

# Test cell inventory fixture.
@pytest.fixture(ids=invfn, params=[
    ('hosts/single', 1, 'centos7'),
    ('hosts/single', 1, 'centos8'),
    ('hosts/single', 1, 'debian10'),
    ('hosts/multi', 9, 'centos7'),
    ('hosts/build', 3, 'centos7'),
])
def inventory(request):
    hosts, num, os_ = request.param
    guests = []
    for i in range(num):
        g = Guest('afs%02d' % (i + 1), 'base-%s' % os_, update_resolver=True)
        guests.append(g)
    for g in guests:
        g.create()
    for line in ansible('all', i=hosts, m='wait_for_connection',
                         _cwd='../playbooks', _env=env, _iter=True):
        log.info('wait_for_connection: %s' % line.rstrip())
    yield(hosts)
    for g in guests:
        g.destroy()

# Helper to run a playbook.
def run_playbook(playbook, inventory):
    log.info('Running playbook %s' % playbook)
    for line in ansible_playbook(playbook, i=inventory, _cwd='../playbooks', _env=env, _iter=True):
        log.info('ansible: %s', line.strip())

# Test build-only playbooks.
@pytest.mark.parametrize('playbook', ['build01.yaml', 'build02.yaml', 'build03.yaml'])
def test_build(guest, playbook):
    run_playbook(playbook, 'hosts/single')

# Create test cells and run robotest.
def test_testcell(inventory):
    run_playbook('testcell.yaml', inventory)
