import json

import pytest

from ansible.errors import AnsibleError
from ansible_collections.openafs_contrib.openafs.plugins.lookup.counter import LookupModule


@pytest.fixture
def counter_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ANSIBLE_OPENAFS_COUNTER_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def counter(counter_dir):
    return LookupModule()


def test_next(counter):
    assert counter.run(["test_a"]) == [1]
    assert counter.run(["test_a"]) == [2]
    assert counter.run(["test_a,next"]) == [3]


def test_current(counter):
    assert counter.run(["test_a,current"]) == [0]
    counter.run(["test_a"])
    assert counter.run(["test_a,current"]) == [1]
    assert counter.run(["test_a,current"]) == [1]


def test_reset(counter):
    counter.run(["test_a", "test_a"])
    assert counter.run(["test_a,reset"]) == [0]
    assert counter.run(["test_a,current"]) == [0]
    assert counter.run(["test_a"]) == [1]


def test_multiple_terms(counter):
    assert counter.run(["test_a", "test_b", "test_c"]) == [1, 1, 1]
    assert counter.run(["test_a", "test_b,next", "test_c,current"]) == [2, 2, 1]


def test_counters_are_saved(counter_dir):
    LookupModule().run(["test_a", "test_b"])
    assert LookupModule().run(["test_a,current"]) == [1]
    saved = json.loads((counter_dir / "counter.json").read_text())
    assert saved == {"test_a": 1, "test_b": 1}


def test_counter_dir_is_created(tmp_path, monkeypatch):
    counter_dir = tmp_path / "missing" / "dir"
    monkeypatch.setenv("ANSIBLE_OPENAFS_COUNTER_DIR", str(counter_dir))
    assert LookupModule().run(["test_a"]) == [1]
    assert (counter_dir / "counter.json").exists()


def test_invalid_operation(counter):
    with pytest.raises(AnsibleError, match="Invalid operation: bogus"):
        counter.run(["test_a,bogus"])
