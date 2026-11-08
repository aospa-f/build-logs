#!/usr/bin/env bash
set -e
ulimit -n 65536 || true
cd /serverhive5/raizenftw/aospa

export USE_CCACHE=1
export CCACHE_EXEC=$(which ccache)
export CCACHE_DIR=/serverhive5/raizenftw/.ccache

echo "=== Launching build at $(date) ==="
export GOMEMLIMIT=16GiB
export GOGC=50
# Patches are already committed in the aospa-f repos; skipping re-apply on this tree.
# bash /serverhive5/raizenftw/build-logs/scripts/apply_all_patches.sh /serverhive5/raizenftw/aospa
# rm -rf /serverhive5/raizenftw/aospa/out/target/product/giulia/obj/DTB_OBJ/out/* 2>/dev/null || true
./rom-build.sh giulia
echo "=== Build completed at $(date) ==="
