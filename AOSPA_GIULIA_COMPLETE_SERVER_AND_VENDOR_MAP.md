# Complete Server Infrastructure, Repository Catalog & Vendor Extraction Map
## Paranoid Android (AOSPA) Calcite — OnePlus 13R (giulia / SM8650)

This document is an exhaustive, authoritative blueprint of the entire ROM build environment, repository hierarchy, vendor proprietary blob origin, extraction mechanics from Stock OxygenOS, and kernel integration. With this guide, anyone can recreate, maintain, or rebuild the ROM without ambiguity.

---

## 1. System & Server Environment Overview

* **Target Device**: OnePlus 13R (`giulia` / model `CPH2691IN` / hardware board `OP5D3BL1`).
* **Platform / SoC**: Qualcomm Snapdragon 8 Gen 3 (`sm8650` / Pineapple architecture).
* **Android / AOSPA Base**: Android 15 / AOSPA Calcite (based on `android-17.0.0_r1` tag).
* **Build Flavor**: Production `user` build signed with private `release-keys` (`aospa_giulia-user`).
* **Server Root Directory**: `/serverhive5/raizenftw/` (referred to as `~`).

### Required Environment Flags & Tools
When building on any server, ensure the following parameters are exported:
```bash
export USE_CCACHE=1
export CCACHE_EXEC=$(which ccache)
export CCACHE_DIR=/serverhive5/raizenftw/.ccache
export GOMEMLIMIT=16GiB
export GOGC=50
ulimit -n 65536
```

---

## 2. Server Directory Layout

```text
/serverhive5/raizenftw/
├── aospa/                                    # Main ROM source repository (~350–400 GB)
│   ├── .repo/                                # Repo tool internal database & manifests
│   │   ├── manifests/                        # Primary manifest repository (aospa-f/manifest)
│   │   └── local_manifests/                  # Device-specific overrides & extra trees
│   │       ├── giulia.xml                    # Vendor & toolchain dependencies
│   │       └── baristablend.xml              # Qualcomm HAL overrides (display, audio, GPS)
│   ├── build/                                # Build system engines
│   │   ├── make/                             # aospa-f/aospa_build_make (calcite)
│   │   ├── soong/                            # oplus-8650-clo/android_build_soong (calcite)
│   │   └── release/                          # aospa-f/aospa_build_release (calcite)
│   ├── device/oneplus/                       # Device tree definitions
│   │   ├── giulia/                           # aospa-f/device_oneplus_giulia (calcite)
│   │   ├── giuliac/                          # aospa-f/device_oneplus_giuliac (calcite)
│   │   └── sm8650-common/                    # aospa-f/device_oneplus_sm8650-common (calcite)
│   ├── frameworks/base/                      # aospa-f/aospa_frameworks_base (stock-qs)
│   ├── hardware/oplus/                       # aospa-f/hardware_oplus (calcite)
│   ├── kernel/oneplus/                       # Kernel sources & devicetrees
│   │   ├── sm8650/                           # aospa-f/kernel_oneplus_sm8650 (calcite)
│   │   ├── sm8650-devicetrees/               # aospa-f/kernel_oneplus_sm8650-devicetrees (calcite)
│   │   └── sm8650-modules/                   # aospa-f/kernel_oneplus_sm8650-modules (calcite)
│   ├── packages/apps/                        # System & Settings applications
│   │   ├── Settings/                         # aospa-f/aospa_packages_apps_Settings (calcite)
│   │   ├── ParanoidSystemUI/                 # aospa-f/aospa_packages_apps_Paranoid_SystemUI (stock-qs)
│   │   ├── BypassCharge/                     # aospa-f/packages_apps_BypassCharge (calcite)
│   │   ├── GameSpace/                        # clo-for-giulia/packages_apps_GameSpace (calcite)
│   │   ├── LunarisDolby/                     # aosp-for-giulia/android_packages_apps_LunarisDolby (16)
│   │   └── Launcher3/                        # aospa-f/aospa_packages_apps_Launcher3 (stock-qs)
│   ├── vendor/                               # Proprietary vendor blobs & packages
│   │   ├── aospa/                            # aospa-f/aospa_vendor_aospa (axion-scene-qs)
│   │   ├── aospa-priv/security/              # PRIVATE RELEASE KEYSET (CRITICAL - DO NOT COMMIT)
│   │   ├── google/gms/                       # Google Mobile Services prebuilts (calcite)
│   │   ├── oneplus/giulia/                   # Device proprietary blobs (TheMuppets lineage-23.2)
│   │   ├── oneplus/sm8650-common/            # SoC proprietary blobs (TheMuppets lineage-23.2)
│   │   ├── oneplus/sm8650-oss/               # Open-source HALs (touch, display, sensors)
│   │   ├── oneplus/ir/                       # Consumer IR blaster HAL
│   │   ├── oplus/camera/                     # Stock OPlus Hasselblad Camera package & HALs
│   │   ├── sony/dolby/                       # Dolby Atmos audio DSP blobs
│   │   └── qcom/                             # Qualcomm Snapdragon 8 Gen 3 platform HALs
│   ├── out/                                  # Build artifacts & compilation intermediates
│   │   └── target/product/giulia/            # Target partition images (system.img, etc.)
│   └── rom-build.sh                          # Main ROM build orchestrator
├── build-logs/                               # aospa-f/build-logs (main) - Documentation & scripts
└── .ccache/                                  # Persistent compiler cache (~50 GB)
```

