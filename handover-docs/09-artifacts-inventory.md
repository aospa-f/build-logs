# 09 — Artifacts inventory

## On the laptop
| Path | What | md5 |
|---|---|---|
| `/home/raizen/Downloads/aospa-calcite-unofficial-giulia-20261108.zip` | **Flashed userdebug fallback** zip (server build 18:59) | `99ce27d11208702d66bf246c287c7269` |
| `/home/raizen/Downloads/aospa-calcite-unofficial-giulia-user-testkeys-20261108.zip` | `user`+`test-keys` intermediate (release-key build attempt #1) — document-only, not a flash target | `1935be7d1add95eea53ad927af397552` |
| `/home/raizen/aospa-keys-backup/security/` | **private release keyset backup** — 18 files (9 `.pk8` + 9 `.x509.pem`) | — |
| `/home/raizen/rom-handover-20261108.md` | Single-file handover (superseded by this suite) | — |
| `/home/raizen/aospa-handover/*.md` | This documentation suite (11 docs) | — |
| `/tmp/opencode/verify_user_rom*.sh` | Post-build props audit scripts (used for the test-keys build; recreate/refresh per `10`) | — |

## On waffle
| Path | What |
|---|---|
| `/serverhive5/raizenftw/aospa` | Full source tree (manifest: repo-managed workspace) |
| `/serverhive5/raizenftw/aospa/out/target/product/giulia/` | Build output dir — **as of 2026-11-08 (late): no OTA `.zip` present on the server anymore** (the test-keys OTA + its safety copy were moved/removed; the laptop zips below are the only reference copies). `out/` retains the partial `user`-variant device-graph state (26% cache). A new build regenerates `aospa_giulia-ota.zip` fresh. |
| `/serverhive5/raizenftw/aospa/vendor/aospa-priv/security/` | **Live** private keyset (never commit; backup exists on laptop) |
| `/serverhive5/raizenftw/build-logs/` | All historical & current build logs (including `release_build.log`, `memwatch.log`, and all session run logs) — backed up & pushed to [`aospa-f/build-logs`](https://github.com/aospa-f/build-logs) |

## Reference extractions & mirrors (waffle)
| Path | Purpose |
|---|---|
| `/serverhive5/raizenftw/ronard_extract/` | Ronard's 27/10 giulia ROM: `payload.bin` (3.0 GB) + `extracted_20261107_203216/{system,vendor,odm}.img`; his `system/build.prop` = the production-recipe reference (`user/release-keys`, no spoof, no custom AVB) |
| `/serverhive5/raizenftw/romaudit/` | Other ROM mirrors used for comparisons: `axion_settings`, `crdroid_fb`, `crdroid_settings`, `penguinos_fb`, `penguinos_settings`, `voltage_settings` |

## Out-tree basics
- Partition props to audit post-build: `out/target/product/giulia/{system,system_ext,vendor,odm}/build.prop`
- Shipped init binary: `out/target/product/giulia/system/bin/init` (`strings | grep warranty` ⇒ 2 hits expected)
- OTA container key: `META-INF/*.RSA` in the zip = `releasekey` after the flip
