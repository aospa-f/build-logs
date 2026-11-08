#!/usr/bin/env bash
set -e
cd /serverhive5/raizenftw/aospa/packages/apps/Launcher3

git add quickstep/res/values/config.xml quickstep/src/com/android/launcher3/QuickstepTransitionManager.java
git commit --author="TwistedVision518 <pranavpraveen0@gmail.com>" -F - <<'EOF'
Launcher3: Optimize app open and close animations

Adapted from Project-PenguinOS:
  96c71da Launcher3: Optimize app-open/close animation performance
  6c42ffe Launcher3: fix jitter/overshoot in animations
  8b4a646 Launcher3: use DECELERATE_1_5 for horizontal app-open motion

Keep the spring bounce on the icon scale only, while corner radius,
shadow and crop rect use the flat deceleration curve. Shorten the launch
and closing durations and lower the enhanced depth blur radius.

Co-authored-by: TwistedVision518 <pranavpraveen0@gmail.com>
Co-authored-by: beingashwani <ashwanic177@gmail.com>
Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF

git add -A
git commit -F - <<'EOF'
Launcher3: Adapt icon pack support to AOSPA 17

Port the Project-PenguinOS icon pack stack, originally from Shade
Launcher. Preserve the original icon pack implementation and follow-up
fixes by Amir Zaidi, DennySPb, Nauval Rizky, Pranav Vashi, Adithya R and
others.

AOSPA 17 no longer has the older DrawableFactory/ResourceBasedOverride
layer, so keep the current PendingAppWidgetHostView icon path. Keep the
no-wrap hint local to ThirdPartyIconUtils, move the icon pack menu to
res/menu, and expose the icon pack settings activity from Launcher
preferences.

Co-authored-by: Amir Zaidi <azaidi@live.nl>
Co-authored-by: DennySPb <dennyspb@gmail.com>
Co-authored-by: Nauval Rizky <enuma.alrizky@gmail.com>
Co-authored-by: Pranav Vashi <neobuddy89@gmail.com>
Co-authored-by: Adithya R <gh0strider.2k18.reborn@gmail.com>
Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF

git status --short
git log --oneline -8