---

## 3. Complete Repository & Remote Mapping Catalog

| Local Path in Tree | Remote Repository URL | Active Branch | Description / Customizations |
| :--- | :--- | :--- | :--- |
| `build/make` | `https://github.com/aospa-f/aospa_build_make` | `calcite` | Core Makefile rules, partition targets, release packaging |
| `build/soong` | `https://github.com/oplus-8650-clo/android_build_soong` | `calcite` | Blueprint compiler with Qualcomm SM8650 namespace support |
| `build/release` | `https://github.com/aospa-f/aospa_build_release` | `calcite` | Android release configuration and aconfig flag defaults |
| `frameworks/base` | `https://github.com/aospa-f/aospa_frameworks_base` | `stock-qs` | Framework core, SystemUI, Extra Brightness sliders, QS landscape fix, unlock haptics suppression |
| `packages/apps/Settings` | `https://github.com/aospa-f/aospa_packages_apps_Settings` | `calcite` | System Settings app, Vibrate on Screen Unlock toggle, GameSpace settings, touch polling persist |
| `packages/apps/ParanoidSystemUI` | `https://github.com/aospa-f/aospa_packages_apps_Paranoid_SystemUI` | `stock-qs` | Stock QS tiles list, Refresh Rate & Network Mode tile specs |
| `packages/apps/Launcher3` | `https://github.com/aospa-f/aospa_packages_apps_Launcher3` | `stock-qs` | AOSPA Launcher with custom gesture insets and animations |
| `packages/apps/BypassCharge` | `https://github.com/aospa-f/packages_apps_BypassCharge` | `calcite` | OnePlus battery bypass charging control |
| `packages/apps/GameSpace` | `https://github.com/clo-for-giulia/packages_apps_GameSpace` | `calcite` | Gaming floating handle, FPS monitor, DND trigger |
| `packages/apps/LunarisDolby` | `https://github.com/aosp-for-giulia/android_packages_apps_LunarisDolby` | `16` | Dolby Atmos user control interface |
| `device/oneplus/giulia` | `https://github.com/aospa-f/device_oneplus_giulia` | `calcite` | OnePlus 13R device tree, proprietary-files list, audio/display configs |
| `device/oneplus/sm8650-common` | `https://github.com/aospa-f/device_oneplus_sm8650-common` | `calcite` | Common SM8650 device tree, board configs, sepolicy, init scripts |
| `hardware/oplus` | `https://github.com/aospa-f/hardware_oplus` | `calcite` | OPlus touch, display mode, vibration, alert slider interfaces |
| `kernel/oneplus/sm8650` | `https://github.com/aospa-f/kernel_oneplus_sm8650` | `calcite` | Linux 6.1 GKI kernel with SM8650 OnePlus drivers |
| `kernel/oneplus/sm8650-devicetrees` | `https://github.com/aospa-f/kernel_oneplus_sm8650-devicetrees` | `calcite` | Device tree source overlays (DTS/DTBO) |
| `kernel/oneplus/sm8650-modules` | `https://github.com/aospa-f/kernel_oneplus_sm8650-modules` | `calcite` | Out-of-tree kernel modules (WLAN, audio, touch) |
| `vendor/oneplus/giulia` | `https://github.com/TheMuppets/proprietary_vendor_oneplus_giulia` | `lineage-23.2` | Pre-extracted device-specific proprietary blobs from OxygenOS |
| `vendor/oneplus/sm8650-common` | `https://github.com/TheMuppets/proprietary_vendor_oneplus_sm8650-common` | `lineage-23.2` | Pre-extracted SM8650 common proprietary blobs from OxygenOS |
| `vendor/oneplus/sm8650-oss` | `https://github.com/aospa-f/vendor_oneplus_sm8650-oss` | `calcite` | Open-source touch (`vendor.oplus.hardware.touch@2.0-service`) |
| `vendor/oplus/camera` | `https://github.com/aospa-f/vendor_oplus_camera` | `calcite` | Stock OPlus Camera APK and underlying OEM camera imaging pipeline |
| `vendor/sony/dolby` | `https://github.com/aosp-for-giulia/proprietary_vendor_sony_dolby` | `16` | Dolby Atmos DSP binaries and audio effects |
| `vendor/oneplus/ir` | `https://github.com/aosp-for-giulia/vendor_oneplus_ir` | `16` | Infrared transmitter HAL and service |
| `vendor/google/gms` | `https://github.com/ThankYouMario/vendor_google_gms` | `calcite` | Google Mobile Services prebuilts |
| `vendor/aospa` | `https://github.com/aospa-f/aospa_vendor_aospa` | `axion-scene-qs` | AOSPA branding, product configs (`aospa_giulia.mk`), signing logic |
| `build-logs` | `https://github.com/aospa-f/build-logs` | `main` | Build scripts, patchers, recovery docs, setup manuals |

