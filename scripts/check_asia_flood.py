import os
import zipfile
import pandas as pd
import json

base = r"C:\Users\harini\Downloads\drive-download-20261101T162443Z-1-001"
z_path = os.path.join(base, "archive (2).zip")

with zipfile.ZipFile(z_path, "r") as zf:
    with zf.open("ASIA_FLOOD_25YEAR_DATASET/data/station_daily_data.csv") as f:
        df = pd.read_csv(f)
    print("Stations count:", df["station_name"].nunique())
    print("Basins present:", df["basin"].unique())
    print("Countries present:", df["country"].unique())
    godavari = df[df["basin"].str.contains("Godavari", case=False, na=False)]
    print("Godavari records count in sample station file:", len(godavari))

    # Also check full file
    with zf.open("ASIA_FLOOD_25YEAR_DATASET/data/station_daily_data_full.csv") as f:
        # Just check unique basins without loading 57MB all at once
        basins_full = set()
        for chunk in pd.read_csv(f, chunksize=50000, usecols=["basin", "station_name", "country", "latitude", "longitude"]):
            basins_full.update(chunk["basin"].unique())
            god_chunk = chunk[chunk["basin"].str.contains("Godavari", case=False, na=False)]
            if len(god_chunk) > 0:
                print("Found Godavari in full dataset! Stations:", god_chunk["station_name"].unique())
        print("All Basins in full dataset:", basins_full)
