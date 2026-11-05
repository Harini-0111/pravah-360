"""
Monitor Earth Engine Export Task and Download Completed Tiles from Google Drive
================================================================================
Project: AI-Based Flood Risk, Impact Assessment and Emergency Decision Support
Study Area: Lower Godavari Basin (21 Mandals), Andhra Pradesh, India
Target Acquisition: Sentinel-1A Ascending Track 129 (July 16, 2022)
Phase: Phase 3.2B - Sentinel-1 Track 129 Export and Raster Validation
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from ee import oauth
import ee

TASK_ID = 'CBE724WRHLCB2F2YHZL6C6V5'
PROJECT_ID = 'silent-eye-430214-t0'
DEST_DIR = Path('data/processed/sentinel1/track129_20220716')
DEST_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_TILES = [
    's1a_t129_20220716_flood_peak_utm44n_10m-0000000000-0000000000.tif',
    's1a_t129_20220716_flood_peak_utm44n_10m-0000000000-0000010240.tif',
    's1a_t129_20220716_flood_peak_utm44n_10m-0000010240-0000000000.tif',
    's1a_t129_20220716_flood_peak_utm44n_10m-0000010240-0000010240.tif'
]

def get_access_token():
    cred_file = Path.home() / '.config' / 'earthengine' / 'credentials'
    with open(cred_file, 'r') as f:
        creds = json.load(f)

    data = urllib.parse.urlencode({
        'client_id': oauth.CLIENT_ID,
        'client_secret': oauth.CLIENT_SECRET,
        'refresh_token': creds['refresh_token'],
        'grant_type': 'refresh_token'
    }).encode()

    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())['access_token']

def check_task_status(task_id):
    ee.Initialize(project=PROJECT_ID)
    status_list = ee.data.getTaskStatus(task_id)
    if not status_list:
        return None
    return status_list[0]

def list_drive_files(access_token):
    q = "trashed = false and (name contains 's1a_t129_20220716_flood_peak_utm44n_10m' or name contains 'LowerGodavari')"
    url = 'https://www.googleapis.com/drive/v3/files?q=' + urllib.parse.quote(q) + '&fields=files(id,name,size,mimeType)'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode()).get('files', [])

def download_file_resumable(file_id, dest_path, target_size, max_retries=10):
    """Downloads or resumes a file from Google Drive using HTTP Range requests."""
    chunk_size = 1024 * 1024 * 8  # 8 MB chunks
    
    for attempt in range(1, max_retries + 1):
        try:
            token = get_access_token()
            existing_size = dest_path.stat().st_size if dest_path.exists() else 0
            
            if target_size > 0 and existing_size == target_size:
                print(f"[+] {dest_path.name} already complete ({existing_size / (1024*1024):.2f} MB).", flush=True)
                return True
                
            if existing_size > target_size and target_size > 0:
                print(f"[!] Warning: local file larger than target. Overwriting from start.", flush=True)
                existing_size = 0
                open_mode = 'wb'
            elif existing_size > 0:
                open_mode = 'ab'
            else:
                open_mode = 'wb'

            headers = {'Authorization': f'Bearer {token}'}
            if existing_size > 0:
                headers['Range'] = f'bytes={existing_size}-'
                print(f"[*] Resuming {dest_path.name} from byte {existing_size:,} ({existing_size / (1024*1024):.1f} MB / {target_size / (1024*1024):.1f} MB) [Attempt {attempt}]...", flush=True)
            else:
                print(f"[*] Downloading {dest_path.name} ({target_size / (1024*1024):.1f} MB) [Attempt {attempt}]...", flush=True)

            url = f'https://www.googleapis.com/drive/v3/files/{file_id}?alt=media'
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=45) as resp, open(dest_path, open_mode) as out_f:
                current = existing_size
                last_report = current
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    out_f.write(chunk)
                    out_f.flush()
                    current += len(chunk)
                    if current - last_report >= 64 * 1024 * 1024 or current == target_size:
                        pct = (current / target_size * 100.0) if target_size > 0 else 0.0
                        print(f"    [{dest_path.name}] {current / (1024*1024):.1f} MB / {target_size / (1024*1024):.1f} MB ({pct:.1f}%)", flush=True)
                        last_report = current

            final_size = dest_path.stat().st_size
            if target_size > 0 and final_size == target_size:
                print(f"[+] Saved {dest_path.name} ({final_size / (1024*1024):.2f} MB) successfully!\n", flush=True)
                return True
            else:
                print(f"[!] Size mismatch: got {final_size}, expected {target_size}. Retrying...", flush=True)
                time.sleep(3)
        except Exception as e:
            print(f"[!] Download attempt {attempt} failed: {e}. Retrying in 5 seconds...", flush=True)
            time.sleep(5)
            
    print(f"[x] Failed to download {dest_path.name} after {max_retries} attempts.", flush=True)
    return False

def monitor_and_download(task_id=TASK_ID, wait_for_completion=True, poll_interval=15):
    print("=" * 80, flush=True)
    print("SENTINEL-1 TRACK 129 EXPORT MONITOR & RESUMABLE DOWNLOADER", flush=True)
    print("=" * 80, flush=True)
    print(f"Task ID:    {task_id}", flush=True)
    print(f"Project ID: {PROJECT_ID}", flush=True)
    print(f"Dest Dir:   {DEST_DIR.resolve()}", flush=True)
    print("-" * 80, flush=True)

    while True:
        status = check_task_status(task_id)
        if not status:
            print("[!] Could not retrieve task status. Retrying...", flush=True)
            time.sleep(poll_interval)
            continue

        state = status.get('state', 'UNKNOWN')
        desc = status.get('description', '')
        print(f"[{time.strftime('%H:%M:%S')}] Task: {task_id} | State: {state}", flush=True)

        if state == 'FAILED':
            print(f"\n[!] Task failed! Error: {status.get('error_message')}", flush=True)
            sys.exit(1)
        elif state == 'CANCELLED':
            print("\n[!] Task was cancelled.", flush=True)
            sys.exit(1)
        elif state == 'COMPLETED':
            print(f"\n[+] Task COMPLETED successfully on Earth Engine servers!", flush=True)
            break
        elif not wait_for_completion:
            return state

        time.sleep(poll_interval)

    # Task is completed - download files
    print("\n[*] Querying Google Drive for exported tiles...", flush=True)
    tif_files = []
    for retry in range(15):
        token = get_access_token()
        files = list_drive_files(token)
        tif_files = [f for f in files if f.get('name', '').endswith('.tif')]
        print(f"[{time.strftime('%H:%M:%S')}] Found {len(tif_files)}/4 TIFF tile(s) in Drive...", flush=True)
        if len(tif_files) >= 4:
            break
        time.sleep(10)

    # Sort tiles in standard grid order: NW, NE, SW, SE
    def sort_key(f):
        fname = f.get('name', '')
        for idx, exp in enumerate(EXPECTED_TILES):
            if fname == exp:
                return idx
        return 99
    tif_files = sorted(tif_files, key=sort_key)

    for f in tif_files:
        sz = int(f.get('size', 0)) / (1024 * 1024)
        print(f"  - {f.get('name')} ({sz:.1f} MB, ID: {f.get('id')})", flush=True)

    downloaded = 0
    for f in tif_files:
        fname = f.get('name')
        fid = f.get('id')
        target_size = int(f.get('size', 0))
        out_path = DEST_DIR / fname
        ok = download_file_resumable(fid, out_path, target_size)
        if ok:
            downloaded += 1
        else:
            print(f"[!] Error downloading {fname}", flush=True)

    print(f"\n[+] Successfully verified/downloaded {downloaded}/{len(tif_files)} tiles to {DEST_DIR}", flush=True)
    return 'COMPLETED' if downloaded == len(tif_files) else 'INCOMPLETE'

if __name__ == '__main__':
    tid = sys.argv[1] if len(sys.argv) > 1 else TASK_ID
    monitor_and_download(tid)