---

## 4. Manifest System & Initialization

### A. Primary Manifest
* Initialized via:
  ```bash
  repo init -u https://github.com/aospa-f/manifest -b calcite
  ```
* Includes:
  * `aosp.xml`: Base AOSP Android 15 repositories.
  * `aospa.xml`: Paranoid Android core framework, system apps, and vendor packages.
  * `oplus.xml`: OnePlus 13R device, kernel, hardware, camera, and Dolby trees.

### B. Local Manifests (`~/.repo/local_manifests/`)
Placed in `.repo/local_manifests/` prior to `repo sync`:
1. **`giulia.xml`**:
   - Imports `vendor/oneplus/giulia` and `vendor/oneplus/sm8650-common` from `TheMuppets` (`lineage-23.2`).
   - Imports GCC 4.9 toolchains required by legacy kernel build scripts.
2. **`baristablend.xml`**:
   - Imports Qualcomm HAL overrides (`calcite-8650` branch from `aospa-op12`):
     - `hardware/qcom/display`
     - `hardware/qcom/gps`
     - `vendor/qcom/opensource/audio-hal/primary-hal`
     - `vendor/qcom/opensource/audio-hal/st-hal-ar`
     - `vendor/qcom/opensource/audioreach-graphservices`
     - `vendor/qcom/opensource/agm`
     - `vendor/qcom/opensource/pal`

---

