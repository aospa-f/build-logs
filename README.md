# OnePlus 13R / Ace 5 (`giulia`) - AOSPA Calcite Build Environment & Logs

Repository maintaining all initial build logs, verified fixes, patches, platform sync manifests, and automation scripts for building **Paranoid Android (AOSPA) Calcite** on the **OnePlus 13R / OnePlus Ace 5 (`giulia` / SM8650 `pineapple`)**.

---

## 📁 Repository Structure

```
build-logs/
├── README.md                      # Master build & setup documentation
├── logs/
│   └── 2026-10-13_initial_build_log.md  # Complete step-by-step initial build log & issue postmortem
├── local_manifests/
│   ├── giulia.xml                 # Local manifest linking AOSPA, dyruz10 trees, and clo-for-giulia
│   └── baristablend.xml           # Qualcomm SM8650 audio/display HAL platform sync definitions
├── patches/                       # 14 discrete verified patches across all modified projects
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
└── scripts/
    ├── setup_fresh_server.sh      # Installs all Ubuntu dependencies, ccache, repo tool
    ├── sync_manifest.sh           # Inits calcite manifest, deploys manifests, syncs & patches
    ├── apply_all_patches.sh       # Automatically applies all 14 patches with 3-way fallback
    ├── track_clo_upstream.sh      # Tracks & merges changes from clo-for-giulia upstream
    ├── push_all_to_github.sh      # Creates/pushes build-logs repo & forks clo-for-giulia repos
    └── upload_gofile.py           # Automated uploader for fast ROM sharing via GoFile
```

---

## 🚀 Quick Start on a Fresh ServerHive / Linux Server

To build the ROM on a brand new, clean server without encountering any build errors:

### 1. Configure the Environment
```bash
git clone https://github.com/dyruz10/build-logs.git ~/build-logs
bash ~/build-logs/scripts/setup_fresh_server.sh
```

### 2. Sync and Patch the Tree
```bash
bash ~/build-logs/scripts/sync_manifest.sh ~/aospa
```

### 3. Run the Build
```bash
cd ~/aospa
./rom-build.sh giulia -v userdebug -t release
```

Output package will be generated at:
`~/aospa/out/target/product/giulia/aospa-calcite-<date>-gms-giulia.zip`

---

## 🔄 Tracking `clo-for-giulia` Upstream

When Ronard (`clo-for-giulia`) pushes new commits to the device, vendor, or kernel trees:

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

---

## 📦 Verified Artifacts from Initial Build (2026-10-13)

* **Full ROM ZIP (3.21 GB):** [Download from GoFile](https://gofile.io/d/EHcXKleX)
* **Boot Partitions Archive (34 MB):** [Download from GoFile](https://gofile.io/d/kavlXLya)
