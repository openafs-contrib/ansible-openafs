from click.testing import CliRunner
from afs_scenario.main import main

def make_template(name):
    test_template = "[[ bogus_name ]]"
    with open(name, 'w') as fh:
        fh.write(test_template)

def test_undefined():
    runner = CliRunner()
    with runner.isolated_filesystem():
        make_template('bogus.yml.j2')
        result = runner.invoke(main, ['init', '-d', '.'])
        assert result.exception
        assert "'bogus_name' is undefined" in result.exception.message
        assert result.exit_code != 0
