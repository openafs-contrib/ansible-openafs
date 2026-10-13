Development
===========

Source
------

The source code for the **OpenAFS Ansible Collection** is available on
`GitHub`_. Ansible requires collections to be located in a directory named
``ansible_collections/<namespace>/<name>``, so clone the repository into an
``ansible_collections/openafs_contrib/openafs`` directory:

.. _`GitHub`: https://github.com/openafs-contrib/ansible-openafs

.. code-block:: bash

   mkdir -p collections/ansible_collections/openafs_contrib
   cd collections/ansible_collections/openafs_contrib
   git clone https://github.com/openafs-contrib/ansible-openafs openafs
   cd openafs

To build and install the collection from the source code:

.. code-block:: bash

   tox -e install

To use the collection directly from the source tree instead of installing
it, set the ``ANSIBLE_COLLECTIONS_PATH`` environment variable to the
top-level ``collections`` directory:

.. code-block:: bash

   export ANSIBLE_COLLECTIONS_PATH=/path/to/collections

Testing
-------

The tests are run with `tox`_. The test environments are defined in the
``tox.ini`` file. Run ``tox list`` to show the test environments, including
which ones are run by default.

.. _`tox`: https://tox.wiki

Requirements
~~~~~~~~~~~~

* `tox`_ 4.0 or later
* Python 3; install each of the Python versions in the ``py`` test
  environments shown by ``tox list`` to run all of the unit tests
* `podman`_, to run the role and playbook tests

.. _`podman`: https://podman.io

Unit tests, compatibility tests, and lint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run ``tox`` without arguments to run the default test environments:

.. code-block:: bash

   tox

The test environments are named as follows:

``pyXY``
   Run the plugin unit tests with Python X.Y, using the latest version of
   ``ansible-core`` available for that Python version.

``ansible-coreXYZ``
   Run the unit tests and a syntax check of the playbooks with
   ``ansible-core`` version X.YZ. For example, ``ansible-core219`` tests with
   ``ansible-core`` 2.19. Environments for some older versions are defined,
   but are not run by default.

``lint``
   Check the roles and playbooks with ``ansible-lint``.

To run a single test environment, use the ``-e`` option:

.. code-block:: bash

   tox -e ansible-core219

Run the test environments in parallel with the ``-p`` option:

.. code-block:: bash

   tox -p auto

Role and playbook tests
~~~~~~~~~~~~~~~~~~~~~~~

The roles and playbooks are tested with `Molecule`_. The test instances are
created as `podman`_ containers running systemd, so the tests can be run on
a development machine without any other test infrastructure.

.. _`Molecule`: https://docs.ansible.com/projects/molecule/

Run the role tests:

.. code-block:: bash

   tox -e roles

Run the playbook tests:

.. code-block:: bash

   tox -e playbooks

The tests are run for each of the operating systems listed in the test files.
Arguments after ``--`` are passed to ``pytest``. Use the ``-k`` option to
select tests by name and operating system, and the ``-x`` option to stop on
the first failure:

.. code-block:: bash

   tox -e roles -- -k "openafs_devel and alma9" -x

The output of each test is saved to a log file in the ``.tox/<env>/test-logs``
directory (for example, ``.tox/roles/test-logs``), along with a summary of the
test results in ``summary.txt`` and a JUnit XML report in ``junit.xml``.

.. note::

   The OpenAFS kernel module can not be loaded in a container, so the
   ``openafs_client`` and ``openafs_devel_kernel`` role tests and the
   ``default`` and ``cluster`` playbook tests are skipped.

Running Molecule directly
~~~~~~~~~~~~~~~~~~~~~~~~~

The Molecule scenarios are located in the ``molecule`` directory of each role
and in the ``extensions/molecule`` directory for the playbooks. Use
``tox -e dev`` to create a virtualenv with Molecule and the other test
requirements installed, then run ``molecule`` in the role directory (or the
``extensions`` directory for the playbook scenarios):

.. code-block:: bash

   tox -e dev
   source .tox/dev/bin/activate
   export ANSIBLE_COLLECTIONS_PATH=/path/to/collections
   cd roles/openafs_server
   molecule test -s default

To keep the test instance for debugging, run the scenario in steps:

.. code-block:: bash

   molecule converge -s default
   molecule login -s default
   molecule destroy -s default

Operating systems
~~~~~~~~~~~~~~~~~

Set the ``AFS_TEST_OS`` environment variable to the operating system to be
tested when running ``molecule`` directly. The default is ``alma9``.

.. code-block:: bash

   AFS_TEST_OS=debian13 molecule test -s default

The available operating systems and their base container images are listed
in ``extensions/molecule/resources/podman/images.yml``. To test another
operating system, add the base image for the operating system to that file.

Container images
~~~~~~~~~~~~~~~~

A test image is built for each operating system the first time it is tested,
by installing Python, ``sudo``, and ``systemd`` in the base image. The test
images are named ``localhost/molecule-openafs-<os>`` and are reused by later
test runs. Remove a test image to rebuild it with the latest packages:

.. code-block:: bash

   podman images 'localhost/molecule-openafs-*'
   podman rmi localhost/molecule-openafs-alma9

Documentation
-------------

The documentation is built with `Sphinx`_. Build the documentation with:

.. _`Sphinx`: https://www.sphinx-doc.org

.. code-block:: bash

   tox -e docs

The HTML pages are written to the ``docs/build/html`` directory.
