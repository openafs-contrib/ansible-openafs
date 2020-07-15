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

class VmError(Exception):
    pass

# Avoid printing errors to the console. Exceptions are logged below.
def libvirt_callback(userdata, err):
    pass

libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)


class Guest:
    def __init__(self, name,
                 template='template',
                 pool='default',
                 dns='example.com',
                 uri=None,
                 update_resolver=False):
        log.debug('Guest(): name=%s, template=%s' % (name, template))
        self.name = name
        self.template = template
        self.pool = pool
        self.dns = dns
        self.update_resolver = update_resolver
        if uri is None:
            uri = os.environ.get('LIBVIRT_DEFAULT_URI')
        log.debug("Opening libvirt connnection '%s'.", uri)
        self.conn = libvirt.open(uri)

    def __del__(self):
        if self.conn:
            log.debug('Closing libvirt connnection')
            self.conn.close()

    def __enter__(self):
        self.create()
        return self

    def __exit__(self, type, value, traceback):
        self.destroy()

    def query_pool(self):
        """
        Query libvirt for a pool path.

        name: name of the pool to query
        """
        path = None
        for pool in self.conn.listAllStoragePools():
            xml = pool.XMLDesc()
            root = ET.fromstring(xml)
            if self.pool == root.find('name').text:
                log.debug(xml)
                path = root.find('target/path').text
        log.info("Pool '%s' path is '%s'.", self.pool, path)
        return path

    def query_networks(self, bridge):
        """
        Query libvirt for network info.

        Find the address for the network with this bridge name.
        """
        networks = []
        for network in self.conn.listAllNetworks():
            xml = network.XMLDesc()
            log.debug(xml)
            root = ET.fromstring(xml)
            info = dict()
            info['bridge'] = root.find('bridge').get('name')
            info['address'] = root.find('ip').get('address')
            networks.append(info)
        for network in networks:
            if bridge and bridge == network.get('bridge'):
                return network.get('address')
        return None

    def query(self, key='check'):
        """
        Query libvirt for guest information.

        key: one of 'check', 'mac', 'bridge', 'disk_files'
        """
        assert key in ('check', 'mac', 'bridge', 'disk_files')
        try:
            domain = self.conn.lookupByName(self.name)
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
            log.debug("Domain '%s' info: %s", self.name, info)
            return info.get(key)
        except libvirt.libvirtError as e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                if key != 'check':
                    log.info("Domain '%s' not found.", self.name)
                return None
            else:
                raise e

    def snapshots(self):
        snapshots = []
        for line in virsh('snapshot-list', self.name, '--name', _iter=True):
            line = line.rstrip()
            if line:
                snapshots.append(line)
        return snapshots

    def create(self):
        """
        Create a guest from a pre-existing template. Save and reuse the
        assigned mac address if the guest is recreated.
        """
        log.debug('create: name=%s, template=%s, pool=%s, self.dns=%s',
                  self.name, self.template, self.pool, self.dns)

        self.path = self.query_pool()
        self.image = '%s/%s.qcow2' % (self.path, self.name)
        if os.path.exists(self.image):
            raise VmError("Image '%s' already exists." % self.image)

        clone_args = dict(
            quiet=True,
            auto_clone=True,
            o=self.template,
            n=self.name,
            f=self.image,
        )

        # Add --mac option from the last generation.
        mac_path = os.environ.get('VM_MAC_PATH', '~/.vm')
        mac_file = os.path.expanduser('%s/%s.mac' % (mac_path, self.name))
        if os.path.exists(mac_file):
            with open(mac_file, 'r') as f:
                clone_args['mac'] = f.read().strip()

        log.info("Cloning template '%s' to guest '%s'.", self.template, self.name)
        log.debug("clone_args='%s'", clone_args)
        virt_clone(**clone_args)

        if not os.path.exists(self.image):
            raise VmError("Failed to create image '%s'." % self.image)

        # Save our mac address for the next generation.
        mac = self.query('mac')
        if mac and mac != clone_args.get('mac'):
            log.debug("Writing '%s' to file '%s'.", mac, mac_file)
            with open(mac_file, 'w') as f:
                f.write('%s\n' % mac)

        # The new image will be owned by root when the libvirt uri is
        # 'qemu:///system'.  Make it writable so we can sysprep it.
        if not os.access(self.image, os.R_OK | os.W_OK):
            log.info("Changing file '%s' ownership to '%d'.", self.image, os.geteuid())
            sudo('chown', os.geteuid(), self.image)
            os.chmod(self.image, 0o664)

        log.info("Preparing image '%s'.", self.image)
        virt_sysprep(
            quiet=True,
            add=self.image,
            hostname='%s.%s' % (self.name, self.dns),
            operations='defaults,-ssh-hostkeys,-ssh-userdir')

        log.info("Starting guest '%s'.", self.name)
        virsh('autostart', self.name)
        virsh('start', self.name)

        # Optionally, update the local systemd resolver.
        if self.update_resolver:
            if not self.dns:
                VmError("Unable to update resolver; dns name is missing.")
            bridge = self.query(key='bridge')
            if not bridge:
                VmError("Unable to update resolver; bridge for domain '%s' not found." % self.name)
                return 1
            address = self.query_networks(bridge)
            if not address:
                VmError("Unable to update resolver; gatawate address not found for bridge '%s'." % bridge)
            log.info("Adding '%s' to systemd-resolved: '%s' (%s).", self.dns, bridge, address)
            sudo('systemd-resolve', '--interface', bridge, '--set-dns', address, '--set-domain', self.dns)

    def destroy(self):
        """
        Destroy a guest and remove the disk files.
        """
        log.debug('destroy: name=%s', self.name)

        disk_files = self.query('disk_files')
        if disk_files is None:
            log.info("Skipping destroy; domain '%s' not found.", self.name)
            return 0

        for snapshot in self.snapshots():
            log.info("Deleting snapshot '%s' from domain '%s'.", snapshot, self.name)
            virsh('snapshot-delete', self.name, snapshot)

        log.info("Destroying domain '%s'.", self.name)
        try:
            virsh('destroy', self.name)
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

        log.info("Undefining domain '%s'.", self.name)
        virsh('undefine', self.name)


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
        parser.add_argument('-u', '--update-resolver', help='update the local name resolver',
                            action='store_true')
        parser.add_argument('-v', '--verbose', help='increase log verbosity, -v, -vv, ...',
                            action='count', default=0)
        args = parser.parse_args(args)
        set_verbosity(args.verbose)
        log.debug('create: %s', args)

        guest = Guest(args.name, args.template, pool=args.pool, dns=args.dns,
                      update_resolver=args.update_resolver)
        guest.create()
    elif cmd == 'destroy':
        parser = argparse.ArgumentParser(description='Destroy guest.')
        parser.add_argument('name', help='guest name')
        parser.add_argument('-v', '--verbose', help='increase log verbosity, -v, -vv, ...',
                            action='count', default=0)
        args = parser.parse_args(args)
        set_verbosity(args.verbose)
        log.debug('destroy: %s', args)

        guest = Guest(args.name)
        guest.destroy()
    else:
        usage()
    return 0

if __name__ == '__main__':
    main()
