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

To build and install the collection from the source tree, run the commands:

.. code-block:: bash

   ansible-galaxy collection build --output-path builds .
   ansible-galaxy collection install --force builds/openafs_contrib-openafs-*.tar.gz

Testing
-------

The tests are run with `tox`_ and the `tox-ansible`_ plugin. The tox
configuration is in the ``pyproject.toml`` file. The ``tox-ansible`` plugin
generates the test environments for the supported Python and ``ansible-core``
versions, and tox installs the plugin automatically when it is needed.

Requirements
~~~~~~~~~~~~

* Linux
* Python 3.11 or later, and the Python versions to be tested
* `tox`_ 4.x
* `podman`_, configured to run rootless containers
* ``git``
* A `Proxmox VE`_ server, for the scenarios which load the OpenAFS kernel
  module. See `Proxmox scenarios`_.

.. _`Proxmox VE`: https://www.proxmox.com/en/proxmox-virtual-environment

Other packages are installed in the tox test environments as needed.

The role and playbook tests run in `podman`_ containers created from a test
image for each operating system. The test images are built from the
``containers/<os>/Containerfile`` files and are named
``localhost/ansible-openafs-<os>``. Build the test images before running the
role and playbook tests:

.. code-block:: bash

   tox -e images

Run ``tox -e images`` again to rebuild the images after changing a
``Containerfile``.

Test environments
~~~~~~~~~~~~~~~~~

To list the test environments, run:

.. code-block:: bash

   tox --ansible -l

The test environments are named ``<type>-py<python>-<ansible-core>``, for
example ``unit-py3.14-2.21``. The test types are:

``unit``
   Run the unit tests in ``tests/unit`` with ``pytest``. This includes a
   syntax check of the playbooks.

``sanity``
   Run ``ansible-test sanity`` on the collection. The sanity test ignore files
   are in ``tests/sanity``.

``molecule``
   Run a role or playbook test with Molecule. See `Role and playbook tests`_.

``galaxy``
   Check the collection with the Galaxy importer.

To run a test environment, use the ``-e`` option:

.. code-block:: bash

   tox --ansible -e unit-py3.14-2.21
   tox --ansible -e sanity-py3.14-2.21

Arguments after ``--`` are passed to ``pytest`` in the ``unit`` environments
and to ``ansible-test sanity`` in the ``sanity`` environments. For example:

.. code-block:: bash

   tox --ansible -e unit-py3.14-2.21 -- -k test_syntax_check
   tox --ansible -e sanity-py3.14-2.21 -- --test pep8

To run all of the unit or sanity test environments in parallel:

.. code-block:: bash

   tox --ansible --matrix-scope unit -p auto
   tox --ansible --matrix-scope sanity -p auto

Role and playbook tests
~~~~~~~~~~~~~~~~~~~~~~~

The role and playbook tests are Molecule scenarios in the
``extensions/molecule`` directory. The scenarios are named
``role_<role>_<variant>`` and ``playbook_<playbook>_<variant>``. Each scenario
lists the operating systems to be tested as Molecule platforms, and Molecule
creates a container for each platform, so the operating systems are tested in
parallel. The scenarios use the Molecule ``podman`` driver from the
`molecule-plugins`_ package.

.. _`molecule-plugins`: https://github.com/ansible-community/molecule-plugins

The ``molecule`` test environments run all of the scenarios, one after
another, with ``molecule test --all``:

.. code-block:: bash

   tox --ansible -e molecule-py3.14-2.21

Arguments after ``--`` are passed to ``molecule test``. For example, to skip a
scenario:

.. code-block:: bash

   tox --ansible -e molecule-py3.14-2.21 -- --exclude role_openafs_server_source

To run a single scenario, run Molecule directly. See `Running Molecule
directly`_.

Do not run more than one ``molecule`` test environment at the same time (for
example with ``tox -p``). The environments use the same container names, so
they would conflict.

The ``role_openafs_server_source`` scenario builds OpenAFS from the
``openafs-stable-1_8_16_1`` git tag by default. Set ``AFS_GIT_VERSION`` to
build a different git tag or branch:

.. code-block:: bash

   AFS_GIT_VERSION=openafs-stable-1_8_x tox --ansible -e molecule-py3.14-2.21

