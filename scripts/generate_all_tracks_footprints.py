"""
Generate multi-track footprint and coverage comparison GeoJSON for Sentinel-1.
Exports footprints for Track 92 (Descending), Track 19 (Descending), and Track 129 (Ascending).
"""

import os
import json
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
from shapely import wkt

def clean_footprint_wkt(fp_str):
    if not fp_str:
        return None
    try:
        wkt_str = fp_str.split(";")[-1].strip("'\" \t\r\n")
        return wkt.loads(wkt_str)
    except Exception:
        return None

# Load Mandals
with open("data/processed/boundaries/lower_godavari_mandals.geojson", "r", encoding="utf-8") as f:
    mandals_fc = json.load(f)

mandals_union = unary_union([shape(f["geometry"]) for f in mandals_fc["features"]])
total_mandals_area = mandals_union.area

# Load S1 Catalogue
with open("data/raw/sentinel1/sentinel1_scene_catalogue.json", "r", encoding="utf-8") as f:
    cat = json.load(f)

tracks = {
    92: {"name": "Track 92 (Descending) - June 8 & July 14", "pass": "Descending", "footprints": []},
    19: {"name": "Track 19 (Descending) - June 3 & June 15", "pass": "Descending", "footprints": []},
    129: {"name": "Track 129 (Ascending) - July 16", "pass": "Ascending", "footprints": []}
}

for grp in cat:
    for sc in cat[grp]:
        name = sc["name"]
        poly = clean_footprint_wkt(sc.get("footprint"))
        if not poly:
            continue
        parts = name.split("_")
        abs_orb = int(parts[6])
        rel_orb = ((abs_orb - 73) % 175) + 1
        if rel_orb in tracks:
            tracks[rel_orb]["footprints"].append(poly)

fc = {
    "type": "FeatureCollection",
    "features": []
}

for t_id, t_info in sorted(tracks.items()):
    u_poly = unary_union(t_info["footprints"])
    inter = u_poly.intersection(mandals_union)
    pct = (inter.area / total_mandals_area) * 100.0
    fc["features"].append({
        "type": "Feature",
        "properties": {
            "track_number": t_id,
            "track_name": t_info["name"],
            "pass_direction": t_info["pass"],
            "mandals_coverage_percentage": round(pct, 2),
            "area_covered_sq_deg": round(inter.area, 4)
        },
        "geometry": mapping(u_poly)
    })

out_file = os.path.join("data", "processed", "sentinel1", "sentinel1_all_tracks_coverage.geojson")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(fc, f, indent=2)

print(f"Generated multi-track comparison GeoJSON at: {out_file}")
for feat in fc["features"]:
    p = feat["properties"]
    print(f"  Track {p['track_number']} ({p['pass_direction']}): {p['mandals_coverage_percentage']}% of Lower Godavari Mandals")
