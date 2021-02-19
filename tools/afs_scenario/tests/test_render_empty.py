from click.testing import CliRunner
from afs_scenario.main import main

def test_empty():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['init'])
        assert not result.exception
        assert result.exit_code == 0
