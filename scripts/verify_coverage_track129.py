import json
from shapely.geometry import shape
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

with open("data/processed/boundaries/lower_godavari_mandals.geojson", "r", encoding="utf-8") as f:
    mandals_fc = json.load(f)

with open("data/raw/sentinel1/sentinel1_scene_catalogue.json", "r", encoding="utf-8") as f:
    cat = json.load(f)

t129_fps = []
for sc in cat["flood_peak"]:
    parts = sc["name"].split("_")
    abs_orb = int(parts[6])
    rel_orb = ((abs_orb - 73) % 175) + 1
    if rel_orb == 129:
        poly = clean_footprint_wkt(sc.get("footprint"))
        if poly:
            t129_fps.append(poly)

u_t129 = unary_union(t129_fps)
mandals_union = unary_union([shape(f["geometry"]) for f in mandals_fc["features"]])

total_area = mandals_union.area
inter_total = u_t129.intersection(mandals_union).area
pct_total = (inter_total / total_area) * 100.0
print(f"Total 21-mandal study area: {total_area:.6f} sq deg")
print(f"Track 129 union intersection: {inter_total:.6f} sq deg")
print(f"Overall Track 129 coverage percentage: {pct_total:.2f}%")

print("\nPer-Mandal Coverage Breakdown:")
partially_covered = []
for f in mandals_fc["features"]:
    props = f["properties"]
    name = props.get("NAME_3") or props.get("shapeName") or props.get("mandal_name")
    dist = props.get("NAME_2") or props.get("district_name")
    geom = shape(f["geometry"])
    m_area = geom.area
    c_area = u_t129.intersection(geom).area
    pct = (c_area / m_area) * 100.0
    if pct < 99.9:
        partially_covered.append((name, dist, pct, m_area, c_area))
    print(f"  {name:25s} | {dist:25s} | {pct:6.2f}% covered")

print(f"\nMandals with < 99.9% coverage: {len(partially_covered)}")
for name, dist, pct, m_area, c_area in partially_covered:
    uncovered_sq_deg = m_area - c_area
    print(f"  {name} ({dist}): {pct:.2f}% covered (uncovered area: {uncovered_sq_deg:.6f} sq deg)")
