"""
Define Study Area for Lower Godavari Basin, Andhra Pradesh, India.
Outputs study area GeoJSON and bounding box definitions.
"""
import json
import os

STUDY_AREA_BBOX = {
    "min_lon": 81.0,
    "min_lat": 16.3,
    "max_lon": 82.8,
    "max_lat": 17.9,
    "description": "Lower Godavari Basin, Andhra Pradesh (downstream from Polavaram / Rajamahendravaram through Dowleswaram Barrage to Gautami & Vasishta delta outlets in the Bay of Bengal)",
    "districts_covered": [
        "East Godavari",
        "West Godavari",
        "Dr. B.R. Ambedkar Konaseema",
        "Kakinada",
        "Eluru",
        "Alluri Sitharama Raju (southern mandals)"
    ],
    "historical_flood_benchmark": {
        "event": "July 2022 Godavari Flood",
        "peak_discharge_cusecs": 2580000,
        "peak_dates": ["2022-07-15", "2022-07-16"],
        "gauge_station": "Dowleswaram Sir Arthur Cotton Barrage"
    }
}

def create_geojson():
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Lower Godavari Basin Study Area",
                    "state": "Andhra Pradesh",
                    "country": "India",
                    "epsg": 4326
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [STUDY_AREA_BBOX["min_lon"], STUDY_AREA_BBOX["min_lat"]],
                        [STUDY_AREA_BBOX["max_lon"], STUDY_AREA_BBOX["min_lat"]],
                        [STUDY_AREA_BBOX["max_lon"], STUDY_AREA_BBOX["max_lat"]],
                        [STUDY_AREA_BBOX["min_lon"], STUDY_AREA_BBOX["max_lat"]],
                        [STUDY_AREA_BBOX["min_lon"], STUDY_AREA_BBOX["min_lat"]]
                    ]]
                }
            }
        ]
    }
    
    out_dir = os.path.join("data", "processed", "boundaries")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "lower_godavari_study_area.geojson")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)
    print(f"Study area GeoJSON written to {out_path}")

    bbox_path = os.path.join(out_dir, "study_area_bbox.json")
    with open(bbox_path, "w", encoding="utf-8") as f:
        json.dump(STUDY_AREA_BBOX, f, indent=2)
    print(f"Study area BBOX metadata written to {bbox_path}")

if __name__ == "__main__":
    create_geojson()
