# Sentinel-1 SAR Satellite Imagery Technical Validation Report

**Project**: Explainable Geospatial AI for Flood Risk, Impact Assessment and Emergency Decision Support
**Phase**: Phase 3 — Flood Data Validation and Analysis
**Study Area**: Lower Godavari Basin ($16.3^\circ\text{N}-17.9^\circ\text{N}$, $81.0^\circ\text{E}-82.8^\circ\text{E}$)
**Target Event**: July 2022 Godavari River Flood (Peak: July 14–18, 2022)
**Date**: November 1, 2026

---

## 1. Executive Summary

A comprehensive scientific audit of the Sentinel-1 Synthetic Aperture Radar (SAR) dataset was performed. The Copernicus Data Space Ecosystem (CDSE) scene catalogue contains **8 flood-peak scenes** (July 14 & 16, 2022) and **12 pre-flood baseline scenes** (June 2022).

### Honest Scientific Reality Check:
- **Scene Catalogue & Metadata**: **VALIDATED & VERIFIED** (all 20 scenes catalogued with timestamps, footprint polygons, polarizations, and orbits).
- **Temporal & Geometric Pairing**: **SCIENTIFICALLY SOUND** (identical relative orbit and pass direction identified between pre-flood baseline and flood peak).
- **Physical Raster Availability**: **NOT CURRENTLY STORED ON LOCAL DISK**. Multi-gigabyte Level-1 GRD `.SAFE` archives or 10m Radiometrically Terrain Corrected (RTC) GeoTIFFs have not yet been downloaded locally.
- **Scientific Usability Verdict**: **PARTIALLY READY (CATALOGUE VERIFIED, RASTERS PENDING EXPORT)**. Local pixel-by-pixel change detection cannot run until rasters are exported via the configured Google Earth Engine pipeline or downloaded from CDSE.

---

## 2. Scene Inventory & Acquisition Metadata

All scenes are C-band SAR Level-1 Ground Range Detected High-Resolution (GRDH) acquired in Interferometric Wide (IW) swath mode with dual polarization (VV + VH).

### 2.1 Flood-Peak Imagery (July 14–18, 2022)

| Scene Identifier | Date & Time (UTC) | Pass Direction | Polarizations | Product Size | Footprint Intersection |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `S1A_IW_GRDH_1SDV_20220714T003035...A0B3_COG.SAFE` | 2022-07-14 00:30:35 | Descending | VV + VH | 1,203.9 MB | Upper delta (Papikonda to Rajahmundry) |
| `S1A_IW_GRDH_1SDV_20220714T003100...62E6_COG.SAFE` | 2022-07-14 00:31:00 | Descending | VV + VH | 1,176.3 MB | Lower delta & Konaseema island coast |
| `S1A_IW_GRDH_1SDV_20220716T124350...C3FF_COG.SAFE` | 2022-07-16 12:43:50 | Ascending | VV + VH | 1,131.0 MB | Southern delta & Krishna-Godavari coast |
| `S1A_IW_GRDH_1SDV_20220716T124419...33F9_COG.SAFE` | 2022-07-16 12:44:19 | Ascending | VV + VH | 1,195.5 MB | Central delta (Dowleswaram, Kakinada) |
| `S1A_IW_GRDH_1SDV_20220714T003035...9B2C.SAFE` | 2022-07-14 00:30:35 | Descending | VV + VH | 1,626.6 MB | Standard SAFE package (Northern tile) |
| `S1A_IW_GRDH_1SDV_20220714T003100...63A0.SAFE` | 2022-07-14 00:31:00 | Descending | VV + VH | 1,626.5 MB | Standard SAFE package (Southern tile) |
| `S1A_IW_GRDH_1SDV_20220716T124350...8156.SAFE` | 2022-07-16 12:43:50 | Ascending | VV + VH | 1,877.1 MB | Standard SAFE package (Southern tile) |
| `S1A_IW_GRDH_1SDV_20220716T124419...E87B.SAFE` | 2022-07-16 12:44:19 | Ascending | VV + VH | 1,616.5 MB | Standard SAFE package (Northern tile) |

