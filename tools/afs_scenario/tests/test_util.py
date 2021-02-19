from afs_scenario.util import NestedDict
import pytest

def test_nd_put():
    nd = NestedDict()
    nd['a.x'] = 'one'
    nd['a.y'] = 'two'
    nd['a.z.u'] = 'three'
    nd['b'] = 'four'
    assert nd.d['a']['x'] == 'one'
    assert nd.d['a']['y'] == 'two'
    assert nd.d['a']['z']['u'] == 'three'
    assert nd.d['b'] == 'four'
    with pytest.raises(ValueError):
        nd['b.a'] = 'bogus'

def test_nd_get():
    d = {
        'a': {
            'x': {
                'u': 'one',
                'v': 'two'
            },
            'y': {
                'u': 'three',
            },
        },
        'b': 'four',
    }
    nd = NestedDict(d)
    assert nd['a.x.u'] == 'one'
    assert nd['a.x.v'] == 'two'
    assert nd['a.y.u'] == 'three'
    assert nd['b'] == 'four'
    with pytest.raises(KeyError):
        nd['notfound']
    with pytest.raises(KeyError):
        nd['not.found']

def test_nd_update():
    test_config = {
        'test': {
            'one': 'this is value 1',
            'two': 'yes',
        },
    }
    nd = NestedDict(test_config)
    nd['test.one'] = 'changed'
    nd['test.three'] = 'added'

    assert nd.d['test']['one'] == 'changed'
    assert nd.d['test']['two'] == 'yes'
    assert nd.d['test']['three'] == 'added'

def test_nd_contains():
    nd = NestedDict()
    nd['test.one'] = 'one'
    nd['test.three'] = 'three'
    assert 'test.one' in nd
    assert not 'test.two' in nd
    with pytest.raises(ValueError):
        0 in nd
