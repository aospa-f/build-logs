#!/usr/bin/env bash
#
# apply_all_patches.sh
# Automatically applies all custom patches and prebuilts to a fresh AOSPA tree.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PATCHES_DIR="${ROOT_DIR}/patches"
PREBUILTS_DIR="${ROOT_DIR}/prebuilts"

AOSPA_DIR="${1:-${HOME}/aospa}"

if [ ! -d "${AOSPA_DIR}" ]; then
    echo "[-] Error: AOSP source directory '${AOSPA_DIR}' not found."
    echo "    Usage: $0 [path/to/aospa]"
    exit 1
fi

echo "[+] Applying all fixes to AOSPA tree at: ${AOSPA_DIR}"

declare -A PATCH_MAP=(
    ["build_make.patch"]="build/make"
    ["build_soong.patch"]="build/soong"
    ["device_oneplus_sm8650-common_volume_steps.patch"]="device/oneplus/sm8650-common"
    ["frameworks_base_hd_icon_toggle.patch"]="frameworks/base"
    ["frameworks_base_virtual_hal_block.patch"]="frameworks/base"
    ["frameworks_base_statusbar_burnin.patch"]="frameworks/base"
    ["frameworks_base_volume_steps.patch"]="frameworks/base"
    ["frameworks_av_appvolume.patch"]="frameworks/av"
    ["frameworks_base_night_light.patch"]="frameworks/base"
    ["hardware_qcom_display.patch"]="hardware/qcom/display"
    ["kernel_oneplus_sm8650.patch"]="kernel/oneplus/sm8650"
    ["vendor_aospa.patch"]="vendor/aospa"
    ["vendor_aospa_volume_steps.patch"]="vendor/aospa"
    ["vendor_oneplus_sm8650-common_irqbalance.patch"]="vendor/oneplus/sm8650-common"
    ["vendor_qcom_common_perf.patch"]="vendor/qcom/common"
    ["vendor_qcom_opensource_commonsys_fm.patch"]="vendor/qcom/opensource/commonsys/fm"
)

APPLIED_COUNT=0
SKIPPED_COUNT=0

for PATCH_FILE in $(printf "%s\n" "${!PATCH_MAP[@]}" | sort); do
    TARGET_SUBDIR="${PATCH_MAP[$PATCH_FILE]}"
    TARGET_PATH="${AOSPA_DIR}/${TARGET_SUBDIR}"
    PATCH_PATH="${PATCHES_DIR}/${PATCH_FILE}"

    if [ ! -f "${PATCH_PATH}" ]; then
        echo "[-] Patch not found: ${PATCH_PATH}"
        continue
    fi

    if [ ! -d "${TARGET_PATH}" ]; then
        echo "[!] Warning: Target directory '${TARGET_PATH}' does not exist, skipping ${PATCH_FILE}"
        continue
    fi

    if [ "${PATCH_FILE}" = "vendor_oneplus_giulia.patch" ] && [ ! -d "${TARGET_PATH}/.git" ]; then
        echo "[*] vendor/oneplus/giulia is a locally extracted vendor tree, skipping patch"
        continue
    fi

    if [ "${PATCH_FILE}" = "vendor_oneplus_sm8650-common_irqbalance.patch" ] && [ ! -d "${TARGET_PATH}/.git" ]; then
        TARGET_FILE="${TARGET_PATH}/proprietary/vendor/bin/init.qti.kernel.sh"
        if [ -f "${TARGET_FILE}" ] && ! grep -q "start vendor.msm_irqbalance" "${TARGET_FILE}"; then
            echo "[*] Already applied: ${PATCH_FILE} (extracted vendor tree)"
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
            continue
        fi
        if [ -f "${TARGET_FILE}" ] && patch -d "${TARGET_PATH}" -p1 --forward < "${PATCH_PATH}"; then
            echo "[+] Applied to extracted vendor tree: ${PATCH_FILE}"
            APPLIED_COUNT=$((APPLIED_COUNT + 1))
            continue
        fi
        echo "[-] Error: could not apply ${PATCH_FILE} to extracted vendor tree"
        exit 1
    fi

    # Check if patch is already applied
    if git -C "${TARGET_PATH}" apply --reverse --check "${PATCH_PATH}" >/dev/null 2>&1; then
        echo "[*] Already applied: ${PATCH_FILE} -> ${TARGET_SUBDIR}"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
        continue
    fi

    echo "[+] Applying: ${PATCH_FILE} -> ${TARGET_SUBDIR}"
    if git -C "${TARGET_PATH}" apply --whitespace=nowarn "${PATCH_PATH}"; then
        APPLIED_COUNT=$((APPLIED_COUNT + 1))
    else
        echo "[-] Failed to apply ${PATCH_FILE} to ${TARGET_SUBDIR}."
        echo "    Attempting 3-way merge apply..."
        git -C "${TARGET_PATH}" apply --3way "${PATCH_PATH}" || {
            echo "[-] Error: Failed to apply patch ${PATCH_FILE}"
            exit 1
        }
        APPLIED_COUNT=$((APPLIED_COUNT + 1))
    fi
