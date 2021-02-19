from pathlib import Path
from click.testing import CliRunner
from afs_scenario.main import main

def test_setup_with_options():
    args = [
        'setup',
        '-c', 'output.yml',
        '-o', 'driver.name=delegated',
        '-o', 'driver.provider=libvirt',
        '-o', 'driver.options.host=foo.example.com',
        '-o', 'driver.options.connection=ssh',
        '-o', 'driver.options.port=22',
        '-o', 'driver.options.loglevel=debug',
        '-o', 'driver.options.python_interpreter=/usr/bin/python3',
        '-o', 'platforms.instance_prefix=molecule-',
        '-o', 'prepare.import_playbook=myplaybook.yaml',
        '-o', 'prepare.rewrite_etc_hosts=yes',
    ]
    expected_yaml = """\
---
driver:
  name: delegated
  options:
    connection: ssh
    host: foo.example.com
    loglevel: debug
    port: '22'
    python_interpreter: /usr/bin/python3
  provider: libvirt
platforms:
  instance_prefix: molecule-
prepare:
  import_playbook: myplaybook.yaml
  rewrite_etc_hosts: 'yes'
"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, args)
        output = Path('output.yml')
        assert result.exception is None
        assert result.exit_code == 0
        assert output.is_file()
        assert output.read_text() == expected_yaml
