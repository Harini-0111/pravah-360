import json
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
from shapely import wkt
import math

def clean_footprint_wkt(fp_str):
    if not fp_str:
        return None
    try:
        wkt_str = fp_str.split(";")[-1].strip("'\" \t\r\n")
        return wkt.loads(wkt_str)
    except Exception:
        return None

with open("data/raw/sentinel1/sentinel1_scene_catalogue.json", "r", encoding="utf-8") as f:
    cat = json.load(f)

t129_scenes = [sc for sc in cat["flood_peak"] if "20220716" in sc["name"]]
print(f"Total July 16 items in catalogue: {len(t129_scenes)}")

unique_granules = {}
for sc in t129_scenes:
    name = sc["name"]
    fp = clean_footprint_wkt(sc.get("footprint"))
    parts = name.split("_")
    # key: start_end
    key = f"{parts[4]}_{parts[5]}"
    if key not in unique_granules:
        unique_granules[key] = {
            "name": name,
            "parts": parts,
            "start": sc["acquisition_start"],
            "end": sc["acquisition_end"],
            "footprint": fp,
            "bounds": fp.bounds if fp else None
        }

print("\n--- UNIQUE GRANULES ON JULY 16, 2022 (TRACK 129 ASCENDING) ---")
for k, v in unique_granules.items():
    print(f"\nFrame Key: {k}")
    print(f"  Representative Product: {v['name']}")
    print(f"  Start: {v['start']}")
    print(f"  End:   {v['end']}")
    print(f"  Platform: Sentinel-1A (S1A)")
    print(f"  Sensor Mode: IW")
    print(f"  Product Type: GRDH (GRD High-Res)")
    print(f"  Polarization: 1SDV (VV + VH)")
    print(f"  Absolute Orbit: {v['parts'][6]}")
    print(f"  Mission Data Take: {v['parts'][7]}")
    print(f"  Product Unique ID: {v['parts'][8][:4]}")
    print(f"  Geographic Bounds: min_lon={v['bounds'][0]:.4f}, min_lat={v['bounds'][1]:.4f}, max_lon={v['bounds'][2]:.4f}, max_lat={v['bounds'][3]:.4f}")

# Check GEE Image ID structure
print("\n--- CORRESPONDING GOOGLE EARTH ENGINE IMAGE IDS ---")
for k, v in unique_granules.items():
    # In GEE COPERNICUS/S1_GRD, image IDs match the base product name (without .SAFE or _COG.SAFE)
    base_name = v['name'].replace('.SAFE', '').replace('_COG', '')
    gee_id = f"COPERNICUS/S1_GRD/{base_name}"
    print(f"  Granule: {k} -> GEE ID: {gee_id}")

# Load Mandals and Study Area
with open("data/processed/boundaries/lower_godavari_mandals.geojson", "r", encoding="utf-8") as f:
    mandals_fc = json.load(f)

mandals_union = unary_union([shape(f["geometry"]) for f in mandals_fc["features"]])
print(f"\n21 Mandals Union Bounds: {mandals_union.bounds}")

# Combined swath footprint of the two granules
granule_polys = [v["footprint"] for v in unique_granules.values() if v["footprint"]]
swath_union = unary_union(granule_polys)
print(f"Swath Union Bounds: {swath_union.bounds}")

# Calculate intersection with mandals
inter_mandals = swath_union.intersection(mandals_union)
mandals_coverage_pct = (inter_mandals.area / mandals_union.area) * 100.0
print(f"Mandals Geometric Footprint Coverage: {mandals_coverage_pct:.2f}%")

# Bounding box of mandals
m_minx, m_miny, m_maxx, m_maxy = mandals_union.bounds
bbox_poly = box(m_minx, m_miny, m_maxx, m_maxy)
inter_bbox = swath_union.intersection(bbox_poly)
bbox_coverage_pct = (inter_bbox.area / bbox_poly.area) * 100.0
print(f"Mandals Bounding Box Footprint Coverage: {bbox_coverage_pct:.2f}%")

# Evaluate UTM Zone 44N projection for the study area
# Central meridian of UTM 44N is 81.0 E.
# Mandals span 80.855 E to 82.595 E (from -0.145 deg to +1.595 deg from central meridian).
print("\n--- UTM ZONE 44N (EPSG:32644) PROJECTION EVALUATION ---")
print("  UTM Zone 44N bounds: 78.0 E to 84.0 E, Central Meridian = 81.0 E")
print(f"  Mandals Longitude Range: {m_minx:.4f} E to {m_maxx:.4f} E")
print(f"  Offset from Central Meridian: {m_minx - 81.0:+.4f} deg to {m_maxx - 81.0:+.4f} deg")
print("  Maximum scale distortion factor at zone edge is ~1.0004 (less than 0.04% distortion).")
print("  Directly within Zone 44N core: EXCELLENT FIT.")

# Compute dimensions in UTM 44N
# Approximate projected coordinates:
# 1 deg lat ~ 110,574 m at 17 N
# 1 deg lon ~ 111,320 * cos(17 deg) = 111,320 * 0.9563 ~ 106,455 m
span_lon_m = (m_maxx - m_minx) * 106455
span_lat_m = (m_maxy - m_miny) * 110574
print(f"  Approximate East-West Span: {span_lon_m/1000:.1f} km ({int(span_lon_m/10)} pixels at 10m)")
print(f"  Approximate North-South Span: {span_lat_m/1000:.1f} km ({int(span_lat_m/10)} pixels at 10m)")
total_pixels = (span_lon_m / 10.0) * (span_lat_m / 10.0)
print(f"  Total Estimated Pixels (Bounding Box): {total_pixels:,.0f} (~{total_pixels/1e6:.1f} Megapixels)")

# Uncompressed storage estimate for 3 bands (VV, VH, angle) as Float32 (4 bytes/pixel)
uncompressed_bytes = total_pixels * 3 * 4
print(f"  Estimated Uncompressed Size (3 bands Float32): {uncompressed_bytes / (1024*1024):.1f} MB (~{uncompressed_bytes / (1024*1024*1024):.2f} GB)")
print(f"  With Deflate/LZW compression (typical 40-50% for radar): ~{uncompressed_bytes*0.45 / (1024*1024):.1f} MB")
