# 08 — Phone identity, flashed state & validation history

## Device
- OnePlus 13R (IN) — model `CPH2691`, marketing device string `OP5D3BL1`, SoC **sm8650**.
- Target/product: `aospa_giulia`. Bootloader unlocked (orange state, real) — spoof claims the opposite in props per user requirements.

## Currently flashed build (baseline, keeps features while production zip is awaited)
- Our userdebug AOSPA build: laptop copy `/home/raizen/Downloads/aospa-calcite-unofficial-giulia-20261108.zip`,
  md5 `99ce27d11208702d66bf246c287c7269` (server build from 18:59, 2026-11-07/08).
- Flash state healthy at last audit.
- Security Patch: **November 2026** (`ro.build.version.security_patch=2026-11-01`, `ro.vendor.build.security_patch=2026-11-05`).

## Health audit results (on the flashed userdebug)
- **SELinux enforcing**, only benign OEM AVC denials: `servicemanager → display-color HAL`,
  Play Store `verified_contents` reads.
- 0 ANRs; 1 normal wakelock; battery 33.8 °C at audit time; no crashes except a
  self-inflicted one (`adb shell svc nfc enable` from my own testing — unrelated to ROM).
- Boot-state props verified **live**: `verifiedbootstate=green`, `flash.locked=1`,
  `vbmeta.device_state=locked`, `veritymode=enforcing` (spoof already active).
- Remaining deltas vs "production" at that time: `ro.build.type=userdebug`, `ro.build.tags=test-keys`.

## User preferences currently set on the phone
- NFC toggled **off** (works when enabled — re-enable manually).
- Burn-in protection `0` (old settings data had re-enabled it; drifting-bar artifact eliminated).
- High Touch Polling Rate: verified live on hardware.
  - Switch in Display Settings: toggles `debug.touch_polling_mode` (1 ↔ 0), `settings get secure touch_polling_enabled` (1 ↔ 0).
  - Hardware driver node: `/sys/bus/platform/drivers/synaptics_tcm_hbp/synaptics_tcm_hbp.0/high_rate` verified flipping between `1` and `0`.
  - Zero crashes / zero ANRs on toggle.
- LTPO Refresh Rate: verified live on hardware.
  - Real-time CRTC monitor: `/sys/devices/platform/soc/ae00000.qcom,mdss_mdp/drm/card0/sde-crtc-0/measured_fps`.
  - Dynamic behavior: ramps to 120 Hz on touch/gesture flings, ramps down to 1 Hz on idle/static frames across apps.

## Post-production-flash validation checklist (**no adb root on user builds!**)
Non-root commands only:
```bash
getprop ro.build.type                # expect user
getprop ro.build.tags                # expect release-keys
getprop ro.build.fingerprint         # ends ":user/release-keys"
getprop | grep -E "warranty_bit|verifiedbootstate|flash.locked|vintage"   # green/locked/enforcing + 0/0
dumpsys battery | grep -i temp
```
Feature pass (manual, user-verified): FOD unlock, NFC toggle on→reads, status bar
(anomaly-free end side, no HD/carets), QS extra-dim slider drag direction + commit,
bypass tile long-press opens its settings, touch polling switch writes the prop,
burn-in stays off.

## Historical note (deprecated procedure)
Pre-flash era bind-mount live-push (`mount --bind` + dalvik-cache/profile clearing +
app-process restart) is obsolete — the flashed image carries everything. If ever
revived on a debug build: requires `adb root`; clear
`/data/dalvik-cache/arm64/system_ext@priv-app@<App>@<App>.apk@classes{,.vdex}` and
`/data/misc/profiles/cur/0/<pkg>`; restart only the app process.
