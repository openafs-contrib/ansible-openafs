import yaml
from click.testing import CliRunner
from afs_scenario.main import main

def test_extra():
    test_config = {
        'test': {
            'one': 'this is value 1',
            'two': 'yes',
        }
    }
    test_template = """
        Test1 [[ test.one ]]
        [% if test.two is defined %]
        Test2 [[ test.two ]]
        [% endif %]
        [% if test.three is defined %]
        Test3 [[ test.three ]]
        [% endif %]
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('config.yml', 'w') as fh:
            yaml.dump(test_config, fh)
        with open('test_template.yml.j2', 'w') as fh:
            fh.write(test_template)

        result = runner.invoke(main,
            ['init', '-d', '.', '-c', 'config.yml', '-e', 'test.one=override', '-e', 'test.three=added'])
        assert not result.exception
        assert result.exit_code == 0

        with open('test_template.yml') as fh:
           rendered_text = fh.read()
        assert 'Test1 override' in rendered_text
        assert 'Test2 yes' in rendered_text
        assert 'Test3 added' in rendered_text
