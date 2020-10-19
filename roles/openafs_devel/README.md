# Ansible Role: OpenAFS development

Install development packages and provide modules to build an OpenAFS binary
distribution from source code.

## Role Variables

    afs_devel_oracle_key: $HOME/.certs/pkg.oracle.com.key.pem
    afs_devel_oracle_cert: $HOME/.certs/pkg.oracle.com.certificate.pem

Keys for Solaris Studio installation.

## Modules

    openafs_build: Build OpenAFS binaries
    openafs_install: Install OpenAFS binaries

## License

BSD

## Author Information

Copyright (c) 2018-2020 Sine Nomine Associates
