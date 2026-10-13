#!/usr/bin/env bash
#
# track_clo_upstream.sh
# Manages upstream tracking from clo-for-giulia (Ronard's repositories).
#
set -euo pipefail

AOSPA_DIR="${1:-${HOME}/aospa}"
ACTION="${2:-status}"

if [ ! -d "${AOSPA_DIR}" ]; then
    echo "[-] Error: AOSP source directory '${AOSPA_DIR}' not found."
    echo "    Usage: $0 [path/to/aospa] [status|fetch|diff|merge]"
    exit 1
fi

declare -A CLO_REPOS=(
    ["device/oneplus/giulia"]="android_device_oneplus_giulia:celerity"
    ["device/oneplus/sm8650-common"]="android_device_oneplus_sm8650-common:celerity"
    ["kernel/oneplus/sm8650"]="android_kernel_oneplus_sm8650:celerity"
    ["kernel/oneplus/sm8650-devicetrees"]="android_kernel_oneplus_sm8650-devicetrees:celerity"
    ["kernel/oneplus/sm8650-modules"]="android_kernel_oneplus_sm8650-modules:celerity"
    ["build/make"]="build_make:celerity"
    ["build/soong"]="build_soong:celerity"
    ["frameworks/av"]="frameworks_av:celerity"
    ["frameworks/native"]="android_frameworks_native:celerity"
    ["device/qcom/sepolicy_vndr"]="android_device_qcom_sepolicy_vndr:celerity"
    ["device/qcom/common"]="device_qcom_common:celerity"
    ["vendor/qcom/common"]="vendor_qcom_common:celerity"
    ["hardware/oplus"]="android_hardware_oplus:celerity"
    ["vendor/qcom/opensource/thermal-hal"]="android_hardware_qcom_thermal:celerity"
    ["vendor/qcom/opensource/libvmmem"]="android_vendor_qcom_opensource_libvmmem:celerity"
    ["vendor/oneplus/ir"]="vendor_oneplus_ir:celerity"
    ["vendor/sony/dolby"]="proprietary_vendor_sony_dolby:celerity"
    ["packages/apps/LunarisDolby"]="android_packages_apps_LunarisDolby:celerity"
)

echo "=========================================================="
echo " CLO-FOR-GIULIA UPSTREAM TRACKER (${ACTION})"
echo " Target Tree: ${AOSPA_DIR}"
echo "=========================================================="

for REL_PATH in "${!CLO_REPOS[@]}"; do
    TARGET_DIR="${AOSPA_DIR}/${REL_PATH}"
    ENTRY="${CLO_REPOS[$REL_PATH]}"
    REPO_NAME="${ENTRY%%:*}"
    UPSTREAM_BRANCH="${ENTRY##*:}"
    UPSTREAM_URL="https://github.com/clo-for-giulia/${REPO_NAME}.git"

    if [ ! -d "${TARGET_DIR}/.git" ]; then
        continue
    fi

    echo ""
    echo ">>> ${REL_PATH} (${REPO_NAME}) [${UPSTREAM_BRANCH}]"

    # Configure upstream remote if missing
    if ! git -C "${TARGET_DIR}" remote get-url upstream >/dev/null 2>&1; then
        echo "    Adding upstream remote: ${UPSTREAM_URL}"
        git -C "${TARGET_DIR}" remote add upstream "${UPSTREAM_URL}" || true
    fi

    case "${ACTION}" in
        fetch)
            git -C "${TARGET_DIR}" fetch upstream "${UPSTREAM_BRANCH}" --quiet
            INCOMING=$(git -C "${TARGET_DIR}" rev-list HEAD..upstream/"${UPSTREAM_BRANCH}" --count 2>/dev/null || echo 0)
            echo "    Fetched. New upstream commits: ${INCOMING}"
            ;;
        diff)
            git -C "${TARGET_DIR}" fetch upstream "${UPSTREAM_BRANCH}" --quiet
            echo "    --- Upstream changes summary ---"
            git -C "${TARGET_DIR}" log HEAD..upstream/"${UPSTREAM_BRANCH}" --oneline -n 5 || echo "    (No incoming changes)"
            ;;
        merge)
            git -C "${TARGET_DIR}" fetch upstream "${UPSTREAM_BRANCH}" --quiet
            CURRENT_BRANCH=$(git -C "${TARGET_DIR}" rev-parse --abbrev-ref HEAD)
            echo "    Merging upstream/${UPSTREAM_BRANCH} into ${CURRENT_BRANCH}..."
            git -C "${TARGET_DIR}" merge upstream/"${UPSTREAM_BRANCH}" || {
                echo "    [!] Merge conflict in ${REL_PATH}. Resolve manually or abort with: git merge --abort"
            }
            ;;
        status|*)
            git -C "${TARGET_DIR}" fetch upstream "${UPSTREAM_BRANCH}" --quiet || true
            INCOMING=$(git -C "${TARGET_DIR}" rev-list HEAD..upstream/"${UPSTREAM_BRANCH}" --count 2>/dev/null || echo 0)
            AHEAD=$(git -C "${TARGET_DIR}" rev-list upstream/"${UPSTREAM_BRANCH}"..HEAD --count 2>/dev/null || echo 0)
            echo "    Status: [Ahead by ${AHEAD} commits | Behind upstream by ${INCOMING} commits]"
            ;;
    esac
done

echo ""
echo "[✓] Upstream tracking operation (${ACTION}) completed!"
