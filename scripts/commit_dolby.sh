#!/usr/bin/env bash
set -e

BASE=/serverhive5/raizenftw/aospa

cd "$BASE/device/oneplus/giulia"
git add Android.bp device.mk dolby prebuilt
git commit -F - <<'EOF'
giulia: Rebuild the Dolby C2 service from AOSPA source

Replace the stock OOS 16 Dolby C2 service and the CFI-free prebuilt HIDL
library with a small AOSPA-built service. The service links the stock
libcodec2_store_dolby.so but uses AOSPA's libcodec2_hidl, libhidlbase and
libutils, so the ComponentStore object layout and refcounting match the
rest of the system.

Remove the Ronard HIDL prebuilt and its symlink override; the AOSPA vendor
variant of android.hardware.media.c2@1.0 is now used directly.

Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF
git push github calcite

cd "$BASE/vendor/sony/dolby"
git add Android.bp proprietary-files.txt
git commit -F - <<'EOF'
dolby: Drop the prebuilt C2 service

The C2 service is now built from AOSPA source in
device/oneplus/giulia/dolby. Remove the stock service binary and its
prebuilt module while keeping the Dolby store and the existing init/VINTF
files.

Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF
git branch -f calcite HEAD
git push github calcite

git -C "$BASE/device/oneplus/giulia" log -1 --oneline
git -C "$BASE/vendor/sony/dolby" log -1 --oneline
