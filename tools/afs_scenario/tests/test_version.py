from click.testing import CliRunner
from afs_scenario.main import main

def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert result.output != ''
