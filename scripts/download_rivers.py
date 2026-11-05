"""
Download and extract HydroSHEDS HydroRIVERS for the Godavari Basin and Lower Godavari study area.
Source: WWF HydroSHEDS HydroRIVERS v1.0 Asia.
"""
import os
import zipfile
import requests
import json

RAW_DIR = os.path.join("data", "raw", "rivers")
PROC_DIR = os.path.join("data", "processed", "rivers")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)

HYDRORIVERS_URL = "https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_as_shp.zip"
ZIP_PATH = os.path.join(RAW_DIR, "HydroRIVERS_v10_as_shp.zip")

def download_hydrorivers():
    if os.path.exists(ZIP_PATH) and os.path.getsize(ZIP_PATH) > 50000000:
        print(f"Already downloaded: {ZIP_PATH} ({os.path.getsize(ZIP_PATH)} bytes)")
        return
    print(f"Downloading HydroRIVERS Asia dataset ({HYDRORIVERS_URL})...")
    resp = requests.get(HYDRORIVERS_URL, stream=True, timeout=180)
    with open(ZIP_PATH, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    print(f"Downloaded {ZIP_PATH} ({os.path.getsize(ZIP_PATH)} bytes)")

def extract_metadata():
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        files = z.namelist()
        print(f"Archive contents: {files}")
        # Extract files to raw directory
        z.extractall(RAW_DIR)
    print(f"Extracted HydroRIVERS files to {RAW_DIR}")

if __name__ == "__main__":
    download_hydrorivers()
    extract_metadata()
