#!/usr/bin/python
# Copyright (c) 2020, Sine Nomine Associates
# BSD 2-Clause License


def _od2a(options, prefix=None):
    args = []
    for k, v in options.items():
        if prefix:
            args.append(_o2a(k, v, prefix=prefix))
        elif k in ('enable', 'disable', 'with', 'without'):
            if isinstance(v, dict):
                args.extend(_od2a(v, prefix=k))
            elif isinstance(v, list):
                args.extend(_ol2a(v, prefix=k))
            else:
                args.append(_o2a(v, prefix=k))
        else:
            args.append(_o2a(k, v))
    return args


def _ol2a(options, prefix=None):
    args = []
    for v in options:
        if isinstance(v, dict):
            args.extend(_od2a(v, prefix=prefix))
        else:
            args.append(_o2a(v, prefix=prefix))
    return args


def _o2a(name, value=None, prefix=None):
    if prefix:
        name = '%s-%s' % (prefix, name)
    if not value:
        arg = '--%s' % name
    elif isinstance(value, (dict, list)):
        raise ValueError('Unexpected dict or list: %s' % name)
    elif value is True:
        arg = '--%s' % (name)
    else:
        arg = '--%s=%s' % (name, value)
    return arg


def options_to_args(options):
    """ Convert option dictionary to a list of command line arguments.

    Special handling for the enable, disable, with, without keys. Treat
    these keys (at just the top-level) as a tree of options so we can make
    the yaml look nicer.
    """
    args = []
    if isinstance(options, dict):
        args.extend(_od2a(options))
    elif isinstance(options, list):
        args.extend(_ol2a(options))
    else:
        args.append(_o2a(options))
    return args
