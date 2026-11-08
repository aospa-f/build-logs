#!/usr/bin/env bash
set -e
BASE=/serverhive5/raizenftw/aospa

# 1. Alert slider popup removal
cd "$BASE/hardware/oplus"
git add packages/KeyHandler/AndroidManifest.xml \
    packages/KeyHandler/res/xml/button_panel.xml \
    packages/KeyHandler/src/org/lineageos/settings/device/KeyHandler.kt
git commit -F - <<'EOF'
KeyHandler: Remove the alert slider popup

Stop broadcasting slider state changes and remove the SystemUI overlay
plugin registration, so changing the alert slider no longer shows an
icon or text popup. Ringer-mode handling, media mute and haptics are
unchanged.

The removed dialog was originally written by CypherOS, Paranoid Android,
LineageOS and Yet Another AOSP Project.

Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF

# 2. Clock and date backend
cd "$BASE/frameworks/base"
git add packages/SystemUI/src/com/android/systemui/statusbar/policy/Clock.java \
    packages/SystemUI/src/com/android/systemui/tuner/TunerService.java \
    packages/SystemUI/res/values/attrs.xml \
    packages/SystemUI/res/layout/status_bar.xml
git commit --author="Pranav Vashi <neobuddy89@gmail.com>" -F - <<'EOF'
SystemUI: Add status bar clock and date customization

Forward-port the status-bar date controls from VoltageOS and add the
bold clock and period separator options from Lunaris.

The clock stays in the left status bar container. There is no clock
position setting, and the QS header clock keeps its own XML style.
Settings are stored in Settings.Secure to match AOSPA's existing
clock_seconds key and Secure-only TunerService.

Original status bar clock customization: Lars Greiss
Rewrite and date controls: Pranav Vashi
Bold clock and period separator: Pranav Vashi
Lunaris integration: Ghosuto
Forward port: VoltageOS

Co-authored-by: Lars Greiss <kufikugel@googlemail.com>
Co-authored-by: Ghosuto <clash.raja10@gmail.com>
Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF

# 3. QS tiles
cd "$BASE/frameworks/base"
git add packages/SystemUI/src/com/android/systemui/qs/tiles/RefreshRateTile.kt \
    packages/SystemUI/src/com/android/systemui/qs/tiles/RefreshRateTileModule.kt \
    packages/SystemUI/src/com/android/systemui/qs/tiles/PreferredNetworkTile.kt \
    packages/SystemUI/src/com/android/systemui/qs/tiles/PreferredNetworkTileModule.kt \
    packages/SystemUI/res/drawable/ic_refresh_rate.xml \
    packages/SystemUI/res/values/config.xml \
    packages/SystemUI/res/values/aospa_strings.xml \
    packages/SystemUI/src/com/android/systemui/dagger/SystemUIModule.java
git commit -F - <<'EOF'
SystemUI: Add refresh rate and preferred network tiles

Add a two-mode refresh rate tile:
- 90 Hz adaptive: peak 90, minimum 0
- 120 Hz locked: peak 120, minimum 120

Add a three-mode network tile for the default data SIM:
- 5G only
- 4G only
- Preferred 5G

The network tile uses the public TelephonyManager allowed-network-types
API because SystemUI already holds MODIFY_PHONE_STATE. NetToggle by
Dhangofa was used as a behaviour reference only; its GPL-3.0 code was
not copied.

Credits:
- Nameless-AOSP refresh rate tile: jhonboy121
- A16 QS adaptation: Dmitrii
- Nameless-AOSP preferred network tile: cjh1249131356, ShevT
- Lunaris integration: Pranav Vashi, Ghosuto

Co-authored-by: jhonboy121 <alfredmathew05@gmail.com>
Co-authored-by: Dmitrii <bankersenator@gmail.com>
Co-authored-by: cjh1249131356 <cjh1249131356@gmail.com>
Co-authored-by: ShevT <evgeny.shishkov@gmail.com>
Co-authored-by: Pranav Vashi <neobuddy89@gmail.com>
Co-authored-by: Ghosuto <clash.raja10@gmail.com>
Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF

