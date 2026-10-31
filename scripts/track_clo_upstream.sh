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
    ["device/oneplus/giulia"]="device_oneplus_giulia:calcite"
    ["device/oneplus/sm8650-common"]="device_oneplus_sm8650-common:calcite"
    ["kernel/oneplus/sm8650"]="kernel_oneplus_sm8650:calcite"
    ["kernel/oneplus/sm8650-devicetrees"]="kernel_oneplus_sm8650-devicetrees:calcite"
    ["kernel/oneplus/sm8650-modules"]="kernel_oneplus_sm8650-modules:calcite"
    ["hardware/oplus"]="hardware_oplus:calcite"
    ["vendor/oplus/camera"]="vendor_oplus_camera:calcite"
    ["vendor/oneplus/sm8650-oss"]="vendor_oneplus_sm8650-oss:calcite"
    ["device/qcom/sepolicy_vndr"]="aospa_device_qcom_sepolicy_vndr:calcite"
    ["frameworks/base"]="aospa_frameworks_base:calcite"
    ["frameworks/av"]="aospa_frameworks_av:calcite"
    ["frameworks/native"]="aospa_frameworks_native:calcite"
    ["packages/apps/Settings"]="aospa_packages_apps_Settings:calcite"
    ["vendor/aospa"]="aospa_vendor_aospa:calcite"
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
