"""
Extract Andhra Pradesh and Lower Godavari Basin boundaries from GADM datasets.
"""
import os
import json

RAW_DIR_DIST = os.path.join("data", "raw", "boundaries", "district")
RAW_DIR_MAND = os.path.join("data", "raw", "boundaries", "mandal")
PROC_DIR = os.path.join("data", "processed", "boundaries")

def process_districts():
    raw_json = os.path.join(RAW_DIR_DIST, "gadm41_IND_2.json")
    with open(raw_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    ap_features = []
    godavari_features = []
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        state = props.get("NAME_1", "")
        district = props.get("NAME_2", "")
        if state == "AndhraPradesh":
            ap_features.append(feat)
            if district in ["EastGodavari", "WestGodavari"]:
                godavari_features.append(feat)
                
    ap_dist_path = os.path.join(PROC_DIR, "andhra_pradesh_districts.geojson")
    godavari_dist_path = os.path.join(PROC_DIR, "lower_godavari_districts.geojson")
    
    with open(ap_dist_path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": ap_features}, f, indent=2)
    with open(godavari_dist_path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": godavari_features}, f, indent=2)
        
    print(f"Saved {len(ap_features)} AP districts to {ap_dist_path}")
    print(f"Saved {len(godavari_features)} Lower Godavari districts to {godavari_dist_path}")

def process_mandals():
    raw_json = os.path.join(RAW_DIR_MAND, "gadm41_IND_3.json")
    with open(raw_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    godavari_mandals = []
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        state = props.get("NAME_1", "")
        district = props.get("NAME_2", "")
        if state == "AndhraPradesh" and district in ["EastGodavari", "WestGodavari"]:
            godavari_mandals.append(feat)
            
    godavari_mandal_path = os.path.join(PROC_DIR, "lower_godavari_mandals.geojson")
    with open(godavari_mandal_path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": godavari_mandals}, f, indent=2)
        
    print(f"Saved {len(godavari_mandals)} Lower Godavari mandals/taluks to {godavari_mandal_path}")

if __name__ == "__main__":
    process_districts()
    process_mandals()
