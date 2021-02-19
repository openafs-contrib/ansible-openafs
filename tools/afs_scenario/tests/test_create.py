from pathlib import Path
import yaml
from click.testing import CliRunner
from afs_scenario.main import main

def test_create():
    scenario_name = 'test_scenario'
    options = [
        'create',
        '-s', scenario_name,
        '-r', 'test_role',
        '--instance-name', 'test',
        '--num-instances', '1',
        '--group', 'group_a',
        '--group', 'group_b',
    ]
    runner = CliRunner()
    with runner.isolated_filesystem():
        molecule = Path('molecule')
        scenario = molecule / scenario_name
        drivers = molecule / '__drivers__'
        molecule_yml = scenario / 'molecule.yml.j2'
        result = runner.invoke(main, options)
        assert result.exit_code == 0
        assert molecule.is_dir()
        assert drivers.is_dir()
        assert scenario.is_dir()
        assert molecule_yml.is_file()

def test_create_force():
    scenario_name = 'test_scenario'
    options = [
        'create',
        '-s', scenario_name,
        '-r', 'test_role',
        '--instance-name', 'test',
        '--num-instances', '1',
        '--group', 'group_a',
        '--group', 'group_b',
    ]
    runner = CliRunner()
    with runner.isolated_filesystem():
        molecule = Path('molecule')
        scenario = molecule / scenario_name
        drivers = molecule / '__drivers__'
        molecule_yml = scenario / 'molecule.yml.j2'
        result = runner.invoke(main, options)
        assert result.exit_code == 0
        assert molecule.is_dir()
        assert drivers.is_dir()
        assert scenario.is_dir()
        assert molecule_yml.is_file()

        options.append('--force')
        result = runner.invoke(main, options)
        assert result.exit_code == 0
        assert molecule.is_dir()
        assert drivers.is_dir()
        assert scenario.is_dir()
        assert molecule_yml.is_file()

def test_create_groups_instances():
    scenario_name = 'test_scenario'
    options = [
        'create',
        '-s', scenario_name,
        '-r', 'test_role',
        '--instance-name', 'test',
        '--num-instances', '3',
        '--group', 'a',
        '--group', 'b=1',
        '--group', 'c=2,3',
    ]
    runner = CliRunner()
    with runner.isolated_filesystem():
        molecule = Path('molecule')
        scenario = molecule / scenario_name
        drivers = molecule / '__drivers__'
        molecule_yml_j2 = scenario / 'molecule.yml.j2'
        molecule_yml = scenario / 'molecule.yml'
        result = runner.invoke(main, options)
        assert result.exit_code == 0
        assert molecule.is_dir()
        assert drivers.is_dir()
        assert scenario.is_dir()
        assert molecule_yml_j2.is_file()

        result = runner.invoke(main, ['init'])
        m = yaml.safe_load(molecule_yml.read_text())
        assert m['platforms'][0]['groups'].sort() == list(['a', 'b']).sort()
        assert m['platforms'][1]['groups'].sort() == list(['a', 'c']).sort()
        assert m['platforms'][2]['groups'].sort() == list(['a', 'c']).sort()

def test_create_playbooks():
    scenario_name = 'test_scenario'
    options = [
        'create',
        '-s', scenario_name,
        '-p', 'playbook1.yml',
        '-p', 'playbook2.yml',
        '--instance-name', 'test',
        '--num-instances', '1',
        '--group', 'group_a',
        '--group', 'group_b',
    ]
    runner = CliRunner()
    with runner.isolated_filesystem():
        molecule = Path('molecule')
        scenario = molecule / scenario_name
        drivers = molecule / '__drivers__'
        converge_yml = scenario / 'converge.yml'
        result = runner.invoke(main, options)
        assert result.exit_code == 0
        assert molecule.is_dir()
        assert drivers.is_dir()
        assert scenario.is_dir()
        assert converge_yml.is_file()
        c = yaml.safe_load(converge_yml.read_text())
        assert c[0]['import_playbook'] == 'playbook1.yml'
        assert c[1]['import_playbook'] == 'playbook2.yml'