# 4. Screen-off gesture key handler
cd "$BASE/frameworks/base"
git add services/core/java/com/android/server/policy/KeyHandler.java
git commit -F - <<'EOF'
SystemUI: Add screen-off music and volume gestures

Extend the existing off-screen gesture handler with volume up/down
actions and gate play/pause, previous, next and volume gestures on an
active media session from the selected music apps.

The gesture key codes come from the LineageOS vendor.lineage.touch HAL
and its OPlus touch implementation.

Original off-screen gesture handler: Carlo Savignano
Paranoid Android and LineageOS integration: the respective projects

Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF

# 5. Settings Display entry
cd "$BASE/packages/apps/Settings"
git add res/xml/display_settings.xml
git commit -F - <<'EOF'
Settings: Add clock and date entry under Display

Expose the status bar clock/date screen from Display settings. The
screen itself lives in ParanoidSettings.

Credits for the clock/date backend:
Lars Greiss, Pranav Vashi, Ghosuto, VoltageOS.

Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF

# 6. ParanoidSettings UI
cd "$BASE/packages/apps/ParanoidSettings"
git switch -c calcite 2>/dev/null || git switch calcite
git add res/xml/status_bar_clock_settings.xml \
    res/values/aospa_strings.xml \
    res/values/aospa_arrays.xml \
    res/xml/offscreen_gesture_settings.xml \
    src/co/aospa/settings/display/StatusBarClockSettings.java \
    src/co/aospa/settings/display/StatusBarClockPreferenceController.java \
    src/co/aospa/settings/gestures/OffscreenGestureSettings.java
git commit -F - <<'EOF'
Settings: Add clock/date controls and screen-off music apps

Add the Clock and date screen with seconds, AM/PM, date visibility,
date format, date case, date position, bold clock and period separator
controls.

Add a multi-select Music apps preference to the existing screen-off
gesture screen. The selected packages are stored in Settings.System and
are used by the framework gesture handler to gate media and volume
actions on a playing media session.

Supported off-screen gestures come from the LineageOS vendor.lineage.touch
HAL. The app selector lists MediaBrowserService providers and music
activities; Auxio and vivi-music were used as test apps only.

Credits:
- Clock/date backend: Lars Greiss, Pranav Vashi, Ghosuto, VoltageOS
- Off-screen gestures: Carlo Savignano, Paranoid Android, LineageOS
- Test apps: oxygencobalt/Auxio, vivizzz007/vivi-music

Co-authored-by: Pranav Vashi <neobuddy89@gmail.com>
Co-authored-by: Ghosuto <clash.raja10@gmail.com>
Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF

# 7. Giulia gesture overlay
cd "$BASE/device/oneplus/giulia"
git add overlay/OPlusFrameworksResTarget/res/values/config.xml
git commit -F - <<'EOF'
giulia: Enable screen-off touch gestures

Enable the framework off-screen gesture handler and map the Synaptics
S3910 gesture scan codes to previous, next, play/pause, volume up and
volume down.

The touch HAL exposes directional one-finger swipes but only a single
two-finger down swipe, so volume uses the supported one-finger up/down
pair.

Gesture key codes and the touch HAL are from the LineageOS Project.

Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF

# 8. Touch gesture bitmask at boot
cd "$BASE/device/oneplus/sm8650-common"
git add init/init.oplus.rc
git commit -F - <<'EOF'
sm8650-common: Enable the touch gesture bitmask at boot

Enable the left/right Vee, circle and one-finger up/down gesture bits in
the OPlus touch panel so the framework screen-off gesture handler can
receive them.

The gesture bitmask and node come from the LineageOS vendor.lineage.touch
implementation.

Signed-off-by: raizenftw <raizen.mad@gmail.com>
EOF

echo "=== COMMITS ==="
for d in hardware/oplus frameworks/base packages/apps/Settings packages/apps/ParanoidSettings device/oneplus/giulia device/oneplus/sm8650-common; do
    echo "--- $d"
    git -C "$BASE/$d" log --oneline -3
    git -C "$BASE/$d" status --short | head
done
