"""
Exact Geometric Intersection of Copernicus DEM Mosaic with 21 Mandals
"""
import json
from pathlib import Path
from shapely.geometry import shape, box, Polygon, MultiPolygon
import math

WORKSPACE = Path(r"C:\major project")
MANDALS_PATH = WORKSPACE / "data" / "processed" / "boundaries" / "lower_godavari_mandals.geojson"

with open(MANDALS_PATH, "r", encoding="utf-8") as f:
    mandals = json.load(f)["features"]

# DEM bounds: Lon [81.0, 83.0], Lat [16.0, 18.0]
dem_box = box(81.0, 16.0, 83.0, 18.0)

# Authalic area formula
R_AUTH = 6371007.1809
def ring_area(coords):
    if len(coords) < 3: return 0.0
    if coords[0] != coords[-1]: coords = list(coords) + [coords[0]]
    total = 0.0
    for i in range(len(coords) - 1):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[i+1]
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dlam = math.radians(lon2 - lon1)
        while dlam > math.pi: dlam -= 2 * math.pi
        while dlam < -math.pi: dlam += 2 * math.pi
        total += dlam * (math.sin(phi1) + math.sin(phi2)) / 2.0
    return abs(total) * (R_AUTH ** 2)

def poly_area(poly):
    if isinstance(poly, Polygon):
        ext = ring_area(poly.exterior.coords)
        inte = sum(ring_area(i.coords) for i in poly.interiors)
        return (ext - inte) / 1e6 # km2
    elif isinstance(poly, MultiPolygon):
        return sum(poly_area(p) for p in poly.geoms)
    return 0.0

print(f"{'Mandal':20s} | {'Total km2':10s} | {'DEM Covered km2':16s} | {'Missing km2':12s} | {'Coverage %':10s}")
print("-" * 75)

total_basin_area = 0.0
total_covered_area = 0.0

for feat in mandals:
    name = feat["properties"].get("NAME_3")
    g = shape(feat["geometry"])
    tot_a = poly_area(g)
    
    # Intersection with DEM box
    inter = g.intersection(dem_box)
    cov_a = poly_area(inter)
    miss_a = tot_a - cov_a
    pct = (cov_a / tot_a * 100) if tot_a > 0 else 0.0
    
    total_basin_area += tot_a
    total_covered_area += cov_a
    
    if miss_a > 0.01:
        print(f"{name:20s} | {tot_a:10.2f} | {cov_a:16.2f} | {miss_a:12.2f} | {pct:9.2f}% (GAP IDENTIFIED)")
    else:
        print(f"{name:20s} | {tot_a:10.2f} | {cov_a:16.2f} | {miss_a:12.2f} | {pct:9.2f}%")

total_miss = total_basin_area - total_covered_area
total_pct = (total_covered_area / total_basin_area * 100)

print("-" * 75)
print(f"{'BASIN TOTAL':20s} | {total_basin_area:10.2f} | {total_covered_area:16.2f} | {total_miss:12.2f} | {total_pct:9.2f}%")
