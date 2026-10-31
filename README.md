# OnePlus 13R / Ace 5 (`giulia`) - AOSPA-F Build Automation & Environment

Repository maintaining verified build automation, platform manifests, patches, and setup scripts for building **AOSPA-F (Calcite)** on the **OnePlus 13R / OnePlus Ace 5 (`giulia` / SM8650 `pineapple`)**.

---

## 📱 Firmware & Blob Source: OnePlus 13R India (`IN 16.0.10.600`) OxygenOS 16

The ROM is built with official **OnePlus 13R India (`IN 16.0.10.600`) OxygenOS 16** firmware:
* **All-in-One Single ROM ZIP**: All India `16.0.10.600` firmware partitions (`abl`, `aop`, `aop_config`, `bluetooth`, `cpucp`, `cpucp_dtb`, `devcfg`, `dsp`, `engineering_cdt`, `featenabler`, `hyp`, `imagefv`, `keymaster`, `modem`, `oplus_sec`, `oplusstanvbk`, `qupfw`, `shrm`, `splash`, `tz`, `uefi`, `uefisecapp`, `xbl`, `xbl_config`, `xbl_ramdump`) are embedded directly into `payload.bin`.
* **No Separate Firmware / Boot / Recovery Zips**: Flashing the single ROM ZIP flashes both Android and all India firmware in one pass.
* **Zero ColorOS 17 Blobs**: Built strictly against OxygenOS 16 base (`TheMuppets` lineage-23.2 + local official India 16.0.10.600 images).

---

## 📁 Repository Structure

```
build-logs/
├── README.md                      # Master build & setup documentation
├── local_manifests/
│   ├── giulia.xml                 # Local manifest linking aospa-f trees and TheMuppets OOS16
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
│   ├── vendor_oneplus_giulia.patch       # Includes SHA1 checks for India 16.0.10.600 radio images
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
    ├── apply_all_patches.sh       # Automatically applies patches and deploys India 16.0.10.600 firmware
    ├── track_clo_upstream.sh      # Tracks & merges changes from clo-for-giulia upstream
    └── upload_gofile.py           # Automated uploader for fast ROM sharing via GoFile
```

---

## 🚀 Quick Start on a Fresh ServerHive / Linux Server

When you launch a brand new ServerHive or Ubuntu instance, building is completely automated.

### Option A: Complete 1-Command Automated Build (Recommended)
Run this single command on a fresh server to configure packages, sync trees, apply patches, deploy India 16.0.10.600 firmware, and compile the single ROM zip:
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
repo init -u https://github.com/aospa-f/manifest -b calcite --git-lfs
mkdir -p .repo/local_manifests
cp ~/build-logs/local_manifests/*.xml .repo/local_manifests/
repo sync -c -j$(nproc --all) --force-sync --no-clone-bundle --no-tags
```

#### 4. Apply prebuilts, platform patches & deploy India firmware
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

## ⚡ Flashing the ROM (LFFF Tool)

The recommended flashing method for the OnePlus 13R is using **LFFF (LibreFastbootFirmwareFlasher)**:
* Tool Repository: [https://github.com/mrFrok/LibreFastbootFirmwareFlasher](https://github.com/mrFrok/LibreFastbootFirmwareFlasher)
* Guide: [Flashing custom ROMs on OnePlus 13R / Ace 5](https://github.com/yashaswee-exe/AndroidGuides/wiki/Flashing-custom-ROMs-on-a-OnePlus-13R-Ace5)

1. Connect device in bootloader mode (`fastboot`).
2. Open LFFF and select the single generated `aospa-calcite-*.zip` (or the extracted `payload.bin`).
3. LFFF flashes boot and India firmware partitions in `fastboot`, reboots to `fastbootd`, flashes all dynamic logical partitions (`system`, `system_ext`, `product`, `odm`, `vendor`), and formats data.
