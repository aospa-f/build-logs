#!/usr/bin/env bash
#
# sync_manifest.sh
# Initializes AOSPA Calcite, installs local manifests, syncs trees, and applies patches.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

AOSPA_DIR="${1:-${HOME}/aospa}"
THREADS="$(nproc --all)"

echo "[+] Target tree: ${AOSPA_DIR}"
mkdir -p "${AOSPA_DIR}"
cd "${AOSPA_DIR}"

if [ ! -d ".repo" ]; then
    echo "[+] Initializing AOSPA manifest (calcite)..."
    repo init -u https://github.com/AOSPA/manifest -b calcite --git-lfs
fi

# Deploy local manifests
echo "[+] Deploying OnePlus 13R (giulia) local manifests..."
mkdir -p .repo/local_manifests
cp "${ROOT_DIR}/local_manifests/"*.xml .repo/local_manifests/

echo "[+] Syncing source tree (${THREADS} threads)..."
repo sync -c -j"${THREADS}" --force-sync --no-clone-bundle --no-tags

echo "[+] Applying verified build patches..."
bash "${SCRIPT_DIR}/apply_all_patches.sh" "${AOSPA_DIR}"

echo "[✓] Source tree synchronized and patched successfully!"
echo "    Ready to build: cd ${AOSPA_DIR} && ./rom-build.sh giulia -v userdebug -t release"
