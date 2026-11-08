#!/usr/bin/env bash
set -e

BASE=/serverhive5/raizenftw/aospa

cd "$BASE/vendor/aospa"
git add axion
git commit -F - <<'EOF'
axion: Import AxionOS 2.9 Quick Settings UI

Import the AxionOS Quick Settings implementation and its Compose
preference dependencies from AxionAOSP/android_axion_sdk
(lineage-23.2, AxionOS 2.9).

The port keeps the Axion tile grid, header, media panel, panel editor and
together/separate modes. AOSPA-specific compatibility shims live in
frameworks/base.

The imported code is Apache-2.0; original copyright notices are
preserved.

Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF
git push aospa calcite

cd "$BASE/frameworks/base"
git add \
    packages/SystemUI/Android.bp \
    packages/SystemUI/compose/features/src/com/android/systemui/qs/ui/composable/QuickSettingsShadeOverlay.kt \
    packages/SystemUI/compose/features/src/com/android/systemui/shade/ui/composable/ShadeHeader.kt \
    packages/SystemUI/res/values/axion_qs_compat.xml \
    packages/SystemUI/src/com/android/systemui/dagger/ReferenceSystemUIModule.java \
    packages/SystemUI/src/com/android/systemui/qs/panels/ui/compose/infinitegrid/CommonTile.kt \
    packages/SystemUI/src/com/android/systemui/qs/shared/ui/QuickSettings.kt \
    packages/SystemUI/src/com/android/systemui/shade/ShadeHeaderController.kt \
    packages/SystemUI/src/com/android/systemui/statusbar/phone/CentralSurfacesImpl.java
git commit -F - <<'EOF'
SystemUI: Port AxionOS 2.9 Quick Settings

Wire the imported Axion QS implementation into the SystemUI fragment
path and adapt it to AOSPA 17:

- register AxQsFragmentCompose and instantiate it from CentralSurfaces
- expose the Axion QS resources and Compose dependencies to SystemUI
- add AOSPA compatibility for tile state, haptics, media element keys,
  brightness/policy imports, overlay header hiding and missing resources
- use ShadeStatusBarComponentsInteractor for the QS enable state
- keep a single activation owner for AxQsViewModel

Axion-only features that depend on APIs not present in AOSPA 17 are
disabled: tile reveal motion, media overscroll-to-dismiss and the
foreground-services overflow entry.

Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF
git push aospa calcite

git -C "$BASE/vendor/aospa" log -1 --oneline
git -C "$BASE/frameworks/base" log -1 --oneline
