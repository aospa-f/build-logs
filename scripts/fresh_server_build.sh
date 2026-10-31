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
echo "  Variant:      ${VARIANT} | Build Type: ${BUILD_TYPE}"
echo "  Firmware:     OnePlus 13R India (IN 16.0.10.600) OOS16"
echo "  Org:          aospa-f (https://github.com/aospa-f)"
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
    repo init -u https://github.com/aospa-f/manifest -b calcite --git-lfs
else
    echo "[✓] Repo already initialized in ${AOSPA_DIR}."
fi

# ------------------------------------------------------------------
# Step 3: Install aospa-f Local Manifests & Sync Source Tree
# ------------------------------------------------------------------
echo ""
echo "[Step 3/5] Setting up local manifests and syncing repositories..."
mkdir -p .repo/local_manifests
if [ -d "${ROOT_DIR}/local_manifests" ]; then
    echo "[+] Deploying local manifests from build-logs..."
    cp -r "${ROOT_DIR}/local_manifests/"*.xml .repo/local_manifests/
fi

SYNC_THREADS="$(( THREADS > 32 ? 32 : THREADS ))"
echo "[+] Syncing source tree (${SYNC_THREADS} network threads)..."
repo sync -c -j"${SYNC_THREADS}" --force-sync --no-clone-bundle --no-tags

# ------------------------------------------------------------------
# Step 4: Apply Verified Fixes, India Firmware & Patches
# ------------------------------------------------------------------
echo ""
echo "[Step 4/5] Applying verified platform patches and deploying India 16.0.10.600 firmware..."
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

BUILD_CMD=("./rom-build.sh" "${DEVICE}" -t "${VARIANT}")
if [ "${BUILD_TYPE}" = "alpha" ] || [ "${BUILD_TYPE}" = "beta" ] || [ "${BUILD_TYPE}" = "stable" ]; then
    BUILD_CMD+=("-v" "${BUILD_TYPE}")
fi
"${BUILD_CMD[@]}"

ROM_ZIP=$(find "${AOSPA_DIR}/out/target/product/${DEVICE}" -maxdepth 1 -name "aospa-*.zip" ! -name "*ota*" 2>/dev/null | head -n 1 || echo "")

echo ""
echo "============================================================"
echo "  [✓] Build finished successfully!"
if [ -n "${ROM_ZIP}" ]; then
    echo "  Single ROM ZIP Package: ${ROM_ZIP}"
    echo "  Size: $(du -h "${ROM_ZIP}" | cut -f1)"
else
    echo "  Output target: ${AOSPA_DIR}/out/target/product/${DEVICE}/"
fi
echo "  (All OnePlus 13R India 16.0.10.600 firmware partitions are included in payload.bin)"
echo "============================================================"
