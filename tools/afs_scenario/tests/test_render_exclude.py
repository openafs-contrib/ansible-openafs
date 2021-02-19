import os
import yaml

from click.testing import CliRunner
from afs_scenario.main import main

def make_context(name):
    test_context = {
        'test1': 'from context file',
        '__exclude__': ['no.yml.j2'],
    }
    with open(name, 'w') as fh:
       yaml.dump(test_context, fh)

def make_template(name):
    test_template = """
        Test1 [[ test1 ]]
    """
    with open(name, 'w') as fh:
        fh.write(test_template)

def read_file(name):
    with open(name) as fh:
        return fh.read()

def test_exclude_option():
    runner = CliRunner()
    with runner.isolated_filesystem():
        make_template('yes.yml.j2')
        make_template('no.yml.j2')

        result = runner.invoke(main,
            ['init', '-d', '.', '-x', 'no.yml.j2', '-e', 'test1=xyzzy'])

        assert not result.exception
        assert result.exit_code == 0
        assert os.path.exists('yes.yml')
        assert not os.path.exists('no.yml')
        assert 'Test1 xyzzy' in read_file('yes.yml')

def test_exclude_context():
    runner = CliRunner()
    with runner.isolated_filesystem():
        make_context('config.yml')
        make_template('yes.yml.j2')
        make_template('no.yml.j2')

        result = runner.invoke(main, ['init', '-d', '.', '-c', 'config.yml'])

        assert not result.exception
        assert result.exit_code == 0
        assert os.path.exists('yes.yml')
        assert not os.path.exists('no.yml')
        assert 'Test1 from context file' in read_file('yes.yml')
