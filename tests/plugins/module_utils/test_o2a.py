import sys
sys.path.append('plugins/module_utils')
sys.path.append('../plugins/module_utils')
sys.path.append('../../plugins/module_utils')
import o2a      # noqa: E402
import pytest   # noqa: E402


testcases = [
    # ('', []), ?

    ({}, []),

    ('quiet',
     ['--quiet']),

    (['quiet', 'config-cache'],
     ['--quiet', '--config-cache']),

    ({'prefix': '/usr/local/openafs'},
     ['--prefix=/usr/local/openafs']),

    ({'prefix': '/usr/local/openafs', 'quiet': True},
     ['--prefix=/usr/local/openafs', '--quiet']),

    ({'enable': 'debug'},
     ['--enable-debug']),

    ({'enable': ['debug'], 'disable': 'kernel-module'},
     ['--enable-debug', '--disable-kernel-module']),

    ({'enable': ['debug', 'debug-lwp']},
     ['--enable-debug', '--enable-debug-lwp']),

    ({'enable': ['debug', 'debug-lwp'], 'disable': ['kernel-module']},
     ['--enable-debug', '--enable-debug-lwp', '--disable-kernel-module']),

    ({'with': {'krb5': '/path/to/krb5'}},
     ['--with-krb5=/path/to/krb5']),

    ({'with': [{'krb5': '/path/to/krb5'}, 'linux-kernel-packaging']},
     ['--with-krb5=/path/to/krb5', '--with-linux-kernel-packaging']),

    ({'quiet': True,
      'prefix': '/usr',
      'bindir': '/usr/bin',
      'libdir': '/usr/lib64',
      'sbindir': '/usr/sbin',
      'enable':
          ['debug', 'redhat-buildsys', 'transarc-paths', 'kernel-module'],
      'disable': 'strip-binaries',
      'with': [{'krb5': '/path/to/krb5'}, 'linux-kernel-packaging'],
      'without': 'swig'},
     ['--quiet',
      '--prefix=/usr',
      '--enable-debug',
      '--enable-redhat-buildsys',
      '--enable-transarc-paths',
      '--enable-kernel-module',
      '--sbindir=/usr/sbin',
      '--disable-strip-binaries',
      '--with-krb5=/path/to/krb5',
      '--with-linux-kernel-packaging',
      '--libdir=/usr/lib64',
      '--bindir=/usr/bin',
      '--without-swig']),

    ({'with': [], 'without': [], 'enable': [], 'disable': []}, []),
]


@pytest.mark.parametrize('options,expected_args', testcases)
def test_valid_options(options, expected_args):
    args = o2a.options_to_args(options)
    assert sorted(args) == sorted(expected_args)


@pytest.mark.parametrize(
    'options', [
        {'bogus': {'x': 'a'}},
        {'enable': {'enable': {'bar': 'baz'}}}])
def test_invalid_options(options):
    with pytest.raises(ValueError):
        o2a.options_to_args(options)
