"""
Detailed Spatial Coverage Verification for Track 92 (June 8 & July 14).
Evaluates actual spatial intersections with the 21 Lower Godavari Mandals.
Generates coverage GeoJSON files for visualization.
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

# Load Study Bounding Box
STUDY_BBOX = {"min_lon": 81.0, "min_lat": 16.3, "max_lon": 82.8, "max_lat": 17.9}
bbox_geom = box(STUDY_BBOX["min_lon"], STUDY_BBOX["min_lat"], STUDY_BBOX["max_lon"], STUDY_BBOX["max_lat"])

# Load Mandals GeoJSON
with open("data/processed/boundaries/lower_godavari_mandals.geojson", "r", encoding="utf-8") as f:
    mandals_fc = json.load(f)

mandals_dict = {}
mandal_geoms = []
for feat in mandals_fc["features"]:
    name = feat["properties"].get("NAME_3") or feat["properties"].get("mandal")
    geom = shape(feat["geometry"])
    mandals_dict[name] = geom
    mandal_geoms.append(geom)

mandals_union = unary_union(mandal_geoms)
total_mandals_area = mandals_union.area

# Load S1 Catalogue
with open("data/raw/sentinel1/sentinel1_scene_catalogue.json", "r", encoding="utf-8") as f:
    cat = json.load(f)

# Extract footprints for June 8 and July 14 (Track 92)
footprints_june08 = []
footprints_july14 = []
footprints_july16 = []
footprints_june15 = []

for grp in cat:
    for sc in cat[grp]:
        name = sc["name"]
        poly = clean_footprint_wkt(sc.get("footprint"))
        if not poly:
            continue
        if "20220608" in name and poly not in footprints_june08:
            footprints_june08.append(poly)
        elif "20220714" in name and poly not in footprints_july14:
            footprints_july14.append(poly)
        elif "20220716" in name and poly not in footprints_july16:
            footprints_july16.append(poly)
        elif "20220615" in name and poly not in footprints_june15:
            footprints_june15.append(poly)

u_june08 = unary_union(footprints_june08)
u_july14 = unary_union(footprints_july14)
u_july16 = unary_union(footprints_july16)
u_june15 = unary_union(footprints_june15)

# 1. Bounding box coverage
cov_bbox_june08 = (u_june08.intersection(bbox_geom).area / bbox_geom.area) * 100
cov_bbox_july14 = (u_july14.intersection(bbox_geom).area / bbox_geom.area) * 100
common_bbox_track92 = u_june08.intersection(u_july14).intersection(bbox_geom)
cov_bbox_common = (common_bbox_track92.area / bbox_geom.area) * 100

# 2. Actual Mandals coverage
inter_m_june08 = u_june08.intersection(mandals_union)
inter_m_july14 = u_july14.intersection(mandals_union)
common_mandals_track92 = u_june08.intersection(u_july14).intersection(mandals_union)

cov_m_june08 = (inter_m_june08.area / total_mandals_area) * 100
cov_m_july14 = (inter_m_july14.area / total_mandals_area) * 100
cov_m_common = (common_mandals_track92.area / total_mandals_area) * 100

print("=== SPATIAL COVERAGE AUDIT (TRACK 92) ===")
print(f"Study Area Bounding Box: {bbox_geom.area:.3f} deg2")
print(f"Mandals Polygon Union:   {total_mandals_area:.3f} deg2")
print(f"June 08 BBox Coverage:   {cov_bbox_june08:.2f}% | Mandals Union Coverage: {cov_m_june08:.2f}%")
print(f"July 14 BBox Coverage:   {cov_bbox_july14:.2f}% | Mandals Union Coverage: {cov_m_july14:.2f}%")
print(f"Common Track 92 Coverage: BBox {cov_bbox_common:.2f}% | Mandals Union {cov_m_common:.2f}%")

# Mandal-by-Mandal analysis for Track 92
print("\n=== MANDAL-BY-MANDAL COVERAGE (TRACK 92 COMMON FOOTPRINT) ===")
covered_mandals = []
partial_mandals = []
uncovered_mandals = []

mandal_coverage_stats = {}
for name, m_poly in sorted(mandals_dict.items()):
    cov_area = common_mandals_track92.intersection(m_poly).area
    pct = (cov_area / m_poly.area) * 100.0
    mandal_coverage_stats[name] = pct
    if pct >= 95.0:
        covered_mandals.append((name, pct))
    elif pct > 5.0:
        partial_mandals.append((name, pct))
    else:
        uncovered_mandals.append((name, pct))

print(f"Fully Covered Mandals (>=95%): {len(covered_mandals)}")
for n, p in covered_mandals:
    print(f"  - {n}: {p:.1f}%")

print(f"\nPartially Covered Mandals (5% - 95%): {len(partial_mandals)}")
for n, p in partial_mandals:
    print(f"  - {n}: {p:.1f}%")

print(f"\nUncovered / Minimal Mandals (<5%): {len(uncovered_mandals)}")
for n, p in uncovered_mandals:
    print(f"  - {n}: {p:.1f}%")

# Coverage with July 16 (Track 129 Ascending)
inter_m_july16 = u_july16.intersection(mandals_union)
cov_m_july16 = (inter_m_july16.area / total_mandals_area) * 100
combined_j14_j16 = unary_union([u_july14, u_july16]).intersection(mandals_union)
cov_combined = (combined_j14_j16.area / total_mandals_area) * 100

print("\n=== COMPLEMENTARY TRACK 129 (JULY 16) COVERAGE ===")
print(f"July 16 (Track 129) Mandals Coverage: {cov_m_july16:.2f}%")
print(f"Combined July 14 (Trk 92) + July 16 (Trk 129) Coverage: {cov_combined:.2f}%")

# Coverage with Track 19 (June 3 / June 15)
inter_m_june15 = u_june15.intersection(mandals_union)
cov_m_june15 = (inter_m_june15.area / total_mandals_area) * 100
print(f"Track 19 (June 15) Mandals Coverage: {cov_m_june15:.2f}%")

# Generate Coverage GeoJSON Files
out_dir = os.path.join("data", "processed", "sentinel1")
os.makedirs(out_dir, exist_ok=True)

# 1. Track 92 Common Footprint
fc_t92 = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Track 92 Common Footprint (June 8 & July 14)",
                "relative_orbit": 92,
                "pass": "Descending",
                "coverage_mandals_pct": round(cov_m_common, 2)
            },
            "geometry": mapping(common_mandals_track92)
        }
    ]
}
with open(os.path.join(out_dir, "coverage_track92_mandals.geojson"), "w", encoding="utf-8") as f:
    json.dump(fc_t92, f, indent=2)

# 2. Mandal coverage breakdown GeoJSON
fc_mandals_eval = {
    "type": "FeatureCollection",
    "features": []
}
for feat in mandals_fc["features"]:
    name = feat["properties"].get("NAME_3") or feat["properties"].get("mandal")
    pct = mandal_coverage_stats.get(name, 0.0)
    category = "Fully Covered" if pct >= 95 else ("Partially Covered" if pct > 5 else "Uncovered")
    fc_mandals_eval["features"].append({
        "type": "Feature",
        "properties": {
            **feat["properties"],
            "track92_coverage_pct": round(pct, 2),
            "coverage_category": category
        },
        "geometry": feat["geometry"]
    })

with open(os.path.join(out_dir, "mandals_track92_coverage_status.geojson"), "w", encoding="utf-8") as f:
    json.dump(fc_mandals_eval, f, indent=2)

print(f"\nSaved coverage GeoJSON files to {out_dir}:")
print("  - coverage_track92_mandals.geojson")
print("  - mandals_track92_coverage_status.geojson")
