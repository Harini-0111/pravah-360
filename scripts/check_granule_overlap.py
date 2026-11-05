import json
from shapely.geometry import shape
from shapely import wkt

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

t129 = [sc for sc in cat["flood_peak"] if "20220716" in sc["name"]]
s_sc = [sc for sc in t129 if "C3FF" in sc["name"]][0]
n_sc = [sc for sc in t129 if "33F9" in sc["name"]][0]

s_fp = clean_footprint_wkt(s_sc["footprint"])
n_fp = clean_footprint_wkt(n_sc["footprint"])

overlap = s_fp.intersection(n_fp)
print(f"Overlap exists? {not overlap.is_empty}")
print(f"Overlap area: {overlap.area:.6f} sq deg")
print(f"Southern frame area: {s_fp.area:.6f} sq deg")
print(f"Northern frame area: {n_fp.area:.6f} sq deg")
print(f"Overlap percentage of southern frame: {(overlap.area / s_fp.area) * 100:.2f}%")
print(f"Overlap bounds (min_lon, min_lat, max_lon, max_lat): {overlap.bounds}")
print(f"Latitude range of overlap zone: {overlap.bounds[1]:.4f} N to {overlap.bounds[3]:.4f} N (~{(overlap.bounds[3]-overlap.bounds[1])*110.6:.1f} km along-track)")