To add an operating system to a scenario, add a platform to the scenario
``molecule.yml`` file. The first platform is a YAML anchor with the settings
shared by all of the platforms, so only the name and image are needed:

.. code-block:: yaml

   platforms:
     - &platform
       name: server-alma10
       image: localhost/ansible-openafs-alma10
       ...
     - <<: *platform
       name: server-debian13
       image: localhost/ansible-openafs-debian13

.. note::

   The OpenAFS kernel module can not be loaded in a container, so the
   scenarios which install the OpenAFS client run on Proxmox virtual
   machines. See `Proxmox scenarios`_. The ``openafs_devel_kernel`` scenario
   installs the kernel headers for the newest kernel in the package
   repositories, since the kernel running in a container is the host kernel.

Proxmox scenarios
~~~~~~~~~~~~~~~~~

The scenarios named ``*_proxmox`` run on virtual machines cloned from a
template on a `Proxmox VE`_ server, with the `molecule-proxmox`_ driver. The
``molecule`` test environments run these scenarios with the others, so a
Proxmox server is needed to run all of the tests. Without one, exclude the
Proxmox scenarios:

.. code-block:: bash

   tox --ansible -e molecule-py3.14-2.21 -- \
       --exclude role_openafs_client_proxmox \
       --exclude playbook_local_install_proxmox \
       --exclude playbook_deploy_cell_proxmox

.. _`molecule-proxmox`: https://molecule-proxmox.readthedocs.io

The Proxmox API connection settings are read from a secrets file, which is
kept outside the source tree. The default location is
``~/.config/molecule/proxmox_secrets.yml``:

.. code-block:: yaml

   api_host: proxmox.example.com
   api_user: molecule@pve
   api_token_id: molecule
   api_token_secret: <secret>

Restrict the permissions of the secrets file with ``chmod 600``. The secrets
file may instead be an executable which prints the settings, for example to
read them from a password manager.

Name the Proxmox platforms with the ``ansible-openafs-`` prefix, for example
``ansible-openafs-client-alma10``, so the test virtual machines are easy to
find on a shared Proxmox server.

The template must have the ``qemu-guest-agent`` installed and enabled, since
the driver gets the virtual machine address from the guest agent. The template
must allow ``ssh`` logins with a key, by a user with passwordless ``sudo``.
Use a separate key pair for the test virtual machines, without a passphrase,
and add the public key to the template:

.. code-block:: bash

   ssh-keygen -t ed25519 -N '' -C molecule-proxmox -f ~/.ssh/molecule_proxmox

Set the following environment variables to override the defaults:

``AFS_PROXMOX_SECRETS``
   The secrets file. Default: ``~/.config/molecule/proxmox_secrets.yml``
``AFS_PROXMOX_NODE``
   The Proxmox node name. Default: ``pve``
``AFS_PROXMOX_SSH_USER``
   The ``ssh`` user. Default: ``molecule``
``AFS_PROXMOX_SSH_IDENTITY_FILE``
   The ``ssh`` private key. Default: ``~/.ssh/molecule_proxmox``
``AFS_PROXMOX_VALIDATE_CERTS``
   Validate the Proxmox API TLS certificate. Default: ``false``
``AFS_PROXMOX_TEMPLATE_ALMA10``
   The AlmaLinux 10 template name. Default: ``alma10``

Running Molecule directly
~~~~~~~~~~~~~~~~~~~~~~~~~

Running Molecule directly is faster when working on a role, and makes it
possible to keep the test containers for debugging. Run the ``molecule``
test environment with ``tox`` once to create it, then activate it and run
``molecule`` in the collection root directory:

.. code-block:: bash

   source .tox/molecule-py3.14-2.21/bin/activate
   export ANSIBLE_COLLECTIONS_PATH=.
   molecule test -s role_openafs_server_default

``ANSIBLE_COLLECTIONS_PATH=.`` is the setting used by ``tox``. It keeps
collections installed in ``~/.ansible/collections`` from being used instead of
the collection in the source tree.

