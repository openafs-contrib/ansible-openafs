import os
from click.testing import CliRunner
from afs_scenario.main import main

def make_template(name):
    test_template = """
        Test1 [[ test1 ]]
    """
    with open(name, 'w') as fh:
        fh.write(test_template)

def read_file(name):
    with open(name) as fh:
        return fh.read()

def test_recursive():
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('d1')
        os.makedirs('d1/d2')
        make_template('t1.yml.j2')
        make_template('d1/t1.yml.j2')
        make_template('d1/d2/t1.yml.j2')

        result = runner.invoke(main, ['init', '-d', '.', '--recursive', '-e', 'test1=xyzzy'])

        assert not result.exception
        assert result.exit_code == 0
        assert os.path.exists('t1.yml')
        assert os.path.exists('d1/t1.yml')
        assert os.path.exists('d1/d2/t1.yml')
        assert 'Test1 xyzzy' in read_file('t1.yml')
        assert 'Test1 xyzzy' in read_file('d1/t1.yml')
        assert 'Test1 xyzzy' in read_file('d1/d2/t1.yml')
