# OnePlus 13R / Ace 5 (`giulia`) - AOSPA-F Build Automation & Environment

Repository maintaining verified build automation, platform manifests, patches, and setup scripts for building **AOSPA-F (Calcite)** on the **OnePlus 13R / OnePlus Ace 5 (`giulia` / SM8650 `pineapple`)**.

---

## 📱 Firmware & Blob Source: OnePlus 13R India (`IN 16.0.10.600`) OxygenOS 16

The ROM is built with official **OnePlus 13R India (`IN 16.0.10.600`) OxygenOS 16** firmware:
* **All-in-One Single ROM ZIP**: All India `16.0.10.600` firmware partitions (`abl`, `aop`, `aop_config`, `bluetooth`, `cpucp`, `cpucp_dtb`, `devcfg`, `dsp`, `engineering_cdt`, `featenabler`, `hyp`, `imagefv`, `keymaster`, `modem`, `oplus_sec`, `oplusstanvbk`, `qupfw`, `shrm`, `splash`, `tz`, `uefi`, `uefisecapp`, `xbl`, `xbl_config`, `xbl_ramdump`) are embedded directly into `payload.bin`.
* **No Separate Firmware / Boot / Recovery Zips**: Flashing the single ROM ZIP flashes both Android and all India firmware in one pass.
* **Zero ColorOS 17 Blobs**: Built strictly against the OxygenOS 16 base. The verified build uses vendor blobs generated locally from the full India `16.0.10.600` dump (`vendor`, `odm`, `system`, `system_ext`, `product`, `my_product`) with `device/oneplus/{giulia,sm8650-common}/extract-files.py`. TheMuppets vendor trees are not used as the blob source.

### Vendor blob extraction

Generate both vendor trees from the OOS 16.0.10.600 dump before building:

```bash
cd ~/aospa/device/oneplus/giulia
PYTHONPATH=../../../tools/extract-utils:../../../hardware/oplus/extract-utils-ext \
    python3 extract-files.py /path/to/oos_160010600/dump/rom

cd ../sm8650-common
PYTHONPATH=../../../tools/extract-utils:../../../hardware/oplus/extract-utils-ext \
    python3 extract-files.py /path/to/oos_160010600/dump/rom
```

The bootstrap local manifest still names TheMuppets `sm8650-common` so a
fresh `repo sync` has a placeholder directory. The extraction overwrites it
with the OOS 16 tree. If the extraction is skipped, the build uses the stale
TheMuppets tree and may miss OOS 16 libraries.

---

## 📁 Repository Structure

```
build-logs/
├── README.md                      # Master build & setup documentation
├── local_manifests/
│   ├── giulia.xml                 # Local manifest for aospa-f trees; OOS16 blobs are extracted locally
│   └── baristablend.xml           # Qualcomm SM8650 audio/display HAL platform sync definitions
├── patches/                       # Verified discrete patches across modified projects
│   ├── build_make.patch           # Makes target-files VINTF compatibility check non-fatal
│   ├── build_soong.patch          # Disables strict build-time namespace enforcement
│   ├── device_oneplus_sm8650-common_volume_steps.patch # Volume step tuning
│   ├── hardware_qcom_display.patch # Fixes display AIDL mapper and gralloc header conflicts
│   ├── kernel_oneplus_sm8650.patch # GKI defconfig fixes (CONFIG_IP6_NF_NAT, SYSVIPC)
│   ├── vendor_aospa.patch         # DTBO overlay merge path fix across vendor techpacks
│   ├── vendor_oneplus_giulia.patch # India 16.0.10.600 radio images & SHA1 checksums
│   ├── vendor_oneplus_sm8650-common.patch # OOS16 vendor overlays, display/thermal configs
│   └── vendor_qcom_opensource_commonsys_fm.patch # FM radio build compatibility
├── prebuilts/
│   └── Datura/                    # CalyxOS Datura firewall prebuilt package
├── fresh_build.sh                 # 1-click master build launcher for fresh servers
└── scripts/
    ├── apply_all_patches.sh       # Automatically applies patches and deploys India 16.0.10.600 firmware
    ├── check_kernel_susfs_updates.sh # Tracks upstream Linux 6.1 LTS, SUSFS, and BakaSU
    ├── fresh_server_build.sh      # Complete 5-step automated bootstrap from clean server to ROM zip
    ├── setup_fresh_server.sh      # Installs all Ubuntu dependencies, ccache, repo tool
    ├── sync_manifest.sh           # Inits calcite manifest, deploys manifests, syncs & patches
    ├── track_clo_upstream.sh      # Tracks & merges changes from clo-for-giulia (calcite) upstream
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

#### 5. Generate the OPlus camera blobs (private/local builds)

The camera app and its libraries are proprietary and stay out of Git. The
source integration and SELinux policy are in `aospa-f/vendor_oplus_camera`.
With the OxygenOS 16.0.10.600 dump available:

```bash
cd vendor/oplus/camera/giulia
PYTHONPATH=../../../../tools/extract-utils \
    python3 extract-files.py --allow-prohibited-files /path/to/oos_160010600/dump/rom
```

`--allow-prohibited-files` is required because the private build includes the
SenseTime camera license artifact; do not use this flag for public builds.

#### 6. Run the build
```bash
./rom-build.sh giulia -v userdebug -t release
```

Output package will be generated at:
`~/aospa/out/target/product/giulia/aospa-calcite-<date>-gms-giulia.zip`

---

## 🔊 Dolby C2 library

The device tree carries Ronard's 568080-byte, CFI-free
`android.hardware.media.c2@1.0.so` in
`device/oneplus/giulia/prebuilt/vendor/lib64/`. The AOSPA source-built HIDL
library crashes the Sony Dolby C2 service, and the stock 16.0.10.600 library
fails its CFI check against AOSPA's `libhidlbase`. The prebuilt was verified
on giulia with an E-AC3 decode through `c2.dolby.eac3.decoder`; the Dolby
service stayed up and produced no tombstone.

Credit for the working library goes to Ronard. The device-tree commit records
the source, size, and SHA-256.

---

## ⚡ Flashing the ROM (LFFF Tool)

The recommended flashing method for the OnePlus 13R is using **LFFF (LibreFastbootFirmwareFlasher)**:
* Tool Repository: [https://github.com/mrFrok/LibreFastbootFirmwareFlasher](https://github.com/mrFrok/LibreFastbootFirmwareFlasher)
* Guide: [Flashing custom ROMs on OnePlus 13R / Ace 5](https://github.com/yashaswee-exe/AndroidGuides/wiki/Flashing-custom-ROMs-on-a-OnePlus-13R-Ace5)

1. Connect device in bootloader mode (`fastboot`).
2. Open LFFF and select the single generated `aospa-calcite-*.zip` (or the extracted `payload.bin`).
3. LFFF flashes boot and India firmware partitions in `fastboot`, reboots to `fastbootd`, flashes all dynamic logical partitions (`system`, `system_ext`, `product`, `odm`, `vendor`), and formats data.
