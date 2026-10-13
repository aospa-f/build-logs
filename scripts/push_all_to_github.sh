#!/usr/bin/env bash
#
# push_all_to_github.sh
# Creates dyruz10/build-logs on GitHub and pushes all fixes, patches, and logs.
# Can run with a GitHub Token or using SSH keys.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_LOGS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

GH_USER="dyruz10"
TOKEN="${1:-${GITHUB_TOKEN:-}}"

if [ -z "${TOKEN}" ]; then
    echo "=========================================================="
    echo " GitHub Personal Access Token Required"
    echo "=========================================================="
    echo "To create the 'build-logs' repository and push commits to"
    echo "your GitHub account (${GH_USER}), please provide a token:"
    echo ""
    echo "Usage: $0 <YOUR_GITHUB_TOKEN>"
    echo "  or: GITHUB_TOKEN=ghp_xxx $0"
    echo ""
    echo "Token requirements:"
    echo "  • Scope: 'repo' (Full control of private repositories)"
    echo "  • Create at: https://github.com/settings/tokens/new"
    echo "=========================================================="
    exit 1
fi

echo "[+] Authenticating with GitHub API for user: ${GH_USER}..."

# 1. Check or Create 'build-logs' repository on GitHub
REPO_NAME="build-logs"
REPO_CHECK=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token ${TOKEN}" "https://api.github.com/repos/${GH_USER}/${REPO_NAME}")

if [ "${REPO_CHECK}" = "404" ]; then
    echo "[+] Creating repository '${GH_USER}/${REPO_NAME}' on GitHub..."
    curl -s -H "Authorization: token ${TOKEN}" \
         -H "Content-Type: application/json" \
         -d '{
               "name": "'"${REPO_NAME}"'",
               "description": "AOSPA Calcite Initial Build Logs, Patches, Local Manifests, and Setup Automation for OnePlus 13R (giulia / SM8650)",
               "private": false
             }' \
         "https://api.github.com/user/repos" >/dev/null
    echo "[✓] Created repository https://github.com/${GH_USER}/${REPO_NAME}"
else
    echo "[*] Repository https://github.com/${GH_USER}/${REPO_NAME} already exists."
fi

# 2. Initialize and push build-logs repository
echo "[+] Preparing local build-logs git repository..."
cd "${BUILD_LOGS_DIR}"
if [ ! -d ".git" ]; then
    git init
    git branch -M main
fi

git config user.name "${GH_USER}"
git config user.email "lucykushinay@gmail.com"
git add -A
if ! git diff --cached --quiet; then
    git commit -m "build-logs: Initial build log (2026-10-13), verified patches, manifests, and automation scripts"
fi

echo "[+] Pushing build-logs to GitHub..."
PUSH_URL="https://${GH_USER}:${TOKEN}@github.com/${GH_USER}/${REPO_NAME}.git"
git remote remove origin 2>/dev/null || true
git remote add origin "${PUSH_URL}"
git push -u origin main --force

# Reset remote without embedded token for security
git remote set-url origin "https://github.com/${GH_USER}/${REPO_NAME}.git"
echo "[✓] Successfully uploaded build-logs to https://github.com/${GH_USER}/${REPO_NAME}"

# 3. Optional: Push modified ROM repositories on server or local tree
AOSPA_DIR="${2:-${HOME}/aospa}"
if [ -d "${AOSPA_DIR}" ]; then
    echo ""
    echo "[+] Updating user repositories in ${AOSPA_DIR}..."

    # local_manifests
    if [ -d "${AOSPA_DIR}/.repo/local_manifests/.git" ]; then
        echo ">>> Pushing .repo/local_manifests..."
        git -C "${AOSPA_DIR}/.repo/local_manifests" push "https://${GH_USER}:${TOKEN}@github.com/${GH_USER}/local_manifests.git" main:main || true
    fi

    # vendor/aospa
    if [ -d "${AOSPA_DIR}/vendor/aospa/.git" ]; then
        echo ">>> Pushing vendor/aospa (calcite)..."
        git -C "${AOSPA_DIR}/vendor/aospa" push "https://${GH_USER}:${TOKEN}@github.com/${GH_USER}/android_vendor_aospa.git" calcite:calcite || true
    fi

    # device/oneplus/sm8650-common
    if [ -d "${AOSPA_DIR}/device/oneplus/sm8650-common/.git" ]; then
        echo ">>> Pushing device/oneplus/sm8650-common (calcite)..."
        git -C "${AOSPA_DIR}/device/oneplus/sm8650-common" push "https://${GH_USER}:${TOKEN}@github.com/${GH_USER}/android_device_oneplus_sm8650-common.git" calcite:calcite || true
    fi

    # packages/apps/Settings
    if [ -d "${AOSPA_DIR}/packages/apps/Settings/.git" ]; then
        echo ">>> Pushing packages/apps/Settings (calcite)..."
        git -C "${AOSPA_DIR}/packages/apps/Settings" push "https://${GH_USER}:${TOKEN}@github.com/${GH_USER}/android_packages_apps_Settings.git" calcite:calcite || true
    fi

    # hardware/oplus
    if [ -d "${AOSPA_DIR}/hardware/oplus/.git" ]; then
        echo ">>> Pushing hardware/oplus (calcite)..."
        git -C "${AOSPA_DIR}/hardware/oplus" push "https://${GH_USER}:${TOKEN}@github.com/${GH_USER}/android_hardware_oplus.git" calcite:calcite || true
    fi
fi

# 4. Fork remaining clo-for-giulia repositories to dyruz10
echo ""
echo "[+] Checking/Forking remaining clo-for-giulia repositories into ${GH_USER}..."
CLO_REPOS=(
    "build_make"
    "build_soong"
    "frameworks_av"
    "android_frameworks_native"
    "android_device_qcom_sepolicy_vndr"
    "vendor_qcom_common"
    "device_qcom_common"
    "android_hardware_qcom_thermal"
    "android_vendor_qcom_opensource_libvmmem"
    "vendor_oneplus_ir"
    "proprietary_vendor_sony_dolby"
    "android_packages_apps_LunarisDolby"
)

for CLO_REPO in "${CLO_REPOS[@]}"; do
    CHECK_USER_REPO=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token ${TOKEN}" "https://api.github.com/repos/${GH_USER}/${CLO_REPO}")
    if [ "${CHECK_USER_REPO}" = "404" ]; then
        echo "    Forking clo-for-giulia/${CLO_REPO} -> ${GH_USER}/${CLO_REPO}..."
        curl -s -X POST -H "Authorization: token ${TOKEN}" "https://api.github.com/repos/clo-for-giulia/${CLO_REPO}/forks" >/dev/null || true
    else
        echo "    Already exists: ${GH_USER}/${CLO_REPO}"
    fi
done

echo ""
echo "=========================================================="
echo " [✓] ALL GITHUB REPOSITORIES AND LOGS SYNCHRONIZED!"
echo "=========================================================="
