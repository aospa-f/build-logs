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
    ["device_oneplus_sm8650-common.patch"]="device/oneplus/sm8650-common"
    ["hardware_qcom_display.patch"]="hardware/qcom/display"
    ["kernel_oneplus_sm8650.patch"]="kernel/oneplus/sm8650"
    ["vendor_aospa.patch"]="vendor/aospa"
    ["vendor_qcom_opensource_commonsys_fm.patch"]="vendor/qcom/opensource/commonsys/fm"
)

APPLIED_COUNT=0
SKIPPED_COUNT=0

for PATCH_FILE in "${!PATCH_MAP[@]}"; do
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
# Deduplicate vendor trees (sm8650-common and giulia)
# ------------------------------------------------------------------
if [ -f "${SCRIPT_DIR}/dedup_vendor.py" ]; then
    echo "[+] Running vendor deduplication script..."
    python3 "${SCRIPT_DIR}/dedup_vendor.py" "${AOSPA_DIR}"
fi

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


echo ""
echo "[✓] All patches and India firmware applied successfully!"
echo "    Applied patches: ${APPLIED_COUNT} | Already present: ${SKIPPED_COUNT}"
