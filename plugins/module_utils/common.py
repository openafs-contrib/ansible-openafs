#!/usr/bin/python
# Copyright (c) 2020, Sine Nomine Associates
# BSD 2-Clause License


import contextlib               # noqa: E402
import errno                    # noqa: E402
import json                     # noqa: E402
import os                       # noqa: E402
import shutil                   # noqa: E402
import subprocess               # noqa: E402
import syslog                   # noqa: E402
import tempfile                 # noqa: E402


class Logger:
    def __init__(self, name, **kwargs):
        self.name = name
        syslog.openlog(name, 0, syslog.LOG_USER)

    def debug(self, fmt, *args):
        syslog.syslog(syslog.LOG_DEBUG, fmt % (args))

    def info(self, fmt, *args):
        syslog.syslog(syslog.LOG_INFO, fmt % (args))

    def warning(self, fmt, *args):
        syslog.syslog(syslog.LOG_WARNING, fmt % (args))

    def error(self, fmt, *args):
        syslog.syslog(syslog.LOG_ERR, fmt % (args))

    # aliases
    warn = warning
    err = error


@contextlib.contextmanager
def chdir(path):
    """
    Change directory context manager.
    """
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


@contextlib.contextmanager
def tmpdir():
    """
    Temporary directory context manager.
    """
    previous = os.getcwd()
    tmp = tempfile.mkdtemp()
    os.chdir(tmp)
    try:
        yield tmp
    finally:
        os.chdir(previous)
        shutil.rmtree(tmp)


def execute(cmd):
    """
    Execute a command and return stdout as captured string.
    """
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    o, e = proc.communicate()
    rc = proc.returncode
    try:
        output = o.decode()
    except (UnicodeDecodeError, AttributeError):
        pass
    try:
        error = e.decode()
    except (UnicodeDecodeError, AttributeError):
        pass
    if rc:
        message = 'Failed: %s, code %d' % (cmd, rc)
        if error:
            message += '\nError:\n' + error
        raise Exception(message)
    return output


def lookup_facts():
    """
    Return the local facts as a dict.
    """
    try:
        with open('/etc/ansible/facts.d/openafs.fact') as f:
            facts = json.load(f)
    except IOError as e:
        if e.errno == errno.ENOENT:
            facts = {}
        else:
            raise
    return facts


def lookup_fact(name, section=None, default=None):
    """
    Lookup a local fact.
    """
    facts = lookup_facts()
    if section:
        value = facts.get(section, {}).get(name, default)
    else:
        value = facts.get(name, default)
    return value
