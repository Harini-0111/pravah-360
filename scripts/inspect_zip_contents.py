import os
import zipfile
import pandas as pd
import io

base = r"C:\Users\harini\Downloads\drive-download-20261101T162443Z-1-001"

print("--- INSPECTING archive (1).zip ---")
with zipfile.ZipFile(os.path.join(base, "archive (1).zip"), "r") as zf:
    for name in zf.namelist():
        print(f"\n>> File: {name}")
        content = zf.read(name)
        if name.endswith(".md"):
            print(content[:500].decode("utf-8", errors="ignore"))
        elif name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
            print(f"Shape: {df.shape}, Columns: {list(df.columns)}")
            print(df.head(3))

print("\n--- INSPECTING archive.zip ---")
with zipfile.ZipFile(os.path.join(base, "archive.zip"), "r") as zf:
    for name in zf.namelist():
        print(f"\n>> File: {name}")
        with zf.open(name) as f:
            df = pd.read_csv(f, nrows=3)
            print(f"Columns: {list(df.columns)}")
            print(df.head(2))

print("\n--- INSPECTING archive (2).zip ---")
with zipfile.ZipFile(os.path.join(base, "archive (2).zip"), "r") as zf:
    for name in zf.namelist():
        print(f"\n>> File: {name}")
        if name.endswith((".md", ".json")):
            content = zf.read(name).decode("utf-8", errors="ignore")
            print(content[:400])
        elif name.endswith(".csv"):
            with zf.open(name) as f:
                df = pd.read_csv(f, nrows=3)
                print(f"Columns: {list(df.columns)}")
                print(df.head(2))
        elif name.endswith(".geojson"):
            content = zf.read(name).decode("utf-8", errors="ignore")
            print(f"GeoJSON snippet: {content[:300]}")
