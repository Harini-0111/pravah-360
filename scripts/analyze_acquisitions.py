import json
from collections import defaultdict
from shapely.geometry import shape, box
from shapely.ops import unary_union
from shapely import wkt

with open("data/raw/sentinel1/sentinel1_scene_catalogue.json", "r", encoding="utf-8") as f:
    cat = json.load(f)

items = []
for grp in cat:
    for sc in cat[grp]:
        items.append(sc)

print(f"Total catalogued entries: {len(items)}")

acqs = defaultdict(list)
for it in items:
    name = it["name"]
    parts = name.split("_")
    key = (parts[0], parts[4], parts[5], parts[6], parts[7])
    acqs[key].append(it)

print(f"Unique physical satellite acquisitions (granule time-slices): {len(acqs)}")

for k, representations in sorted(acqs.items()):
    plat, start, stop, abs_orb, dtake = k
    print(f"\nAcquisition Slice: {start} to {stop} | Datatake: {dtake} | Abs Orbit: {abs_orb}")
    print(f"  Representations count: {len(representations)}")
    for rep in representations:
        is_cog = "COG" in rep["name"]
        rep_type = "COG Representation" if is_cog else "Standard SAFE"
        print(f"    - {rep_type}: {rep['name']} ({rep['size_mb']} MB)")
