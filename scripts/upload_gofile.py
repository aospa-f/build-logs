#!/usr/bin/env python3
import sys, os, urllib.request, json, subprocess

def upload_to_gofile(filepath):
    if not os.path.exists(filepath):
        print(f'File not found: {filepath}')
        return None
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f'Uploading {filepath} ({size_mb:.2f} MB) to GoFile...')
    try:
        req = urllib.request.Request('https://api.gofile.io/servers', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            servers = data.get('data', {}).get('servers', [])
            server = servers[0]['name'] if servers else 'store1'
    except Exception as e:
        print(f'Failed to get GoFile server: {e}')
        server = 'store1'
    
    token = ''
    try:
        acc_req = urllib.request.Request('https://api.gofile.io/accounts', data=b'', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(acc_req) as resp:
            acc_data = json.loads(resp.read().decode())
            token = acc_data.get('data', {}).get('token', '')
    except Exception as e:
        print(f'Failed to get guest token: {e}')

    cmd = ['curl', '-s', '-H', f'Authorization: Bearer {token}', '-F', f'file=@{filepath}', f'https://{server}.gofile.io/contents/uploadfile']
    try:
        res = subprocess.check_output(cmd)
        res_data = json.loads(res.decode())
        if res_data.get('status') == 'ok':
            url = res_data['data']['downloadPage']
            print(f'DOWNLOAD_URL: {url}')
            return url
        else:
            print(f'Upload failed: {res_data}')
            return None
    except Exception as e:
        print(f'Curl execution failed: {e}')
        return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        upload_to_gofile(sys.argv[1])
    else:
        print('Usage: upload_gofile.py <filepath>')
