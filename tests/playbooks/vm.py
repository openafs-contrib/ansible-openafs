#!/usr/bin/env python3
# Copyright (c) 2020 Sine Nomine Associates

"""
Create guests from pre-existing template images.

Requires: libvirt, virt-clone, virst-sysprep
"""

import argparse
import libvirt
import logging
import os
import sh
import sys
import xml.etree.ElementTree as ET

log = logging.getLogger(__name__)
sudo = sh.Command('sudo')
virsh = sh.Command('virsh')
virt_clone = sh.Command('virt-clone')
virt_sysprep = sh.Command('virt-sysprep')

# Avoid printing errors to the console. Exceptions are logged below.
def libvirt_callback(userdata, err):
    pass

libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)

def query_domain(name, key='info'):
    """
    Query libvirt for guest information.

    name: name of the domain (guest)
    key: one of 'check', 'mac', 'bridge', 'disk_files'
    """
    assert key in ('check', 'mac', 'bridge', 'disk_files')
    uri = os.environ.get('LIBVIRT_DEFAULT_URI')
    try:
        conn = libvirt.open(uri)
        domain = conn.lookupByName(name)
        xml = domain.XMLDesc()
        log.debug(xml)
        if key == 'check':
            return True
        root = ET.fromstring(xml)
        info = {'disk_files': []}
        for interface in root.findall('devices/interface[@type="bridge"]'):
            info['mac'] = interface.find('mac').get('address')
            info['bridge'] = interface.find('source').get('bridge')
        for device in root.findall('devices/disk[@type="file"]'):
            info['disk_files'].append(device.find('source').get('file'))
        conn.close()
        log.debug("Domain '%s' info: %s", name, info)
        return info.get(key)
    except libvirt.libvirtError as e:
        if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
            if key != 'check':
                log.info("Domain '%s' not found.", name)
            return None
        else:
            raise e

def query_pool(name):
    """
    Query libvirt for a pool path.

    name: name of the pool to query
    """
    path = None
    uri = os.environ.get('LIBVIRT_DEFAULT_URI')
    conn = libvirt.open(uri)
    for pool in conn.listAllStoragePools():
        xml = pool.XMLDesc()
        root = ET.fromstring(xml)
        if name == root.find('name').text:
            log.debug(xml)
            path = root.find('target/path').text
    conn.close()
    log.info("Pool '%s' path is '%s'.", name, path)
    return path

def query_networks(bridge):
    """
    Query libvirt for network info.

    Find the address for the network with this bridge name.
    """
    uri = os.environ.get('LIBVIRT_DEFAULT_URI')
    conn = libvirt.open(uri)
    networks = []
    for network in conn.listAllNetworks():
        xml = network.XMLDesc()
        log.debug(xml)
        root = ET.fromstring(xml)
        info = dict()
        info['bridge'] = root.find('bridge').get('name')
        info['address'] = root.find('ip').get('address')
        networks.append(info)
    conn.close()
    for network in networks:
        if bridge and bridge == network.get('bridge'):
            return network.get('address')
    return None

def create_guest(name,
                 template,
                 path='/var/lib/libvirt/images',
                 dns='example.com',
                 update_resolver=True):
    """
    Create a guest from a pre-existing template. Save and reuse the
    assigned mac address if the guest is recreated.
    """
    log.debug('create_guest: name=%s, template=%s, path=%s, dns=%s',
              name, template, path, dns)

    mac_path = os.environ.get('VM_MAC_PATH', '~/.vm')
    mac_file = os.path.expanduser('%s/%s.mac' % (mac_path, name))

    image = '%s/%s.qcow2' % (path, name)
    if os.path.exists(image):
        log.info("Skipping create; image '%s' already exists.", image)
        return 0

    clone_args = dict(
        quiet=True,
        auto_clone=True,
        o=template,
        n=name,
        f=image,
    )

    # Add --mac option from the last generation.
    if os.path.exists(mac_file):
        with open(mac_file, 'r') as f:
            clone_args['mac'] = f.read().strip()

    log.info("Cloning template '%s' to guest '%s'.", template, name)
    log.debug("clone_args='%s'", clone_args)
    virt_clone(**clone_args)

    if not os.path.exists(image):
        raise AssertionError("Failed to create image '%s'.", image)

    # Save our mac address for the next generation.
    mac = query_domain(name, 'mac')
    if mac and mac != clone_args.get('mac'):
        log.debug("Writing '%s' to file '%s'.", mac, mac_file)
        with open(mac_file, 'w') as f:
            f.write('%s\n' % mac)

    # The new image will be owned by root when the libvirt uri is
    # 'qemu:///system'.  Make it writable so we can sysprep it.
    if not os.access(image, os.R_OK | os.W_OK):
        log.info("Changing file '%s' ownership to '%d'.", image, os.geteuid())
        sudo('chown', os.geteuid(), image)
        os.chmod(image, 0o664)

    log.info("Preparing image '%s'.", image)
    virt_sysprep(
        quiet=True,
        add=image,
        hostname='%s.%s' % (name, dns),
        operations='defaults,-ssh-hostkeys,-ssh-userdir')

    log.info("Starting guest '%s'.", name)
    virsh('autostart', name)
    virsh('start', name)

    # Optionally, update the local systemd resolver.
    if update_resolver:
        if not dns:
            log.error("Unable to update resolver; dns name is missing.")
            return 1
        bridge = query_domain(name, key='bridge')
        if not bridge:
            log.error("Unable to update resolver; bridge for domain '%s' not found.", name)
            return 1
        address = query_networks(bridge)
        if not address:
            log.error("Unable to update resolver; gatawate address not found for bridge '%s'.", bridge)
            return 1
        log.info("Adding '%s' to systemd-resolved: '%s' (%s).", dns, bridge, address)
        sudo('systemd-resolve', '--interface', bridge, '--set-dns', address, '--set-domain', dns)

