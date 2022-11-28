.. _openafs_service_properties_module:


openafs_service_properties -- Manage Solaris service properties.
================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Set service properties using the Solaris svc commands.






Parameters
----------

  state (optional, any, None)
    If ``present`` the ``property`` will be set to the given ``value``.

    If ``absent`` the ``property`` will be deleted.


  service (True, any, None)
    The SMF service name.


  instance (optional, any, default)
    The SMF service instance name.


  property (True, any, None)
    The property name.


  value (optional, any, None)
    The property value. Requiried when ``state`` is ``present``.


  single (optional, bool, True)
    If True, the value is a single string.

    If False, the value is a space separated list of strings.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Set client startup arguments.
      openafs_service_property:
        state: present
        service: network/openafs/client
        instance: default
        property: afsd/arguments
        value: -dynroot -fakestat -afsd
        single: no



Return Values
-------------

service (always, str, )
  SMF service name


instance (always, str, )
  SMF service instance


property (always, str, )
  SMF service property name


value (on success, str, )
  SMF service property value


single (always, bool, )
  Value is a single string





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

