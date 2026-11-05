"""
Inspect WorldPop raster and evaluate exact overlay mechanics
"""
import json
from pathlib import Path
import tifffile
import numpy as np
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

WORKSPACE = Path(r"C:\major project")
WP_PATH = WORKSPACE / "data" / "processed" / "population" / "worldpop_lower_godavari_2020.tif"
MANDALS_PATH = WORKSPACE / "data" / "processed" / "boundaries" / "lower_godavari_mandals.geojson"

# 1. Read metadata from tifffile
with tifffile.TiffFile(str(WP_PATH)) as tif:
    print("=== WORLDPOP TIFF METADATA ===")
    print("Series length:", len(tif.series))
    page = tif.pages[0]
    print("Shape:", page.shape)
    print("Dtype:", page.dtype)
    print("Axes:", page.axes)
    print("Tags:")
    for tag in page.tags:
        if tag.name in ("ModelPixelScaleTag", "ModelTiepointTag", "GeoKeyDirectoryTag", "GDAL_NODATA", "ImageDescription"):
            print(f"  {tag.name}: {tag.value}")

data = tifffile.imread(str(WP_PATH))
print(f"\nData Stats:")
print(f"Min: {np.nanmin(data)}, Max: {np.nanmax(data)}, Mean: {np.nanmean(data)}")
print(f"Total cells: {data.size}")
valid_mask = (data >= 0) & (data < 1e6) & (~np.isnan(data))
print(f"Valid cells (>=0 and <1e6): {np.sum(valid_mask)}")
print(f"Invalid / NoData cells: {np.sum(~valid_mask)}")
print(f"Sum of ALL valid cells in raw GeoTIFF: {np.sum(data[valid_mask]):,.2f}")

# 2. Check extent and resolution
# From ModelPixelScale and ModelTiepoint or dataset metadata
# Let's inspect GeoKeys if available, or examine metadata files
meta_path = WORKSPACE / "data" / "metadata" / "phase1_dataset_inventory.json"
if meta_path.exists():
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    print("\nPhase 1 Metadata for WorldPop:")
    for entry in meta:
        if "worldpop" in entry.get("file", "").lower():
            print(json.dumps(entry, indent=2))
