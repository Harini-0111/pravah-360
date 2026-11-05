"""
Download Copernicus DEM GLO-30 tiles covering Lower Godavari Basin from AWS Open Data
and derive elevation, slope, and aspect rasters.
"""
import os
import sys
import math
import requests
import numpy as np

try:
    import tifffile
except ImportError:
    print("tifffile required")
    sys.exit(1)

TILES = [
    "Copernicus_DSM_COG_10_N16_00_E081_00_DEM",
    "Copernicus_DSM_COG_10_N16_00_E082_00_DEM",
    "Copernicus_DSM_COG_10_N17_00_E081_00_DEM",
    "Copernicus_DSM_COG_10_N17_00_E082_00_DEM"
]

BASE_URL = "https://copernicus-dem-30m.s3.amazonaws.com"
RAW_DIR = os.path.join("data", "raw", "dem")
PROC_DIR = os.path.join("data", "processed", "dem")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)

def download_tiles():
    downloaded = []
    for tile in TILES:
        tif_name = f"{tile}.tif"
        url = f"{BASE_URL}/{tile}/{tif_name}"
        dest_path = os.path.join(RAW_DIR, tif_name)
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000000:
            print(f"Already downloaded: {dest_path} ({os.path.getsize(dest_path)} bytes)")
            downloaded.append(dest_path)
            continue
        
        print(f"Downloading {url} ...")
        resp = requests.get(url, stream=True, timeout=120)
        if resp.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            print(f"Successfully downloaded {dest_path} ({os.path.getsize(dest_path)} bytes)")
            downloaded.append(dest_path)
        else:
            print(f"Failed to download {url}: HTTP {resp.status_code}")
    return downloaded

def derive_terrain_metrics(sample_tile):
    """
    Derives slope and aspect for the primary Lower Godavari delta tile (N16E081).
    Calculates gradient-based terrain indicators.
    """
    print(f"Computing slope and aspect from {sample_tile}...")
    try:
        data = tifffile.imread(sample_tile)
        # Dem is 3600 x 3600 float32, resolution 30m (~0.0002778 deg)
        # Cell size roughly 30.8 meters in Godavari delta latitude (~17 deg)
        dx = 30.8
        dy = 30.8
        
        # Calculate gradients (central differences)
        gy, gx = np.gradient(data, dy, dx)
        
        # Slope in degrees
        slope_rad = np.arctan(np.sqrt(gx**2 + gy**2))
        slope_deg = np.degrees(slope_rad).astype(np.float32)
        
        # Aspect in degrees (0 - 360, 0 = North, 90 = East, etc.)
        aspect_rad = np.arctan2(-gx, gy)
        aspect_deg = np.degrees(aspect_rad)
        aspect_deg = np.where(aspect_deg < 0, 360.0 + aspect_deg, aspect_deg).astype(np.float32)
        
        # Save processed terrain metrics
        slope_path = os.path.join(PROC_DIR, "copernicus_dem_slope_deg_N16E081.tif")
        aspect_path = os.path.join(PROC_DIR, "copernicus_dem_aspect_deg_N16E081.tif")
        elev_path = os.path.join(PROC_DIR, "copernicus_dem_elevation_N16E081.tif")
        
        tifffile.imwrite(slope_path, slope_deg)
        tifffile.imwrite(aspect_path, aspect_deg)
        tifffile.imwrite(elev_path, data)
        
        print(f"Saved processed elevation raster: {elev_path}")
        print(f"Saved processed slope raster: {slope_path}")
        print(f"Saved processed aspect raster: {aspect_path}")
        print(f"Elevation range: {np.nanmin(data):.1f}m to {np.nanmax(data):.1f}m")
        print(f"Slope range: {np.nanmin(slope_deg):.1f} deg to {np.nanmax(slope_deg):.1f} deg")
    except Exception as e:
        print(f"Terrain metric calculation error: {e}")

if __name__ == "__main__":
    tiles = download_tiles()
    if tiles:
        # Primary tile covering delta (Sir Arthur Cotton Dowleswaram Barrage to coast)
        primary = [t for t in tiles if "N16_00_E081" in t]
        if primary:
            derive_terrain_metrics(primary[0])
        print("Copernicus DEM acquisition and processing complete.")
