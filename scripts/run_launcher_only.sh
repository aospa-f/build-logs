#!/usr/bin/env bash
set -e
ulimit -n 65536 || true
cd /serverhive5/raizenftw/aospa
export USE_CCACHE=1
export CCACHE_EXEC=$(which ccache)
export CCACHE_DIR=/serverhive5/raizenftw/.ccache
export GOMEMLIMIT=16GiB
export GOGC=50
echo "=== Launcher compile start $(date) ==="
./rom-build.sh giulia -j32 -m Launcher3QuickStep
echo "=== Launcher compile done $(date) ==="
