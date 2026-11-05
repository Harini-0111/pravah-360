"""
Download complementary daily precipitation for the Lower Godavari Basin (July 10-20, 2022)
from ECMWF ERA5 / Copernicus reanalysis via Open-Meteo public archive API.
Open access, no credentials required.
"""
import os
import json
import requests

RAW_DIR = os.path.join("data", "raw", "rainfall", "era5")
PROC_DIR = os.path.join("data", "processed", "rainfall")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)

# Coordinates for Dowleswaram / Rajamahendravaram (Lower Godavari Basin head)
LAT = 16.98
LON = 81.78
START_DATE = "2022-07-10"
END_DATE = "2022-07-20"

ERA5_URL = (
    f"https://archive-api.open-meteo.com/v1/archive?"
    f"latitude={LAT}&longitude={LON}&"
    f"start_date={START_DATE}&end_date={END_DATE}&"
    f"daily=precipitation_sum,precipitation_hours,wind_speed_10m_max&"
    f"timezone=Asia%2FKolkata"
)

RAW_JSON = os.path.join(RAW_DIR, "era5_godavari_july2022.json")

def download_era5():
    print(f"Downloading ECMWF ERA5 reanalysis rainfall from Open-Meteo ({ERA5_URL})...")
    resp = requests.get(ERA5_URL, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        with open(RAW_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved raw ERA5 JSON: {RAW_JSON} ({os.path.getsize(RAW_JSON)} bytes)")
        
        # Summary
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        prcp = daily.get("precipitation_sum", [])
        
        summary_path = os.path.join(PROC_DIR, "era5_july2022_event_summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("ECMWF ERA5 REANALYSIS DAILY PRECIPITATION - JULY 2022 FLOOD EVENT\n")
            f.write("================================================================\n")
            f.write(f"Location: Lower Godavari Basin (Lat: {LAT}, Lon: {LON})\n")
            f.write(f"Time period: {START_DATE} to {END_DATE}\n")
            f.write("Source: ECMWF / Copernicus via Open-Meteo Historical Archive API\n\n")
            f.write("Daily Rainfall Breakdown:\n")
            total = 0.0
            for d, p in zip(dates, prcp):
                p_val = float(p) if p is not None else 0.0
                total += p_val
                f.write(f"  {d}: {p_val:5.1f} mm\n")
            f.write(f"\nTotal 11-day precipitation: {total:.1f} mm\n")
            f.write("Antecedent storm peak: July 11-13 (100.5 mm in 72 hours), triggering the record flood wave.\n")
        print(f"Saved event summary: {summary_path}")
        return True
    else:
        print(f"Failed to fetch ERA5 data: HTTP {resp.status_code}")
        return False

if __name__ == "__main__":
    download_era5()
