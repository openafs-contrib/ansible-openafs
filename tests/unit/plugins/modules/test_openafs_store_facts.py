import pytest

from ansible_collections.openafs_contrib.openafs.plugins.modules.openafs_store_facts import (
    update_facts,
)

testcases = [
    # New facts are added.
    ("update", {}, {"a": 1}, {"a": 1}),
    ("set", {}, {"a": 1}, {"a": 1}),
    # Scalar values are replaced.
    ("update", {"a": 1, "b": 2}, {"a": 3}, {"a": 3, "b": 2}),
    ("set", {"a": 1, "b": 2}, {"a": 3}, {"a": 3, "b": 2}),
    # Dictionary values are merged by update and replaced by set.
    ("update", {"a": {"x": 1, "y": 2}}, {"a": {"y": 3, "z": 4}}, {"a": {"x": 1, "y": 3, "z": 4}}),
    ("set", {"a": {"x": 1, "y": 2}}, {"a": {"y": 3, "z": 4}}, {"a": {"y": 3, "z": 4}}),
    # List values are extended by update and replaced by set.
    ("update", {"a": [1, 2]}, {"a": [3, 4]}, {"a": [1, 2, 3, 4]}),
    ("update", {"a": [1, 2]}, {"a": [2, 3]}, {"a": [1, 2, 3]}),
    ("update", {"a": [1, 2]}, {"a": [1, 2]}, {"a": [1, 2]}),
    ("set", {"a": [1, 2]}, {"a": [3, 4]}, {"a": [3, 4]}),
    # Values of different types are replaced.
    ("update", {"a": [1, 2]}, {"a": {"x": 1}}, {"a": {"x": 1}}),
    ("update", {"a": {"x": 1}}, {"a": "text"}, {"a": "text"}),
]


@pytest.mark.parametrize("state,facts,new_facts,expected", testcases)
def test_update_facts(state, facts, new_facts, expected):
    assert update_facts(facts, new_facts, state) == expected


def test_update_facts_is_idempotent():
    facts = {"a": [1], "b": {"x": 1}}
    new_facts = {"a": [2], "b": {"y": 2}}
    first = update_facts(facts, new_facts, "update")
    second = update_facts(dict(first), new_facts, "update")
    assert second == {"a": [1, 2], "b": {"x": 1, "y": 2}}
