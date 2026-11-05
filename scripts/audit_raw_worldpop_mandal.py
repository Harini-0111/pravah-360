"""
Inspect raw full-India WorldPop raster for the 21 mandals
"""
import os
import json
import tifffile
import numpy as np
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

RAW_FILE = os.path.join("data", "raw", "population", "ind_ppp_2020_1km_Aggregated_UNadj.tif")
MANDALS_PATH = os.path.join("data", "processed", "boundaries", "lower_godavari_mandals.geojson")

with open(MANDALS_PATH, "r", encoding="utf-8") as f:
    mandals = json.load(f)["features"]
mandal_geoms = [(m["properties"].get("NAME_3"), shape(m["geometry"])) for m in mandals]
mandal_tree = STRtree([g for _, g in mandal_geoms])

with tifffile.TiffFile(RAW_FILE) as tif:
    page = tif.pages[0]
    data = page.asarray()
    tags = {tag.name: tag.value for tag in page.tags}

scale = tags.get("ModelPixelScaleTag", (0.0083333333, 0.0083333333, 0))
tiepoint = tags.get("ModelTiepointTag", (0, 0, 0, 68.1166667, 37.0833333, 0))

origin_x = tiepoint[3]
origin_y = tiepoint[4]
pixel_width = scale[0]
pixel_height = scale[1]

# Entire 21 mandals bounding box:
# Min Lon: 80.8550, Max Lon: 82.5953, Min Lat: 16.3101, Max Lat: 18.0057
min_col = int((80.85 - origin_x) / pixel_width)
max_col = int((82.60 - origin_x) / pixel_width) + 1
min_row = int((origin_y - 18.01) / pixel_height)
max_row = int((origin_y - 16.30) / pixel_height) + 1

print(f"Sub-window rows: {min_row} to {max_row} ({max_row - min_row} rows)")
print(f"Sub-window cols: {min_col} to {max_col} ({max_col - min_col} cols)")

sub_data = data[min_row:max_row, min_col:max_col]

# Check population by mandal
mandal_pop = {name: 0.0 for name, _ in mandal_geoms}
mandal_cells = {name: 0 for name, _ in mandal_geoms}
mandal_west_pop = {name: 0.0 for name, _ in mandal_geoms}

for r_idx in range(sub_data.shape[0]):
    row = min_row + r_idx
    lat = origin_y - (row + 0.5) * pixel_height
    for c_idx in range(sub_data.shape[1]):
        col = min_col + c_idx
        lon = origin_x + (col + 0.5) * pixel_width
        val = sub_data[r_idx, c_idx]
        if val < 0 or val > 1e6 or np.isnan(val):
            continue
        pt = Point(lon, lat)
        cands = mandal_tree.query(pt)
        for idx in cands:
            name, geom = mandal_geoms[idx]
            if geom.contains(pt):
                mandal_pop[name] += float(val)
                mandal_cells[name] += 1
                if lon < 81.0:
                    mandal_west_pop[name] += float(val)
                break

print("\n=== POPULATION FROM RAW FULL-INDIA WORLDPOP ===")
print(f"{'Mandal':20s} | {'Total Pop':11s} | {'Cells':6s} | {'Pop < 81.0E':12s} | {'Pct < 81.0E':11s}")
print("-" * 75)
total_all = 0.0
total_west = 0.0
for name, _ in mandal_geoms:
    tot = mandal_pop[name]
    west = mandal_west_pop[name]
    total_all += tot
    total_west += west
    pct_west = (west / tot * 100) if tot > 0 else 0.0
    print(f"{name:20s} | {tot:11,.0f} | {mandal_cells[name]:6d} | {west:12,.0f} | {pct_west:10.2f}%")

print("-" * 75)
print(f"{'TOTAL 21 MANDALS':20s} | {total_all:11,.0f} | {sum(mandal_cells.values()):6d} | {total_west:12,.0f} | {(total_west/total_all*100):10.2f}%")
