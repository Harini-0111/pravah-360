"""
Sentinel-1A Track 129 Export Dispatcher (Google Earth Engine Python API)
========================================================================
Project: AI-Based Flood Risk, Impact Assessment and Emergency Decision Support
Study Area: Lower Godavari Basin (21 Mandals), Andhra Pradesh, India
Target Acquisition: Sentinel-1A Ascending Track 129 (July 16, 2022)
Phase: Phase 3.2B - Sentinel-1 Track 129 Export and Raster Validation

Usage:
    .venv/Scripts/python.exe scripts/gee/dispatch_sentinel1_track129_export.py [--project <PROJECT_ID>] [--status <TASK_ID>]
"""

import os
import sys
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# CDSE Product IDs (ESA package manifest CRC):
CDSE_IMAGE_IDS = [
    'S1A_IW_GRDH_1SDV_20220716T124350_20220716T124419_044126_05445C_C3FF',
    'S1A_IW_GRDH_1SDV_20220716T124419_20220716T124444_044126_05445C_33F9'
]

# Google Earth Engine Catalog Asset IDs for the identical Datatake 05445C / Orbit 044126 acquisition:
GEE_IMAGE_IDS = [
    'S1A_IW_GRDH_1SDV_20220716T124350_20220716T124419_044126_05445C_8156',
    'S1A_IW_GRDH_1SDV_20220716T124419_20220716T124444_044126_05445C_E87B'
]

TARGET_IMAGE_IDS = GEE_IMAGE_IDS

EXPORT_CONFIG = {
    'crs': 'EPSG:32644',
    'scale': 10,
    'folder': 'LowerGodavari_Floods_2022',
    'fileNamePrefix': 's1a_t129_20220716_flood_peak_utm44n_10m',
    'description': 'Sentinel1_Track129_LowerGodavari_FloodPeak_20220716_UTM44N_10m',
    'fileDimensions': [10240, 10240],
    'maxPixels': 1e9,
    'nodata': -9999.0
}

def check_task_status(task_id, project=None):
    import ee
    try:
        ee.Initialize(project=project)
        status = ee.data.getTaskStatus(task_id)
        print(f"Task ID: {task_id}")
        print(f"State: {status[0]['state']}")
        print(f"Description: {status[0].get('description')}")
        if 'error_message' in status[0]:
            print(f"Error: {status[0]['error_message']}")
        return status[0]
    except Exception as e:
        print(f"Failed to check task status: {e}")
        return None

def dispatch_export(project_id=None):
    import ee
    
    # 1. Determine project ID
    proj = project_id or os.getenv('EARTHENGINE_PROJECT')
    if not proj or proj == 'your-gee-project-id':
        print("\n" + "="*80)
        print("[!] ERROR: No valid Earth Engine / Google Cloud Project ID configured.")
        print("="*80)
        print("To trigger export via Python API, provide a valid project ID:")
        print("  1. Pass as flag:  .venv\\Scripts\\python.exe scripts/gee/dispatch_sentinel1_track129_export.py --project <YOUR_PROJECT_ID>")
        print("  2. Or set in .env: EARTHENGINE_PROJECT=<YOUR_PROJECT_ID>")
        print("\nAlternatively, run the export directly in Google Earth Engine Code Editor:")
        print("  1. Open https://code.earthengine.google.com/")
        print("  2. Paste contents of scripts/gee/gee_sentinel1_track129_export_config.js")
        print("  3. Set RUN_EXPORT = true; on line 20")
        print("  4. Click 'Run' at top, then click 'Run' in the 'Tasks' tab on the right.")
        print("  5. The 4 GeoTIFF tiles will export to Google Drive folder 'LowerGodavari_Floods_2022'.")
        print("="*80 + "\n")
        sys.exit(1)

    print(f"[*] Initializing Earth Engine with project: '{proj}'...")
    try:
        ee.Initialize(project=proj)
        print("[+] Earth Engine initialized successfully.")
    except Exception as e:
        print(f"[!] Authentication/Initialization failed: {e}")
        print("Please verify your Google Cloud project permissions or re-authenticate using `earthengine authenticate`.")
        sys.exit(1)

    # 2. Build collection
    print("[*] Assembling Sentinel-1A Track 129 collection for July 16, 2022...")
    s1_col = (ee.ImageCollection('COPERNICUS/S1_GRD')
              .filter(ee.Filter.inList('system:index', TARGET_IMAGE_IDS))
              .filterDate('2022-07-16T00:00:00', '2022-07-16T23:59:59')
              .filter(ee.Filter.eq('instrumentMode', 'IW'))
              .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
              .filter(ee.Filter.eq('relativeOrbitNumber_start', 129))
              .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
              .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')))

    count = s1_col.size().getInfo()
    print(f"[+] Found {count} matching granules in collection (Expected: 2).")
    if count != 2:
        print(f"[!] ERROR: Expected exactly 2 granules, but found {count}. Aborting for safety.")
        sys.exit(1)

    # 3. Define study area bbox
    study_area_bbox = ee.Geometry.Polygon([
        [[80.8550, 16.3101],
         [82.5953, 16.3101],
         [82.5953, 18.0057],
         [80.8550, 18.0057],
         [80.8550, 16.3101]]
    ], None, False)

    # 4. Prepare mosaic with uniform Float32 precision and NoData sentinel
    # Note: In COPERNICUS/S1_GRD, VV/VH are double and angle is float.
    # Casting to float satisfies the requirement: 'Data type: Float32'.
    s1_selected = s1_col.select(['VV', 'VH', 'angle'])
    s1_mosaic = s1_selected.mosaic().clip(study_area_bbox)
    export_image = s1_mosaic.toFloat().unmask(EXPORT_CONFIG['nodata']).toFloat()

    # 5. Create export task
    print("[*] Creating Earth Engine export task to Google Drive...")
    task = ee.batch.Export.image.toDrive(
        image=export_image,
        description=EXPORT_CONFIG['description'],
        folder=EXPORT_CONFIG['folder'],
        fileNamePrefix=EXPORT_CONFIG['fileNamePrefix'],
        region=study_area_bbox,
        scale=EXPORT_CONFIG['scale'],
        crs=EXPORT_CONFIG['crs'],
        maxPixels=int(EXPORT_CONFIG['maxPixels']),
        fileDimensions=EXPORT_CONFIG['fileDimensions'],
        formatOptions={'cloudOptimized': True}
    )

    task.start()
    task_id = task.id
    print(f"\n[+] EXPORT TASK DISPATCHED SUCCESSFULLY!")
    print(f"    Task ID:     {task_id}")
    print(f"    Description: {EXPORT_CONFIG['description']}")
    print(f"    Drive Folder:{EXPORT_CONFIG['folder']}")
    print(f"    Prefix:      {EXPORT_CONFIG['fileNamePrefix']}")
    print(f"    CRS / Scale: {EXPORT_CONFIG['crs']} @ {EXPORT_CONFIG['scale']}m")
    print(f"    Tiles:       4 GeoTIFF sub-tiles (fileDimensions: [10240, 10240])")
    print("\nMonitor progress with:")
    print(f"    .venv\\Scripts\\python.exe scripts/gee/dispatch_sentinel1_track129_export.py --status {task_id}")
    return task_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dispatch Sentinel-1 Track 129 GEE Export")
    parser.add_argument('--project', type=str, help="Google Cloud / Earth Engine Project ID")
    parser.add_argument('--status', type=str, help="Check status of a specific task ID")
    args = parser.parse_args()

    if args.status:
        check_task_status(args.status, project=args.project)
    else:
        dispatch_export(project_id=args.project)