## 5. Stock OxygenOS `super.img` Extraction Deep Dive

If you ever need to update or extract proprietary vendor blobs directly from official OnePlus OxygenOS firmware without relying on third-party repositories, this section details the complete extraction pipeline.

### A. Source Firmware Versions
* **OnePlus 13R**: `CPH2691_16.0.10.600(EX01)` (OxygenOS 16 base).
* **OnePlus 12 (Common Base)**: `CPH2573_16.0.10.501(EX01)` (Snapdragon 8 Gen 3 platform base).

### B. Partition Map inside Stock OOS `super.img` & `payload.bin`

When extracting the stock OxygenOS OTA or full package, `super.img` contains several dynamic sub-partitions. Here is where every component originates:

| Partition | Sub-Directory in Vendor | What is Extracted / Required by ROM |
| :--- | :--- | :--- |
| **`odm.img`** | `proprietary/odm/` | **Camera Tunings & ISP**: Sensor calibration, chromatix profiles (`odm/etc/camera/`).<br>**Audio Calibration (ACDB)**: `odm/etc/acdbdata/` calibration workspaces for earpiece, speaker, mic.<br>**ADSP Hexagon DSP**: `odm/lib/rfsa/adsp/` DSP libraries for noise cancellation & voice.<br>**Smart PA Amplifier**: `odm/lib64/libtfa98xx.so` for TFA98xx dual speaker amplification.<br>**ANT+ Firmware**: `odm/vendor/firmware/antdtx.*`.<br>**Display Panel Chaplin**: `odm/lib64/libPanelChaplin.so` for display calibration. |
| **`vendor.img`** | `proprietary/vendor/` | **Qualcomm Hardware HALs**: Adreno GPU driver (`libGLESv2_adreno.so`), Vulkan driver.<br>**Biometrics / Goodix Fingerprint**: FOD daemon & client libraries.<br>**Sensors & DSP**: Qualcomm sensor registry, sensor HAL daemons (`sensors.qti.so`).<br>**Thermal Engine**: `vendor/bin/thermal-engine` and device thermal configs.<br>**QCC & Connectivity**: Bluetooth controller firmware, Wi-Fi configuration profiles. |
| **`system.img`** | `proprietary/system/` | Core framework jars, system libraries, and base SELinux policy files. |
| **`system_ext.img`** | `proprietary/system_ext/` | OEM privileged apps and helper services. |
| **`product.img`** | `proprietary/product/` | Regional configuration overlays and carrier configuration bundles. |
| **`my_product.img`** | Extracted via OPlus utils | OnePlus custom device settings, camera feature flags, and haptic motor waveform definitions. |
| **`my_engineering.img`** | Extracted via OPlus utils | Hardware engineering diagnostics and factory calibration tables. |
| **`my_stock.img`** | Extracted via OPlus utils | Stock media assets, ringtones, and notification audio. |
| **`my_manifest.img`** | Extracted via OPlus utils | Treble HAL compatibility matrix and VINTF manifests. |

---

### C. Step-by-Step Manual Extraction Procedure

#### 1. Unpack the Stock Firmware
Using `payload-dumper-go`:
```bash
payload-dumper-go -o /tmp/extracted_stock payload.bin
```

#### 2. Unpack `super.img` (Dynamic Partitions)
```bash
lpunpack /tmp/extracted_stock/super.img /tmp/partitions/
```
This produces:
* `odm_a.img`, `vendor_a.img`, `system_a.img`, `system_ext_a.img`, `product_a.img`
* `my_product_a.img`, `my_engineering_a.img`, `my_stock_a.img`, `my_manifest_a.img`

