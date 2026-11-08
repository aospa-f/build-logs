# 12 — waffle server layout & how to run builds

**Server:** `ssh waffle` — the laptop's `~/.ssh/config` maps it to
`raizenftw@waffle.serverhive.in`, port 22, key `~/.ssh/id_ed25519`
(`StrictHostKeyChecking accept-new`, `ForwardAgent yes`); no password needed.
If key auth ever fails after a server maintenance, log in once by password from a
terminal and re-append `~/.ssh/id_ed25519.pub` to `~/.ssh/authorized_keys`.

Home on waffle = **`/serverhive5/raizenftw`**. Hardware: 192 cores, ~755 GiB RAM,
14 T NVMe on `/serverhive5`. It is a **shared build farm** (RBE) with co-tenants —
see farm mechanics below.

## Directory map

```
/serverhive5/raizenftw/                      ← ~ on waffle
├── aospa                                    ← the ROM source tree (repo-managed manifest workspace)
│   ├── rom-build.sh -> vendor/aospa/build.sh    ← official build entry point (use this)
│   ├── build/                                   envsetup.sh, make/ (build/make), release/ (build/release)
│   │      ├── make/      local-only commit 167aae1200 (classic NFC stack) — no org repo yet
│   │      └── release/   local-only commit 30815ed (NFC flag pinning)     — no org repo yet
│   ├── device/oneplus/{sm8650-common,giulia}/   device trees (pushed, clean)
│   ├── frameworks/base/                         status-bar work — branch `stock-qs`
│   ├── packages/apps/{Settings,BypassCharge}/   pushed, clean
│   ├── system/core/                             init spoof commit 72801d0 — detached HEAD — no org repo yet
│   ├── kernel/oneplus/sm8650/                   kernel source (built by the helper on demand)
│   ├── vendor/
│   │   ├── aospa/          ROM config. products/giulia/aospa_giulia.mk (mode toggle below),
│   │   │                   build.sh (= rom-build.sh), version.mk (AOSPA_BUILDTYPE cosmetics)
│   │   ├── aospa-priv/security/   PRIVATE release keyset (18 files) — untracked, NEVER commit/push
│   │   └── oneplus/sm8650-oss/    OPlus HAL prebuilts: FOD, NFC, touch, ...
│   └── out/target/product/giulia/               build outputs (see below)
│
├── build-logs/         build logs (release_build.log = release-keys effort history)
├── ronard_extract/extracted_20261107_203216/    Ronard 27/10 giulia reference (user/release-keys, plain)
├── romaudit/           other-ROM mirrors for comparison (crdroid, penguinos, voltage, axion)
└── (strays at tree root: build_latest.log, test_kati.log, build_parallel.sh, run_build.sh,
    disregard/, vendor_*.themuppets.bak, proprietary_vendor_sony_dolby/ — leftovers/experiments,
    none of them part of the build; leave alone)
```

Note those stray scripts (`build_parallel.sh`, `run_build.sh`) are **not** the build
entry point — always use **`./rom-build.sh`** (the vendor/aospa official helper).

### Inside `out/target/product/giulia/`

| Path | Meaning |
|---|---|
| `aospa_giulia-ota.zip` | the flashable OTA — the build's final product |
| `{system,system_ext,vendor,odm}/build.prop`(+`odm/etc/`) | per-partition props — post-build audit greps these (`ro.build.type`, `ro.build.tags`, fingerprints) |
| `system/bin/init` | shipped init — the boot-state spoof lives in `SetSafetyNetProps()` (`strings … \| grep warranty` ⇒ 2 hits) |
| `ota_metadata(.pb)` | OTA metadata emitted per build |

## Which signing mode is the tree in? (one check)

```bash
ssh waffle "grep -n PRODUCT_DEFAULT_DEV_CERTIFICATE /serverhive5/raizenftw/aospa/vendor/aospa/products/giulia/aospa_giulia.mk"
```

