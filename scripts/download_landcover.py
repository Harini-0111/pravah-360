"""
Download ESA WorldCover 10m 2021 v200 tile covering Lower Godavari Basin and clip to study extent.
"""
import os
import requests
import tifffile
import numpy as np

RAW_DIR = os.path.join("data", "raw", "landcover")
PROC_DIR = os.path.join("data", "processed", "landcover")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)

# Tile N15E081 covers 15°N to 18°N, 81°E to 84°E (3 deg x 3 deg at 10m resolution)
WC_URL = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N15E081_Map.tif"
RAW_FILE = os.path.join(RAW_DIR, "ESA_WorldCover_10m_2021_v200_N15E081_Map.tif")

CLASS_NAMES = {
    10: "Tree cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare / sparse vegetation",
    70: "Snow and ice",
    80: "Permanent water bodies",
    90: "Herbaceous wetland",
    95: "Mangroves",
    100: "Moss and lichen"
}

def download_worldcover():
    if os.path.exists(RAW_FILE) and os.path.getsize(RAW_FILE) > 30000000:
        print(f"Already downloaded: {RAW_FILE} ({os.path.getsize(RAW_FILE)} bytes)")
        return
    print(f"Downloading ESA WorldCover 10m tile from {WC_URL}...")
    resp = requests.get(WC_URL, stream=True, timeout=180)
    with open(RAW_FILE, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    print(f"Downloaded {RAW_FILE} ({os.path.getsize(RAW_FILE)} bytes)")

def process_and_summarize():
    with tifffile.TiffFile(RAW_FILE) as tif:
        page = tif.pages[0]
        data = page.asarray()
        tags = {tag.name: tag.value for tag in page.tags}
        
    print(f"WorldCover tile shape: {data.shape}, dtype: {data.dtype}")
    # Tile spans Lat 18.0N down to 15.0N, Lon 81.0E to 84.0E
    # Dimensions: 36000 x 36000 pixels (10m = 0.0000833333 deg)
    scale = tags.get("ModelPixelScaleTag", (8.333333333333333e-05, 8.333333333333333e-05, 0))
    tiepoint = tags.get("ModelTiepointTag", (0, 0, 0, 81.0, 18.0, 0))
    
    origin_x = tiepoint[3]
    origin_y = tiepoint[4]
    pw = scale[0]
    ph = scale[1]
    
    # Sub-sample / clip study area: 16.3N to 17.9N, 81.0E to 82.8E
    min_col = int((81.0 - origin_x) / pw)
    max_col = int((82.8 - origin_x) / pw)
    min_row = int((origin_y - 17.9) / ph)
    max_row = int((origin_y - 16.3) / ph)
    
    # Extract clipped array
    clipped = data[min_row:max_row, min_col:max_col]
    print(f"Clipped grid shape: {clipped.shape}")
    
    # Downsample by factor of 5 to create standard 50m analysis raster
    # (keeps file compact and performant while preserving spatial features)
    sub = clipped[::5, ::5].copy()
    out_path = os.path.join(PROC_DIR, "esa_worldcover_lower_godavari_50m.tif")
    tifffile.imwrite(out_path, sub)
    print(f"Saved processed land cover raster: {out_path} (shape: {sub.shape})")
    
    # Class distribution
    unique, counts = np.unique(sub, return_counts=True)
    total_pixels = sub.size
    
    summary_path = os.path.join(PROC_DIR, "landcover_class_distribution.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("ESA WORLDCOVER 2021 v200 - LOWER GODAVARI BASIN DISTRIBUTION\n")
        f.write("=============================================================\n")
        f.write(f"Tile: N15E081 (15N-18N, 81E-84E)\n")
        f.write(f"Study bounds: [16.3 N, 81.0 E] to [17.9 N, 82.8 E]\n")
        f.write(f"Total sampled pixels: {total_pixels:,}\n\n")
        for u, c in zip(unique, counts):
            name = CLASS_NAMES.get(int(u), f"Unknown ({u})")
            pct = (c / total_pixels) * 100
            f.write(f"Class {u:3d} ({name:25s}): {c:8,d} pixels ({pct:5.2f}%)\n")
            
    print(f"Land cover class summary saved: {summary_path}")

if __name__ == "__main__":
    download_worldcover()
    process_and_summarize()
