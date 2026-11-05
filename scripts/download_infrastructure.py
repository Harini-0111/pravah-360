"""
Download critical infrastructure features from OpenStreetMap for Lower Godavari Basin.
Queries Overpass API for hospitals, clinics, schools, emergency shelters, bridges, and primary road networks.
"""
import os
import json
import time
import requests

RAW_DIR = os.path.join("data", "raw", "infrastructure")
PROC_DIR = os.path.join("data", "processed", "infrastructure")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
BBOX = "(16.3,81.0,17.9,82.8)"

QUERIES = {
    "healthcare": f"""[out:json][timeout:60];
(
  node["amenity"="hospital"]{BBOX};
  way["amenity"="hospital"]{BBOX};
  node["amenity"="clinic"]{BBOX};
  node["amenity"="doctors"]{BBOX};
);
out center tags;
""",
    "education": f"""[out:json][timeout:60];
(
  node["amenity"="school"]{BBOX};
  node["amenity"="college"]{BBOX};
  way["amenity"="school"]{BBOX};
);
out center tags 500;
""",
    "emergency_shelters": f"""[out:json][timeout:60];
(
  node["amenity"="shelter"]{BBOX};
  node["emergency"="shelter"]{BBOX};
  node["shelter_type"="cyclone"]{BBOX};
  node["building"="cyclone_shelter"]{BBOX};
  way["amenity"="shelter"]{BBOX};
);
out center tags;
""",
    "bridges_and_major_roads": f"""[out:json][timeout:90];
(
  way["bridge"="yes"]{BBOX};
  way["highway"="motorway"]{BBOX};
  way["highway"="trunk"]{BBOX};
  way["highway"="primary"]{BBOX};
);
out count;
"""
}

def fetch_and_save_geojson():
    stats = {}
    for layer_name, q in QUERIES.items():
        raw_path = os.path.join(RAW_DIR, f"osm_{layer_name}.json")
        proc_path = os.path.join(PROC_DIR, f"osm_{layer_name}.geojson")
        
        print(f"Querying Overpass for {layer_name}...")
        try:
            resp = requests.post(OVERPASS_URL, data={"data": q}, headers={"User-Agent": "FloodIntelligenceSystem/1.0"}, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                with open(raw_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                
                # Convert to GeoJSON FeatureCollection
                features = []
                for el in data.get("elements", []):
                    lat = el.get("lat") or el.get("center", {}).get("lat")
                    lon = el.get("lon") or el.get("center", {}).get("lon")
                    if lat and lon:
                        features.append({
                            "type": "Feature",
                            "properties": {
                                "id": el.get("id"),
                                "type": el.get("type"),
                                "tags": el.get("tags", {})
                            },
                            "geometry": {
                                "type": "Point",
                                "coordinates": [lon, lat]
                            }
                        })
                
                geojson = {
                    "type": "FeatureCollection",
                    "features": features
                }
                with open(proc_path, "w", encoding="utf-8") as f:
                    json.dump(geojson, f, indent=2)
                    
                count = len(features) if features else data.get("elements", [{}])[0].get("tags", {}).get("total", "Count query")
                stats[layer_name] = count
                print(f"Successfully saved {layer_name}: {len(features)} spatial features to {proc_path}")
            else:
                print(f"Overpass query {layer_name} returned HTTP {resp.status_code}")
        except Exception as e:
            print(f"Error querying {layer_name}: {e}")
        time.sleep(2)  # Avoid hammering Overpass API
        
    summary_file = os.path.join(PROC_DIR, "infrastructure_summary.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("OPENSTREETMAP INFRASTRUCTURE SUMMARY - LOWER GODAVARI BASIN\n")
        f.write("===========================================================\n")
        f.write(f"Study bounds: {BBOX}\n\n")
        for k, v in stats.items():
            f.write(f"- {k.replace('_', ' ').title()}: {v}\n")
    print(f"Infrastructure extraction complete. Summary in {summary_file}")

if __name__ == "__main__":
    fetch_and_save_geojson()
