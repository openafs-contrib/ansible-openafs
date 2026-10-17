import pytest

from ansible_collections.openafs_contrib.openafs.plugins.modules.openafs_build_packages import (
    rpmbuild_args,
)

RPMBUILD = "/usr/bin/rpmbuild"
TOPDIR = "/home/tester/rpmbuild"
SPEC = "/home/tester/rpmbuild/SPECS/openafs.spec"
DEFINE_TOPDIR = ["--define", "_topdir %s" % TOPDIR]

testcases = [
    ("source", None, ["-bs"]),
    ("source", "6.12.0", ["-bs"]),
    ("all", None, ["-ba"]),
    ("all", "6.12.0", ["-ba", "--define", "kernvers 6.12.0"]),
    (
        "userspace",
        None,
        ["-ba", "--define", "build_userspace 1", "--define", "build_modules 0"],
    ),
    (
        "modules",
        None,
        ["-ba", "--define", "build_userspace 0", "--define", "build_modules 1"],
    ),
    (
        "modules",
        "6.12.0",
        [
            "-ba",
            "--define",
            "build_userspace 0",
            "--define",
            "build_modules 1",
            "--define",
            "kernvers 6.12.0",
        ],
    ),
]


@pytest.mark.parametrize("build,kernvers,expected", testcases)
def test_rpmbuild_args(build, kernvers, expected):
    args = rpmbuild_args(RPMBUILD, TOPDIR, build, kernvers)
    assert args == [RPMBUILD] + DEFINE_TOPDIR + expected + [SPEC]
