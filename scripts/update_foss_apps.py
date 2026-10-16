#!/usr/bin/env python3
#
# Copyright (C) 2026 AOSPA-Faye
# SPDX-License-Identifier: Apache-2.0
#
# update_foss_apps.py
# Automatically checks for and downloads the latest F-Droid releases
# of the default FOSS replacement applications during ROM compilation.
#

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

TRACKED_APPS = {
    "com.bnyro.clock": "BnyroClock.apk",
    "net.youapps.calcyou": "CalcYou.apk",
    "com.bnyro.contacts": "ConnectYou.apk",
    "helium314.keyboard": "HeliBoard.apk",
    "de.jeanlucmakiola.calendula": "Calendula.apk",
    "com.afkanerd.deku": "DekuSMS.apk",
}

# Mapping of GitHub repositories to local APK filename
GITHUB_APPS = {
    "com.resukisu.resukisu": {
        "repo": "Baka-SU/BakaSU",
        "apk": "BakaSU.apk",
        "asset_suffix": "arm64-v8a-release.apk",
    }
}

USER_AGENT = "AOSPA-Faye-Updater/1.0 (Linux; Android Rom Builder)"
VERSIONS_FILE = "versions.json"


def check_and_update(target_dir: str, force: bool = False):
    print("============================================================")
    print("  FOSS Apps Auto-Updater (F-Droid Tracker)")
    print(f"  Target Directory: {target_dir}")
    print("============================================================")

    os.makedirs(target_dir, exist_ok=True)
    versions_path = os.path.join(target_dir, VERSIONS_FILE)

    current_versions = {}
    if os.path.exists(versions_path):
        try:
            with open(versions_path, "r", encoding="utf-8") as f:
                current_versions = json.load(f)
        except Exception as e:
            print(f"[!] Warning: Could not read {VERSIONS_FILE}: {e}")

    updated_any = False

    for pkg_id, apk_name in TRACKED_APPS.items():
        apk_path = os.path.join(target_dir, apk_name)
        apk_exists = os.path.exists(apk_path)

        print(f"\n[•] Checking package: {pkg_id} ({apk_name})...")
        try:
            api_url = f"https://f-droid.org/api/v1/packages/{pkg_id}"
            req = urllib.request.Request(api_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            suggested_code = data.get("suggestedVersionCode")
            packages = data.get("packages", [])
            latest_pkg = next((p for p in packages if p.get("versionCode") == suggested_code), packages[0] if packages else None)
            version_name = latest_pkg.get("versionName", "unknown") if latest_pkg else "unknown"

            cached_code = current_versions.get(pkg_id, {}).get("versionCode")

            print(f"    Available on F-Droid: v{version_name} (code: {suggested_code})")
            print(f"    Local status:         {'present' if apk_exists else 'missing'} (cached code: {cached_code})")

            needs_download = force or (not apk_exists) or (cached_code != suggested_code)

            if not needs_download:
                print(f"    [✓] {apk_name} is already at the latest version.")
                continue

            download_url = f"https://f-droid.org/repo/{pkg_id}_{suggested_code}.apk"
            print(f"    [↓] Downloading updated APK: {download_url} ...")

            tmp_apk_path = apk_path + ".tmp"
            dl_req = urllib.request.Request(download_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(dl_req, timeout=60) as dl_resp, open(tmp_apk_path, "wb") as out_f:
                total_bytes = 0
                while True:
                    chunk = dl_resp.read(65536)
                    if not chunk:
                        break
                    out_f.write(chunk)
                    total_bytes += len(chunk)

            # Sanity check: Ensure valid APK (ZIP header starts with PK\x03\x04)
            with open(tmp_apk_path, "rb") as check_f:
                magic = check_f.read(4)
                if magic != b"PK\x03\x04":
                    raise ValueError(f"Downloaded file does not have valid APK/ZIP header (magic: {magic})")

            os.replace(tmp_apk_path, apk_path)
            print(f"    [✓] Successfully installed {apk_name} ({total_bytes / (1024*1024):.2f} MB)")

            current_versions[pkg_id] = {
                "versionName": version_name,
                "versionCode": suggested_code,
                "apk": apk_name,
            }
            updated_any = True

        except Exception as e:
            print(f"    [!] Warning: Failed to query/download {pkg_id}: {e}")
            if apk_exists:
                print(f"    [*] Keeping existing local {apk_name} without halting build.")
            else:
                print(f"    [!] Error: {apk_name} is missing and could not be downloaded.")

    for pkg_id, info in GITHUB_APPS.items():
        apk_name = info["apk"]
        repo = info["repo"]
        suffix = info["asset_suffix"]
        apk_path = os.path.join(target_dir, apk_name)
        apk_exists = os.path.exists(apk_path)

        print(f"\n[•] Checking GitHub release: {pkg_id} ({apk_name} from {repo})...")
        try:
            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            gh_headers = {"User-Agent": USER_AGENT}
            token = os.environ.get("GITHUB_TOKEN")
            if token:
                gh_headers["Authorization"] = f"token {token}"
            req = urllib.request.Request(api_url, headers=gh_headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                rel_data = json.loads(resp.read().decode("utf-8"))

            tag_name = rel_data.get("tag_name", "unknown")
            asset = next((a for a in rel_data.get("assets", []) if a.get("name", "").endswith(suffix)), None)
            if not asset:
                asset = next((a for a in rel_data.get("assets", []) if a.get("name", "").endswith(".apk")), None)

            if not asset:
                print(f"    [!] No suitable APK asset found for {pkg_id} in {tag_name}")
                continue

            download_url = asset["browser_download_url"]
            cached_ver = current_versions.get(pkg_id, {}).get("versionName")

            print(f"    Available on GitHub: {tag_name}")
            print(f"    Local status:        {'present' if apk_exists else 'missing'} (cached: {cached_ver})")

            needs_download = force or (not apk_exists) or (cached_ver != tag_name)
            if not needs_download:
                print(f"    [✓] {apk_name} is already at the latest release ({tag_name}).")
                continue

            print(f"    [↓] Downloading updated APK: {download_url} ...")
            tmp_apk_path = apk_path + ".tmp"
            dl_req = urllib.request.Request(download_url, headers=gh_headers)
            with urllib.request.urlopen(dl_req, timeout=60) as dl_resp, open(tmp_apk_path, "wb") as out_f:
                total_bytes = 0
                while True:
                    chunk = dl_resp.read(65536)
                    if not chunk:
                        break
                    out_f.write(chunk)
                    total_bytes += len(chunk)

            with open(tmp_apk_path, "rb") as check_f:
                magic = check_f.read(4)
                if magic != b"PK\x03\x04":
                    raise ValueError(f"Downloaded file is not a valid APK (magic: {magic})")

            os.replace(tmp_apk_path, apk_path)
            print(f"    [✓] Successfully installed {apk_name} ({total_bytes / (1024*1024):.2f} MB)")

            current_versions[pkg_id] = {
                "versionName": tag_name,
                "apk": apk_name,
            }
            updated_any = True
        except Exception as e:
            print(f"    [!] Warning: Failed to check/download {pkg_id} from GitHub: {e}")
            if apk_exists:
                print(f"    [*] Keeping existing local {apk_name} without halting build.")
            else:
                print(f"    [!] Error: {apk_name} is missing and could not be downloaded.")

    if updated_any:
        try:
            with open(versions_path, "w", encoding="utf-8") as f:
                json.dump(current_versions, f, indent=2)
            print(f"\n[✓] Updated version cache saved to {VERSIONS_FILE}")
        except Exception as e:
            print(f"[!] Warning: Could not save {VERSIONS_FILE}: {e}")

    print("\n============================================================")
    print("  [✓] FOSS Apps check completed!")
    print("============================================================\n")


def main():
    parser = argparse.ArgumentParser(description="Update default FOSS APKs from F-Droid for ROM build.")
    parser.add_argument("--target-dir", default=os.path.dirname(os.path.abspath(__file__)),
                        help="Target directory to store APKs (default: script directory)")
    parser.add_argument("--force", action="store_true", help="Force redownloading even if version matches")
    args = parser.parse_args()

    check_and_update(args.target_dir, args.force)


if __name__ == "__main__":
    main()
