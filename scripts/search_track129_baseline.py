import requests
import json

url = (
    "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
    "$filter=Collection/Name eq 'SENTINEL-1' and "
    "contains(Name,'GRD') and contains(Name,'IW') and "
    "OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((81.0 16.3, 82.8 16.3, 82.8 17.9, 81.0 17.9, 81.0 16.3))') and "
    "ContentDate/Start gt 2022-01-01T00:00:00.000Z and ContentDate/Start lt 2022-07-31T23:59:59.000Z"
    "&$top=1000"
)

print("Querying CDSE for pre-flood scenes between 2022-05-15 and 2022-07-16...")
try:
    resp = requests.get(url, timeout=30)
    print("Status:", resp.status_code)
    if resp.status_code == 200:
        items = resp.json().get("value", [])
        print(f"Total items returned: {len(items)}")
        track129_items = []
        all_tracks = set()
        for it in items:
            name = it.get("Name")
            parts = name.split("_")
            abs_orb = int(parts[6])
            rel_orb = ((abs_orb - 73) % 175) + 1
            all_tracks.add(rel_orb)
            acq = it.get("ContentDate", {}).get("Start")
            if rel_orb == 129:
                track129_items.append(it)
                print(f"MATCH TRACK 129: {acq} | Abs {abs_orb} | {name}")
        
        print(f"\nAll relative orbits present in this window: {sorted(list(all_tracks))}")
        print(f"Total Track 129 scenes found: {len(track129_items)}")
        
        # Save results to a json file
        with open("data/raw/sentinel1/track129_cdse_search_results.json", "w", encoding="utf-8") as f:
            json.dump(track129_items, f, indent=2)
            
    else:
        print("Error response:", resp.text[:400])
except Exception as e:
    print("Exception during CDSE query:", e)
