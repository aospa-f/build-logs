# 09 — Artifacts inventory

## On waffle
| Path | What |
|---|---|
| `/serverhive5/raizenftw/aospa/out/target/product/giulia/aospa-calcite-unofficial-giulia-20261108.zip` | **Production ROM Zip** (`user` + `release-keys`, 2.9 GB, Nov 2026 patch) |
| `/serverhive5/raizenftw/aospa/out/target/product/giulia/aospa_giulia-ota.zip` | **Target OTA Package** (2.9 GB) |
| `/serverhive5/raizenftw/extracted_release_user_20261108/extracted_20261108_155027/` | Extracted partition images (`boot`, `init_boot`, `recovery`, `system`, `vendor`, `odm`, `product`, `system_ext`, `vbmeta`, etc.) |
| `/serverhive5/raizenftw/aospa/vendor/aospa-priv/security/` | **Live private keyset** (18 files: 9 `.pk8` + 9 `.x509.pem` + symlinks, never commit) |
| `/serverhive5/raizenftw/build-logs/` | Build logs and documentation suite |
| `/serverhive5/raizenftw/build-logs/release_user_build.log` | Full build log of successful production user/release-keys build |

## On the laptop
| Path | What |
|---|---|
| `/home/raizen/aospa-keys-backup/security/` | **Private release keyset backup** — mirrored with waffle |
| `/home/raizen/Downloads/aospa-calcite-unofficial-giulia-20261108.zip` | Prior userdebug build zip |
| `/home/raizen/aospa-handover/*.md` | Local documentation backup |

## Reference extractions & mirrors (waffle)
| Path | Purpose |
|---|---|
| `/serverhive5/raizenftw/ronard_extract/` | Ronard 27/10 giulia ROM payload & images |
| `/serverhive5/raizenftw/romaudit/` | Other ROM comparisons |

## Validated Output Properties
- `ro.build.type`: `user`
- `ro.build.tags`: `release-keys`
- `ro.build.version.security_patch`: `2026-11-01`
- `ro.system.build.fingerprint`: `OnePlus/aospa_giulia/giulia:17/CQ2A.260820.002-CP2A.260605.016/eng.nobody:user/release-keys`
- 6 Spoofed props in `system/bin/init`: `verifiedbootstate`, `flash.locked`, `vbmeta.device_state`, `veritymode`, `warranty_bit` (both keys)
