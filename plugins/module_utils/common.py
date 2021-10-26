#!/usr/bin/python
# Copyright (c) 2020, Sine Nomine Associates
# BSD 2-Clause License


import syslog                   # noqa: E402


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