The Molecule ``prerun`` is disabled in ``extensions/molecule/config.yml``,
which is merged into each scenario ``molecule.yml``. The ``tox`` environment
already has the collection and the test requirements installed, and the
prerun would install another copy of the collection in
``~/.ansible/collections``, which is shared by all of the test environments,
so environments run in parallel would race to install it. Do not enable the
prerun.

To test a single platform and keep the container for debugging:

.. code-block:: bash

   molecule test -s role_openafs_server_default -p server-alma10 --destroy never
   molecule login -s role_openafs_server_default -h server-alma10
   molecule converge -s role_openafs_server_default -- --limit server-alma10
   molecule destroy -s role_openafs_server_default

Only ``molecule test`` accepts the ``-p`` option. The other ``molecule``
commands act on all of the platforms in the scenario, but ``converge`` passes
the arguments after ``--`` to ``ansible-playbook``, so ``--limit`` can be used
to converge a single platform. The source tree is installed as an editable
collection, so changes to the roles are used on the next ``converge``.

Setting up a test machine
~~~~~~~~~~~~~~~~~~~~~~~~~

The role and playbook tests take a long time to run on all of the operating
systems, so it is useful to run them on a separate test machine, for example
nightly. To set up a test machine:

1. Install ``podman``, ``git``, and the Python versions to be tested, and
   install ``tox``, for example with ``pipx install tox``.

2. Check that rootless podman works for the test user. The test user needs
   subordinate uid and gid ranges in ``/etc/subuid`` and ``/etc/subgid``:

   .. code-block:: bash

      podman info
      podman run --rm registry.fedoraproject.org/fedora echo ok

3. Raise the inotify instances limit. Each test container runs ``systemd``,
   which uses several inotify instances, and the default limit of 128 per user
   can be reached with as few as 10 containers, depending on what else the
   user is running. When the limit is reached, the test containers exit or
   ``systemd`` fails to start in them.

   .. code-block:: bash

      echo 'fs.inotify.max_user_instances = 1024' | sudo tee /etc/sysctl.d/99-inotify.conf
      sudo sysctl --system

4. To run the tests from ``cron`` or a ``systemd`` timer, enable lingering for
   the test user, so the user ``systemd`` instance and ``XDG_RUNTIME_DIR``
   needed by rootless podman are available without a login session:

   .. code-block:: bash

      sudo loginctl enable-linger $USER

   The tests need ``XDG_RUNTIME_DIR`` to be set. In a ``cron`` job, set it
   with ``export XDG_RUNTIME_DIR=/run/user/$(id -u)``.

5. Clone the repository and build the test images:

   .. code-block:: bash

      git clone https://github.com/openafs-contrib/ansible-openafs
      cd ansible-openafs
      tox -e images

6. Run the tests and save the output:

   .. code-block:: bash

      mkdir -p logs
      tox --ansible -e molecule-py3.14-2.21 > logs/molecule-py3.14-2.21.log 2>&1

   The output ends with a summary which shows which steps of each scenario
   passed and failed, and the Ansible play recap of each step shows which
   platform failed.

To do
~~~~~

The role and playbook tests are a work in progress. The goal for the next
prerelease is to test all of the roles and playbooks on ``alma10`` with the
newest Python and ``ansible-core`` (``molecule-py3.14-2.21``), then to add the
other operating systems and older versions as they pass.

Conventions for the integration tests:

* Use one scenario for each role and playbook variant, with one platform for
  each operating system to be tested. Do not use environment variables to
  select the operating system.
* Each scenario has a ``verify.yml`` which checks the results of the role,
  for example that the services are running. Use the facts saved by the roles
  in ``ansible_local.openafs`` (such as the program paths in ``bins`` and the
  service names) instead of operating system specific values.
* Test the real installs. Do not fake package installs (an experiment with
  fake package modules is on the ``tests-fakes`` branch).
* Fix role bugs found by the tests in the roles, in separate commits from the
  tests, instead of working around them in the tests.
* Never run Molecule or ``ansible-galaxy`` with ``ANSIBLE_COLLECTIONS_PATH``
  set to a directory which contains the source tree.
* The sanity and unit tests must pass. Run ``tox -e format`` after changing
  the Python code.

Scenarios to add for ``alma10``:

Each scenario in ``extensions/molecule`` is run by the ``molecule`` test
environments, so only add a scenario when it is ready to run.

