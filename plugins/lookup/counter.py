from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
  name: counter
  short_description: Persistent counters.
  description:
    - Increment named integer counters.

    - Counter values are saved in a json file on the controller. The default
      location of the counter file is C(~/.ansible/counter.json) Set the
      C(ANSIBLE_OPENAFS_COUNTER_DIR) environment variable to specify an
      alternate location.

    - By default, the the M(counter) lookup plugin increments then returns
      the incremented counter value.

    - Specify the C(,current) suffix on the counter name to retrieve the
      current counter value without incrementing the counter.

    - Specify the C(,reset) suffix on the counter name to reset the counter
      value to zero.

    - File locking used for mutual exclusion in case more than one playbook is
      running at a time.

  options:
    _terms:
      description:
        - list of counter names, in the form I(<name>[,<operation>]), where
          I(<name>) is the counter name and I(<operation>) is one of
          C(next), C(current), C(reset)
        - The default operation is C(next)
      required: True
  author: Michael Meffie
"""

EXAMPLES = """
- name: "Lookup the current value of test_a."
  debug:
    msg: "{{ lookup('openafs_contrib.openafs.counter', 'test_a,current') }}"

- name: "Increment counter test_a."
  debug:
    msg: "{{ lookup('openafs_contrib.openafs.counter', 'test_a') }}"

- name: "Increment counters using 'with_' syntax."
  debug:
    var: item
  with_openafs_contrib.openafs.counter:
    - test_a
    - test_b
    - test_c

- name: "Reset counters using 'with_' syntax."
  assert:
    that: item == 0
  with_openafs_contrib.openafs.counter:
    - test_a,reset
    - test_b,reset
    - test_c,reset
"""

RETURN = """
  _list:
    description: List of counter values.
    type: list
    elements: int
"""

import contextlib     # noqa: E402
import errno          # noqa: E402
import fcntl          # noqa: E402
import json           # noqa: E402
import os             # noqa: E402

from ansible.plugins.lookup import LookupBase  # noqa: E402
from ansible.errors import AnsibleError        # noqa: E402


@contextlib.contextmanager
def lock(filename):
    with open(filename, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield f
        fcntl.flock(f, fcntl.LOCK_UN)


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        ret = []
        try:
            self.init_paths()
            for term in terms:
                if ',' in term:
                    name, op = term.split(',', 1)
                else:
                    name, op = term, 'next'
                with lock(self.lockfile):
                    if op == 'next':
                        value = self.get_next(name)
                    elif op == 'current':
                        value = self.get_current(name)
                    elif op == 'reset':
                        value = self.reset(name)
                    else:
                        raise ValueError('Invalid operation: %s' % (op))
                    ret.append(value)
        except Exception as e:
            raise AnsibleError(e)
        return ret

    def init_paths(self):
        directory = os.path.expanduser(os.getenv(
                      'ANISIBLE_OPENAFS_COUNTER_DIR', '~/.ansible'))
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.lockfile = os.path.join(directory, 'counter.lock')
        self.filename = os.path.join(directory, 'counter.json')

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                self.counters = json.load(f)
        except IOError as e:
            if e.errno == errno.ENOENT:
                self.counters = {}
            else:
                raise
        return self.counters

    def store(self):
        with open(self.filename, 'w') as f:
            json.dump(self.counters, f, indent=4)
        return 0

    def reset(self, name):
        self.load()
        self.counters[name] = 0
        self.store()
        return 0

    def get_current(self, name):
        self.load()
        return self.counters.get(name, 0)

    def get_next(self, name):
        self.load()
        value = self.counters.get(name, 0) + 1
        self.counters[name] = value
        self.store()
        return value
