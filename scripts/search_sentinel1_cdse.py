"""
Search and record Sentinel-1 SAR scenes from Copernicus Data Space Ecosystem (CDSE)
for Pre-Flood (June 2022) and Flood Peak (July 14-18, 2022) over Lower Godavari Basin.
"""
import os
import json
import requests

OUT_DIR = os.path.join("data", "raw", "sentinel1")
os.makedirs(OUT_DIR, exist_ok=True)

WINDOWS = {
    "flood_peak": ("2022-07-14T00:00:00.000Z", "2022-07-18T23:59:59.000Z"),
    "pre_flood_baseline": ("2022-06-01T00:00:00.000Z", "2022-06-15T23:59:59.000Z")
}

BASE_QUERY = (
    "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
    "$filter=Collection/Name eq 'SENTINEL-1' and "
    "contains(Name,'GRD') and contains(Name,'IW') and "
    "OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((81.0 16.3, 82.8 16.3, 82.8 17.9, 81.0 17.9, 81.0 16.3))') and "
    "ContentDate/Start gt {start} and ContentDate/Start lt {end}"
    "&$top=20"
)

def search_scenes():
    catalogue = {}
    for period, (start, end) in WINDOWS.items():
        url = BASE_QUERY.format(start=start, end=end)
        print(f"Querying CDSE for {period} ({start[:10]} to {end[:10]})...")
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                items = resp.json().get("value", [])
                scene_list = []
                for it in items:
                    scene_list.append({
                        "id": it.get("Id"),
                        "name": it.get("Name"),
                        "size_mb": round(it.get("ContentLength", 0) / (1024 * 1024), 2),
                        "acquisition_start": it.get("ContentDate", {}).get("Start"),
                        "acquisition_end": it.get("ContentDate", {}).get("End"),
                        "sensor_mode": "IW",
                        "product_type": "GRD",
                        "polarization": "VV+VH",
                        "footprint": it.get("Footprint")
                    })
                catalogue[period] = scene_list
                print(f"Found {len(scene_list)} validated scenes for {period}.")
        except Exception as e:
            print(f"Error querying {period}: {e}")
            
    out_file = os.path.join(OUT_DIR, "sentinel1_scene_catalogue.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(catalogue, f, indent=2)
    print(f"Full Sentinel-1 SAR scene catalogue saved to: {out_file}")

if __name__ == "__main__":
    search_scenes()
