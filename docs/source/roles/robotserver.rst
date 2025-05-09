openafs_robotserver - Robotframework Remote Server
=================================================

Description
-----------

Install the Robot Framework remote server on test nodes for distributed
integration testing.


Variables
---------

afs_robotserver_virtualenv
  Specifies the path to install the robot server on the test node.

  Default: ``/opt/robotserver``

afs_robotserver_user
  Specifies the user name the robot server runs as.  This user will
  be created if it does not exist.

  Default: ``robot``

afs_robotserver_group
  Specifies the group name the robot user belongs to. This group will
  be created if it does not exist.

  Default: ``robot``

afs_robotserver_library
  Specifies the Python package name of the keyword library to install from
  PyPI.  Specify a the package name and optionally the version specifier, or the
  URL of the package file or the path of the package file already present on the
  remote node.

  Default: ``robotframework_openafslibrary``
