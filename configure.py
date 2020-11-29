#!/usr/bin/env python
# Copyright (c) 2020 Sine Nomine Associates

import os
import argparse

driver_option_names = [
    'driver',
    'driver_provider',
    'driver_libvirt_host',
    'driver_libvirt_prepare',
    'driver_libvirt_logfile',
    'driver_libvirt_loglevel',
    'driver_libvirt_python_interpreter',
]

def config_file(config, name):
    with open('%s.in' % name, 'r') as f:
        text = f.read()
    for key, value in config.items():
        text = text.replace('@%s@' % key.upper(), value)
    with open(name, 'w') as f:
        f.write(text)
        print('Wrote:', name)

def config_files(config, *names):
    for name in names:
        config_file(config, name)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--topdir', default=os.getcwd())
    p.add_argument('--python', default='python')
    p.add_argument('--cookiecutter', default='cookiecutter')
    p.add_argument('--instance_prefix', default='m-')
    p.add_argument('--update-kernel', default='no')
    for d in driver_option_names:
        p.add_argument('--%s' % d.replace('_', '-'), default='')
    config = vars(p.parse_args())

    # Format extra context parameters for cookiecutter command line.
    driver_options = []
    for d in driver_option_names:
        if config[d]:
            driver_options.append('='.join((d, config[d])))
    config['driver_options'] = ' '.join(driver_options)

    config_files(
        config,
        'Makefile',
        'roles/openafs_cell/Makefile',
        'roles/openafs_client/Makefile',
        'roles/openafs_common/Makefile',
        'roles/openafs_devel/Makefile',
        'roles/openafs_krbclient/Makefile',
        'roles/openafs_krbserver/Makefile',
        'roles/openafs_robotest/Makefile',
        'roles/openafs_server/Makefile',
        'tests/Makefile',
        'tests/playbooks/Makefile',
    )

if __name__ == '__main__':
    main()
