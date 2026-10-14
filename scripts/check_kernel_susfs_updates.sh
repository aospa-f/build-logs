#!/usr/bin/env bash
#
# check_kernel_susfs_updates.sh
# Checks for upstream updates across Linux 6.1, SUSFS (simonpunk), and BakaSU
#
set -euo pipefail

echo "============================================================"
echo "  Kernel, SUSFS & BakaSU Upstream Version Tracker"
echo "  Target: OnePlus 13R / Ace 5 (SM8650 pineapple / Linux 6.1)"
echo "============================================================"
echo ""

# 1. Check Latest Linux 6.1 LTS release
echo "[1/3] Checking latest Linux 6.1 upstream from kernel.org..."
LATEST_6_1=$(curl -s https://www.kernel.org/finger_banner | grep "6.1." | head -n 1 | awk '{print $NF}' || echo "Unknown")
echo "      Upstream Linux 6.1 LTS release: ${LATEST_6_1}"

# 2. Check Latest SUSFS commits from simonpunk/susfs4ksu
echo ""
echo "[2/3] Checking latest SUSFS (simonpunk/susfs4ksu)..."
SUSFS_COMMIT=$(curl -s "https://gitlab.com/api/v4/projects/simonpunk%2Fsusfs4ksu/repository/commits?ref_name=gki-android14-6.1&per_page=1" | jq -r '.[0] | "\(.short_id) - \(.title) (\(.committed_date[:10]))"' || echo "Failed to fetch")
SUSFS_DEV_COMMIT=$(curl -s "https://gitlab.com/api/v4/projects/simonpunk%2Fsusfs4ksu/repository/commits?ref_name=gki-android14-6.1-dev&per_page=1" | jq -r '.[0] | "\(.short_id) - \(.title) (\(.committed_date[:10]))"' || echo "Failed to fetch")
echo "      Latest gki-android14-6.1:     ${SUSFS_COMMIT}"
echo "      Latest gki-android14-6.1-dev: ${SUSFS_DEV_COMMIT}"

# 3. Check Latest BakaSU (sync-susfs branch)
echo ""
echo "[3/3] Checking latest BakaSU (Baka-SU/BakaSU)..."
BAKASU_COMMIT=$(curl -s "https://api.github.com/repos/Baka-SU/BakaSU/commits?sha=sync-susfs&per_page=1" | jq -r '.[0] | "\(.sha[:8]) - \(.commit.message | split("\n")[0]) (\(.commit.author.date[:10]))"' || echo "Failed to fetch")
echo "      Latest sync-susfs:           ${BAKASU_COMMIT}"

echo ""
echo "============================================================"
echo "  Current aospa-faye Status:"
echo "  • Kernel Tree:   Linux 6.1.176 (aospa-faye/android_kernel_oneplus_sm8650)"
echo "  • SUSFS Engine:  v2.3.0 in-tree with all 13 stealth flags active"
echo "  • BakaSU Root:   sync-susfs synced to aospa-faye/BakaSU"
echo "============================================================"
