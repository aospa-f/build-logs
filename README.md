# OnePlus 13R / Ace 5 (`giulia`) - AOSPA-F Build Environment & Automation

Repository maintaining verified build automation, patches, platform manifests, and setup scripts for building **AOSPA-F (Calcite)** on the **OnePlus 13R / OnePlus Ace 5 (`giulia` / SM8650 `pineapple`)**.

---

## 📁 Repository Structure

```
build-logs/
├── README.md                      # Master build & setup documentation
├── logs/
│   └── 2026-10-13_initial_build_log.md  # Complete step-by-step initial build log & issue postmortem
├── local_manifests/
│   ├── giulia.xml                 # Local manifest linking AOSPA, aospa-f trees, and TheMuppets OOS16 fw
│   └── baristablend.xml           # Qualcomm SM8650 audio/display HAL platform sync definitions
├── patches/                       # Verified discrete patches across modified projects
│   ├── build_soong.patch
│   ├── device_oneplus_sm8650-common.patch
│   ├── device_qcom_sepolicy_vndr.patch
│   ├── external_dtc.patch
│   ├── hardware_oplus.patch
│   ├── hardware_qcom_display.patch
│   ├── kernel_oneplus_sm8650.patch
│   ├── packages_apps_Settings.patch
│   ├── vendor_aospa.patch
│   ├── vendor_oneplus_giulia.patch
│   ├── vendor_oneplus_sm8650-common.patch
│   ├── vendor_qcom_common.patch
│   └── vendor_qcom_opensource_commonsys_fm.patch
├── prebuilts/
│   └── Datura/                    # CalyxOS Datura firewall prebuilt package
├── fresh_build.sh                 # 1-click master build launcher for fresh servers
└── scripts/
    ├── fresh_server_build.sh      # Complete 5-step automated bootstrap from clean server to ROM zip
    ├── setup_fresh_server.sh      # Installs all Ubuntu dependencies, ccache, repo tool
    ├── sync_manifest.sh           # Inits calcite manifest, deploys manifests, syncs & patches
    ├── apply_all_patches.sh       # Automatically applies all verified patches with 3-way fallback
    ├── track_clo_upstream.sh      # Tracks & merges changes from clo-for-giulia upstream
    ├── push_all_to_github.sh      # Creates/pushes build-logs repo & forks clo-for-giulia repos
    └── upload_gofile.py           # Automated uploader for fast ROM sharing via GoFile
```

---

## 📱 Firmware & Blob Source: OxygenOS 16 (Not ColorOS)

The proprietary vendor blobs and firmware images are sourced directly from **TheMuppets** on branch `lineage-23.2`:
* **`vendor/oneplus/giulia`**: Sourced from `TheMuppets/proprietary_vendor_oneplus_giulia` (`lineage-23.2`), verified on latest **OxygenOS 16 (`OOS 11.F.53`)**. Includes full modem, bootloader, trustzone, DSP, and radio images extracted from `CPH2691_16.0.2.400(EX01)`.
* **`vendor/oneplus/sm8650-common`**: Sourced from `TheMuppets/proprietary_vendor_oneplus_sm8650-common` (`lineage-23.2`), verified on latest **OxygenOS 16 (`OOS 11.F.58`)**.
* **Zero ColorOS 17 blobs**: No `COS 17` or unverified Chinese ColorOS builds are used.

---

## 🚀 Quick Start on a Fresh ServerHive / Linux Server

When you launch a brand new ServerHive or Ubuntu instance, building is completely automated.

### Option A: Complete 1-Command Automated Build (Recommended)
Run this single command on a fresh server to configure packages, sync trees, apply patches, and compile the ROM:
```bash
git clone https://github.com/aospa-f/build-logs.git ~/build-logs && bash ~/build-logs/fresh_build.sh
```

---

### Option B: Step-by-Step Manual Execution

If you prefer to run each step manually:

#### 1. Clone build tools & automated setup
```bash
git clone https://github.com/aospa-f/build-logs.git ~/build-logs
```

#### 2. Run system setup (installs ccache, packages, python, repo)
```bash
bash ~/build-logs/scripts/setup_fresh_server.sh
```

#### 3. Initialize source tree and sync using aospa-f local manifests
```bash
mkdir -p ~/aospa && cd ~/aospa
repo init -u https://github.com/AOSPA/manifest -b calcite --git-lfs
mkdir -p .repo/local_manifests
cp ~/build-logs/local_manifests/*.xml .repo/local_manifests/
repo sync -c -j$(nproc --all) --force-sync --no-clone-bundle --no-tags
```

#### 4. Apply prebuilts & verified platform patches
```bash
bash ~/build-logs/scripts/apply_all_patches.sh ~/aospa
```

#### 5. Run the build
```bash
./rom-build.sh giulia -v userdebug -t release
```

Output package will be generated at:
`~/aospa/out/target/product/giulia/aospa-calcite-<date>-gms-giulia.zip`

---

## 🔄 Tracking `clo-for-giulia` Upstream

When Ronard (`clo-for-giulia`) pushes new commits to device, vendor, or kernel trees:

1. **Check status of incoming changes:**
   ```bash
   bash ~/build-logs/scripts/track_clo_upstream.sh ~/aospa status
   ```

2. **Inspect what changed:**
   ```bash
   bash ~/build-logs/scripts/track_clo_upstream.sh ~/aospa diff
   ```

3. **Fetch & Merge into your branch:**
   ```bash
   bash ~/build-logs/scripts/track_clo_upstream.sh ~/aospa merge
   ```

---

## ⚡ Flashing the ROM (LFFF Tool)

The recommended flashing method for the OnePlus 13R is using **LFFF (LibreFastbootFirmwareFlasher)**:
* Tool Repository: [https://github.com/mrFrok/LibreFastbootFirmwareFlasher](https://github.com/mrFrok/LibreFastbootFirmwareFlasher)
* Guide: [Flashing custom ROMs on OnePlus 13R / Ace 5](https://github.com/yashaswee-exe/AndroidGuides/wiki/Flashing-custom-ROMs-on-a-OnePlus-13R-Ace5)

1. Connect device in bootloader mode (`fastboot`).
2. Open LFFF and select `aospa-calcite-*.zip` (or the extracted `payload.bin`).
3. LFFF flashes boot partitions in `fastboot`, reboots to `fastbootd`, flashes all dynamic logical partitions (`system`, `system_ext`, `product`, `odm`, `vendor`), and formats data.
