
import unittest
import ddt
import openafs_build

@ddt.ddt
class ConfigureOptionToArgsTest(unittest.TestCase):

    @ddt.data(
        ({}, []),
        ('quiet', ['--quiet']),
        (
            ['quiet', 'config-cache'],
            ['--quiet', '--config-cache']
        ),
        (
            {'prefix': '/usr/local/openafs'},
            ['--prefix=/usr/local/openafs']
        ),
        (
            {'prefix': '/usr/local/openafs', 'quiet': True},
            ['--prefix=/usr/local/openafs', '--quiet']
        ),
        (
            {'enable': 'debug'},
            ['--enable-debug'],
        ),
        (
            {'enable': ['debug'], 'disable': 'kernel-module'},
            ['--enable-debug', '--disable-kernel-module'],
        ),
        (
            {'enable': ['debug', 'debug-lwp']},
            ['--enable-debug', '--enable-debug-lwp'],
        ),
        (
            {'enable': ['debug', 'debug-lwp'], 'disable': ['kernel-module']},
            ['--enable-debug', '--enable-debug-lwp', '--disable-kernel-module'],
        ),
        (
            {'with': {'krb5': '/path/to/krb5'}},
            ['--with-krb5=/path/to/krb5'],
        ),
        (
            {'with': [{'krb5': '/path/to/krb5'}, 'linux-kernel-packaging']},
            ['--with-krb5=/path/to/krb5', '--with-linux-kernel-packaging'],
        ),
        (
           {
               'quiet': True,
               'prefix': '/usr',
               'bindir': '/usr/bin',
               'libdir': '/usr/lib64',
               'sbindir': '/usr/sbin',
               'enable': ['debug', 'redhat-buildsys', 'transarc-paths', 'kernel-module'],
               'disable': 'strip-binaries',
               'with': [{'krb5': '/path/to/krb5'}, 'linux-kernel-packaging'],
               'without': 'swig',
            },
            [
                '--quiet',
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
                '--without-swig',
            ]
        ),
    )
    def test_options_to_args(self, case):
        options, expected = case
        got = openafs_build.options_to_args(options)
        self.assertEqual(sorted(got), sorted(expected))

    @ddt.data(
        {'bogus': {'x': 'a'}},
        {'enable': {'enable': {'bar': 'baz'}}},
    )
    def test_bogus_options(self, case):
        with self.assertRaises(ValueError):
            openafs_build.options_to_args(case)


if __name__ == '__main__':
    unittest.main()
