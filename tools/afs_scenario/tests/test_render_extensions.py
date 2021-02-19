from click.testing import CliRunner
from afs_scenario.main import main

def test_extensions():
    test_config = """\
---
x:
  y:
    a: apple
    b: orange
    c:
      - sour cherry
      - sweet cherry
"""
    test_template = """\
---
# flavors
[[ x | to_nice_yaml ]]
"""
    expected = """\
---
# flavors
y:
    a: apple
    b: orange
    c:
    - sour cherry
    - sweet cherry
"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('config.yml', 'w') as fh:
            fh.write(test_config)
        with open('test_template.yml.j2', 'w') as fh:
            fh.write(test_template)

        result = runner.invoke(main, ['init', '-d', '.', '-c', 'config.yml'])
        assert not result.exception
        assert result.exit_code == 0

        with open('test_template.yml') as fh:
           rendered_text = fh.read()
        assert rendered_text == expected
