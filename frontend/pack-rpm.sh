#!/usr/bin/env bash
set -euo pipefail

# pack-rpm.sh - create a source tarball and optionally run rpmbuild
# Usage: ./pack-rpm.sh [--build]

NAME=gdo-frontend
VERSION=1.0.0
TARBALL=${NAME}-${VERSION}.tar.gz

HERE=$(cd "$(dirname "$0")" && pwd)
TMPDIR=$(mktemp -d)

echo "Creating source tarball ${TARBALL}..."
cd "$HERE"

# create a clean staging dir without the generated artifacts
STAGEDIR=${TMPDIR}/${NAME}-${VERSION}
mkdir -p "$STAGEDIR"

# copy files (omit the tarball itself and RPM build artifacts)
shopt -s extglob 2>/dev/null || true
cp -a -- !("${TARBALL}") "$STAGEDIR" 2>/dev/null || cp -a . "$STAGEDIR"

pushd "$TMPDIR" >/dev/null
tar -czf "$TARBALL" "${NAME}-${VERSION}"
mv "$TARBALL" "$HERE/"
popd >/dev/null

echo "Source tarball created: $HERE/$TARBALL"

if [ "${1:-}" = "--build" ]; then
    echo "Running rpmbuild -ba ... (requires rpmbuild)
If building on non-Linux, use WSL/Docker."
    mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    mv "$HERE/$TARBALL" ~/rpmbuild/SOURCES/
    cp "$HERE/frontend.spec" ~/rpmbuild/SPECS/
    rpmbuild -ba ~/rpmbuild/SPECS/frontend.spec
    echo "rpmbuild finished. Check ~/rpmbuild/RPMS and ~/rpmbuild/SRPMS"
fi
