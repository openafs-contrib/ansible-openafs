# Copyright (c) 2020-2021 Sine Nomine Associates
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THE SOFTWARE IS PROVIDED 'AS IS' AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Common functions and classes."""

import os
import pathlib

import click

def default_config_path():
    """
    Determine the afs-scenario configuration default path.
    """
    path = os.environ.get('AFS_SCENARIO_CONFIG', None)
    if not path:
        appdir = click.get_app_dir('afs-scenario')
        path = str(pathlib.Path(appdir) / 'driver.yml')
    return path

class NestedDict:
    """
    Add and lookup elements in a dictionary of dictionaries
    using a dotted key notation.
    """
    def __init__(self, d=None):
        if d is None:
            d = dict()
        if not isinstance(d, dict):
            raise ValueError('d must be a dictionary')
        self.d = d

    def __setitem__(self, key, value):
        self.put(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def put(self, key, value):
        """
        Set a value by dotted key notation.
        Example:
            nd.put('a.b.c', 'hello') -> {'a': {'b': {'c': 'hello'}}}
        """
        def _put(d, keys, value):
            if len(keys) == 1:
                key = keys[0]
                d[key] = value
            else:
                key = keys.pop(0)
                if key not in d:
                    d[key] = {}
                if not isinstance(d[key], dict):
                    raise ValueError("Parent '%s' is not a dictionary." % key)
                else:
                    _put(d[key], keys, value)
        if not hasattr(key, 'split'):
            raise ValueError("Invalid key type: '%s' (%s)" % (key, type(key)))
        _put(self.d, key.split('.'), value)

    def get(self, key):
        """
        Lookup a value by dotted key notation.
        Example:
            nd.put('a.b.c', 'hello') -> {'a': {'b': {'c': 'hello'}}}
            nd.get('a.b.c') -> 'hello'
        """
        def _get(d, subkeys):
            if not isinstance(d, dict):
                raise ValueError("Parent is not a dictionary in key '%s'" % key)
            k = subkeys.pop(0)
            if not subkeys:
                value = d[k]
            else:
                value = _get(d[k], subkeys)
            return value
        if not hasattr(key, 'split'):
            raise ValueError("Invalid key type: '%s' (%s)" % (key, type(key)))
        value = _get(self.d, key.split('.'))
        return value
