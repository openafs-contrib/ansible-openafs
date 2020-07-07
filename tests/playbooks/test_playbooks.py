import logging
import os
import sh
import unittest
import ddt
from playbooks import vm

log = logging.getLogger(__name__)
ansible = sh.Command('ansible')
ansible_playbook = sh.Command('ansible-playbook')

def setup_logging():
    logfile = os.environ.get('TEST_LOG', '/var/tmp/test.log')
    verbose = os.environ.get('TEST_VERBOSE', 'no').lower()
    if verbose == 'yes' or verbose == '1':
        level = logging.DEBUG
        verbosity = 2
    else:
        level = logging.INFO
        verbosity = 1
    print("Writing log to '%s'." % logfile)
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)-7s %(message)s',
        filename=logfile,
        filemode='w')
    vm.set_verbosity(verbosity)
    log = logging.getLogger(__name__)
    if verbose == 'yes' or verbose == '1':
        formatter = logging.Formatter('%(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        vm_log = logging.getLogger(vm.__name__)
        vm_log.addHandler(console)
        log.addHandler(console)
    return log

@ddt.ddt
class SingleHostPlaybookTest(unittest.TestCase):
    def __init__(self, methodName='runTest', template=None):
        super(SingleHostPlaybookTest, self).__init__(methodName)
        self.template = template
        self.domain = 'afs01'
        self.dns = 'example.com'
        self.vpath = vm.query_pool('default')
        self.env = os.environ.copy()
        self.env['ANSIBLE_NOCOLOR'] = 'yes'
        self.playbookdir = os.environ.get('TEST_PLAYBOOK_DIR', '../playbooks')

    @classmethod
    def new(cls, template):
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(cls)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(cls(name, template=template))
        return suite

    def setUp(self):
        log.info('Test setup')
        if not vm.query_domain(self.domain, 'check'):
            vm.destroy_guest(self.domain)
        vm.create_guest(self.domain, self.template, path=self.vpath,
                        dns=self.dns, update_resolver=True)
        args = dict(_cwd=self.playbookdir, _env=self.env, _iter=True)
        try:
            for line in ansible('all', inventory='hosts/example01', m='wait_for_connection', **args):
                log.info('setup: %s', line.strip())
        except sh.ErrorReturnCode as erc:
            self.fail('unable to connect')
        except sh.SignalException as se:
            self.fail('interrupted')

    def tearDown(self):
        log.info('Test teardown')
        vm.destroy_guest(self.domain)

    @ddt.data(
        'build01.yaml',
        'build02.yaml',
        'build03.yaml',
        'testcell.yaml',
    )
    def test_playbook(self, playbook):
        args = dict(
            inventory='hosts/example01',
            _cwd=self.playbookdir,
            _env=self.env,
            _iter=True,
        )
        try:
            log.info("Running playbook: %s/%s on %s." % \
                (self.playbookdir, playbook, self.template))
            for line in ansible_playbook(playbook, **args):
                log.info('ansible: %s', line.strip())
        except sh.ErrorReturnCode as erc:
            self.fail('playbook failed')
        except sh.SignalException as se:
            self.fail('playbook interrupted')

def main():
    setup_logging()
    suite = unittest.TestSuite()
    suite.addTest(SingleHostPlaybookTest.new('base-centos7'))
    suite.addTest(SingleHostPlaybookTest.new('base-centos8'))
    suite.addTest(SingleHostPlaybookTest.new('base-debian10'))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    main()
