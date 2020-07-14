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

@pytest.fixture(params=['centos7', 'centos8', 'debian10'])
def guest(request):
    template = 'base-%s' % request.param
    with Guest('afs01', template, update_resolver=True) as g:
        for line in ansible('all', i='hosts/example01', m='wait_for_connection',
                            _cwd='../playbooks', _env=env, _iter=True):
            log.info('wait_for_connection: %s' % line.rstrip())
        yield(g)

@pytest.fixture(params=[
    ('hosts/example01', 1, 'centos7'),
    ('hosts/example01', 1, 'centos8'),
    ('hosts/example01', 1, 'debian10'),
    ('hosts/example02', 9, 'centos7'),
])
def inventory(request):
    inv, num, os_ = request.param
    guests = []
    for i in range(num):
        g = Guest('afs%02d' % (i + 1), 'base-%s' % os_, update_resolver=True)
        guests.append(g)
    for g in guests:
        g.create()
    for line in ansible('all', i=inv, m='wait_for_connection',
                         _cwd='../playbooks', _env=env, _iter=True):
        log.info('wait_for_connection: %s' % line.rstrip())
    yield(inv)
    for g in guests:
        g.destroy()

@pytest.mark.parametrize('playbook', ['build01.yaml', 'build02.yaml', 'build03.yaml'])
def test_build(guest, playbook):
    log.info('Running playbook %s on guest %s' % (playbook, guest.name))
    for line in ansible_playbook(playbook, i='hosts/example01',
                                 _cwd='../playbooks', _env=env, _iter=True):
        log.info('ansible: %s', line.strip())

def test_testcell(inventory):
    playbook = 'testcell.yaml'
    log.info('Running %s on inventory %s' % (playbook, inventory))
    for line in ansible_playbook(playbook, i='hosts/example01',
                                 _cwd='../playbooks', _env=env, _iter=True):
        log.info('ansible: %s', line.strip())
