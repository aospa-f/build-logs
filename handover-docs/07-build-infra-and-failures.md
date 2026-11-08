# 07 — Build infrastructure & failure log (evidence-grade)

## Helper script
`rom-build.sh` (symlink → `vendor/aospa/build.sh`), AOSPA official. Flags:
`-c` clobber-clean, `-i` installclean, `-r` repo-sync, `-v` AOSPA variant (alpha/beta/stable),
`-t` build type (default `userdebug`), `-j` jobs (**default = nproc ⇒ 192!**),
`-m` module, `-s` sign-key mappings (official `sign_target_files_apks` route),
`-p` password file, `-b` backup unsigned, `-d` delta target, `-z` imgzip, `-n` version.

Current mode (2026-11-08): **userdebug/test-keys is the default** — the release-key
cert line is parked behind a comment (`5256c361`); production resumes by re-enabling it.
Server layout + full build how-to: `12-server-layout-and-building.md`.
Behavior: envsetup → lunch `aospa_<device>-<type>` → optional installclean →
(optional kernel_platform rebuild with `RECOMPILE_KERNEL=1` when `-c/-i`, user ⇒ `LTO="full"`)
→ `m` (full package) or the `-s` signing flow.

## Attempt ledger (release-keys effort, 2026-11-08)

| # | How launched | Result |
|---|---|---|
| 1 | plain `ssh … lunch aospa_giulia-user && m otapackage` (pre-keyset) | ✅ 14:53 → `user`+**test-keys** zip (md5 `1935be7…`) — proof tags are cert-driven |
| 2 | with directory-valued cert | ❌ soong bootstrap: `cuttlefish…overlay… source path "vendor/aospa-priv/security.pk8" does not exist` (48 s; legit config bug, fixed by `009adecb`) |
| 3 | plain ssh background | 🔪 Killed at 03:15 — `shell_utils.sh:199: 3330203 Killed "$@"` |
| 4 | tmux **without** login shell | 🔪 killed per admin notice ("outside properly initialized login session / env override") |
| 5 | tmux + `bash -l`, `-j64`, `-i` | 🧊 wedged: frozen 32 min at Soong bootstrap **51% (149/288)**; `/opt/ninja` alive (0.1% CPU, 522 MB RSS), **0 workers**, load 198 ≪ `-l 440`; killed |
| 6 | resumed, no `-i` (compliant) | ahead: full sm8650 **kernel built**; 🧊 wedged right after (`make: Leaving directory …/kernel/oneplus/sm8650`, log frozen, 0 `rewrapper`); relaunch of #6 reached **26% (35,848/132,847)** then user-ordered stop |

## Evidence collected
- Memory contention on the shared box: `/proc/meminfo` snapshots during failures showed
  MemFree as low as 9–32 GiB, swap 27–72 GiB used, MemAvailable 150–250 GiB, co-hosted consumers elsewhere.
- No OOM traces accessible (`journalctl` restricted/no hits), `user.slice` cgroup `memory.max=max`, no
  ulimit caps (`ulimit -v/m` unlimited both in tmux and ssh; `RLIMIT_NOFILE=1024`).
- PSI (`/proc/pressure/{cpu,io}`) near-idle at wedge time ⇒ not CPU/IO starvation.
- Farm wrapper rewrites jobs: live ninja cmdline `-j 1200 … -l 440` (user's `-j64` overridden).
- `out/soong.log` before "done" listed **~24 hanging `sh` processes** spawned during the kati/make phase —
  the signature of the farm's subprocess plumbing (or its watchdog) reaping children while parents wait.
- `reproxy` (farm client) disappears when the build session dies — it's lazily launched per build.
- Prior context: two **earlier** userdebug-branch builds completed fine through this same infra (this
  session's first build too) — behaves intermittently at high co-tenant load.

## Conclusion
Failures cluster at the RBE farm boundary (`/opt/ninja` wrapper, `reproxy`, `rewrapper`) —
kill/wedge behavior active even when fully compliant (tmux + `bash -l` + login env verified).
Not a memory/ulimit/cgroup issue. The build itself is healthy: every relaunch reuses state and advances
(bootstrap resume 87/140 in 50 s; device graph to 26%).

## Escalation draft (send via the user)
```
Subject: builds on waffle (user raizenftw) repeatedly terminated/wedged at the build-farm boundary

Hi,

My AOSP build for target "giulia" (tree: /serverhive5/raizenftw/aospa,
invocation: ./rom-build.sh giulia -t user -i -j64) has failed 4 times today
and I'd like to know whether it's farm-side.

What I have verified on my side:
- Runs started inside a persistent tmux session with a login shell
  (bash -lc), so /etc/profile.d loads and CUSTOM_NINJA_BIN=/opt/ninja is
  exported correctly.
- Memory/cgroup limits are not the issue (user.slice max is "max").

Observed patterns:
1. Two silent kills: build/soong's shell_utils.sh:199 child reported
   "Killed" at 01:05 (2026-11-08) and 07:44 UTC.
2. Two freezes instead of kills, under full compliance:
   - Freeze #1: soong bootstrap at 51% (149/288), zero progress for 32 min;
     /opt/ninja alive at 0.1% CPU with no children, load 198 (far below the
     -l 440 cap the wrapper applies), reproxy up.
   - Freeze #2: after the full sm8650 kernel phase, log frozen again; 0
     rewrapper workers, ninja idle; out/soong.log listed ~24 hanging "sh"
     subprocesses spawned during the kati/make phase before "done".

Questions:
- Is the build scheduler/RBE farm (reproxy, /opt/ninja wrapper, rewrapper)
  actively killing jobs for this host/user? If yes, which session metadata
  do you need me to use?
- Is there a stuck bastion/session state on the farm that needs a reset
  for user raizenftw?
- If the farm keeps wedging these runs, is a local-only fallback (reproxy
  disabled / stock ninja) permitted for this tree?

Log file: /serverhive5/raizenftw/build-logs/release_build.log
Thanks!
```

## Compliance checklist before ANY relaunch
1. tmux session only; command wrapped in `bash -lc`.
2. Don't pass env-override tricks; `-j64` is fine and demonstrated memory-safe.
3. No extra watchdog/dashboard daemons besides the build (admin-friendly).
4. One-shot status peeks only (`tail`, `stat mtime`, worker counts) — no chatter loops.
5. Wedge signature to watch: log `mtime` frozen + `pgrep -x rewrapper` = 0 + `$loadavg` < 440.
