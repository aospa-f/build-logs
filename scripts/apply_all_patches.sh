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
    ["build_soong.patch"]="build/soong"
    ["device_oneplus_sm8650-common.patch"]="device/oneplus/sm8650-common"
    ["device_qcom_sepolicy_vndr.patch"]="device/qcom/sepolicy_vndr"
    ["external_dtc.patch"]="external/dtc"
    ["hardware_oplus.patch"]="hardware/oplus"
    ["hardware_qcom_display.patch"]="hardware/qcom/display"
    ["kernel_oneplus_sm8650.patch"]="kernel/oneplus/sm8650"
    ["packages_apps_Settings.patch"]="packages/apps/Settings"
    ["vendor_aospa.patch"]="vendor/aospa"
    ["vendor_oneplus_giulia.patch"]="vendor/oneplus/giulia"
    ["vendor_oneplus_sm8650-common.patch"]="vendor/oneplus/sm8650-common"
    ["vendor_qcom_common.patch"]="vendor/qcom/common"
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

# Ensure FOSS replacement apps are checked for updates from F-Droid
if [ -f "${AOSPA_DIR}/packages/apps/FOSSApps/update_foss_apps.py" ]; then
    python3 "${AOSPA_DIR}/packages/apps/FOSSApps/update_foss_apps.py" || true
fi

echo ""
echo "[✓] All patches applied successfully!"
echo "    Applied: ${APPLIED_COUNT} | Already present: ${SKIPPED_COUNT}"
