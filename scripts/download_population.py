"""
Download WorldPop India population raster (2020 UN-adjusted) and clip to Lower Godavari Basin.
"""
import os
import requests
import tifffile
import numpy as np

RAW_DIR = os.path.join("data", "raw", "population")
PROC_DIR = os.path.join("data", "processed", "population")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)

WP_URL = "https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/2020/IND/ind_ppp_2020_1km_Aggregated_UNadj.tif"
RAW_FILE = os.path.join(RAW_DIR, "ind_ppp_2020_1km_Aggregated_UNadj.tif")

def download_worldpop():
    if os.path.exists(RAW_FILE) and os.path.getsize(RAW_FILE) > 10000000:
        print(f"Already downloaded: {RAW_FILE} ({os.path.getsize(RAW_FILE)} bytes)")
        return
    print(f"Downloading WorldPop India population raster from {WP_URL}...")
    resp = requests.get(WP_URL, stream=True, timeout=120)
    with open(RAW_FILE, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    print(f"Downloaded {RAW_FILE} ({os.path.getsize(RAW_FILE)} bytes)")

def clip_to_lower_godavari():
    with tifffile.TiffFile(RAW_FILE) as tif:
        page = tif.pages[0]
        data = page.asarray()
        tags = {tag.name: tag.value for tag in page.tags}
        
    print(f"Original shape: {data.shape}, dtype: {data.dtype}")
    # Extent tags
    scale = tags.get("ModelPixelScaleTag", (0.0083333333, 0.0083333333, 0))
    tiepoint = tags.get("ModelTiepointTag", (0, 0, 0, 68.1166667, 37.0833333, 0))
    
    origin_x = tiepoint[3]
    origin_y = tiepoint[4]
    pixel_width = scale[0]
    pixel_height = scale[1]
    
    # Study Area: min_lon=81.0, max_lon=82.8, min_lat=16.3, max_lat=17.9
    min_col = int((81.0 - origin_x) / pixel_width)
    max_col = int((82.8 - origin_x) / pixel_width)
    min_row = int((origin_y - 17.9) / pixel_height)
    max_row = int((origin_y - 16.3) / pixel_height)
    
    clipped = data[min_row:max_row, min_col:max_col].copy()
    valid_mask = (clipped >= 0) & (clipped < 1e6)
    total_est_pop = float(np.sum(clipped[valid_mask]))
    
    out_path = os.path.join(PROC_DIR, "worldpop_lower_godavari_2020.tif")
    tifffile.imwrite(out_path, clipped)
    
    summary_path = os.path.join(PROC_DIR, "population_exposure_baseline.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("WORLDPOP 2020 LOWER GODAVARI BASIN SUMMARY\n")
        f.write("=========================================\n")
        f.write(f"Source: WorldPop 2020 UN-adjusted 1km Population Grid (India)\n")
        f.write(f"Bounding Box: [16.3 N, 81.0 E] to [17.9 N, 82.8 E]\n")
        f.write(f"Grid dimensions: {clipped.shape[0]} rows x {clipped.shape[1]} cols\n")
        f.write(f"Total baseline population in Lower Godavari box: {total_est_pop:,.0f} persons\n")
        f.write(f"Max cell density: {np.nanmax(clipped[valid_mask]):,.1f} persons/km²\n")
        f.write(f"Mean density: {np.nanmean(clipped[valid_mask]):,.1f} persons/km²\n")
        f.write("\nNOTE: These demographic figures represent geospatial statistical population estimates. They must never be described as confirmed affected persons.\n")

    print(f"Clipped population raster saved: {out_path} (shape: {clipped.shape})")
    print(f"Baseline Lower Godavari population estimate: {total_est_pop:,.0f} persons")

if __name__ == "__main__":
    download_worldpop()
    clip_to_lower_godavari()