#. ``role_openafs_client_proxmox``: the other client install methods
   (packages, kmod, source).
#. ``role_openafs_client_default``: (optional) test what can be tested in a
   container, for example installing the client and building (not loading)
   the kernel module. Building the kernel module in a container needs:

   * the kernel headers for a kernel version other than the running (host)
     kernel; set ``afs_kernel_version``, as in the
     ``role_openafs_devel_kernel_default`` scenario, and change the
     ``openafs_client`` role to use ``afs_kernel_version`` instead of
     ``ansible_kernel`` (it is used to select the kmod packages);
   * ``configure`` options which point to the installed kernel headers, for
     example ``--with-linux-kernel-headers=/usr/src/kernels/<version>``;
   * a new option for the ``openafs_build`` module to give the kernel version,
     since the module checks that the kernel module was built for the running
     kernel (``verify_kernel_module`` uses ``platform.release()``).

#. ``role_openafs_server_packages``, ``role_openafs_server_sdist``, and
   ``role_openafs_server_bdist``: the other server install methods. These need
   the OpenAFS release files. See ``legacy/tests/release_files.py`` and
   ``legacy/tests/integration/openafs.yml``, which download the source
   distribution from openafs.org and the RPM packages from Sine Nomine.
#. ``role_openafs_robotserver_default`` and
   ``playbook_deploy_robotserver_default``: low priority, since the
   ``openafs_robotserver`` role is planned to be moved to a separate
   repository.

Other operating systems and versions:

#. Add the other operating systems to each scenario. The
   ``role_openafs_krbserver_default`` and ``role_openafs_krbclient_default``
   scenarios passed on all of the test images before they were reduced to
   ``alma10`` (except the ``krbclient`` scenario on ``opensuse16``, which needs
   the untested ``roles/openafs_krbclient/vars/openSUSE_Leap-16.yaml`` fix).
#. The ``role_openafs_devel_kernel_default`` scenario finds the newest
   ``kernel-devel`` package with ``dnf``. Add the equivalent for ``apt`` and
   ``zypper``.
#. Run the scenarios with the oldest supported versions, for example
   ``molecule-py3.11-2.19``.

Known bugs:

* ``openafs_build_packages`` and ``openafs_build_redhat_rpms``: the ``build``
  option checks for ``module``, but the choice is ``modules``, so
  ``build: modules`` runs ``rpmbuild`` without a ``-b`` option. The branch
  also sets ``build_modules 0`` instead of ``1``. Add unit tests for the
  ``rpmbuild`` arguments.
* ``openafs_store_facts``: ``state: update`` appends a list value to an
  existing list as a single element, instead of extending the list.
* ``openafs_build_redhat_rpms`` looks like an older copy of the RPM support in
  ``openafs_build_packages``.

Other work:

* Write the module unit tests in ``tests/unit/plugins/modules`` (they are
  stubs now).
* Add a ``lint`` test environment for ``ansible-lint``.
* Remove the ``legacy`` directory when the new tests replace it.
* ``pytest-ansible`` is deprecated (end of life December 2026). When
  ``tox-ansible`` stops using it, remove the ``/collections/`` entry from
  ``.gitignore``.
* Speed up the tests, for example by caching the packages in the test images.
* Run the scenarios in parallel. Each scenario has its own containers and
  podman network, but the Molecule ``--workers`` option runs all of the
  scenarios on the instances of the ``default`` scenario, so it can not be
  used with these scenarios.

Code formatting
---------------

The Python code is formatted with `black`_. To format the code, run:

.. _`black`: https://black.readthedocs.io

.. code-block:: bash

   tox -e format

Documentation
-------------

The documentation is built with `Sphinx`_. To build the documentation, run:

.. _`Sphinx`: https://www.sphinx-doc.org

.. code-block:: bash

   python3 -m venv .venv
   .venv/bin/pip install -r docs/requirements.txt
   .venv/bin/sphinx-build -M html docs/source docs/build

The HTML pages are written to the ``docs/build/html`` directory.


.. _`tox`: https://tox.wiki
.. _`tox-ansible`: https://github.com/ansible/tox-ansible
.. _`podman`: https://podman.io
