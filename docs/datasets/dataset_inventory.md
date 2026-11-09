# PRAVAH 360: Dataset Inventory, Provenance & Acquisition Guide

## 1. Study Area Definition

- **Region:** Lower Godavari Basin & Delta, Andhra Pradesh, India.
- **Geographic Bounding Box:** `[81.0° E, 16.3° N]` to `[82.8° E, 17.9° N]`.
- **Target Coordinate Reference System (CRS):**
  - **Storage & Vector Presentation:** EPSG:4326 (WGS 84 geographic 2D coordinates).
  - **Planar Geospatial Analysis:** EPSG:32644 (WGS 84 / UTM Zone 44N, meters).
- **Study Units:** 21 Mandals across Dr. B.R. Ambedkar Konaseema, East Godavari, and West Godavari districts.
- **Authoritative Baseline Population:** 9,126,353 residents (WorldPop 2020 UN-adjusted).
- **Mapped Critical Facilities:** 1,542 lifelines (healthcare, education, shelters, bridges) from OpenStreetMap.

---

## 2. Dataset Inventory Table

| Dataset Name | Source / Provider | Spatial Resolution / Extent | Temporal Coverage | Role in PRAVAH 360 | Storage Location | Size | Licensing |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Copernicus DEM (GLO-30)** | European Space Agency (ESA) | 30 m grid / Study area | 2021 release | Elevation, slope, aspect, Topographic Wetness Index (TWI) inputs for AHP | `data/raw/dem/` & `data/processed/dem/` | ~250 MB | Open Access (Copernicus) |
| **ESA WorldCover 10m** | European Space Agency | 10 m grid / Tile N15E081 | 2021 v200 | Land use / land cover (LULC) infiltration factor for AHP | `data/processed/landcover/` | 15.8 MB (clipped) | CC-BY 4.0 |
| **HydroRIVERS** | HydroSHEDS / WWF | Vector lines / Global | v10 | Basin river topology, distance-to-river channel factor | `data/processed/rivers/` | 1.28 MB (clipped) | Open for research |
| **WorldPop Gridded Population** | WorldPop / Univ. of Southampton | 1 km / 100 m / India | 2020 UN-adjusted | Zonal population exposure assessment across 21 mandals | `data/processed/population/` | 160 KB (clipped) | CC-BY 4.0 |
| **OpenStreetMap Lifelines** | OpenStreetMap Contributors | Vector points & lines | Continual / 2026 snapshot | Critical facility risk mapping (1,542 hospitals, schools, bridges) | `data/processed/infrastructure/` | 0.83 MB | ODbL 1.0 |
| **Sentinel-1 SAR GRD** | Copernicus / ESA via GEE | 10 m / Track 129 / Konaseema | July 16, 2022 (Flood Peak) | Observational candidate water surface extraction & model validation | `data/processed/sentinel1/` | 9.26 MB (GeoJSON) | Open Access (Copernicus) |
| **CWC & WRD River Stage** | Central Water Commission (CWC) / AP WRD | Gauge stations (Dowleswaram, Polavaram, etc.) | July 2022 historic + reference telemetry | Historical hydrograph replay & stage warning comparisons | `data/monitoring/` & `data/reference/` | <1 MB | Public Government Data |
| **APSDMA SACHET Alerts** | Andhra Pradesh State Disaster Management Authority | Mandal-level polygons | Real-time polling | Official cyclone and flood alert ingestion with freshness tracking | `data/monitoring/` | <1 MB | State Government Portal |
| **Open-Meteo Weather API** | Open-Meteo | Single coordinate & gridded | 7-day hourly forecast | Precipitation forecast and atmospheric monitoring | Live REST API | Dynamic | Non-commercial / CC-BY 4.0 |

---

## 3. Large File Handling & Acquisition Instructions

