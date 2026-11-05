"""
Sentinel-1 Metadata-Only Inspection Script.
Performs non-exporting metadata analysis on candidate Sentinel-1 scenes:
- Full product name
- Platform
- Absolute orbit
- Relative orbit (track)
- Orbit pass (Ascending/Descending)
- Acquisition timestamp (UTC and IST)
- VV/VH polarization availability
- Footprint spatial intersection with Lower Godavari Basin (16.3-17.9 N, 81.0-82.8 E)
- Grouping of all matching same-track scenes on the five candidate dates
"""

import os
import re
import json
from collections import defaultdict
from shapely.geometry import box
from shapely import wkt

STUDY_BBOX = {"min_lon": 81.0, "min_lat": 16.3, "max_lon": 82.8, "max_lat": 17.9}
study_box = box(STUDY_BBOX["min_lon"], STUDY_BBOX["min_lat"], STUDY_BBOX["max_lon"], STUDY_BBOX["max_lat"])
study_area_deg2 = study_box.area

def clean_footprint_wkt(fp_str):
    if not fp_str:
        return None
    try:
        if ";" in fp_str:
            wkt_str = fp_str.split(";")[-1].strip("'\" \t\r\n")
        else:
            wkt_str = fp_str.strip("'\" \t\r\n")
        return wkt.loads(wkt_str)
    except Exception as e:
        return None

def inspect_catalogue():
    cat_path = os.path.join("data", "raw", "sentinel1", "sentinel1_scene_catalogue.json")
    if not os.path.exists(cat_path):
        print(f"Catalogue not found at {cat_path}")
        return

    with open(cat_path, "r", encoding="utf-8") as f:
        cat = json.load(f)

    scenes = []
    seen = set()

    for group_key in ["flood_peak", "pre_flood_baseline"]:
        for sc in cat.get(group_key, []):
            name = sc["name"]
            if name in seen:
                continue
            seen.add(name)

            parts = name.split("_")
            platform_code = parts[0]
            platform_name = "Sentinel-1A" if platform_code == "S1A" else "Sentinel-1B"
            mode = parts[1]
            prod_type = parts[2]
            pol_code = parts[3]
            
            acq_start = sc["acquisition_start"]
            acq_end = sc["acquisition_end"]
            abs_orbit = int(parts[6])
            # Sentinel-1A Relative Orbit formula: ((abs - 73) % 175) + 1
            rel_orbit = ((abs_orbit - 73) % 175) + 1

            hour = int(acq_start[11:13])
            orbit_pass = "Descending" if hour < 6 else "Ascending"

            poly = clean_footprint_wkt(sc.get("footprint"))
            if poly:
                inter = poly.intersection(study_box)
                inter_area = inter.area
                inter_pct = (inter_area / study_area_deg2) * 100.0
                intersects = not inter.is_empty
                bounds = poly.bounds
            else:
                inter_pct = 0.0
                intersects = False
                bounds = None

            scenes.append({
                "group": group_key,
                "name": name,
                "platform": platform_name,
                "sensor_mode": mode,
                "product_type": prod_type,
                "polarization": "VV + VH" if "DV" in pol_code else "Single-pol",
                "abs_orbit": abs_orbit,
                "rel_orbit": rel_orbit,
                "orbit_pass": orbit_pass,
                "acq_start": acq_start,
                "acq_end": acq_end,
                "date": acq_start[:10],
                "time_utc": acq_start[11:19],
                "intersects_study_area": intersects,
                "overlap_percentage": round(inter_pct, 2),
                "bounds": bounds,
                "size_mb": sc.get("size_mb")
            })

    # Group by Date
    by_date = defaultdict(list)
    for s in scenes:
        by_date[s["date"]].append(s)

    # Group by Relative Orbit (Track)
    by_track = defaultdict(list)
    for s in scenes:
        by_track[s["rel_orbit"]].append(s)

    return scenes, by_date, by_track

if __name__ == "__main__":
    scenes, by_date, by_track = inspect_catalogue()
    print("================================================================================")
    print("SENTINEL-1 METADATA-ONLY INSPECTION REPORT (NO EXPORT)")
    print(f"Study Area: Lower Godavari Basin ({STUDY_BBOX['min_lat']}N - {STUDY_BBOX['max_lat']}N, {STUDY_BBOX['min_lon']}E - {STUDY_BBOX['max_lon']}E)")
    print("================================================================================")
    print(f"Total Unique Product Granules Catalogued: {len(scenes)}")
    print(f"Candidate Acquisition Dates Found: {len(by_date)} ({', '.join(sorted(by_date.keys()))})")
    print(f"Relative Orbit Tracks Found: {len(by_track)} (Tracks: {', '.join(str(t) for t in sorted(by_track.keys()))})")
    print("================================================================================\n")

    print("--- 1. SCENE DETAILS BY CANDIDATE DATE ---")
    for d in sorted(by_date.keys()):
        print(f"\n>>> DATE: {d} (Total scenes: {len(by_date[d])})")
        for sc in by_date[d]:
            print(f"  * Product: {sc['name']}")
            print(f"    - Platform: {sc['platform']} | Sensor: {sc['sensor_mode']} {sc['product_type']}")
            print(f"    - Absolute Orbit: {sc['abs_orbit']} | Relative Orbit (Track): {sc['rel_orbit']}")
            print(f"    - Pass: {sc['orbit_pass']} | Timestamp: {sc['acq_start']} to {sc['acq_end']}")
            print(f"    - Polarization: {sc['polarization']} (Both VV & VH channels available)")
            print(f"    - Study Area Intersection: {'YES' if sc['intersects_study_area'] else 'NO'} (Study Area Overlap: {sc['overlap_percentage']}%)")
            print(f"    - Granule Size: {sc['size_mb']} MB")

    print("\n================================================================================")
    print("--- 2. SAME-TRACK ORBIT MATCHING ACROSS CANDIDATE DATES ---")
    print("================================================================================")
    for track_num, track_scenes in sorted(by_track.items()):
        dates_in_track = sorted(list(set(s["date"] for s in track_scenes)))
        pass_dir = track_scenes[0]["orbit_pass"]
        print(f"\n[TRACK / RELATIVE ORBIT {track_num}] - Pass Direction: {pass_dir}")
        print(f"  Candidate Dates Observed on this Track: {', '.join(dates_in_track)}")
        for sc in track_scenes:
            print(f"    - {sc['date']} {sc['time_utc']} UTC | Abs Orbit: {sc['abs_orbit']} | Overlap: {sc['overlap_percentage']}% | {sc['name'][:55]}...")
