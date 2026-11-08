# Complete Standalone Setup & Build Guide for AOSPA Giulia (OnePlus 13R)

This guide provides end-to-end instructions to recreate the entire ROM build environment from scratch on a brand-new server or clean machine.

---

## 1. System Requirements & Recommendations

* **Operating System**: Ubuntu 22.04 LTS or 24.04 LTS (x86_64).
* **CPU**: 16+ physical cores recommended (32–64+ ideal for fast compilation).
* **RAM**: Minimum 32 GiB + 32 GiB swap; 64–128 GiB recommended.
* **Storage**: Minimum 350–500 GiB NVMe or high-speed SSD mounted with read/write permissions.

---

## 2. Server Package Prerequisites

Run as a user with `sudo` privileges:

```bash
sudo apt update && sudo apt install -y \
    git git-lfs curl wget python3 python3-pip openjdk-21-jdk \
    build-essential bc bison flex libssl-dev libncurses5-dev \
    libelf-dev rsync zip unzip tmux ccache htop jq libxml2-utils \
    libncurses5 libtinfo5 libstdc++6 zlib1g-dev libgl1-mesa-dev

# Install Google repo tool
mkdir -p ~/.local/bin
curl -s https://storage.googleapis.com/git-repo-downloads/repo > ~/.local/bin/repo
chmod a+x ~/.local/bin/repo

# Ensure ~/.local/bin is in PATH
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

Configure your Git identity:

```bash
git config --global user.name "raizenftw"
git config --global user.email "android@op5d3bl1.local"
```

---

## 3. Cloning & Syncing the Source Tree

### A. Clone the aospa-f Manifest
```bash
mkdir -p ~/aospa && cd ~/aospa
repo init -u https://github.com/aospa-f/manifest -b calcite
```

### B. Place the Local Manifests
The `local_manifests` specify device-specific vendor trees (TheMuppets lineage-23.2) and Qualcomm platform HAL overrides:

```bash
mkdir -p ~/aospa/.repo/local_manifests

# Copy baristablend.xml and giulia.xml from the aospa-f/build-logs repo:
git clone https://github.com/aospa-f/build-logs.git /tmp/build-logs
cp /tmp/build-logs/local_manifests/*.xml ~/aospa/.repo/local_manifests/
```

### C. Sync the Repositories
```bash
cd ~/aospa
repo sync -c -j$(nproc) --force-sync --no-clone-bundle --no-tags
```

---

## 4. Keyset Restoration (Private Release Keys)

The private keyset contains 18 files (9 keypairs) and is never committed to Git. A backup exists on the local workstation at `/home/raizen/aospa-keys-backup/security/`.

### From your local laptop:
```bash
scp -r /home/raizen/aospa-keys-backup/security <new-server>:~/aospa/vendor/aospa-priv/
```

### On the server:
```bash
chmod 700 ~/aospa/vendor/aospa-priv/security
chmod 600 ~/aospa/vendor/aospa-priv/security/*.pk8
chmod 644 ~/aospa/vendor/aospa-priv/security/*.x509.pem
```

---

## 5. Build Modes & Execution

Always build inside a persistent `tmux` session with a login shell (`bash -l`) so environment variables load cleanly.

```bash
# Setup Ccache
export USE_CCACHE=1
export CCACHE_EXEC=$(which ccache)
export CCACHE_DIR=~/.ccache
ccache -M 50G
```

### Mode 1: Default Development Mode (`userdebug` + `test-keys`)
In this mode, `PRODUCT_DEFAULT_DEV_CERTIFICATE` in `vendor/aospa/products/giulia/aospa_giulia.mk` remains commented out (default state).

```bash
tmux new-session -d -s rxbuild \
  "bash -lc \"cd ~/aospa && ./rom-build.sh giulia -j\$(nproc) 2>&1 | tee ~/build-logs/userdebug_build.log\""
```
*Tip*: Add `-i` (installclean) on the very first run if switching from a `user` variant.

### Mode 2: Production Mode (`user` + `release-keys`)
1. In `~/aospa/vendor/aospa/products/giulia/aospa_giulia.mk`, uncomment line 40:
   ```makefile
   PRODUCT_DEFAULT_DEV_CERTIFICATE := vendor/aospa-priv/security/releasekey
   ```
2. Launch the build:
   ```bash
   tmux new-session -d -s rxbuild \
     "bash -lc \"cd ~/aospa && ./rom-build.sh giulia -t user -j\$(nproc) 2>&1 | tee ~/build-logs/release_build.log\""
   ```

To monitor progress:
```bash
tmux attach -t rxbuild      # Detach using Ctrl-b d
# Or:
tail -f ~/build-logs/*.log
```

---

## 6. Post-Build Audit Gate

Before flashing the resulting OTA zip, run the audit checks:

```bash
O=~/aospa/out/target/product/giulia
for f in $O/system/build.prop $O/system_ext/build.prop $O/vendor/build.prop $O/odm/etc/build.prop; do
  echo "== $f =="
  grep -E "^ro\.(build|system|system_ext|vendor|odm)\.build\.(type|tags|fingerprint)\b" "$f"
  grep -acE "test-keys|userdebug" "$f"   # Must return 0 on production builds
done

# Verify boot-state spoofing string in init
strings $O/system/bin/init | grep -a warranty_bit   # Expect 2 hits (ro.boot.warranty_bit and ro.warranty_bit)
```

The flashable OTA zip will be located at:
`~/aospa/out/target/product/giulia/aospa_giulia-ota.zip`

---

## 7. Flashing & Disaster Recovery

If fastboot recovery is needed, flash the partitions in the validated sequence:

```bash
fastboot devices
fastboot flash dtbo dtbo.img
fastboot flash boot boot.img
fastboot flash init_boot init_boot.img
fastboot flash vendor_boot vendor_boot.img
fastboot reboot
```

---

## 8. Server Layout Reference Map

```text
~ (e.g. /serverhive5/raizenftw)
├── aospa/                                    ← ROM repo workspace
│   ├── build/make                            ← aospa-f/aospa_build_make (calcite)
│   ├── build/release                         ← aospa-f/aospa_build_release (calcite)
│   ├── system/core                           ← aospa-f/aospa_system_core (calcite)
│   ├── frameworks/base                       ← aospa-f/aospa_frameworks_base (stock-qs)
│   ├── packages/apps/Settings                ← aospa-f/aospa_packages_apps_Settings (calcite)
│   ├── packages/apps/BypassCharge            ← aospa-f/packages_apps_BypassCharge (sixteen/calcite)
│   ├── device/oneplus/sm8650-common          ← aospa-f/device_oneplus_sm8650-common (calcite)
│   ├── device/oneplus/giulia                 ← aospa-f/device_oneplus_giulia (calcite)
│   ├── vendor/oneplus/sm8650-oss             ← aospa-f/vendor_oneplus_sm8650-oss (calcite)
│   ├── vendor/aospa                          ← aospa-f/aospa_vendor_aospa (axion-scene-qs/calcite)
│   ├── vendor/aospa-priv/security/           ← PRIVATE KEYSET (never push)
│   └── rom-build.sh                          ← Official build helper entrypoint
├── build-logs/                               ← aospa-f/build-logs (main)
│   ├── NEW_SERVER_SETUP.md                   ← This guide
│   ├── handover-docs/                        ← Full 13-part engineering handover suite
│   ├── local_manifests/                      ← giulia.xml, baristablend.xml
│   ├── docs/                                 ← RECOVERY.txt and references
│   └── scripts/                              ← apply_features.py, run_build.sh, patchers
```
