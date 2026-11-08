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
export GOMEMLIMIT=16GiB
export GOGC=50
export CUSTOM_NINJA_BIN=/opt/ninja

echo "=== Launching feature compile at $(date) ==="
./rom-build.sh giulia -j32 -m KeyHandler -m framework-minus-apex -m SystemUI -m Settings
echo "=== Feature compile completed at $(date) ==="