def destroy_guest(name):
    """
    Destroy a guest and remove the disk files.
    """
    log.debug('destroy_guest: name=%s', name)

    disk_files = query_domain(name, 'disk_files')
    if disk_files is None:
        log.info("Skipping destroy; domain '%s' not found.", name)
        return 0

    log.info("Destroying domain '%s'.", name)
    try:
        virsh('destroy', name)
    except sh.ErrorReturnCode as ec:
        if not b'domain is not running' in ec.stderr:
            raise ec

    for disk_file in disk_files:
        pool = None
        volname = None
        for line in virsh('vol-pool', disk_file, _iter=True):
            line = line.strip()
            if line:
                pool = line
        for line in virsh('vol-info', disk_file, _iter=True):
            if line.startswith('Name:'):
                _, volname = line.split(':', 1)
                volname = volname.strip()
        log.debug("pool='%s', volname='%s'", pool, volname)
        if pool and volname:
            log.info("Deleting volume '%s' in pool '%s'.", volname, pool)
            virsh('vol-delete', volname, pool)

    log.info("Undefining domain '%s'.", name)
    virsh('undefine', name)

def set_verbosity(verbose):
    """
    Set the logging verbosity.
    """
    if verbose < 1:
        log.setLevel(logging.WARNING)
        for module in (sh, libvirt):
            handler = logging.getLogger(module.__name__)
            handler.setLevel(logging.ERROR)
    elif verbose == 1:
        log.setLevel(logging.INFO)
        for module in (sh, libvirt):
            handler = logging.getLogger(module.__name__)
            handler.setLevel(logging.ERROR)
    elif verbose == 2:
        log.setLevel(logging.DEBUG)
        for module in (sh, libvirt):
            handler = logging.getLogger(module.__name__)
            handler.setLevel(logging.WARNING)
    elif verbose == 3:
        log.setLevel(logging.DEBUG)
        for module in (sh, libvirt):
            handler = logging.getLogger(module.__name__)
            handler.setLevel(logging.INFO)
    else:
        log.setLevel(logging.DEBUG)
        for module in (sh, libvirt):
            handler = logging.getLogger(module.__name__)
            handler.setLevel(logging.DEBUG)

def main():
    """
    Command line interface to create_guest and destroy_guest.
    """
    logging.basicConfig()

    def usage():
        print('usage: vm create <name> <template> [options]')
        print('       vm destroy <name>')
        sys.exit(1)

    if len(sys.argv) < 2:
        usage()
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'create':
        parser = argparse.ArgumentParser(description='Create guest from template.')
        parser.add_argument('name', help='guest name')
        parser.add_argument('template', help='template image name')
        parser.add_argument('--pool', help='storage pool', default='default')
        parser.add_argument('--dns', help='dns domain', default='example.com')
        parser.add_argument('-u', '--update-resolver', help='update the local dns resolver',
                            action='store_true')
        parser.add_argument('-v', '--verbose', help='increase log verbosity, -v, -vv, ...',
                            action='count', default=0)
        args = parser.parse_args(args)
        set_verbosity(args.verbose)
        log.debug('create: %s', args)
        path = query_pool(args.pool)
        create_guest(args.name, args.template, path=path, dns=args.dns,
                     update_resolver=args.update_resolver)
    elif cmd == 'destroy':
        parser = argparse.ArgumentParser(description='Destroy guest.')
        parser.add_argument('name', help='guest name')
        parser.add_argument('-v', '--verbose', help='increase log verbosity, -v, -vv, ...',
                            action='count', default=0)
        args = parser.parse_args(args)
        set_verbosity(args.verbose)
        log.debug('destroy: %s', args)
        destroy_guest(args.name)
    else:
        usage()
    return 0

if __name__ == '__main__':
    main()
