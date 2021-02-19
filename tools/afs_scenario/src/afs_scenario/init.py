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

"""Render jinja2 templates in a directory tree."""

from pathlib import Path

import click
import jinja2
import jinja2_ansible_filters
import yaml

from afs_scenario.util import default_config_path, NestedDict

def render_template(filename, context):
    """
    Render a template file in place.

    filename (Path) template filename
    context  (dict) context data
    """
    env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(filename.parent),
            extensions=[jinja2_ansible_filters.AnsibleCoreFiltersExtension],
            undefined=jinja2.StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            block_start_string='[%',
            block_end_string='%]',
            variable_start_string='[[',
            variable_end_string=']]',
            comment_start_string='[#',
            comment_end_string='#]')

    template = env.get_template(filename.name)
    text = template.render(**context)

    output = filename.parent / filename.stem
    with open(output, 'w') as fh:
        fh.write(text)
        click.echo('Wrote: %s' % output)

def load_context(ctx, param, value):
    """
    Load the yaml context file.
    """
    context = {}
    config = Path(value)
    if config.is_file():
        click.echo('Reading: %s' % value)
        with config.open() as fh:
            context = yaml.safe_load(fh)
    else:
        click.echo('Warning: configuration file not found: %s' % value)
    # Ensure __exclude__ is a list.
    e = '__exclude__'
    if not e in context:
        context[e] = []
    if not isinstance(context[e], list):
        context[e] = [context[e]] # Convert to a list.
    return context

def validate_extras(ctx, param, values):
    """
    Validate --extra options.
    """
    try:
        extras = []
        for value in values:
            k, v = value.split('=', 1)
            extras.append((k, v))
        return extras
    except ValueError:
        raise click.BadParameter('values must be in the form "<name>=<value>"')

def is_exclusion(t, exclude):
    for e in exclude:
        if t.match(e):
            click.echo("Excluding '%s'; matches pattern '%s'" % (t, e))
            return True
    return False

@click.command()
@click.option('-c', '--config', type=click.Path(), callback=load_context,
              default=default_config_path, metavar='<filename>',
              help='variables yaml file.')
@click.option('-d', '--directory', type=click.Path(), default='molecule', metavar='<path>',
              help='target directory', show_default=True)
@click.option('-x', '--exclude', multiple=True, metavar='<pattern>',
              help='template filename exclusion patterns [default: none]')
@click.option('--recursive/--no-recursive', default=True)
@click.option('-s', '--suffix', default='.j2',
              help='Template filename suffix', show_default=True)
@click.option('-e', '--extra', multiple=True, callback=validate_extras, metavar='<name>=<value>',
              help='Extra variables in the form <section.name>=<value>')
def init(config, directory, exclude, recursive, suffix, extra):
    """
    Initialize molecule files.
    """
    # Support filename exclusion patterns from the command line and from
    # the context file.
    exclude = set(list(exclude) + config.pop('__exclude__'))

    # Add command-line extra variables to the context.
    nd = NestedDict(config)
    for name, value in extra:
        nd[name] = value

    # Render the templates found in the directory tree.
    directory = Path(directory)
    pattern = '*' + suffix
    if recursive:
        pattern = '**/' + pattern
    for filename in directory.glob(pattern):
        if not is_exclusion(filename, exclude):
            render_template(filename, nd.d)
