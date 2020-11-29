import os
import sys

REMOVE = [
{%- if cookiecutter.driver == 'vagrant' %}
    'cleanup.yml',
    'create.yml',
    'destroy.yml',
    'prepare.yml',
    'library/virt_up.py',
    'library',
{%- elif cookiecutter.driver == 'delegated' and cookiecutter.driver_provider == 'libvirt' %}
  {%- if cookiecutter.driver_libvirt_prepare != '' %}
    'prepare.yml',
  {%- endif %}
{%- endif %}
{%- if cookiecutter.with_krbserver == 'yes' or cookiecutter.with_server == 'no' %}
    'files/example-des.keytab',
    'files/example-aes.keytab',
    'files',
{%- endif %}
]

for path in REMOVE:
    path = path.strip()
    if path and os.path.exists(path):
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.unlink(path)
