# 01 — Quick state (read this first)

## Completed and validated
- **Production user + release-keys build**: Successfully built for giulia on 2026-11-08 (`aospa-calcite-unofficial-giulia-20261108.zip`, 2.9 GB). Signed with private keyset (`vendor/aospa-priv/security/releasekey`).
- **Post-build partition & OTA audit passed 100%**:
  - `ro.build.type=user`
  - `ro.build.tags=release-keys`
  - `ro.build.version.security_patch=2026-11-01` (November 2026 security patch)
  - `ro.build.display.id=CQ2A.260820.002-CP2A.260605.016`
  - `ro.system.build.fingerprint=OnePlus/aospa_giulia/giulia:17/CQ2A.260820.002-CP2A.260605.016/eng.nobody:user/release-keys`
  - Extracted `system/bin/init` contains all 6 spoofed props: `ro.boot.verifiedbootstate=green`, `ro.boot.flash.locked=1`, `ro.boot.vbmeta.device_state=locked`, `ro.boot.veritymode=enforcing`, `ro.boot.warranty_bit=0`, `ro.warranty_bit=0`.
  - OTA container signed with private release key; `plat_mac_permissions.xml` signed with private release keys.
- **High touch polling rate fix verified**: Settings crash eliminated (`debug.touch_polling_mode` + `Settings.Secure`), HAL wired directly to the SM8650 Synaptics TCM HBP `high_rate` sysfs node with init triggers. Tested on phone: toggles 0 ↔ 1 cleanly with zero crashes.
- **LTPO display scaling verified**: Dynamic refresh rate verified on phone down to 1 Hz idle and up to 120 Hz in apps and motion via `measured_fps`.
- All source changes committed and pushed to `aospa-f` organization.

## Ready for Flashing
- The production ROM package is ready in `/serverhive5/raizenftw/aospa/out/target/product/giulia/aospa-calcite-unofficial-giulia-20261108.zip`.
- Download to local laptop and flash via recovery sideload (`adb sideload <zip>`). Note: User build disables `adb root` by default.

## Keys
Private keyset: waffle `/serverhive5/raizenftw/aospa/vendor/aospa-priv/security/` — in **no** git repo, must never be pushed. Backup exists at `/home/raizen/aospa-keys-backup/security/`.
