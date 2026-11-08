# 04 — Feature fixes (all validated on the flashed userdebug build)

Each entry: symptom → root cause → fix (files) → validation status.

## FOD (in-display fingerprint)
- **Fix**: ship OSS FOD HAL `fingerprint@2.1-service_uff` incl. rc wiring; HAL is
  `vendor/oneplus/sm8650-oss/...`. Internal `Utils.cpp::kForcedProperties`
  **hard-forces** `ro.boot.vbmeta.device_state=unlocked`, `verifiedbootstate=orange`,
  `boot.mode`‑related reads for the TA — so the global prop spoof can't disturb
  fingerprint enrollment. **Do not modify those interposed values.**
- Validation: HAL process present, sensor unlock works on device.

## NFC
- **Root cause chain** (deep): stock OPlus HAL (`nfc@1.2-oplus` + Extns AIDL) vs
  Android 16 nfcservices APEX client → protocol mismatch; also per-part prop
  plumbing. Fixed by shipping OPlus AIDL+Extns HAL prebuilts
  (`vendor/oneplus/sm8650-oss/nfc/`) via `device/oneplus/sm8650-common/common.mk`,
  **and** forcing the classic stack (commits `167aae1200`, `30815ed`).
- **Validation**: user-confirmed working; user currently keeps NFC toggled **off**
  (re-enable manually as desired). My own test crash was `svc nfc enable` from
  shell (self-inflicted, unrelated).

## Status bar
- **End-side anchoring**: container anchored to right edge (commit `473e394e`);
  layouts `packages/SystemUI/res/layout/status_bar.xml`, `system_icons.xml`.
- **Battery-first measuring + gap compression**: `statusbar/phone/SystemIconsLinearLayout.java`
  (measures battery before others), `StatusIconContainer.java`.
- **4-icon speed-hide rule** in `StatusIconContainer.java`.
- **HD badge / ▲▼ activity carets hidden**: `statusbar/pipeline/mobile/ui/viewmodel/MobileIconViewModel.kt`
  + `MobileIconViewModelKairos.kt` suppression.
- **Burn-in protection default OFF** (it drifted the bar up to 136px and read as a
  "corner gap" bug): `statusbar/BurnInProtectionController.kt` + Settings
  `display_settings.xml` (`abde778adc9`). On the phone the stale-settings value
  was reset to `0`.

## QS / Display
- **Extra-dim slider**: `qs/composefragment/DisplayExtraBrightnessSliders.kt` —
  direction matches the Settings page (left = dimmer); level read from the
  settings table on init (not the manager getter); drags validated with a
  ≥6-level travel threshold before thumb follows; commit on release; echo-free
  ContentObserver sync.
- **Window ignore-secure** (screenshots etc.): LibXZR-style feature, Settings pref +
  WMS support (pushed in earlier session).

## Power/UX
- **Bypass-charge tile long-press → its settings screen**: earlier approach used
  TileService API members that don't exist (`onLongClick` overrides nothing /
  unresolved `startSettingsAndCollapse`); final: manifest route — `DEFAULT`
  category on the `QS_TILE_PREFERENCES` intent-filter (commit `f161fd0`), and the
  dead `onLongClick` override removed from `BypassChargeTileService.java`.
- **Touch polling**:
  - **Symptom**: Toggling "High touch polling rate" in Display Settings immediately crashed Settings (`FATAL EXCEPTION in system_app`).
  - **Root cause**: `TouchPollingPreferenceController.java` tried to set `persist.touch_polling_mode`. In Android 14/15/16 CTS SELinux rules, `system_app` is blocked from writing `default_prop:s0`, throwing a `RuntimeException`. In addition, `vendor.oplus.hardware.touch@2.0-service` (`OplusTouch.cpp`) only started its watcher thread inside the AIDL `initialize()` method (which the framework never calls on boot), and attempted to write to `/proc/touchpanel/report_rate` (node 182) which does not exist on OnePlus 13R.
  - **Fix**:
    1. In Settings (`TouchPollingPreferenceController.java`): switched property to `debug.touch_polling_mode` (writable by `system_app`), added try/catch, and persisted the user preference in `Settings.Secure` (`touch_polling_enabled`).
    2. In Touch HAL (`OplusTouch.cpp`, `OplusTouch.h`, `.rc`): moved watcher thread to the `OplusTouch` constructor so it runs immediately on service boot; wired writes directly to the SM8650 Synaptics TCM HBP kernel driver sysfs node (`/sys/bus/platform/drivers/synaptics_tcm_hbp/synaptics_tcm_hbp.0/high_rate`); reduced polling loop interval from 2000ms to 500ms; and added init triggers in `vendor-oplus-hardware-touch-V2-service.rc` to write to the node on `debug.touch_polling_mode` changes.
  - **Validation**: Verified live on connected phone. Tapping toggle in Settings flips `debug.touch_polling_mode` to 1, `touch_polling_enabled` to 1, and `/sys/bus/.../synaptics_tcm_hbp.0/high_rate` to 1 with 0 crashes; tapping again cleanly flips all back to 0.

## Display / LTPO
- **Dynamic Refresh Rate Scaling (LTPO)**:
  - **Verification**: Verified live on device via `/sys/devices/platform/soc/ae00000.qcom,mdss_mdp/drm/card0/sde-crtc-0/measured_fps`.
  - **Behavior**: Display drops down to **1 Hz** during idle/static display across apps, and instantly scales up to **120 Hz** during touch interaction, flings, and motion. Confirmed working as intended on hardware.

## Deliberately NOT done
- **NFC QS tile** — user: "no need" (AxionParts reverted to `9d391db1`).
- NFC side experiments (custom tile service) — dead end, see above.
