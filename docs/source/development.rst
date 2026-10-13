Development
===========

Source
------

The source code for the **OpenAFS Ansible Collection** is available on
`GitHub`_.

.. _`GitHub`: https://github.com/openafs-contrib/ansible-openafs

.. code-block:: bash

   git clone https://github.com/openafs-contrib/ansible-openafs
   cd ansible-openafs

To install the collection from the source tree, run the command:

.. code-block:: bash

   tox -e install

Testing
-------

The tests are run with `tox`_. The test environments are defined in the
``tox.ini`` file. Run ``tox list`` to show the test environments, including
which ones are run by default.

.. _`tox`: https://tox.wiki

Requirements
~~~~~~~~~~~~

* `tox`_ 4.36 or later (older versions of tox will install the required
  version automatically)
* Python 3; install each of the Python versions in the ``py`` test
  environments shown by ``tox list`` to run all of the unit tests
* `podman`_, to run the role and playbook tests

.. _`podman`: https://podman.io

Unit tests, compatibility tests, and lint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run ``tox`` without arguments to run the default test environments:

.. code-block:: bash

   tox

The lint checks are run first. If the lint checks fail, the remaining test
environments are skipped, so fix the lint errors first.

The test environments are named as follows:

``lint``
   Check the roles and playbooks with ``ansible-lint``.

``pyXY``
   Run the plugin unit tests with Python X.Y, using the latest version of
   ``ansible-core`` available for that Python version.

``ansible-coreXYZ``
   Run a syntax check of the playbooks and the unit tests with
   ``ansible-core`` version X.YZ. For example, ``ansible-core219`` tests with
   ``ansible-core`` 2.19. There is an environment for each supported
   ``ansible-core`` version, from the minimum version given in
   ``meta/runtime.yml``.

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

The ``latest`` test environment runs all of the tests, including the role
and playbook tests, with the latest versions of Python, Ansible, and Molecule:

.. code-block:: bash

   tox -e latest

Running all of the tests takes a long time, since the role and playbook tests
are run for each of the operating systems listed in the test files. Arguments
after ``--`` are passed to ``pytest``. Use the ``-k`` option to select the
tests to run. Use the ``-s`` option to show the full output, and the ``-x``
option to stop on the first failure. For example:

.. code-block:: bash

   tox -e latest -- -k roles
   tox -e latest -- -k playbooks
   tox -e latest -- -s -x -k alma9
   tox -e latest -- -s -x -k "openafs_server and alma9"

The ``sdist`` and ``packages`` scenarios install the OpenAFS release given in
``tests/integration/openafs.yml``. The release source files are downloaded from
`openafs.org`_ and the RPM packages are downloaded from `Sine Nomine`_ the
first time they are needed, and are saved in the
``~/.cache/ansible-openafs/builds`` directory. The ``packages`` scenarios are
skipped for platforms without packages available.

.. _`openafs.org`: https://www.openafs.org
.. _`Sine Nomine`: https://download.sinenomine.net/openafs/

The ``bdist`` and ``source`` scenarios build OpenAFS from a git tag or branch,
which is slow, so they are skipped by default. Use the ``--build`` option to
build OpenAFS and run these scenarios:

.. code-block:: bash

   tox -e latest -- --build openafs-stable-1_8_16_1 -k "openafs_server and alma9"

The output of each test is saved to a log file in the ``.tox/<env>/test-logs``
directory (for example, ``.tox/latest/test-logs``), along with a summary of the
test results in ``summary.txt`` and a JUnit XML report in ``junit.xml``. When
``pytest`` is run without ``tox``, the log files are saved in the
``~/.cache/ansible-openafs/test-logs`` directory.

.. note::

   The OpenAFS kernel module can not be loaded in a container, so the
   ``openafs_client`` and ``openafs_devel_kernel`` role tests and the
   ``default`` and ``cluster`` playbook tests are skipped.

Running Molecule directly
~~~~~~~~~~~~~~~~~~~~~~~~~

The Molecule scenarios are located in the ``extensions/molecule`` directory,
in ``extensions/molecule/<role>/<scenario>`` for the roles and in
``extensions/molecule/playbooks/<scenario>`` for the playbooks. The settings
shared by all of the scenarios are in ``extensions/molecule/config.yml``.

Use ``tox -e dev`` to create a virtualenv with Molecule and the other test
requirements installed, then run ``molecule`` in the collection root
directory:

.. code-block:: bash

   tox -e dev
   source .tox/dev/bin/activate
   molecule test -s openafs_server/default
   molecule test -s playbooks/realm

Molecule installs the collection under test into its own cache directory.

.. warning::

   Do not set ``ANSIBLE_COLLECTIONS_PATH`` to a directory which contains
   your source tree when running Molecule. Some versions of Molecule install
   the collection under test into the first collections path, which removes
   your source tree.

To keep the test instance for debugging, run the scenario in steps:

.. code-block:: bash

   molecule converge -s openafs_server/default
   molecule login -s openafs_server/default
   molecule destroy -s openafs_server/default

Operating systems
~~~~~~~~~~~~~~~~~

Set the ``AFS_TEST_OS`` environment variable to the operating system to be
tested when running ``molecule`` directly. The default is ``alma9``.

.. code-block:: bash

   AFS_TEST_OS=debian13 molecule test -s openafs_server/default

The available operating systems and their base container images are listed
in ``extensions/molecule/resources/podman/images.yml``. To test another
operating system, add the base image for the operating system to that file.

Container images
~~~~~~~~~~~~~~~~

A test image is built for each operating system the first time it is tested,
by installing Python, ``sudo``, and ``systemd`` in the base image. The test
images are named ``localhost/molecule-openafs-<os>`` and are reused by later
test runs. The images are tagged with a checksum of the generated
``Containerfile``, so a new image is built automatically when the
``Containerfile.j2`` template is changed.

Remove a test image to rebuild it with the latest packages:

.. code-block:: bash

   podman images 'localhost/molecule-openafs-*'
   podman rmi localhost/molecule-openafs-alma9:<tag>

Documentation
-------------

The documentation is built with `Sphinx`_. Build the documentation with:

.. _`Sphinx`: https://www.sphinx-doc.org

.. code-block:: bash

   tox -e docs

The HTML pages are written to the ``docs/build/html`` directory.
