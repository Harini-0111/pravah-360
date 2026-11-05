"""
Audit uncovered DEM sliver (Lon < 81.0E)
"""
import json
from pathlib import Path
import tifffile
import numpy as np
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

WORKSPACE = Path(r"C:\major project")
MANDALS_PATH = WORKSPACE / "data" / "processed" / "boundaries" / "lower_godavari_mandals.geojson"
WP_PATH = WORKSPACE / "data" / "processed" / "population" / "worldpop_lower_godavari_2020.tif"
INFRA_DIR = WORKSPACE / "data" / "processed" / "infrastructure"

# Load mandals
with open(MANDALS_PATH, "r", encoding="utf-8") as f:
    mandals = json.load(f)["features"]
mandal_geoms = [(m["properties"].get("NAME_3"), shape(m["geometry"])) for m in mandals]
mandal_tree = STRtree([g for _, g in mandal_geoms])

# Inspect Chintalapudi bounds
chintala = [g for n, g in mandal_geoms if n == "Chintalapudi"][0]
print("Chintalapudi bounds:", chintala.bounds)
print(f"Min Lon: {chintala.bounds[0]:.4f}, Max Lon: {chintala.bounds[2]:.4f}")

# 1. WorldPop cells west of 81.0
wp_data = tifffile.imread(str(WP_PATH))
rows, cols = wp_data.shape
dlat = 1.6 / rows
dlon = 1.8 / cols

wp_west_cells = 0
wp_west_pop = 0.0
wp_chintala_total_pop = 0.0
wp_chintala_total_cells = 0

for r in range(rows):
    lat = 17.9 - (r + 0.5) * dlat
    for c in range(cols):
        val = wp_data[r, c]
        if val < 0 or val > 1e6:
            continue
        lon = 81.0 + (c + 0.5) * dlon
        # Note: WP_extent is 81.0 to 82.8!
        # Wait! Is the WorldPop raster extent itself starting at 81.0E?!

print(f"WorldPop raster extent: does it start at 81.0E?")
print(f"Let's check if WorldPop raster even covers < 81.0E!")
