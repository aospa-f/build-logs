# 03 — Repos, branches, commit ledger

Tree: `/serverhive5/raizenftw/aospa` (repo-managed, per-project git). Branch names
differ per repo (manifest-driven): `frameworks/base` on `stock-qs`; `vendor/aospa`
on `axion-scene-qs`; others on `calcite`.

## Matrix (state at handover)

| Path | GitHub (`aospa-f`) | Branch | Push state |
|---|---|---|---|
| `frameworks/base` | `aospa_frameworks_base` | `stock-qs` | ✅ HEAD `473e394e` (status-bar end anchor) |
| `packages/apps/Settings` | `aospa_packages_apps_Settings` | `calcite` | ✅ `abde778adc9` |
| `packages/apps/BypassCharge` | `packages_apps_BypassCharge` | `calcite` | ✅ `f161fd0` |
| `device/oneplus/sm8650-common` | `device_oneplus_sm8650-common` | `calcite` | ✅ clean |
| `device/oneplus/giulia` | `device_oneplus_giulia` | `calcite` | ✅ clean (also `clo` upstream remote) |
| `vendor/oneplus/sm8650-oss` | `vendor_oneplus_sm8650-oss` | `calcite` | ✅ clean (remote **named `github`**) |
| `vendor/aospa` | `aospa_vendor_aospa` | `axion-scene-qs` (+`calcite` mirror) | ✅ `3d889cb5` + `009adecb` + `5256c361` on both (remote named `aospa`) |
| `system/core` | `aospa_system_core` | `calcite` | ✅ `72801d0` |
| `build/make` | `aospa_build` / `aospa_build_make` | `calcite` | ✅ `167aae1200` |
| `build/release` | `aospa_build_release` | `calcite` | ✅ `30815ed` |

Extra remotes present in tree (multi-fork collaboration, harmless): `shadedark` →
`aospa-shadedark/android_*` on frameworks/base + Settings + vendor/aospa;
`penguinos` → `penguinos-shadedark/frameworks_base`; vendor/aospa/prebuilt →
GitLab `ThankYouMario/android_vendor_aospa_prebuilt` (its untracked `common/`
dir is upstream's artifact — leave alone). Read-only AOSP/CLO remotes:
`oplus-8650-clo/*`, `clo-la` (codelinaro), `clo-for-giulia`.

## Commit ledger (this project)

| Hash | Repo | Commit | Why |
|---|---|---|---|
| `473e394e` | frameworks/base | Anchor the status bar end side to the right edge | anchoring fix (earlier session) |
| (earlier) | frameworks/base | battery-first measuring, HD/carets suppression, 4-icon speed-hide, extra-dim slider, ignore-secure, burn-in default-off | see `04` |
| (earlier) | device/oneplus/sm8650-common, sm8650-oss | NFC HAL prebuilts shipping, FOD rc, touch HAL, BypassCharge | see `04` |
| `f161fd0` | packages/apps/BypassCharge | Route tile long-press to the settings screen manifest-side | `onLongClick()` / `startSettingsAndCollapse()` **do not exist** in this base's TileService; the working pattern is adding `android.intent.category.DEFAULT` to the `QS_TILE_PREFERENCES` intent-filter |
| `abde778adc9` | packages/apps/Settings | Turn status bar burn-in protection off by default | `res/xml/display_settings.xml` `status_bar_burn_in_protection` defaultValue true→false (this file sat uncommitted; flashed ROM was built from the dirty tree — now git matches) |
| `72801d0` | system/core | init: Report an intact warranty state to userspace | adds `ro.boot.warranty_bit=0` + `ro.warranty_bit=0` to `SetSafetyNetProps()` |
| `3d889cb5` | vendor/aospa | giulia: Sign with a private release key set | wires `PRODUCT_DEFAULT_DEV_CERTIFICATE` |
| `009adecb` | vendor/aospa | giulia: Point PRODUCT_DEFAULT_DEV_CERTIFICATE at the releasekey file | fixes the directory-vs-file-basename bug |
| `167aae1200` | build/make | build: Always ship the classic NFC stack | `base_system.mk` + `default_art_config.mk`: the nfcservices APEX NCI client protocol-mismatches the OPlus HAL; force `framework-nfc` + `NfcNci`; drop APEX boot-fragment path |
| `30815ed` | build/release | release: Pin the NFC stack flags to the classic NfcNci path | `flag_values/cp2a/RELEASE_APEX_CONTRIBUTIONS_NFC.textproto`=false, `RELEASE_PACKAGE_NFC_STACK.textproto`="NfcNci" |
| `5256c361` | vendor/aospa | giulia: Return to the in-tree testkey set for now | Parks the release-key wiring behind a comment — production paused, builds are userdebug/test-keys again (mode toggle map in `12`) |

## Pending org-repo creations (user action: create **empty** repos, no README)

```
# after user creates the repos:
cd /serverhive5/raizenftw/aospa/system/core
git remote add aospa-f git@github.com:aospa-f/aospa_system_core.git   (then:) git push aospa-f HEAD:refs/heads/calcite
cd /serverhive5/raizenftw/aospa/build/make      → aospa_build         → git push aospa-f HEAD:refs/heads/calcite
cd /serverhive5/raizenftw/aospa/build/release   → aospa_build_release  → git push aospa-f HEAD:refs/heads/calcite
```
(distant repos are detached-HEAD checkouts; pushing `HEAD:refs/heads/calcite` works fine.)

## Never push
- `vendor/aospa-priv/security/` — private release keyset (see `06`).
- `vendor/aospa/prebuilt/common` — upstream GitLab mirror artifact, not ours.
