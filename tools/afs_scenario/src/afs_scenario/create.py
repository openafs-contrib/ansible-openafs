# Copyright (c) 2020-2021 Sine Nomine Associates
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THE SOFTWARE IS PROVIDED 'AS IS' AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Create initial ansible-openafs scenario files."""

from pathlib import Path
import sys

import click
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import UndefinedVariableInTemplate

def lookup_template(name):
    source = Path(__file__).resolve().parent
    path = source / 'cookiecutter' / name / 'cookiecutter.json'
    if not path.is_file():
        raise LookupError("Template '%s' not found in path '%s'." % (name, path.parent))
    return str(path.parent)

def parse_groups(ctx, param, values):
    """
    Parse the -g/--group list.
    """
    try:
        groups = []
        for value in values:
            if '=' in value:
                name, hosts = value.split('=', 1)
                hosts = list(map(int, hosts.split(',')))
            else:
                name, hosts = value, '*'  # wildcard
            groups.append((name, hosts))
        return groups
    except ValueError:
        raise click.BadParameter('values must be in the form "<name>[=number,...]"')

def verify_groups(groups, num_instances):
    """
    """
    # Check for out of range instance_numbers.
    for name, instances in groups:
        if instances == '*':
            continue
        for i in instances:
            if not 1 <= i <= num_instances:
                raise click.BadParameter('instance number %d out of range for group %s' % (i, name))


@click.command()
@click.option('-f', '--force', is_flag=True, help='Overwrite existing files')
@click.option('-s', '--scenario-name', default='default', help='Scenario name (default: "default")')
@click.option('-r', '--role-name', default='', help='Role name (default: "")')
@click.option('-p', '--playbook', 'playbooks', multiple=True, help='Playbook paths')
@click.option('-g', '--group', 'groups', multiple=True, callback=parse_groups,
              metavar='<name>[=instance-number,...]',
              help='group name, may be given multiple times')
@click.option('-n', '--num-instances', type=int, default=1, help='Number of instances (default: 1)')
@click.option('--instance-name', help='Instance base name (default: "server")')
@click.option('--realm', default='EXAMPLE.COM', help='Realm name (default: "EXAMPLE.COM")')
@click.option('--cell', default='example.com', help='Cell name (default: "example.com")')
@click.option('--install-method', default='managed', help='Install method (default: "managed")')
@click.option('--module-install-method', default='dkms', help='Kernel module install method (default: "dkms")')
@click.option('--selinux-mode', type=click.Choice(['permissive', 'enforcing', 'disabled']), help='Selinux mode')
def create(force, playbooks, groups, instance_name, selinux_mode, **context):
    """
    Create molecule scenario boilerplate.
    """
    # Create a list of group names for each instance number.
    verify_groups(groups, context['num_instances'])
    instance_groups = {}
    for i in range(1, context['num_instances'] + 1):
        names = set()
        for name, instances in groups:
            if instances == '*' or i in instances:
                names.add(name)
        instance_groups[i] = sorted(list(names))
    context['groups'] = instance_groups

    # Default instance name depends on the role name, when a role name is given.
    if instance_name is None:
        instance_name = context['role_name'].replace('openafs_', '')
    if not instance_name:
        instance_name = 'server'
    context['instance_name'] = instance_name

    # Workaround cookiecutter list limitation. (Cookiecutter treats a list
    # as a choice, so lists need to be nested in a dictionary.)
    if playbooks:
        context['playbooks'] = {'paths': list(playbooks)}

    # Set selinux_mode in the context only when --selinux-mode is given.
    if selinux_mode:
        context['selinux_mode'] = selinux_mode

    # Setup our paths.
    molecule_path = Path('./molecule').resolve()
    drivers_path = molecule_path / '__drivers__'
    scenario_path = molecule_path / context['scenario_name']

    # Create the molecule directory and common driver files.
    if not drivers_path.is_dir() or force:
        try:
            cookiecutter(
                lookup_template('drivers'),
                output_dir=str(molecule_path.parent),
                no_input=True,
                overwrite_if_exists=force)
            click.echo('Wrote: %s/' % (drivers_path))
        except UndefinedVariableInTemplate as e:
            click.echo(e, err=True)
            sys.exit(1)

    # Create scenario files under the existing molecule directory.
    if not scenario_path.is_dir() or force:
        try:
            cookiecutter(
                lookup_template('scenario'),
                output_dir=str(molecule_path),
                no_input=True,
                overwrite_if_exists=force,
                extra_context=context)
            click.echo('Wrote: %s/' % scenario_path)
        except UndefinedVariableInTemplate as e:
            click.echo(e, err=True)
            sys.exit(1)
