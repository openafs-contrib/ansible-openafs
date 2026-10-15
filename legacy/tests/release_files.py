"""
Download the OpenAFS release files used by the molecule tests.

The release version, download locations, and test platforms are defined in
integration/openafs.yml. The files are downloaded once and saved in the
builds directory as the archives expected by the molecule scenarios.
"""

import hashlib
import os
import pathlib
import platform
import tarfile
import tempfile
import urllib.request

import yaml

CONFIG_FILE = pathlib.Path(__file__).parent / "integration" / "openafs.yml"


def download(url, path):
    """Download a file."""
    print(f"Downloading {url}")
    with urllib.request.urlopen(url, timeout=60) as response, open(path, "wb") as f:
        while chunk := response.read(1024 * 1024):
            f.write(chunk)


def verify_sha256(path, url):
    """Verify a downloaded file with the published sha256 checksum."""
    with urllib.request.urlopen(url, timeout=60) as response:
        expected = response.read().decode().split()[0]
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            sha256.update(chunk)
    if sha256.hexdigest() != expected:
        raise ValueError(f"Checksum mismatch for {path.name}")


def make_archive(dest, files):
    """Create a gzipped tar archive of the files. The archive is created with
    a temporary name and then renamed, so an incomplete archive is not used."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(f".{dest.name}.tmp")
    with tarfile.open(tmp, "w:gz") as tar:
        for path in files:
            tar.add(path, arcname=path.name)
    os.replace(tmp, dest)
    print(f"Created {dest}")


class ReleaseFiles:

    def __init__(self):
        with open(CONFIG_FILE) as f:
            self.config = yaml.safe_load(f)
        self.version = self.config["openafs_version"]
        self.builds = pathlib.Path(self.config["builds_dir"]).expanduser()
        self.arch = platform.machine()

    def platform(self, os_name):
        return self.config["platforms"].get(os_name, {})

    def osdist(self, os_name):
        return self.platform(os_name).get("osdist", os_name)

    def sdist(self):
        """Return the path to the source distribution archive, downloading the
        release source files if needed."""
        dest = self.builds / f"openafs-{self.version}.sdist.tar.gz"
        if not dest.exists():
            url = self.config["sdist_url"].format(version=self.version)
            with tempfile.TemporaryDirectory() as tmpdir:
                files = []
                for name in self.config["sdist_files"]:
                    path = pathlib.Path(tmpdir) / name.format(version=self.version)
                    download(f"{url}/{path.name}", path)
                    verify_sha256(path, f"{url}/{path.name}.sha256")
                    files.append(path)
                make_archive(dest, files)
        return dest

    def rpms(self, os_name):
        """Return the path to the rpm packages archive, downloading the
        packages if needed. Returns None if there are no packages available
        for the platform."""
        p = self.platform(os_name)
        if "repo" not in p:
            return None
        dest = self.builds / f"openafs-{self.version}-{p['osdist']}-{self.arch}.rpm.tar.gz"
        if not dest.exists():
            names = {"version": self.version, "dist": p["dist"], "arch": self.arch}
            url = self.config["rpms_url"].format(repo=p["repo"], arch=self.arch)
            with tempfile.TemporaryDirectory() as tmpdir:
                files = []
                for name in self.config["rpms"]:
                    path = pathlib.Path(tmpdir) / name.format(**names)
                    download(f"{url}/{path.name}", path)
                    files.append(path)
                make_archive(dest, files)
        return dest

    def find(self, os_name, kind):
        """Return the path to the newest existing archive of the given kind
        (bdist or debs) for the platform, or None if not found."""
        pattern = f"openafs-*-{self.osdist(os_name)}-{self.arch}.{kind}.tar.gz"
        found = sorted(self.builds.glob(pattern), key=lambda p: p.stat().st_mtime)
        return found[-1] if found else None
