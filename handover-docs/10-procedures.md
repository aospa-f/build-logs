# 10 — Runbooks

## A0. Current-mode build — userdebug/test-keys (the default since 2026-11-08)
```bash
ssh waffle
tmux new-session -d -s rxbuild \
  "bash -lc \"cd /serverhive5/raizenftw/aospa && ./rom-build.sh giulia -j64 2>&1 | tee /serverhive5/raizenftw/build-logs/userdebug_build.log\""
```
Add `-i` for the **first** run after the user-variant builds (installclean for the
variant swap). Helper default `-t` is `userdebug`; the cert toggle is parked
(`5256c361`) ⇒ `test-keys`.

## A. Production mode — release-keys (parked; resume here)
(no `-i` on this path; prereq: re-enable the cert toggle per `12`, commit+push)
```bash
ssh waffle
tmux new-session -d -s rxbuild \
  "bash -lc \"cd /serverhive5/raizenftw/aospa && ./rom-build.sh giulia -t user -j64 2>&1 | tee /serverhive5/raizenftw/build-logs/release_build.log\""
```
Success line at the end: `#### build completed successfully (…)` and
`out/target/product/giulia/aospa_giulia-ota.zip` rebuilt.

Direct equivalent (proven earlier in session; use if the helper misbehaves):
```bash
cd /serverhive5/raizenftw/aospa && source build/envsetup.sh && lunch aospa_giulia-user && m otapackage
```

Trace with `kill -9 $(pgrep -x <name>)` per exact name (`soong_ui ninja ckati kati
rewrapper`) when asked to stop; never `pkill -f <string>` — it self-matches over ssh (exit 255).

## B. Farm health probes (one-shot, non-invasive)
```bash
ssh waffle 'date +%H:%M:%S; cat /proc/loadavg; pgrep -x rewrapper | wc -l
stat -c "mtime=%y" /serverhive5/raizenftw/build-logs/release_build.log
tail -n 2 /serverhive5/raizenftw/build-logs/release_build.log; cat /proc/pressure/cpu'
```
Wedge signature: log `mtime` frozen ≥ several minutes, `rewrapper` count 0, `$loadavg` < 440, ninja alive at ~0 % CPU.
Then read `/serverhive5/raizenftw/aospa/out/soong.log` (sanctioned diagnostic).

## C. Post-build audit gate (run BEFORE anything touches the phone)
```bash
O=/serverhive5/raizenftw/aospa/out/target/product/giulia
for f in $O/system/build.prop $O/system_ext/build.prop $O/vendor/build.prop $O/odm/etc/build.prop; do
  echo "== $f"
  grep -E "^ro\.(build|system|system_ext|vendor|odm)\.build\.(type|tags|fingerprint|description)\b" "$f"
  grep -acE "test-keys|userdebug" "$f"   # must print 0
done
strings $O/system/bin/init | grep -a warranty_bit        # expect 2 hits
unzip -p <ota.zip> META-INF/".*RSA" | head -c 400         # container cert check
```
Then md5 both sides and download:
```bash
md5sum $O/../product/giulia/aospa_giulia-ota.zip
scp waffle:$O/../aospa_giulia-ota.zip /home/raizen/Downloads/<new-name>.zip && md5sum <new-name>.zip
```
Optional APK-certificate spot-check: `apksigner verify --print-certs` on extracted
`SystemUI.apk` — expect `CN=AOSPA OP5D3BL1` for default-signed packages (in-tree keys
on name-referenced certs is an acceptable known caveat; report, don't block).

## D. Flash & validate
Standard sideload/recovery flow the user already uses; then run the non-root
checklist in `08` (no `adb root` exists on `user` builds).

## E. Git push of pending local commits (after user creates the 3 empty repos)
```bash
for spec in "system/core:/serverhive5/raizenftw/aospa/system/core:aospa_system_core" \
            "build/make:/serverhive5/raizenftw/aospa/build/make:aospa_build" \
            "build/release:/serverhive5/raizenftw/aospa/build/release:aospa_build_release"; do
  repo=${spec%%:*}; rest=${spec#*:}; path=${rest%%:*}; org=${rest##*:}
  git -C "$path" remote add aospa-f git@github.com:aospa-f/$org.git 2>/dev/null
  git -C "$path" push aospa-f HEAD:refs/heads/calcite
done
```
(All three repos are on detached HEADs with the commits at tip — `HEAD:` push works.)

## F. Never do
- Push anything under `vendor/aospa-priv/` to git.
- Launch builds outside tmux+`bash -l` (admin policy; observed kills).
- `pkill -f` with a string that appears in your own remote command (self-kill, exit 255).
- Re-run `-i` after this point unless certificates change again — it re-wipes installed
  outputs and forces `RECOMPILE_KERNEL=1` (user ⇒ `LTO="full"`).
- Modify the FOD HAL force-list (`Utils.cpp::kForcedProperties` values).
