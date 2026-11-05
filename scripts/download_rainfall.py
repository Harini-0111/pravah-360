"""
Acquire CHIRPS daily precipitation for the Lower Godavari Basin during the July 2022 flood event.
Source: UCSB CHC via Columbia IRI Data Library REST Service.
Product: CHIRPS 2.0 (0.05 deg, daily).
Time period: 2022-07-10 to 2022-07-20 (peak flood July 14-18, 2022).
"""
import os
import requests
import json

RAW_DIR = os.path.join("data", "raw", "rainfall", "chirps")
PROC_DIR = os.path.join("data", "processed", "rainfall")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)

CHIRPS_NC_URL = (
    "https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.daily-improved/.global/.0p05/.prcp/"
    "X/81.0/82.8/RANGEEDGES/Y/16.3/17.9/RANGEEDGES/T/(10%20Jul%202022)/(20%20Jul%202022)/RANGEEDGES/data.nc"
)

RAW_NC_FILE = os.path.join(RAW_DIR, "chirps_godavari_20220710_20220720.nc")

def download_chirps_nc():
    print(f"Downloading CHIRPS daily precipitation netCDF ({CHIRPS_NC_URL})...")
    resp = requests.get(CHIRPS_NC_URL, stream=True, timeout=60)
    if resp.status_code == 200:
        with open(RAW_NC_FILE, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024*64):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded CHIRPS NetCDF: {RAW_NC_FILE} ({os.path.getsize(RAW_NC_FILE)} bytes)")
    else:
        print(f"Failed to download CHIRPS NetCDF: HTTP {resp.status_code}")

def create_event_summary():
    summary_path = os.path.join(PROC_DIR, "chirps_july2022_event_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("CHIRPS v2.0 DAILY PRECIPITATION - JULY 2022 GODAVARI FLOOD EVENT\n")
        f.write("=================================================================\n")
        f.write("Spatial extent: [16.3 N, 81.0 E] to [17.9 N, 82.8 E] (Lower Godavari Basin)\n")
        f.write("Spatial resolution: 0.05 degrees (~5.5 km)\n")
        f.write("Temporal range: 10 July 2022 to 20 July 2022 (daily)\n")
        f.write("File: data/raw/rainfall/chirps/chirps_godavari_20220710_20220720.nc\n\n")
        f.write("Historical Context:\n")
        f.write("- July 11-14, 2022: Intense catchment-wide rainfall over Upper & Middle Godavari (Vidarbha, Telangana, Chhattisgarh)\n")
        f.write("- July 14-16, 2022: Extreme peak inflow into Dowleswaram Barrage (>2.58 million cusecs, 3rd danger signal)\n")
        f.write("- Precipitation units: mm/day\n")
        f.write("\nComplementary Data Notice:\n")
        f.write("- GPM IMERG Daily (0.1 deg) provides satellite GPM-core microwave/IR calibration.\n")
        f.write("- CHIRPS (0.05 deg) incorporates station blending for high-resolution topographic precipitation estimation.\n")
    print(f"Rainfall event summary saved: {summary_path}")

if __name__ == "__main__":
    download_chirps_nc()
    create_event_summary()
