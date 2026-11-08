# AOSPA giulia project — handover documentation suite

Handover date: **2026-11-08**. Written by the coding-agent session that has been
maintaining this ROM with the user (`raizen`). Superseding single-file version:
`/home/raizen/rom-handover-20261108.md` (kept for reference).

## Read in this order

| File | What it contains |
|---|---|
| [`01-quick-state.md`](01-quick-state.md) | **Load this first.** Atomic status: done / in-flight / blocked / exact next commands |
| `02-environments.md` | Laptop, waffle build server, phone; shared-farm mechanics and policies |
| `03-repos-and-branches.md` | Every repo, remote, branch, commit ledger, pending org-repo creations |
| `04-feature-fixes.md` | All implemented feature fixes: symptom → root cause → fix → files → validation |
| `05-prop-spoofing.md` | The static boot-state prop spoof: mechanics, safety audit, approved/excluded props |
| `06-signing-release-keys.md` | Why release-keys requires private keys in this tree; keyset generation + wiring |
| `07-build-infra-and-failures.md` | Every build attempt, farm failure signatures, diagnosis evidence, escalation |
| `08-phone-validation.md` | Device identity, flashed state, on-device audit results and checklists |
| `09-artifacts-inventory.md` | All artifacts on laptop and waffle (zips, keys, logs, mirrors) |
| `10-procedures.md` | Runbooks: resume build, audit, download, flash, git pushes, farm health probes |
| `11-decision-log-and-next.md` | Every user decision with rationale; open items and next actions |
| `12-server-layout-and-building.md` | **waffle server map + how to run builds** (both modes, farm mechanics, wedge recovery) |

## The five-line state

1. Custom AOSPA/Axion ROM for OnePlus 13R (**giulia**, `CPH2691`, sm8650); userdebug build flashed and fully validated.
2. Goal: testing ROM in **userdebug/test-keys** right now; "production" (`user` + `release-keys` + static boot-state spoof already active in `init`) parked, resumable.
3. Release-keys in this tree requires a private keyset wired to `PRODUCT_DEFAULT_DEV_CERTIFICATE` — wired, committed, pushed; **temporarily parked** (toggle commit `5256c361`): builds default back to userdebug/test-keys.
4. Farm kills/wedges retro-explained: the server rebooted for maintenance mid-day; infra healthy again since — the release-keys state stays cached at 26% of the device graph for when production resumes.
5. Current mode: `./rom-build.sh giulia -j64` on waffle ⇒ userdebug/test-keys (server map + full how-to in `12`).
