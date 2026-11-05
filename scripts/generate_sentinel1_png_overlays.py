"""
Generate Web PNG Overlays for Sentinel-1 Track 129 Classification (Phase 5.1)
Warp UTM 44N 50m classified raster to regular EPSG:4326 WGS84 grid.
Produces optimized transparent PNG overlays for Leaflet L.imageOverlay.
"""

import os
import sys
import zlib
import struct
import json
import time
import math
from pathlib import Path
import numpy as np
import tifffile

WORKSPACE = Path(r"C:\major project")
sys.path.insert(0, str(WORKSPACE))

from scripts.extract_sentinel1_water import (
    wgs84_to_utm44n,
    utm44n_to_wgs84,
    MIN_X, MAX_X, MIN_Y, MAX_Y, GRID_RES, ROWS, COLS
)

def write_png_rgba(filename, width, height, rgba_array):
    """Write an RGBA numpy uint8 array (height, width, 4) to an optimized PNG."""
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data))
    
    # Prepend 0 byte (filter type None) to each row
    raw_lines = bytearray()
    line_bytes = width * 4
    for r in range(height):
        raw_lines.append(0)
        raw_lines.extend(rgba_array[r].tobytes())
    
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw_lines), 7)
    
    with open(filename, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', ihdr))
        f.write(chunk(b'IDAT', idat))
        f.write(chunk(b'IEND', b''))

def main():
    t0 = time.time()
    print("=" * 80)
    print("SENTINEL-1 TRACK 129 WEB PNG OVERLAY GENERATOR & VALIDATOR")
    print("=" * 80)

    # 1. Load Original Classified GeoTIFF
    tif_path = WORKSPACE / "data" / "processed" / "sentinel1" / "track129_water_classification.tif"
    print(f"[*] Reading classified GeoTIFF from {tif_path}...", flush=True)
    classification = tifffile.imread(tif_path)
    print(f"[+] Classification raster shape: {classification.shape}, dtype: {classification.dtype}")

    # Check original pixel counts
    orig_counts = {
        0: int(np.count_nonzero(classification == 0)),
        1: int(np.count_nonzero(classification == 1)),
        2: int(np.count_nonzero(classification == 2)),
        3: int(np.count_nonzero(classification == 3)),
        4: int(np.count_nonzero(classification == 4)),
        5: int(np.count_nonzero(classification == 5))
    }
    print("    Original Raster Pixel Distribution:")
    for k, v in orig_counts.items():
        print(f"      Class {k}: {v:9,d} pixels")

    # 2. Define Target Regular WGS84 Grid (EPSG:4326)
    # Covering full study area extent
    west_lon = 80.8500
    east_lon = 82.6150
    south_lat = 16.3000
    north_lat = 18.0150

    d_lon = east_lon - west_lon  # 1.7650 deg
    d_lat = north_lat - south_lat # 1.7150 deg

    # Step: 0.00075 deg (~83m resolution, ideal balance between high visual fidelity and small file size)
    step_deg = 0.00075
    w_out = int(round(d_lon / step_deg)) # ~2353
    h_out = int(round(d_lat / step_deg)) # ~2287

    print(f"\n[*] Target WGS84 Envelope:")
    print(f"    West:  {west_lon:.4f}°E, East:  {east_lon:.4f}°E (Width: {w_out} px)")
    print(f"    South: {south_lat:.4f}°N, North: {north_lat:.4f}°N (Height: {h_out} px)")
    print(f"    Resolution: {step_deg:.6f}° (~83 meters isotropic)")

    # 3. Vectorized Coordinate Transformation (WGS84 -> UTM 44N)
    print("[*] Computing inverse coordinate transform matrix...", flush=True)
    lons = west_lon + (np.arange(w_out) + 0.5) * step_deg
    lats = north_lat - (np.arange(h_out) + 0.5) * step_deg # Row 0 is North

    # Create coordinate grid
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # Vectorized UTM 44N transform
    a = 6378137.0
    f = 1.0 / 298.257223563
    e2 = 2 * f - f * f
    e_prime2 = e2 / (1.0 - e2)
    k0 = 0.9996
    lon0 = 81.0 * math.pi / 180.0

    phi = np.radians(lat_grid)
    lam = np.radians(lon_grid)
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)
    tan_phi = np.tan(phi)

    N = a / np.sqrt(1.0 - e2 * (sin_phi ** 2))
    T = tan_phi ** 2
    C = e_prime2 * (cos_phi ** 2)
    A = (lam - lon0) * cos_phi

    M = a * ((1.0 - e2 / 4.0 - 3.0 * e2 * e2 / 64.0 - 5.0 * e2 * e2 * e2 / 256.0) * phi
             - (3.0 * e2 / 8.0 + 3.0 * e2 * e2 / 32.0 + 45.0 * e2 * e2 * e2 / 1024.0) * np.sin(2.0 * phi)
             + (15.0 * e2 * e2 / 256.0 + 45.0 * e2 * e2 * e2 / 1024.0) * np.sin(4.0 * phi)
             - (35.0 * e2 * e2 * e2 / 3072.0) * np.sin(6.0 * phi))

    utm_x = k0 * N * (A + (1.0 - T + C) * (A ** 3) / 6.0
                      + (5.0 - 18.0 * T + T * T + 72.0 * C - 58.0 * e_prime2) * (A ** 5) / 120.0) + 500000.0
    utm_y = k0 * (M + N * tan_phi * ((A ** 2) / 2.0
                                    + (5.0 - T + 9.0 * C + 4.0 * C * C) * (A ** 4) / 24.0
                                    + (61.0 - 58.0 * T + T * T + 600.0 * C - 330.0 * e_prime2) * (A ** 6) / 720.0))

    # Convert to raster coordinates
    col_idx = np.round((utm_x - MIN_X) / GRID_RES).astype(np.int32)
    row_idx = np.round((MAX_Y - utm_y) / GRID_RES).astype(np.int32)

    # Valid mask within UTM raster dimensions
    valid_bounds = (col_idx >= 0) & (col_idx < COLS) & (row_idx >= 0) & (row_idx < ROWS)

    # Sample classification
    sampled_class = np.zeros((h_out, w_out), dtype=np.uint8)
    sampled_class[valid_bounds] = classification[row_idx[valid_bounds], col_idx[valid_bounds]]

    # 4. Verification of Sampled Representation
    sampled_counts = {
        0: int(np.count_nonzero(sampled_class == 0)),
        1: int(np.count_nonzero(sampled_class == 1)),
        2: int(np.count_nonzero(sampled_class == 2)),
        3: int(np.count_nonzero(sampled_class == 3)),
        4: int(np.count_nonzero(sampled_class == 4)),
        5: int(np.count_nonzero(sampled_class == 5))
    }
    print("\n[+] Resampled Grid Pixel Distribution:")
    for k, v in sampled_counts.items():
        ratio = v / max(1, orig_counts[k]) * ((50.0 / (step_deg * 111320.0)) ** 2)
        print(f"    Class {k}: {v:9,d} pixels (Area ratio vs orig: {ratio:.3f})")

    # 5. Build RGBA Output Arrays
    out_dir = WORKSPACE / "frontend" / "overlays"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Color Palette definitions (RGBA)
    # Class 2: Candidate Floodwater (Electric Cyan #00d2ff, Alpha ~90% -> 230)
    # Class 1: Permanent Water (Deep Blue #2563eb, Alpha ~78% -> 200)
    # Class 3: Ambiguous Wet Soil (Amber #d97706, Alpha ~65% -> 165)

    # A. Candidate Floodwater Overlay Only (Default Active Layer)
    flood_rgba = np.zeros((h_out, w_out, 4), dtype=np.uint8)
    flood_mask = (sampled_class == 2)
    flood_rgba[flood_mask] = [0, 210, 255, 230]

    flood_png_path = out_dir / "sentinel1_flood_candidates_track129.png"
    print(f"\n[*] Writing Candidate Floodwater PNG overlay to {flood_png_path}...", flush=True)
    write_png_rgba(flood_png_path, w_out, h_out, flood_rgba)
    print(f"[+] Saved: {flood_png_path.name} ({flood_png_path.stat().st_size / 1024:.1f} KB)")

    # B. Permanent Water Reference Overlay
    perm_rgba = np.zeros((h_out, w_out, 4), dtype=np.uint8)
    perm_mask = (sampled_class == 1)
    perm_rgba[perm_mask] = [37, 99, 235, 200]

    perm_png_path = out_dir / "sentinel1_permanent_water.png"
    print(f"[*] Writing Permanent Water PNG overlay to {perm_png_path}...", flush=True)
    write_png_rgba(perm_png_path, w_out, h_out, perm_rgba)
    print(f"[+] Saved: {perm_png_path.name} ({perm_png_path.stat().st_size / 1024:.1f} KB)")

    # C. Ambiguous Wet Soil / Low-Backscatter Overlay
    ambig_rgba = np.zeros((h_out, w_out, 4), dtype=np.uint8)
    ambig_mask = (sampled_class == 3)
    ambig_rgba[ambig_mask] = [217, 119, 6, 165]

    ambig_png_path = out_dir / "sentinel1_ambiguous_wetsoil.png"
    print(f"[*] Writing Ambiguous Low-Backscatter PNG overlay to {ambig_png_path}...", flush=True)
    write_png_rgba(ambig_png_path, w_out, h_out, ambig_rgba)
    print(f"[+] Saved: {ambig_png_path.name} ({ambig_png_path.stat().st_size / 1024:.1f} KB)")

    # D. Combined Classified Overlay
    combo_rgba = np.zeros((h_out, w_out, 4), dtype=np.uint8)
    combo_rgba[sampled_class == 1] = [37, 99, 235, 200]
    combo_rgba[sampled_class == 2] = [0, 210, 255, 230]
    combo_rgba[sampled_class == 3] = [217, 119, 6, 165]

    combo_png_path = out_dir / "sentinel1_water_classified_all.png"
    print(f"[*] Writing Combined Classified PNG overlay to {combo_png_path}...", flush=True)
    write_png_rgba(combo_png_path, w_out, h_out, combo_rgba)
    print(f"[+] Saved: {combo_png_path.name} ({combo_png_path.stat().st_size / 1024:.1f} KB)")

    # 6. Save Metadata for Frontend Leaflet Integration
    metadata = {
        "dataset": "Sentinel-1 Track 129 SAR Water Extraction (July 16, 2022)",
        "crs": "EPSG:4326 (WGS84)",
        "bounds": {
            "south": south_lat,
            "west": west_lon,
            "north": north_lat,
            "east": east_lon
        },
        "leaflet_bounds": [
            [south_lat, west_lon],
            [north_lat, east_lon]
        ],
        "dimensions": {
            "width": w_out,
            "height": h_out,
            "resolution_deg": step_deg,
            "approx_resolution_m": 83.5
        },
        "layers": {
            "flood_candidates": {
                "file": "/static/overlays/sentinel1_flood_candidates_track129.png",
                "label": "Sentinel-1 Observed Floodwater Candidates",
                "color_hex": "#00d2ff",
                "class_id": 2,
                "pixels": sampled_counts[2]
            },
            "permanent_water": {
                "file": "/static/overlays/sentinel1_permanent_water.png",
                "label": "Permanent Water Reference",
                "color_hex": "#2563eb",
                "class_id": 1,
                "pixels": sampled_counts[1]
            },
            "ambiguous_water": {
                "file": "/static/overlays/sentinel1_ambiguous_wetsoil.png",
                "label": "Ambiguous Water / Wet Soil",
                "color_hex": "#d97706",
                "class_id": 3,
                "pixels": sampled_counts[3]
            },
            "combined": {
                "file": "/static/overlays/sentinel1_water_classified_all.png",
                "label": "All Water Classes Combined"
            }
        }
    }

    meta_path = WORKSPACE / "data" / "metadata" / "sentinel1_png_overlay_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[+] Saved metadata to {meta_path}")

    # Also mirror metadata into frontend directory for direct client access if needed
    with open(WORKSPACE / "frontend" / "overlays" / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    elapsed = round(time.time() - t0, 1)
    print(f"\n[+] OVERLAY GENERATION COMPLETED SUCCESSFULLY in {elapsed}s.")

if __name__ == "__main__":
    main()
