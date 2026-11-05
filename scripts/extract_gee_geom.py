import json
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

with open("data/processed/boundaries/lower_godavari_mandals.geojson", "r", encoding="utf-8") as f:
    mandals_fc = json.load(f)

mandals_union = unary_union([shape(f["geometry"]) for f in mandals_fc["features"]])
# Convert to GeoJSON mapping
geom_dict = mapping(mandals_union)

with open("data/processed/boundaries/lower_godavari_mandals_union_for_gee.json", "w", encoding="utf-8") as f:
    json.dump(geom_dict, f)

print("Saved GEE geometry JSON!")
print(f"Type: {geom_dict['type']}")
print(f"Number of polygon parts: {len(geom_dict['coordinates'])}")
