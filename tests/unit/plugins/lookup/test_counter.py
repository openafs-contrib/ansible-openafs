import os
import pathlib


def test_counter(tmp_path):
    mypath = pathlib.Path(__file__).parent
    root = mypath.parent.parent.parent.parent
    # Symlink this collection into a temporary collections path, so the
    # source tree may be located in any directory.
    collections = tmp_path / "collections"
    link = collections / "ansible_collections" / "openafs_contrib" / "openafs"
    link.parent.mkdir(parents=True)
    link.symlink_to(root)
    os.environ["ANSIBLE_COLLECTIONS_PATH"] = str(collections)
    os.environ["ANSIBLE_OPENAFS_COUNTER_DIR"] = str(tmp_path)
    cmd = "ansible-playbook %s/test_counter.yml" % mypath
    print()
    print("ANSIBLE_COLLECTIONS_PATH:", collections)
    print("Running:", cmd)
    rc = os.system(cmd)
    assert rc == 0