Due to GitHub's **100 MB per-file upload limit**, raw raster archives exceeding 100 MB are not stored directly in Git. Their processed vector and compressed raster derivatives are committed to Git so the platform works immediately upon cloning.

If you need to reproduce the raw geospatial processing from scratch, follow these instructions:

### A. Raw Sentinel-1 SAR GRD Imagery (July 16, 2022 Flood Event)
- **Files:** `data/processed/sentinel1/track129_20220716/s1a_t129_20220716_flood_peak_utm44n_10m-*.tif` (4 tiles, total ~5.48 GB).
- **How to Reproduce:**
  1. Open Google Earth Engine (GEE).
  2. Use the provided export script: `scripts/gee/dispatch_sentinel1_track129_export.py`.
  3. Filter Collection: `COPERNICUS/S1_GRD` for `instrumentMode: 'IW'`, `orbitProperties_pass: 'DESCENDING'`, `relativeOrbitNumber_start: 129`, date range `2022-07-16`.
  4. The candidate water mask extraction script `scripts/extract_sentinel1_water.py` processes these tiles using Otsu thresholding and slope masking (<5°) to generate `data/processed/sentinel1/track129_flood_water_candidates.geojson` (9.26 MB, tracked in Git).

### B. HydroSHEDS Global River Network
- **Files:** `data/raw/rivers/HydroRIVERS_v10_as_shp/` (~424 MB) and `data/processed/rivers/lower_godavari_hydrorivers.geojson` (1.28 MB).
- **Source:** [HydroSHEDS Asian Region River Network](https://www.hydrosheds.org/products/hydrorivers).
- **Licensing & Staging:** Free for academic/research use. Due to third-party redistribution terms, both the raw shapefile and derived GeoJSON are excluded from public Git staging.
- **Processing:** The raw shapefile is downloaded and spatially clipped to the Lower Godavari boundary locally using `python scripts/download_rivers.py`.

### C. GADM Administrative Boundaries (v4.1)
- **Files:** `data/raw/boundaries/` and `data/processed/boundaries/*.geojson`.
- **Source:** [GADM](https://gadm.org/).
- **Licensing & Staging:** Non-commercial academic license prohibiting public redistribution. Both raw country files and clipped study mandal GeoJSONs are excluded from Git staging.
- **Processing:** Raw files are placed in `data/raw/boundaries/` and processed locally using `python scripts/download_boundaries.py`.

### D. Copernicus Digital Elevation Model (GLO-30)
- **Source:** [Copernicus Open Access Hub / Registry of Open Data on AWS](https://registry.opendata.aws/copernicus-dem/).
- **Tiles:** `N16E081`, `N16E082`, `N17E081`, `N17E082`.
- **Processing:** Merged and derived using GDAL (`slope`, `aspect`, and `fill_nodata`) in `scripts/download_dem.py`.

---

## 4. Distinction Between Dataset Tiers

To maintain strict scientific transparency, PRAVAH 360 enforces clear distinctions across data tiers:

1. **Static Ingestion Tier:** Offline high-resolution EO data (DEM, WorldCover, WorldPop, OSM). Preprocessed, harmonized, and version-controlled.
2. **Observational Validation Tier:** Sentinel-1 Track 129 C-band SAR backscatter acquisition. Used as an empirical candidate water footprint from a real disaster event.
3. **Operational Telemetry Tier:**
   - **Stored Reference Telemetry:** Historical gauge heights from the July 2022 Godavari flood (peak stage 17.85 m at Dowleswaram, 2.58 million cusecs discharge).
   - **Simulated Demonstration Records:** Used to test stage threshold warnings (Warning: 10.0 ft, Danger: 13.75 ft, Extreme Danger: 17.75 ft).
   - **Live Ingestion:** Polled APSDMA SACHET GeoJSON feeds and Open-Meteo forecasts, carrying explicit **Freshness Badges** (e.g., `< 5 min ago`, `Delayed: 4h`, `Offline Cache`).
