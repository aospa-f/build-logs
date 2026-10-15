#!/usr/bin/env python3
"""
MiXplorer & Official Addons Auto-Updater for AOSPA-Faye
Fetches the latest arm64 APKs directly from the developer's official Google Drive folder.
Drive Link: https://drive.google.com/drive/folders/1BfeK39boriHy-9q76eXLLqbCwfV17-Gv
"""

import os
import re
import sys
import http.cookiejar
import urllib.request
import urllib.parse

DRIVE_FOLDER_ID = "1BfeK39boriHy-9q76eXLLqbCwfV17-Gv"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = [('User-Agent', USER_AGENT)]

def fetch_folder_items(folder_id):
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    req = urllib.request.Request(url)
    try:
        html = opener.open(req).read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error accessing folder {folder_id}: {e}")
        return []
    
    unescaped = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), html)
    pattern = r'\[\"([A-Za-z0-9_-]{28,35})\",\[\"' + re.escape(folder_id) + r'\"\],\"([^\"]+)\"'
    items = re.findall(pattern, unescaped)
    return items

def download_file(file_id, dest_path):
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0"
    resp = opener.open(url)
    content = resp.read()
    
    # Check if download confirmation warning page
    if b'uc-download-link' in content or b'download-form' in content:
        html = content.decode('utf-8', errors='ignore')
        uuid_match = re.search(r'name=\"uuid\"\s+value=\"([^\"]+)\"', html)
        confirm_match = re.search(r'name=\"confirm\"\s+value=\"([^\"]+)\"', html)
        if uuid_match:
            uuid_val = uuid_match.group(1)
            confirm_val = confirm_match.group(1) if confirm_match else 't'
            download_url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0&confirm={confirm_val}&uuid={uuid_val}"
            resp = opener.open(download_url)
            content = resp.read()
            
    with open(dest_path, 'wb') as f:
        f.write(content)
    print(f"Successfully downloaded -> {dest_path} ({len(content)} bytes)")

def main():
    print(f"Checking Google Drive addons folder: {DRIVE_FOLDER_ID}...")
    subfolders = fetch_folder_items(DRIVE_FOLDER_ID)
    
    folder_map = {}
    for item_id, item_name in subfolders:
        folder_map[item_name] = item_id
        
    print(f"Found {len(subfolders)} subfolders:")
    for name, fid in folder_map.items():
        print(f"  - {name} ({fid})")
        
    mix_folder_id = None
    for name, fid in folder_map.items():
        if "mixplorer" in name.lower():
            mix_folder_id = fid
            print(f"Selected MiXplorer version folder: {name}")
            break
            
    archive_folder_id = folder_map.get("MiX Archive")
    image_folder_id = folder_map.get("MiX Image")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. MiXplorer (arm64)
    if mix_folder_id:
        items = fetch_folder_items(mix_folder_id)
        arm64_files = [item for item in items if "arm64" in item[1].lower()]
        if arm64_files:
            file_id, file_name = arm64_files[0]
            print(f"\nFound MiXplorer arm64: {file_name}")
            download_file(file_id, os.path.join(script_dir, "MiXplorer.apk"))
            
    # 2. MiXArchive (arm64)
    if archive_folder_id:
        items = fetch_folder_items(archive_folder_id)
        arm64_files = [item for item in items if "arm64" in item[1].lower()]
        if arm64_files:
            file_id, file_name = arm64_files[0]
            print(f"\nFound MiXArchive arm64: {file_name}")
            download_file(file_id, os.path.join(script_dir, "MiXArchive.apk"))

    # 3. MiXImage (arm64)
    if image_folder_id:
        items = fetch_folder_items(image_folder_id)
        arm64_files = [item for item in items if "arm64" in item[1].lower()]
        if arm64_files:
            file_id, file_name = arm64_files[0]
            print(f"\nFound MiXImage arm64: {file_name}")
            download_file(file_id, os.path.join(script_dir, "MiXImage.apk"))
            
    print("\nAll arm64 APKs are up to date.")

if __name__ == "__main__":
    main()
