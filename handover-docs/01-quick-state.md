# 01 — Quick state (read this first)

## Completed and validated
- **Userdebug build** for giulia built, downloaded, **flashed and running on the phone**: all feature fixes live (FOD HAL up, NFC working — user keeps NFC off; each feature's validation evidence in `04`/`08`).
- **High touch polling rate fix verified live**: Settings crash eliminated (`debug.touch_polling_mode` + `Settings.Secure`), HAL wired directly to the SM8650 Synaptics TCM HBP `high_rate` sysfs node with init triggers. Live tested on connected phone: toggles 0 ↔ 1 cleanly with zero crashes.
- **LTPO display scaling verified live**: Dynamic refresh rate verified on phone down to 1 Hz idle and up to 120 Hz in apps and motion via `measured_fps`.
- **Boot-state prop spoof verified live**: `verifiedbootstate=green`, `flash.locked=1`, `vbmeta.device_state=locked`, `veritymode=enforcing` (+ `warranty_bit` pair added later, present in shipped `init` as strings).
- All listed source **changes are committed and pushed** to the `aospa-f` org (see `03`).
- Production recipe fully designed: `user` + private release keyset + `vendor/aospa-priv/` filter ⇒ `ro.build.tags=release-keys` (details in `06`).

## In-flight / interrupted
- **Release-keys build run #6** was stopped by user order at **26% (35,848/132,847)** of the device graph. Everything compiled so far is cached incrementally for when production resumes. Kernel for `kernel/oneplus/sm8650` was fully built in run #6's predecessor.
- **User decision: park release-keys** — the cert line is commented (`5256c361`), so builds default to **userdebug/test-keys** again until further notice.
- Five prior attempts documented in `07`: two silent kills, two farm wedges, one legit error (fixed) — retro-traced to the server rebooting for maintenance.

## Next action
1. Say "go" to launch/resume the userdebug/test-keys build — command in `10.A0`.

## Exact build command (current default mode — userdebug/test-keys)
```bash
ssh waffle
tmux new-session -d -s rxbuild "bash -lc \"cd /serverhive5/raizenftw/aospa && ./rom-build.sh giulia -j64 2>&1 | tee /serverhive5/raizenftw/build-logs/userdebug_build.log\""
```
Add `-i` for the **first** run after the user-variant builds. Then wait for completion (`tail -f` the log). On success run the audit gate in `10.C` — do **not** flash before it passes. Server map, mode toggle and everything build-related: `12-server-layout-and-building.md`.

## Keys
Private keyset: waffle `/serverhive5/raizenftw/aospa/vendor/aospa-priv/security/` — in **no** git repo, must never be pushed. Backup exists at `/home/raizen/aospa-keys-backup/security/`.
