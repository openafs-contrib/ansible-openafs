import os
import pathlib


def test_counter(tmp_path):
    mypath = pathlib.Path(__file__).parent
    collections = mypath.parent.parent.parent.parent.parent.parent
    os.environ["ANSIBLE_COLLECTIONS_PATHS"] = str(collections)
    os.environ["ANSIBLE_OPENAFS_COUNTER_DIR"] = str(tmp_path)
    cmd = "ansible-playbook %s/test_counter.yml" % mypath
    print()
    print("ANSIBLE_COLLECTIONS_PATHS:", collections)
    print("Running:", cmd)
    rc = os.system(cmd)
    assert rc == 0