#### 3. Mount Partitions
```bash
mkdir -p /mnt/stock/{odm,vendor,system,system_ext,product,my_product}
sudo mount -o ro /tmp/partitions/odm_a.img /mnt/stock/odm
sudo mount -o ro /tmp/partitions/vendor_a.img /mnt/stock/vendor
sudo mount -o ro /tmp/partitions/system_a.img /mnt/stock/system
sudo mount -o ro /tmp/partitions/system_ext_a.img /mnt/stock/system_ext
sudo mount -o ro /tmp/partitions/product_a.img /mnt/stock/product
sudo mount -o ro /tmp/partitions/my_product_a.img /mnt/stock/my_product
```

#### 4. Run the Automated Extract Scripts
From the ROM source tree:
```bash
cd ~/aospa/device/oneplus/giulia
./extract-files.py /mnt/stock
```
What this automated script does:
1. Reads `device/oneplus/giulia/proprietary-files.txt` and `device/oneplus/sm8650-common/proprietary-files.txt`.
2. Pulls required files from `/mnt/stock` into:
   - `vendor/oneplus/giulia/proprietary/`
   - `vendor/oneplus/sm8650-common/proprietary/`
3. Applies necessary binary ELF fixups on-the-fly using LineageOS `extract-utils`:
   - **Graphic Buffer ABI Fix**: Replaces `libui.so` dynamic linkage with `libui-stock.so` to bridge AOSP 15 buffer formats with proprietary Qualcomm camera components.
   - **Camera NDK Upgrade**: Rewrites `android.frameworks.cameraservice.device-V1-ndk.so` to `V3-ndk.so`.
   - **Shim Injection**: Injects `libui_shim.so` into `libcwb_qcom_aidl.so`.
   - **Provider Environment**: Adds `setenv JE_MALLOC_ZERO_FILLING 1` to `vendor.camera-provider` init service.
4. Generates `Android.bp`, `Android.mk`, `BoardConfigVendor.mk`, and `giulia-vendor.mk` automatically.

---

## 6. Private Keyset (Production Release Keys)

The production ROM is signed with private release keys located in `vendor/aospa-priv/security/`.
* **Security Rule**: This folder is listed in `.gitignore` and must **NEVER** be pushed to public Git repositories.
* **Workstation Backup**: A complete copy exists on your local laptop at:
  `/home/raizen/aospa-keys-backup/security/`
* **Contents**:
  - `releasekey.pk8`, `releasekey.x509.pem` (OS target & recovery signature)
  - `platform.pk8`, `platform.x509.pem` (System apps & SystemUI)
  - `shared.pk8`, `shared.x509.pem` (Shared user packages)
  - `media.pk8`, `media.x509.pem` (Media provider)
  - `networkstack.pk8`, `networkstack.x509.pem` (NetworkStack components)
  - `bluetooth.pk8`, `bluetooth.x509.pem` (Bluetooth stack)
  - `nfc.pk8`, `nfc.x509.pem` (NFC services)
  - `sdk_sandbox.pk8`, `sdk_sandbox.x509.pem` (SDK Sandbox runtime)
  - `cts_uicc_2021.pk8`, `cts_uicc_2021.x509.pem` (Carrier provisioning)

---

## 7. Build Execution & Target Images

### A. Environment Initialization
```bash
cd ~/aospa
source build/envsetup.sh
lunch aospa_giulia-user
```

### B. Building Target Partition Images (Fastbootd Flashable)
To compile and package the modular partitions:
```bash
m systemimage systemextimage
```
* **Output Artifacts**:
  - `out/target/product/giulia/system.img`: Contains `framework.jar`, `SettingsProvider.apk`, core system binaries.
  - `out/target/product/giulia/system_ext.img`: Contains `Settings.apk` (with unlock vibration toggle) and `ParanoidSystemUI.apk` (with QS landscape fix and haptic suppression).

### C. Flashing via Fastbootd
Reboot phone to `fastbootd` mode:
```bash
adb reboot fastboot
```
Flash updated partitions:
```bash
fastboot flash system system.img
fastboot flash system_ext system_ext.img
fastboot reboot
```

Zero data wipe required; user data and existing app states remain 100% intact.
