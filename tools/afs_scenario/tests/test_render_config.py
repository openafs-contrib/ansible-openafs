import yaml
from click.testing import CliRunner
from afs_scenario.main import main

def test_config():
    test_config = {
        'test1': 'this is value 1',
        'test2': 'yes'
    }
    test_template = """
        Test1 [[ test1 ]]
        [% if test2 is defined %]
        Test2 [[ test2 ]]
        [% endif %]
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('config.yml', 'w') as fh:
            yaml.dump(test_config, fh)
        with open('test_template.yml.j2', 'w') as fh:
            fh.write(test_template)

        result = runner.invoke(main, ['init', '-c', 'config.yml', '-d', '.'])
        assert not result.exception
        assert result.exit_code == 0

        with open('test_template.yml') as fh:
           rendered_text = fh.read()
        assert 'Test1 this is value 1' in rendered_text
        assert 'Test2 yes' in rendered_text
