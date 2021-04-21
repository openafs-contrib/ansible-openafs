.. _openafs_wait_for_registration_module:


openafs_wait_for_registration -- Wait for the fileserver VLDB registration
==========================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Wait for the fileserver VLDB registration to be completed.






Parameters
----------

  timeout (optional, int, 600)
    Maximum time to wait in seconds.


  delay (optional, int, 0)
    Number of seconds to delay before waiting.


  sleep (optional, int, 20)
    Number of seconds to wait between retries.


  signal (optional, bool, True)
    If true, issue a XCPU signal to the fileserver to force it to resend the VLDB registration after ``sleep`` seconds has expired.

    By default, the fileserver will retry the VLDB registration every 5 minutes untill the registration succeeds. This option can be used to force the retry to happen sooner. As a side-effect, XCPU signal will trigger a dump of the fileserver hosts and callback tables, so this option must be used with caution.









Examples
--------

.. code-block:: yaml+jinja

    
    - name: Wait for fileserver registration
      openafs_contrib.openafs.openafs_wait_for_registration:
        sleep: 10
        timeout: 600
        signal: no
      when:
        - afs_is_fileserver





Status
------




- This module is not guaranteed to have a backwards compatible interface. *[preview]*


- This module is maintained by community.



Authors
~~~~~~~

- Michael Meffie

