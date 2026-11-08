#!/bin/bash
# Incremental compile for the four AOSPA feature changes.
# Mirrors the server's sanctioned run_build.sh environment.
set -e
ulimit -n 65536 || true
cd /serverhive5/raizenftw/aospa || exit 1

export USE_CCACHE=1
export CCACHE_EXEC=$(which ccache)
export CCACHE_DIR=/serverhive5/raizenftw/.ccache
export GOMEMLIMIT=16GiB
export GOGC=50

echo "=== Incremental feature compile started at $(date) ==="
source build/envsetup.sh
lunch aospa_giulia-userdebug

set -o pipefail
m -j32 framework-minus-apex SystemUI Settings 2>&1 | tee /serverhive5/raizenftw/build-logs/logs/incremental-features-tmux.log
echo "=== Incremental feature compile finished at $(date) ==="
