from pathlib import Path
from click.testing import CliRunner
from afs_scenario.main import main

def test_setup_interactive_defaults():
    input = ''
    expected_yaml = """\
---
driver:
  name: vagrant
prepare:
  rewrite_etc_hosts: 'no'
"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['setup', '-c', 'output.yml'], input=input)
        assert result.exception is None
        assert result.exit_code == 0
        output = Path('output.yml')
        assert output.is_file()
        assert output.read_text() == expected_yaml

def test_setup_interactive_delegated():
    """
    Interative example:

$ afs-scenario setup -c output.yaml
Choose driver name
1 - vagrant
2 - delegated
 [1]: 2
Driver provider [libvirt]: 
Driver options host [localhost]: foo.example.com
Choose driver options connection
1 - local
2 - ssh
 [2]: 2
Driver options port [22]: 
Driver options loglevel [info]: 
Driver options python interpreter [/usr/bin/python3]: 
Platforms instance prefix []: m-
Prepare import playbook []: myplaybook.yml
Prepare rewrite etc hosts [y/N]: n
Wrote: output.yaml
"""
    input = '2\n\nfoo.example.com\n2\n\n\n\nm-\nmyplaybook.yml\nn\n'
    expected_yaml = """\
---
driver:
  name: delegated
  options:
    connection: ssh
    host: foo.example.com
    loglevel: info
    port: 22
    python_interpreter: /usr/bin/python3
  provider: libvirt
platforms:
  instance_prefix: m-
prepare:
  import_playbook: myplaybook.yml
  rewrite_etc_hosts: 'no'
"""

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['setup', '-c', 'output.yml'], input=input)
        assert result.exception is None
        assert result.exit_code == 0
        output = Path('output.yml')
        assert output.is_file()
        assert output.read_text() == expected_yaml
