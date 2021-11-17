.. _counter_module:


counter -- Persistent counters.
===============================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Increment named integer counters.

Counter values are saved in a json file on the controller. The default location of the counter file is ``~/.ansible/counter.json`` Set the ``ANSIBLE_OPENAFS_COUNTER_DIR`` environment variable to specify an alternate location.

By default, the the :ref:`counter <counter_module>` lookup plugin increments then returns the incremented counter value.

Specify the ``,current`` suffix on the counter name to retrieve the current counter value without incrementing the counter.

Specify the ``,reset`` suffix on the counter name to reset the counter value to zero.

File locking used for mutual exclusion in case more than one playbook is running at a time.






Parameters
----------

  _terms (True, any, None)
    list of counter names, in the form *<name>[,<operation>]*, where *<name>* is the counter name and *<operation>* is one of ``next``, ``current``, ``reset``

    The default operation is ``next``









Examples
--------

.. code-block:: yaml+jinja

    
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



Return Values
-------------

_list (, list, )
  List of counter values.





Status
------





Authors
~~~~~~~

- Michael Meffie

