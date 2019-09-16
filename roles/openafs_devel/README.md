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