- Line **commented out** (state since commit `5256c361`, 2026-11-08):
  build falls back to the in-tree `testkey` ⇒ `userdebug` + **`test-keys`**.
  This is the **current default mode** (user's choice: back to testing builds).
- Line *uncommented*: cert-based signing from `vendor/aospa-priv/security/releasekey`
  ⇒ `ro.build.tags=release-keys` (+ APK re-signs + OTA container key).
  This is the **production mode** (tenant: keyset must exist on waffle; laptop backup
  at `/home/raizen/aospa-keys-backup/security/`). Full mechanics: doc `06`.

## Build farm mechanics (what actually executes your build)

| Component | Role |
|---|---|
| `/etc/profile.d/Z97-rbe4.sh` | profile hook that exports `CUSTOM_NINJA_BIN=/opt/ninja` — loads only in **login shells** (`bash -l`) |
| `/etc/profile.d/Z97-byobu.sh` | companion profile hook (original wrapper at `/srv/ninja`, commented) |
| `/opt/ninja` | server-managed ninja wrapper. **Overrides your `-j`** (observed `-j 1200 -o usesphonyoutputs=yes --frontend_file out/.ninja_fifo`) and applies a **`-l 440` load cap** |
| `/srv/.rbe/reproxy` | RBE farm client daemon — started lazily per build; `pgrep -x reproxy` empty when idle is normal |
| `/srv/.rbe/scandeps_server` | depscanner unix-socket server |
| `rewrapper` | remote-action workers (dozens while compiling; **0 = possibly wedged**) |

Consequences:

- If `/proc/loadavg` (1-min) is **above 440**, ninja mostly **idles** until the farm cools — a build started then will sit quietly and pick up later. Not an error; don't kill it.
- Don't try to "help" with env overrides or a custom ninja — admin policy forbids it, and non-compliant runs get silently reaped (`shell_utils.sh:199 … Killed`).
- Memory contention from co-tenants is real (observed free RAM as low as ~32–40 GiB + heavy swap) — `-j64` is a fair, demonstrated-safe job count (the wrapper overrides `-j` anyway; `-j64` mostly signals intent).

## `rom-build.sh` (AOSPA official helper)

Flags: `-c` clobber-clean, `-i` installclean, `-r` repo-sync, `-v` AOSPA variant
(alpha/beta/stable), **`-t` build type (default `userdebug`)**, `-j` jobs
(**default = nproc ⇒ 192!** always pass `-j64`), `-m` module, `-s` sign-key
mappings (official `sign_target_files_apks` route), `-p` password file, `-b`
backup unsigned, `-d` delta target, `-z` imgzip, `-n` version.

Sequence: `source build/envsetup.sh` → `lunch aospa_<device>-<type>` → optional
installclean → optional kernel rebuild (`RECOMPILE_KERNEL=1` when `-c`/`-i`; the
`user` variant forces `LTO=full`, userdebug doesn't) → `m otapackage`.

## How to run a build (the ONLY compliant form)

Must be: **persistent tmux session + login shell** (`bash -l`). Plain ssh
background runs have been killed by the farm; non-login tmux too.

**Current default mode — userdebug / test-keys** (no further tree changes needed):

```bash
ssh waffle
tmux new-session -d -s rxbuild \
  "bash -lc \"cd /serverhive5/raizenftw/aospa && ./rom-build.sh giulia -j64 2>&1 | tee /serverhive5/raizenftw/build-logs/userdebug_build.log\""
```

- First build after a period of `user`-variant builds: **add `-i`** once
  (installclean for the variant swap; expect slower — kernel may rebuild).
- Watch: `tail -f /serverhive5/raizenftw/build-logs/userdebug_build.log` or
  `tmux attach -t rxbuild` (detach: `Ctrl-b d`).
- Success line at the end: `#### build completed successfully (…)` and a fresh
  `out/target/product/giulia/aospa_giulia-ota.zip`.

**Production mode — release-keys (currently parked):**

1. Uncomment the cert line in `vendor/aospa/products/giulia/aospa_giulia.mk`
   (remove the leading `# ` on line 40).
2. Commit + push both branches (`axion-scene-qs` + `calcite` on remote `aospa`).
3. Build with `-t user` (runbook `10.A`). The release-keys state was cached at
   26% of the device graph — that resume path needs **no `-i`**.
4. Post-build audit gate (`10.C`) is **mandatory** before anything touches
   the phone: zero `test-keys|userdebug` greps across all build.props,
   `strings init | grep warranty` ⇒ 2 hits, OTA container cert check.

## Fast modular compilation & live device testing (no full ROM build)

For targeted bug fixes and live phone verification without 2-hour full builds:

```bash
# 1. Compile individual modules on waffle
ssh waffle
tmux new-session -d -s quickbuild "bash -lc \"cd /serverhive5/raizenftw/aospa && source build/envsetup.sh && lunch aospa_giulia-userdebug && m Settings vendor.oplus.hardware.touch@2.0-service 2>&1 | tee /serverhive5/raizenftw/modular_build.log\""

# 2. Deploy & live-test on connected phone via tmpfs bind-mount (no nosuid):
adb root
adb shell "mkdir -p /tmp"
adb push out/target/product/giulia/system_ext/priv-app/Settings/Settings.apk /tmp/
adb push out/target/product/giulia/system_ext/priv-app/Settings/oat/arm64/Settings.odex /tmp/
adb push out/target/product/giulia/system_ext/priv-app/Settings/oat/arm64/Settings.vdex /tmp/
adb shell "mount --bind /tmp/Settings.apk /system_ext/priv-app/Settings/Settings.apk"
adb shell "mount --bind /tmp/Settings.odex /system_ext/priv-app/Settings/oat/arm64/Settings.odex"
adb shell "mount --bind /tmp/Settings.vdex /system_ext/priv-app/Settings/oat/arm64/Settings.vdex"
adb shell "pkill -f com.android.settings"

# Touch HAL live test:
adb push out/target/product/giulia/odm/bin/hw/vendor.oplus.hardware.touch@2.0-service /tmp/
adb shell "chcon u:object_r:hal_oplus_touch_aidl_exec:s0 /tmp/vendor.oplus.hardware.touch@2.0-service"
adb shell "mount --bind /tmp/vendor.oplus.hardware.touch@2.0-service /odm/bin/hw/vendor-oplus-hardware-touch-V2-service"
adb shell "pkill -f vendor-oplus-hardware-touch"
```

## Stopping / wedges / recovery

- Stop a build: exact-name kills only — `kill -9 $(pgrep -x ninja)` (also
  `soong_ui`, `kati`, `ckati`, `rewrapper`). **Never `pkill -f <string>`** —
  it self-matches your own ssh command line and kills your session (exit 255).
- Wedge signature: log `mtime` frozen for minutes + `pgrep -x rewrapper | wc -l`
  = 0 + loadavg < 440 + ninja alive at ~0 % CPU. Then read
  `/serverhive5/raizenftw/aospa/out/soong.log` (sanctioned diagnostic).
- Kill order: kill tmux session contents cleanly, then relaunch the exact same
  command — the build system resumes incrementally every time (proven across
  six attempts).
- Historical verdict: past kills/wedges traced to the box being rebooted for
  maintenance mid-flight; infra itself works when the farm is healthy.

## One-shot health probe (before launching anything)

```bash
ssh waffle 'date +%H:%M:%S; cat /proc/loadavg; pgrep -x rewrapper | wc -l;
  pgrep -x ninja | wc -l; free -g | head -2;
  stat -c "logmtime=%y" /serverhive5/raizenftw/build-logs/userdebug_build.log 2>/dev/null'
```

Decision rule: loadavg 1-min well below 440 → launch; above → still launch if
patient (it idles until the farm cools), or wait if you want immediate progress.

## Waffle git-remote conventions (this project)

| Tree path | remote name → URL |
|---|---|
| `vendor/aospa` | `aospa` → `git@github.com:aospa-f/aospa_vendor_aospa` (branches `axion-scene-qs` + `calcite`) |
| `vendor/oneplus/sm8650-oss` | `github` → aospa-f org |
| most others | `aospa-f` remote added per-repo (see `03`) |
| upstream refs | `clo`/`clo-la`/`oplus-8650-clo` (read-only), `shadedark` (collab fork) |

Related docs: push runbook `03`/`10.E`, audit gate `10.C`, farm-failure history
`07`, production-mode mechanics `06`, quick state `01`.
