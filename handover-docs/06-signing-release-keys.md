# 06 — Signing & release-keys (the decisive discovery)

## The tree derives `ro.build.tags` from the certificate, NOT the variant

`build/make/core/config.mk` ~1361–1374 (verbatim behavior):
```makefile
# The "test-keys" tag marks builds signed with the old test keys ...
ifeq ($(DEFAULT_SYSTEM_DEV_CERTIFICATE),build/make/target/product/security/testkey)
BUILD_KEYS := test-keys
else ifneq ($(filter vendor/aospa-priv/%,$(DEFAULT_SYSTEM_DEV_CERTIFICATE)),)
BUILD_KEYS := release-keys
else
BUILD_KEYS := dev-keys
endif
BUILD_VERSION_TAGS += $(BUILD_KEYS)
```
And `BUILD_FINGERPRINT` composes `...:$(TARGET_BUILD_VARIANT)/$(BUILD_VERSION_TAGS)`.
`gen_build_prop.py:252` emits `ro.build.tags?=$(BuildVersionTags)` (note the
optional `?` declaration — part of the AOSP `go/arc-android-sigprop-changes` scheme,
same TODO comment lives in the script).

**Consequence**: "Route A" (plain `lunch aospa_giulia-user`, release-keys text for
free) is **impossible** in this tree — empirically proven by the first user build
coming out `ro.build.type=user` + `ro.build.tags=test-keys`. Any private cert
directory path under `vendor/aospa-priv/` ⇒ release-keys ⇒ this is exactly
Ronard-parity (his build.prop shows `user/release-keys`).

## `DEFAULT_SYSTEM_DEV_CERTIFICATE` consumers (all treat it as a FILE basename)
- `config.mk:861-867` — set from `PRODUCT_DEFAULT_DEV_CERTIFICATE`, else in-tree `testkey`.
- `config.mk:873,888` — `MAINLINE_SEPOLICY_DEV_CERTIFICATES := $(dir $(DEFAULT_SYSTEM_DEV_CERTIFICATE))` — **`dir()` keeps working with a basename**.
- `build/make/core/Makefile:947` `DEFAULT_KEY_CERT_PAIR`; `:1485/1513` `$(DEFAULT...).pk8`; `:1490/1516` `ota_from_target_files --package_key $(DEFAULT...)` ⇒ **the OTA zip container is signed with this cert too**.
- Soong side: `device/google/cuttlefish/shared/phone/overlays/core/Android.bp:20`
  (module `cuttlefish_phone_overlay_frameworks_base_core`) appends `.pk8` at
  *bootstrap-parse time* — a **directory** value broke soong with
  `source path "vendor/aospa-priv/security.pk8" does not exist`. Basename fixes it.

## Keyset (private, local-only)
- 9 pairs, RSA-2048 pk8+x509: `releasekey platform shared media networkstack bluetooth nfc sdk_sandbox cts_uicc_2021`
  (mirrors the in-tree `build/make/target/product/security/` family minus `testkey`).
- Location: `/serverhive5/raizenftw/aospa/vendor/aospa-priv/security/` — **untracked, never commit/push**.
- Laptop backup: `/home/raizen/aospa-keys-backup/security/` (18 files).
- Generation (direct openssl; the in-tree `development/tools/make_key` is
  FIFO/`read`-based and fragile over non-interactive ssh; its arg order here is
  `<name> "<subject>"`, RSA via `-f4 2048`):
  ```bash
  openssl genrsa   -out k.pem 2048
  openssl req -new -x509 -sha256 -key k.pem -out <base>.x509.pem -days 10000 \
      -subj "/C=US/ST=California/L=Mountain View/O=AOSPA/OU=AOSPA/CN=AOSPA OP5D3BL1/emailAddress=android@op5d3bl1.local"
  openssl pkcs8 -in k.pem -topk8 -outform DER -out <base>.pk8 -nocrypt
  ```
  (commas need escaping in subjects — we avoided them; spaces in values are fine.)

## Wiring (current, committed)
`vendor/aospa/products/giulia/aospa_giulia.mk:39`:
```makefile
PRODUCT_DEFAULT_DEV_CERTIFICATE := vendor/aospa-priv/security/releasekey
```
History: `3d889cb5` introduced it with a **directory** value (`vendor/aospa-priv/security`)
→ soong bootstrap failure (above) → `009adecb` corrected to the file basename.
Both commits pushed to `axion-scene-qs` + `calcite`.

## What the flip delivers automatically on a user build
- `ro.build.tags` + all partition tags = `release-keys`
- APKs that use the *default* certificate re-signed with our keyset
- OTA container signed with `releasekey.pk8` (coherent props+container)
- `ro.build.fingerprint`/`ro.<partition>.build.fingerprint` end in `user/release-keys`

## Known caveat to verify post-build (not a blocker)
Apps referencing certs by literal name (`certificate: "platform"`, `"shared"`,
`"media"`) may keep resolving to the **in-tree AOSP keys** depending on soong
wiring — the same situation any ordinary unofficial build has; detection apps read
the *prop* surface, not cert hashes, and every unofficial ROM has a different plat
cert anyway (see `11`). The helper's official post-signing route exists if we ever
want 100% coherence: `rom-build.sh -s <keydir>` ⇒
`sign_target_files_apks -o -d ...` + `ota_from_target_files -k <keydir>/releasekey ...`.

## Also known about generated props (from the test-keys build's build.prop)
- `ro.build.description` picked up the AOSPA `BuildDesc` override
  (`qssi_64-user 16 BP2A.250605.015 1786543506192 release-keys`) — already release-keys.
- The auto-composed `ro.system.build.fingerprint` was
  `OnePlus/aospa_giulia/giulia:17/CQ2A.260820.002-CP2A.260605.016/eng.nobody:user/test-keys`
  — after the cert flip it becomes `...:user/release-keys`. The device-tree
  `BuildFingerprint=OnePlus/CPH2691IN/OP5D3BL1:...:user/release-keys` override did
  **not** land in the generated system fingerprint in that build — re-verify at the
  post-build audit and report; both compositions end `user/release-keys` after the flip.
- AOSPA version cosmetics stay `calcite-unofficial...` (`vendor/aospa/target/product/version.mk`
  — `AOSPA_BUILDTYPE` ALPHA/BETA/STABLE env; unset ⇒ `unofficial`). Same as Ronard's.
