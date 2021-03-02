import setuptools
import re

name = 'afs_scenario'
description='Create templated molecule scenarios for openafs_contrib.openafs playbooks and roles.'

def find_version():
    text = open('src/%s/__init__.py' % name).read()
    return re.search(r"__version__\s*=\s*'(.*)'", text).group(1)

setuptools.setup(
    name=name,
    version=find_version(),
    author='Michael Meffie',
    author_email='mmeffie@sinenomine.net',
    description=description,
    long_description=description,
    url='https://github.com/openafs-contrib/ansible-openafs/tree/master/tools/afs_scenario',
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            '%s=%s.__main__:main' % (name.replace('_', '-'), name)
        ]
    },
    install_requires=[
        'Click',
        'cookiecutter',
        'jinja2-ansible-filters',
        'pyyaml',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
