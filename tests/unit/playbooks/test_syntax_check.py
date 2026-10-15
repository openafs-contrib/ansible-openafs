import pathlib
import subprocess

import pytest

PLAYBOOKS_PATH = pathlib.Path(__file__).parents[3] / "playbooks"

# Inventory with the groups used by the playbooks, to avoid warnings about
# unknown host patterns.
INVENTORY = """\
all:
  hosts:
    localhost:
  children:
    afs_kdcs:
    afs_databases:
    afs_fileservers:
    afs_clients:
    afs_admin_client:
"""


@pytest.mark.parametrize(
    "playbook",
    [
        "deploy_cell",
        "deploy_realm",
        "deploy_robotserver",
        "local_devel",
        "local_install",
    ],
)
def test_syntax_check(tmp_path, playbook):
    inventory = tmp_path / "inventory.yaml"
    inventory.write_text(INVENTORY)
    cmd = [
        "ansible-playbook",
        "--syntax-check",
        "-i",
        inventory,
        PLAYBOOKS_PATH / f"{playbook}.yaml",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
