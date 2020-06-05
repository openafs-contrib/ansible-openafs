# Ansible Role: OpenAFS development

Install development packages and provide tasks to build an OpenAFS binary
distribution from source code.

## Role Variables

    afs_devel_build_server: yes

Build the server components.

    afs_devel_build_client: yes

Build the client components, including the OpenAFS kernel module.

    afs_devel_builddir: "/usr/local/src/openafs"

The path of the directory to perform the build.

    afs_devel_destdir: "/tmp/openafs"

The path of the directory to place the generated binary distribution.

    afs_devel_fetch_method: "git"

The arguments used for configuring the build can be overridden by setting
the following variables

    afs_devel_configure_opts: - configure options used for both client and server
    afs_devel_configure_env:  - environment settings used for both client and server

    afs_devel_client_configure_opts: - configure options specific for client builds
    afs_devel_client_configure_env:  - environment settings specific for client builds

    afs_devel_server_configure_opts: - configure options specific for server builds
    afs_devel_server_configure_env:  - environment settings specific for server builds

    The order these are used are:
        - If defined, use the client/server specific settings.
        - Otherwise use the 'afs_devel_configure_' if defined.
        - If neither are defined use the built in defaults.

The method to obtain the source code. One of 'git', or 'none' (or 'skip')
Specify 'none' (or 'skip') to skip this stage.

    afs_devel_git_repo: "https://github.com/openafs/openafs"

The git url to be used to checkout the source code.

    afs_devel_git_ref: "master"

The git branch or tag to be checked out.

## License

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates
