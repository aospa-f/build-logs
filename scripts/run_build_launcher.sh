#!/usr/bin/env bash
set -e
ulimit -n 65536 || true
cd /serverhive5/raizenftw/aospa

restore() {
    cp -f /serverhive5/raizenftw/build-logs/scripts/run_build.sh.original \
        /serverhive5/raizenftw/aospa/run_build.sh
}
trap restore EXIT

export USE_CCACHE=1
export CCACHE_EXEC=$(which ccache)
export CCACHE_DIR=/serverhive5/raizenftw/.ccache

echo "=== Launching Launcher3 feature compile at $(date) ==="
export GOMEMLIMIT=16GiB
export GOGC=50
./rom-build.sh giulia -j32 -m Launcher3QuickStep
echo "=== Launcher3 feature compile completed at $(date) ==="
