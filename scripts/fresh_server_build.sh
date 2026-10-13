#!/usr/bin/env bash
#
# fresh_server_build.sh
# End-to-end automated bootstrap script for building AOSPA Calcite on a fresh server.
#
# Usage:
#   bash ~/build-logs/scripts/fresh_server_build.sh
#   bash ~/build-logs/scripts/fresh_server_build.sh [aospa_dir] [device] [variant] [type]
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

AOSPA_DIR="${1:-${HOME}/aospa}"
DEVICE="${2:-giulia}"
VARIANT="${3:-userdebug}"
BUILD_TYPE="${4:-release}"
THREADS="$(nproc --all)"

echo "============================================================"
echo "  Paranoid Android (AOSPA) Calcite - Fresh Server Build"
echo "  Device:       ${DEVICE} (OnePlus 13R / Ace 5 SM8650)"
echo "  Target Tree:  ${AOSPA_DIR}"
echo "  Variant:      ${VARIANT} | Type: ${BUILD_TYPE}"
echo "  Org:          aospa-faye (https://github.com/aospa-faye)"
echo "============================================================"
echo ""

# ------------------------------------------------------------------
# Step 1: System Dependencies & Environment Setup
# ------------------------------------------------------------------
echo "[Step 1/5] Configuring system packages, ccache, and build tools..."
if ! command -v repo >/dev/null 2>&1 || ! command -v ccache >/dev/null 2>&1; then
    echo "[+] Running setup_fresh_server.sh..."
    bash "${SCRIPT_DIR}/setup_fresh_server.sh"
else
    echo "[✓] Core build tools already present. Ensuring ccache config..."
    ccache -M 100G >/dev/null 2>&1 || true
fi

# Export CCache environment variables for the current session
export USE_CCACHE=1
export CCACHE_EXEC="$(command -v ccache || echo '/usr/bin/ccache')"
export CCACHE_DIR="${HOME}/.ccache"
mkdir -p "${CCACHE_DIR}"

# ------------------------------------------------------------------
# Step 2: Initialize AOSP Source Tree (AOSPA calcite)
# ------------------------------------------------------------------
echo ""
echo "[Step 2/5] Initializing AOSPA calcite manifest..."
mkdir -p "${AOSPA_DIR}"
cd "${AOSPA_DIR}"

if [ ! -d ".repo" ]; then
    repo init -u https://github.com/AOSPA/manifest -b calcite --git-lfs
else
    echo "[✓] Repo already initialized in ${AOSPA_DIR}."
fi

# ------------------------------------------------------------------
# Step 3: Install aospa-faye Local Manifests & Sync Source Tree
# ------------------------------------------------------------------
echo ""
echo "[Step 3/5] Setting up local manifests and syncing repositories..."
if [ ! -d ".repo/local_manifests/.git" ]; then
    rm -rf .repo/local_manifests
    git clone https://github.com/aospa-faye/local_manifests.git .repo/local_manifests
else
    echo "[+] Updating local_manifests from aospa-faye..."
    git -C .repo/local_manifests pull origin main || true
fi

# Ensure local copies from build-logs take precedence if newer
if [ -d "${ROOT_DIR}/local_manifests" ]; then
    cp -r "${ROOT_DIR}/local_manifests/"*.xml .repo/local_manifests/ 2>/dev/null || true
fi

echo "[+] Syncing source tree (${THREADS} threads)..."
repo sync -c -j"${THREADS}" --force-sync --no-clone-bundle --no-tags

# ------------------------------------------------------------------
# Step 4: Apply Verified Fixes, Patches & Prebuilts
# ------------------------------------------------------------------
echo ""
echo "[Step 4/5] Applying verified platform patches and prebuilts..."
bash "${SCRIPT_DIR}/apply_all_patches.sh" "${AOSPA_DIR}"

# ------------------------------------------------------------------
# Step 5: Execute ROM Build
# ------------------------------------------------------------------
echo ""
echo "[Step 5/5] Launching ROM compilation for ${DEVICE}..."
cd "${AOSPA_DIR}"

# Verify build script existence
if [ ! -f "./rom-build.sh" ]; then
    if [ -f "vendor/aospa/build.sh" ]; then
        ln -sf vendor/aospa/build.sh rom-build.sh
    else
        echo "[-] Error: rom-build.sh not found in ${AOSPA_DIR}."
        exit 1
    fi
fi

./rom-build.sh "${DEVICE}" -v "${VARIANT}" -t "${BUILD_TYPE}"

echo ""
echo "============================================================"
echo "  [✓] Build finished successfully!"
echo "  Output target: ${AOSPA_DIR}/out/target/product/${DEVICE}/"
echo "============================================================"
