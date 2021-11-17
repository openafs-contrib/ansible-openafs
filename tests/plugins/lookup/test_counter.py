
import os
import pathlib


def test_counter():
    mypath = pathlib.Path(__file__).parent
    collections = mypath.parent.parent.parent.parent.parent.parent
    os.environ['ANSIBLE_COLLECTIONS_PATHS'] = str(collections)
    cmd = "ansible-playbook %s/test_counter.yml" % mypath
    print()
    print('ANSIBLE_COLLECTIONS_PATHS:', collections)
    print('Running:', cmd)
    rc = os.system(cmd)
    assert rc == 0
