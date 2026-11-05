import requests
import json

def check_window(start, end, label):
    url = (
        "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
        "$filter=Collection/Name eq 'SENTINEL-1' and "
        "contains(Name,'GRD') and contains(Name,'IW') and "
        "OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((81.0 16.3, 82.8 16.3, 82.8 17.9, 81.0 17.9, 81.0 16.3))') and "
        f"ContentDate/Start gt {start} and ContentDate/Start lt {end}"
        "&$top=500"
    )
    print(f"\n--- Checking {label} ({start[:10]} to {end[:10]}) ---")
    resp = requests.get(url, timeout=30)
    if resp.status_code == 200:
        items = resp.json().get("value", [])
        print(f"Total items: {len(items)}")
        t129 = []
        for it in items:
            name = it.get("Name")
            parts = name.split("_")
            abs_orb = int(parts[6])
            # For S1A: ((abs - 73) % 175) + 1
            # For S1B: ((abs - 27) % 175) + 1
            plat = parts[0]
            if plat == "S1A":
                rel = ((abs_orb - 73) % 175) + 1
            else:
                rel = ((abs_orb - 27) % 175) + 1
            if rel == 129:
                t129.append((it.get("ContentDate", {}).get("Start"), plat, name))
        print(f"Track 129 items found: {len(t129)}")
        for acq, plat, name in t129:
            print(f"  {acq[:19]} | {plat} | {name[:60]}...")
        return t129
    else:
        print("Status error:", resp.status_code)
        return []

# Check 2021 dry/pre-monsoon season
check_window("2021-05-01T00:00:00.000Z", "2021-08-01T00:00:00.000Z", "2021 Summer/Monsoon")
# Check August - December 2022 (after July 16)
check_window("2022-07-17T00:00:00.000Z", "2022-10-31T00:00:00.000Z", "Post-Flood 2022")