done

# ------------------------------------------------------------------
# Vendor dedup intentionally disabled.
# It removed vendor libraries that vendor services need; the copies in
# system_ext are not visible to the vendor linker namespace. Use the
# full 16.0.10.600 extraction + extract-files.py instead.
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# Deploy OnePlus 13R India (IN 16.0.10.600) Official Firmware Images
# ------------------------------------------------------------------
RADIO_DIR="${AOSPA_DIR}/vendor/oneplus/giulia/radio"
LOCAL_IN_FW="/home/raizen/oneplus/rom/Super Flasher 13R IN 16.0.10.600/OOS_FILES_HERE"
FW_DOWNLOAD_URL="https://github.com/aospa-f/build-logs/releases/download/fw-13r-in-16.0.10.600/giulia_in_16.0.10.600_radio.tar.gz"

if [ -d "${AOSPA_DIR}/vendor/oneplus/giulia" ]; then
    echo "[+] Deploying OnePlus 13R India (IN 16.0.10.600) firmware images into ${RADIO_DIR}..."
    mkdir -p "${RADIO_DIR}"
    if [ -f "${RADIO_DIR}/abl.img" ]; then
        echo "    OnePlus 13R India firmware images already present in ${RADIO_DIR}."
    elif [ -d "/serverhive5/raizenftw/giulia_radio_backup" ]; then
        echo "    Using firmware backup from /serverhive5/raizenftw/giulia_radio_backup..."
        cp -f /serverhive5/raizenftw/giulia_radio_backup/*.img "${RADIO_DIR}/"
    elif [ -d "${LOCAL_IN_FW}" ]; then
        echo "    Using local India firmware from ${LOCAL_IN_FW}..."
        for img in abl.img aop.img aop_config.img bluetooth.img cpucp.img cpucp_dtb.img devcfg.img dsp.img engineering_cdt.img featenabler.img hyp.img imagefv.img keymaster.img modem.img oplus_sec.img oplusstanvbk.img qupfw.img shrm.img splash.img tz.img uefi.img uefisecapp.img xbl.img xbl_config.img xbl_ramdump.img; do
            if [ -f "${LOCAL_IN_FW}/${img}" ]; then
                cp -f "${LOCAL_IN_FW}/${img}" "${RADIO_DIR}/${img}"
            fi
        done
    else
        echo "    Downloading India 16.0.10.600 firmware package from GitHub release..."
        curl -sL "${FW_DOWNLOAD_URL}" | tar -xz -C "${RADIO_DIR}"
    fi
    echo "[✓] OnePlus 13R India firmware deployed."
fi

# Copy custom prebuilts if present
if [ -d "${PREBUILTS_DIR}/Datura" ]; then
    echo "[+] Deploying prebuilt Datura package..."
    mkdir -p "${AOSPA_DIR}/vendor/aospa/prebuilt/common/app/Datura"
    cp -r "${PREBUILTS_DIR}/Datura/"* "${AOSPA_DIR}/vendor/aospa/prebuilt/common/app/Datura/"
fi

# Ensure KernelSU driver symlink exists if KernelSU repository is present
if [ -d "${AOSPA_DIR}/kernel/oneplus/sm8650/KernelSU/kernel" ]; then
    if [ ! -L "${AOSPA_DIR}/kernel/oneplus/sm8650/drivers/kernelsu" ]; then
        echo "[+] Ensuring KernelSU driver symlink in kernel/oneplus/sm8650/drivers/kernelsu..."
        ln -sf ../KernelSU/kernel "${AOSPA_DIR}/kernel/oneplus/sm8650/drivers/kernelsu"
    fi
fi

# ------------------------------------------------------------------
# Fix rear camera CFI crash, FusionLight ambient brightness, OPlus sensor
# calibration service, tcmd seccomp policy, NFC config, and Dolby/ICC blobs
# ------------------------------------------------------------------
GIULIA_FIXES="${PREBUILTS_DIR}/giulia_fixes"
if [ -d "${GIULIA_FIXES}" ]; then
    echo "[+] Deploying Giulia sensor, FusionLight, NFC, Dolby, and ICC blobs..."
    mkdir -p "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/bin/hw" \
             "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/etc/init" \
             "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/etc/vintf/manifest" \
             "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/etc/fusionlight_profile" \
             "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/lib64" \
             "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/product/etc/permissions" \
             "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/vendor/etc" \
             "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/vendor/firmware" \
             "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/vendor/lib64"

    cp -f "${GIULIA_FIXES}/odm/vendor-oplus-hardware-oplusSensor-V1-service" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/bin/hw/"
    chmod 0755 "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/bin/hw/vendor-oplus-hardware-oplusSensor-V1-service"
    cp -f "${GIULIA_FIXES}/odm/vendor-oplus-hardware-oplusSensor-V1-service.rc" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/etc/init/"
    cp -f "${GIULIA_FIXES}/odm/manifest_oplusSensor_aidl.xml" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/etc/vintf/manifest/"
    cp -f "${GIULIA_FIXES}/odm/fusionlight_Main_1_3.json" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/etc/fusionlight_profile/"
    cp -f "${GIULIA_FIXES}/odm/liboemcrypto.so" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/odm/lib64/"

    cp -f "${GIULIA_FIXES}/product/dolby_vision.cfg" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/product/etc/"
    cp -f "${GIULIA_FIXES}/product/privapp-permissions-euiccgoogle.xml" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/product/etc/permissions/"

    for f in display_apollo_list_AA577_P_3_A0020_dsc_cmd_mode_panel.xml libnfc-nci-NXP.conf libnfc-nxp.conf media_codecs_dolby_vision.xml; do
        cp -f "${GIULIA_FIXES}/vendor/${f}" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/vendor/etc/${f}"
    done
    cp -f "${GIULIA_FIXES}/vendor/libnfc-nci-NXP.conf" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/vendor/etc/libnfc-nci.conf"
    cp -f "${GIULIA_FIXES}/vendor/sn220u.bin" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/vendor/firmware/"
    cp -f "${GIULIA_FIXES}/vendor/libiccprofile.so" "${AOSPA_DIR}/vendor/oneplus/giulia/proprietary/vendor/lib64/"

    for f in public.libraries.txt media_codecs_pineapple.xml media_codecs_cliffs_v0.xml media_codecs_cliffs_v1.xml; do
        cp -f "${GIULIA_FIXES}/vendor/${f}" "${AOSPA_DIR}/vendor/oneplus/sm8650-common/proprietary/vendor/etc/${f}"
    done
fi

# Ensure sensors.fusionlight.so in hals.conf and lseek: 1 in tcmd.policy
HALS_CONF="${AOSPA_DIR}/vendor/oneplus/sm8650-common/proprietary/vendor/etc/sensors/hals.conf"
if [ -f "${HALS_CONF}" ]; then
    sed -i "s/sensors\.qsh\.so/sensors.fusionlight.so/g" "${HALS_CONF}"
fi

TCMD_POLICY="${AOSPA_DIR}/vendor/oneplus/sm8650-common/proprietary/system_ext/etc/seccomp_policy/tcmd.policy"
if [ -f "${TCMD_POLICY}" ]; then
    grep -q "^lseek:" "${TCMD_POLICY}" || echo "lseek: 1" >> "${TCMD_POLICY}"
fi

python3 - "${AOSPA_DIR}" << 'PYPATCH'
import sys
from pathlib import Path

aospa_dir = Path(sys.argv[1])
old_pat = b"mTrimSrcData %d\x00linearmapper\x00"
new_pat = b"mTrimSrcData %d\x00.linearmappe\x00"

for rel in [
    "vendor/oneplus/giulia/proprietary/vendor/lib64/hw/com.qti.chi.override.so",
    "vendor/oneplus/giulia/proprietary/vendor/lib64/libchifeature2.so",
]:
    target = aospa_dir / rel
    if target.is_file():
        data = target.read_bytes()
        if old_pat in data:
            target.write_bytes(data.replace(old_pat, new_pat, 1))
            print(f"[+] Patched rear camera linearmapper keyword in {rel}")
        elif new_pat in data:
            print(f"[*] Rear camera linearmapper fix already present in {rel}")
PYPATCH

echo ""
echo "[✓] All patches and India firmware applied successfully!"
echo "    Applied patches: ${APPLIED_COUNT} | Already present: ${SKIPPED_COUNT}"
