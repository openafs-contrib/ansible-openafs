# Ansible Role: OpenAFS client

Install and configure OpenAFS clients.

## Role Variables

The URL of a yum repo containing OpenAFS client packages for the `package-manager` install method.

    afs_client_install_dkms: no

Install kernel module with DKMS for the `package-manager` install method.

    afs_cacheinfo_mount: /afs
    afs_cacheinfo_cache: /usr/vice/cache
    afs_cacheinfo_size: 50000

The OpenAFS cache configuration parameters; the AFS filesystem mount point, the
cache partition, and the cache manager cache size.  The cache partition should
already exist.

    afs_afsd_opts: -dynroot -fakestat -afsdb

The OpenAFS cache manager startup options.

License
-------

BSD

## Author Information

Copyright (c) 2018-2019 Sine Nomine Associates

[1]: https://github.com/openafs-contrib/ansible-role-openafs-devel