*Note: The catalogue records both Cloud-Optimized GeoTIFF (`_COG.SAFE`) and standard ESA SAFE distributions.*

### 2.2 Pre-Flood Baseline Imagery (June 1–20, 2022)

The catalogue contains 12 baseline scenes acquired between June 3 and June 15, 2022. The most critical pair:
- `2022-06-08T00:30:33` (Descending, VV+VH, 1,158.4 MB)
- `2022-06-08T00:30:58` (Descending, VV+VH, 1,137.4 MB)

---

## 3. Orbit Geometry & Change Detection Compatibility

A foundational requirement for SAR flood change detection is that pre-flood and post-flood imagery must share the **exact same orbital geometry**:
1. **Pass Direction Compatibility**:
   - The **July 14, 2022 00:30 UTC** flood scene is a **Descending** pass.
   - The **June 8, 2022 00:30 UTC** baseline scene is an identical **Descending** pass.
   - Both scenes belong to the exact same relative orbit track (Sentinel-1 has a 12-day orbital repeat cycle; June 8 to July 14 is exactly 36 days $= 3 \times 12\text{ days}$).
2. **Scientific Significance**:
   - Sharing identical track geometry ensures that radar incidence angles across the Godavari delta are identical between the baseline and flood scenes ($\approx 30^\circ\text{ to }45^\circ$).
   - This eliminates topographic shadow shifts and foreshortening differences, allowing pure backscatter changes ($\Delta\sigma^\circ = \sigma^\circ_\text{flood} - \sigma^\circ_\text{baseline}$) to represent physical changes in surface moisture and specular water reflections.

---

## 4. Local Raster Availability & Current Limitations

### 4.1 Verification Findings
- `data/raw/sentinel1/`: Contains `sentinel1_scene_catalogue.json` (11,166 bytes). **Zero `.SAFE` archives or GeoTIFFs**.
- `data/processed/sentinel1/`: Currently empty.
- `scripts/gee/download_sentinel1.py`: Fully written Earth Engine processing script that defines the 10m SAR pipeline (VV, VH, median pre-flood composite, flood mosaic, and difference detection), but requires interactive GEE credentials to trigger Drive exports.

### 4.2 Potential Processing Uncertainties & Methodological Safeguards
When the SAR rasters are processed for Phase 4, the following SAR ambiguities must be addressed:
1. **Paddy Field Ambiguity**: Wet rice paddy fields exhibit low radar backscatter even during normal irrigation, resembling open water. WorldCover cropland masks (Class 40) must be used to differentiate flooded fields from standard crop cycles.
2. **Rough Water / Wind Roughening**: Strong monsoon wind over large water bodies (e.g. Godavari estuary / Bay of Bengal) can increase radar backscatter, masking water surfaces. Combining VV and VH cross-polarization reduces wind sensitivity.
3. **Emergent Vegetation**: Flooded coconut groves and mangrove swamps (Konaseema delta) cause double-bounce radar scattering, resulting in bright rather than dark pixels. A simple low-backscatter threshold will underestimate inundation under dense tree canopies.

---

## 5. Actionable Roadmap for Phase 4 Inundation Mapping

To transition from validated catalogue to pixel-level SAR inundation rasters:
1. **Option A (Google Earth Engine Export)**:
   - Run `python scripts/gee/download_sentinel1.py` with authenticated GEE account.
   - Exports pre-processed 10m calibrated, terrain-corrected $\sigma^\circ$ GeoTIFFs directly to Google Drive.
2. **Option B (Direct CDSE Download)**:
   - Download the target dual-scene pair:
     - Flood: `S1A_IW_GRDH_1SDV_20220714T003035...` & `20220714T003100...` (~2.4 GB)
     - Baseline: `S1A_IW_GRDH_1SDV_20220608T003033...` & `20220608T003058...` (~2.3 GB)
   - Perform radiometric calibration and terrain correction via SNAP or GDAL.
3. **Option C (Multi-Source Proxy / DEM-Hydrodynamic Integration)**:
   - If SAR raster downloads are delayed by network/quotas, proceed with hydrodynamic inundation modeling combining the validated Copernicus DEM (30m DSM), HydroRIVERS routing, and calibrated GPM/CHIRPS rainfall.
