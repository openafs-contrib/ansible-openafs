#!/bin/sh
#
# Build the podman container images for the role and playbook tests.
#
# The tests/podman directory contains a subdirectory with a Containerfile for
# each operating system. The images are named localhost/ansible-openafs-<os>.
# Build the images for all of the operating systems, or only for the given
# ones. Use --update to update the base images and rebuild the images with the
# latest packages.
#
# usage: tests/build-images.sh [--update] [<os> ...]
#
set -e

cd "$(dirname "$0")/podman"

build_options=""
if [ "$1" = "--update" ]; then
    build_options="--pull=always --no-cache"
    shift
fi

if [ $# -eq 0 ]; then
    set -- *
fi

for os in "$@"; do
    if [ ! -f "$os/Containerfile" ]; then
        echo "build-images.sh: No Containerfile for '$os'." >&2
        exit 1
    fi
    echo "Building localhost/ansible-openafs-$os"
    # Build without a podman managed /etc/hosts file, so the Containerfile
    # can add an /etc/hosts file to the image.
    podman build --no-hosts $build_options --tag "localhost/ansible-openafs-$os" "$os"
done
