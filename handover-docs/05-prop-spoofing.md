# 05 — Boot-state prop spoof (static, system-wide)

## Mechanism (why it works with zero config)
- Implemented in `system/core/init/property_service.cpp::SetSafetyNetProps()`
  (function name predates SafetyNet; semantically "report OEM-normal boot state").
- Called from `PropertyInit()` **before** kernel cmdline/bootconfig import —
  so any bootloader-provided overrides for these props are rejected later:
  `ro.*` props are **write-once** (`PropertySet()` returns
  `PROP_ERROR_READ_ONLY_PROPERTY` for a second set; the failure is merely logged).
- **Skipped in recovery** → recovery/sideloading always sees the true state.
- Verified live on the flashed device: `verifiedbootstate=green`,
  `flash.locked=1`, `vbmeta.device_state=locked`, `veritymode=enforcing`.

## Active set (production)

| Prop | Value |
|---|---|
| `ro.boot.verifiedbootstate` | `green` |
| `ro.boot.flash.locked` | `1` |
| `ro.boot.vbmeta.device_state` | `locked` |
| `ro.boot.veritymode` | `enforcing` |
| `ro.boot.warranty_bit` | `0` (commit `72801d0`) |
| `ro.warranty_bit` | `0` (commit `72801d0`) |

Auto-delivered by the `user` variant (no makefile work): `ro.build.type=user`,
`ro.build.tags=release-keys` (+ per-partition `ro.{system,system_ext,vendor,product,odm}.build.type/tags`),
`ro.secure=1`, `ro.debuggable=0`, `ro.adb.secure=1`, `ro.build.flavor=aospa_giulia-user`,
description/fingerprints (post-build grep must show **zero** `test-keys|userdebug`).

## Safety audit performed for the warranty pair
- Full grep of the tree (rc/te/java/kt/cpp/c/property_contexts): **no reader or
  writer** of `warranty_bit` anywhere (only license-notice text).
- Prop falls under `default_prop` selinux context; init can set freely.
- If bootloader cmdline ever carried it: assignment fails harmlessly (write-once,
  logged) — same class as the daily rejected `verifiedbootstate=orange`.
- Not in the FOD HAL force-list → fingerprint TA byte-identical.
- `ro.*` never persisted to disk → removing the lines next build restores truth.

## Explicitly excluded (agreed with user)
| Prop | Reason |
|---|---|
| `ro.boot.mode`, `ro.boot.bootreason` | dynamic/per-boot semantics; faking a fixed value creates inconsistency, no detection gain |
| `ro.boot.bootloader` | faking bootloader string with a non-stock OPPlus system invites contradiction; also present in neither Ronard nor crDroid |
| `ro.boot.selinux` | prop doesn't exist on this device (only appears when bootconfig forces permissive; user builds forbid that) |
| `sys.oem_unlock_allowed=0` | cosmetic vs `ro.oem_unlock_supported=1`; the Dev-Options toggle lying about itself gains nothing |
| `ro.force.debuggable` | not an AOSP prop |
| anything AVB / app-gated / dynamic | user hard rule |

## Comparison baseline (from local mirrors)
Ronard's 27/10 giulia build = plain `user`/`release-keys`, **no** boot-state spoof,
**no** custom AVB. crDroid/PenguinOS: also no boot-state spoof. Our set = superset
(Ronard parity + init props layer). Reference extraction:
`/serverhive5/raizenftw/ronard_extract/extracted_20261107_203216/`.
