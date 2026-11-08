# 02 — Environments

## Laptop (local machine of the user)
- Working dir: `/home/raizen`. adb host. **Phone connects via USB and drops often** — always run `adb devices | tail -n 2` before any phone-side batch.
- Holds: downloaded ROM zips, keyset backup, agent shell logs; `/tmp/opencode` is the approved scratch dir for staging scripts sent to waffle.

## waffle (remote build server)
- Access: `ssh waffle`. Home = `/serverhive5/raizenftw`.
- Repo root: `/serverhive5/raizenftw/aospa` (symlink `~/aospa`).
- Logs: `/serverhive5/raizenftw/build-logs/` (e.g. `release_build.log`).
- Hardware: 192 cores; MemTotal 791,803,732 kB (~755 GiB via `free -g`); swap 100 GiB; `/serverhive5` = 14 T NVMe (`/dev/nvme5n1p1`, ~7.4 T free).
- **Shared farm**: other tenants run concurrently; free RAM was observed as low as ~32–40 GiB with 27 GiB swap during our session; load averages 170–200 with bursts higher.

### Build farm mechanics (important)
| Component | Observed role |
|---|---|
| `/etc/profile.d/Z97-rbe4.sh` | exports `CUSTOM_NINJA_BIN=/opt/ninja` (server build executor); also `Z97-byobu.sh` (commented original at `/srv/ninja`) |
| `/opt/ninja` | server-managed ninja wrapper; **overrides user `-j`** (observed running `-j 1200 -l 440` with `-o usesphonyoutputs=yes`, `--frontend_file out/.ninja_fifo`) |
| `/srv/.rbe/reproxy` | RBE farm client daemon (581 MB RSS when active); started lazily per build; `pgrep -x reproxy` empty when idle is normal |
| `/srv/.rbe/scandeps_server` | depscanner unix-socket server (pfad `out/soong/rbe/depscan_<pid>.sock`) |
| `rewrapper` | remote-action workers (dozens during active compile; 0 when wedged) |

### Admin policy (from a real termination notice)
- Builds must run in a **persistent tmux** session **and** a **login shell** (`bash -l`) so profiles load; do not unset/override env variables (`CUSTOM_NINJA_BIN` etc.).
- Non-login or out-of-session launches cause "orphaned processes" → scheduler kills them silently (observed bash line: `build/soong/bin/../../make/shell_utils.sh: line 199: <pid> Killed "$@"`).
- Compliant launch pattern (current default mode — userdebug/test-keys; full map in `12`):
  `tmux new-session -d -s rxbuild "bash -lc \"cd /serverhive5/raizenftw/aospa && ./rom-build.sh giulia -j64 2>&1 | tee /serverhive5/raizenftw/build-logs/userdebug_build.log\""`
  (the historical release-keys form with `-t user` lives in `10.A` — requires re-enabling the cert toggle first)
- Interaction fact observed: plain non-interactive ssh *did* also expose `CUSTOM_NINJA_BIN` (profile.d gets sourced by the host's bashrc chain), but the policy still demands the login-shell session — comply regardless.

## Phone (OnePlus 13R "giulia")
- Model `CPH2691` (IN retail `CPH2691IN`), device string `OP5D3BL1`, SoC **sm8650** (Snapdragon 8 Gen 3), A/B OTA device.
- Currently flashed: project's own userdebug Oxid ROM build (see `08`).
- Lost after flashing a production (`user`) ROM: `adb root` — all validation must be non-root.
