# 11 — Decision log & open items

## Decisions (chronological, with rationale)

1. **Userdebug first, production second** — validate every feature on the dev build; userdebug zip kept as fallback.
2. **Prop spoof = static system-wide only** — no app-gated/dynamic logic, no Magisk/PIF/TEE/AVB keys; user's explicit boundary. Implemented in `init` (pre-cmdline, write-once wins, recovery skips).
3. **Boot-state spoof already in-tree** — audited: works (`green/locked/enforcing` verified live); no new code needed.
4. **Warranty props added** (`72801d0`) after a safety audit proved zero in-tree consumers, `default_prop` context, harmless rejection semantics, recovery-exempt, FOD-HAL-safe.
5. **Production recipe = Ronard parity + spoof layer** — plain `user` + `release-keys` (verified from his extraction), ours adds the init props. Exclusions: `ro.boot.mode`, `bootreason`, `bootloader`, `selinux`, `sys.oem_unlock_allowed`, `ro.force.debuggable` (each reason in `05`).
6. **Route A rejected by the tree** — `ro.build.tags` is certificate-driven here (first user build empirically proved `test-keys` despite `user` variant). Route A as originally promised is impossible; state it rather than fake it.
7. **Route B-lite = the tree's own `vendor/aospa-priv` hook** — private keyset + one mk line; tags+default-APK certs+OTA container coherent at build time; chosen over (a) post-build `sign_target_files_apks` ceremony (helper `-s` route kept as fallback) and (b) the `BUILD_KEYS` text-hack (touches build/make internals, cert mismatch).
8. **Cert value must be a file basename** — learned from the cuttlefish overlay bootstrap error (`009adecb`).
9. **NFC QS tile abandoned** (user: "no need") — TileService lacks `onLongClick()`/`startSettingsAndCollapse()`; manifest route (`DEFAULT` category on `QS_TILE_PREFERENCES`) later used for BypassCharge instead.
10. **Burn-in protection off** — it drifted the bar (up to 136 px) and looked like a bug; Settings+Controller default off; phone reset to 0.
11. **NFC HAL handling** — ship OPlus AIDL+Extns HALs + force classic `NfcNci`/`framework-nfc` stack (APEX protocol-mismatch), pinned via release aflags (`167aae1200`, `30815ed`).
12. **Build compliance** — adopt admin policy exactly (tmux + `bash -l`, no env override, no extra daemons); `-j64` chosen after observing 192-core default colliding with co-tenant memory pressure.
13. **Farm escalation** — after four boundary failures (two kills, two wedges) even fully compliant, the correct next step is admin contact (draft in `07`); user-ordered build stop honored at 26%.
14. **Keyset custody** — never in git; backup copied to laptop (`/home/raizen/aospa-keys-backup/security/`).
15. **Temporary return to userdebug/test-keys** (user decision, 2026-11-08) — production/release-keys effort parked; the cert line in `aospa_giulia.mk` is commented out (commit `5256c361`, pushed to both branches on remote `aospa`) so builds land on the in-tree testkey set. Rationale: testing mode preferred right now. Production resumes with one uncommented line + `-t user` (runbook `10.A`, toggle map in `12`). Nothing else changes: keyset stays in place on waffle (untracked, laptop backup current), spoof stays in `init`.

## Open items
1. ✅ Resolved: the farm kills/wedges were collateral of a **server reboot for maintenance** (seen as reset uptime + restored key login). The escalation draft in `07` is retired.
2. ✅ Resolved: All pending local commits (`72801d0`, `167aae1200`, `30815ed`) pushed to `aospa_system_core`, `aospa_build`, `aospa_build_make`, and `aospa_build_release` in `aospa-f`.
3. ⏳ Build in the **current default mode** (userdebug/test-keys, runbook `10.A0`) on user go. Farm load may still be high (load 706+ right after the reboot); the wrapper's `-l 440` cap makes the build idle until the farm cools — not an error.
4. ⏸ Parked: release-keys production — uncomment the cert line in `aospa_giulia.mk` (map in `12`), commit+push both branches, then runbook `10.A` (`-t user`; the 26% cached device graph resumes, no `-i`).
5. ⏳ Audit gate (`10.C`) → download → flash → `08` checklist (whichever zip is the flash target).
6. ⏳ Optional post-flash report of any name-referenced cert leftovers (informational).
7. Future (optional): move to the helper's official `-s` full-`sign_target_files_apks` route for 100% cert coherence; keep both keysets and the userdebug fallback forever.

## Context that must survive
- The userdebug fallback zip + md5; the test-keys intermediate artifact; keyset backup location.
- Ronard/romaudit extraction paths for comparison work.
- All feature work lives in pushed commits — the phone runs the userdebug image with them; production zip currently being produced nothing new feature-wise, only signing/variant/keys.
