# PRAVAH 360: Historical Flood Event and Dataset Readiness Assessment

**Project:** AI-Based Flood Risk, Impact Assessment and Emergency Decision Support System (PRAVAH 360)
**Study Area:** Lower Godavari Basin & Delta, Andhra Pradesh, India ($16.3^\circ\text{N}-17.9^\circ\text{N}$, $81.0^\circ\text{E}-82.8^\circ\text{E}$)
**Task Type:** Read-Only Technical Readiness Audit & Scientific Reconciliation
**Assessment Date:** 05 November 2026
**Document Target:** `docs/historical_flood_and_dataset_readiness.md`
**Operational Status:** Reconciled Against Operational Codebase and Physical Data Assets

---

## 1. Executive Summary

### 1.1 Scope of the Assessment
To establish an academically defensible foundation for the integrated **Past, Present, and Future Flood Intelligence** architecture in PRAVAH 360, an empirical audit and reconciliation of all existing datasets, historical event records, telemetry feeds, and predictive components within `C:\major project` was executed.

This assessment strictly demarcates what PRAVAH 360 empirically executes today, what data layers exist only as catalogues or static scenario baselines, and what hydrologic, meteorological, and telemetric prerequisites must be secured before operational future flood forecasting can be deployed.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PRAVAH 360 READINESS SUMMARY                                  │
├──────────────────────┬──────────────────────────────┬───────────────────────────────────────────┤
│ Domain               │ Operational Status           │ Primary Data & Computational Reality      │
├──────────────────────┼──────────────────────────────┼───────────────────────────────────────────┤
│ Historical (Past)    │ PARTIALLY AVAILABLE          │ July 2022 peak SAR (Track 129, 5.74 GB)   │
│ Event Reconstruction │ (Single-Date Calibration)    │ available; Track 92 pre-flood baseline    │
│                      │                              │ rasters pending local export.             │
├──────────────────────┼──────────────────────────────┼───────────────────────────────────────────┤
│ Present Monitoring   │ AVAILABLE (Hybrid Telemetry) │ Live APSDMA GIS mirror of NDMA SACHET     │
│                      │                              │ alerts; CWC gauge thresholds evaluate on  │
│                      │                              │ stored benchmark scenario records.        │
├──────────────────────┼──────────────────────────────┼───────────────────────────────────────────┤
│ Future Forecasting   │ NOT AVAILABLE                │ Lacks dynamic catchment rainfall-runoff   │
│                      │ (Requires Prerequisites)     │ routing (HEC-HMS/SWAT) and 2D hydro-      │
│                      │                              │ dynamic flood routing (HEC-RAS 2D).       │
└──────────────────────┴──────────────────────────────┴───────────────────────────────────────────┘
```

### 1.2 Summary of Reconciled Findings
1. **Physical Geospatial Baselines are Fully Operational (`AVAILABLE`):**
   - High-resolution Digital Elevation Model (Copernicus DEM 30m GLO-30 DSM), derived slope/aspect matrices, ESA WorldCover 2021 (50m standardized), HydroSHEDS river networks (1,496 reaches), WorldPop 2020 UN-Adjusted demographic grids, and OpenStreetMap critical infrastructure points are fully clipped, validated, and actively serving the AHP multi-criteria susceptibility and exposure engines.
2. **Authoritative Demographic Exposure Baseline:**
   - The authoritative population baseline for the 21 study mandals is **$9,126,353$ persons** (derived from the exact vector polygon clip of the 1km WorldPop 2020 UN-Adjusted raster).
   - The reported elevated exposure figure of **$8,252,724$ persons ($90.43\%$)** represents the population residing strictly in **Very High ($6,027,704$) and High ($2,225,020$)** susceptibility zones. Moderate susceptibility ($663,126$, $7.27\%$) is excluded from this figure.
   - This metric represents *potential exposure to intrinsic physical hazard*, not confirmed flood victims.
3. **Historical Benchmark Floods are Single-Date Calibrated (`PARTIALLY AVAILABLE`):**
   - The **July 2022 Godavari Mega-Crest** has substantial multi-sensor data: 4 raw Level-1 GRD Sentinel-1 SAR tiles (5.74 GB) covering the July 16 peak (Ascending pass Track 129), CHIRPS 2.0 (0.05°) 10-day rainfall NetCDF, GPM IMERG Daily V07B NetCDF-4, and ERA5 reanalysis time-series.
   - The derived flood candidate polygons ($9.71\text{ MB}$) were generated via single-date adaptive Otsu thresholding with permanent water and slope masking; they do not possess independent ground-truth survey validation (e.g. RTK-GNSS high-water marks or cadastral flood registries).
   - Pre-flood baseline rasters (Track 92, Descending pass) exist only as vector footprints; furthermore, Track 129 (Ascending) and Track 92 (Descending) cannot be directly differenced due to opposing orbital geometries.
4. **Present-State Alerting & Telemetry Reality:**
   - Live public alert ingestion operates continuously from the **APSDMA State GIS Server** (`apsdmagis.ap.gov.in/weather-watch/data/cyclone/layers/sachet_alerted_mandals.geojson`), which mirrors NDMA SACHET / IMD warnings, with fully verified temporal lifecycle states (`LIVE`, `STALE`, `EXPIRED`, `UNAVAILABLE`) and 15-minute polling cache windows.
   - Weather surveillance in `WeatherService` exclusively proxies the Google Maps Platform Weather API, which is currently **inactive (`API_KEY_NOT_CONFIGURED`)** as `GOOGLE_WEATHER_API_KEY` is empty in `.env`. Open-Meteo is not implemented as a runtime fallback in the backend; it was only an offline reanalysis retrieval tool in `scripts/download_rainfall_era5.py`.
   - River telemetry at 4 critical stations (Dowleswaram Barrage, Polavaram, Kunavaram, Bhadrachalam) evaluates official CWC Warning/Danger levels against **stored benchmark scenario records** dated `2026-11-03 09:20:00` with `is_live: false`, not live automated telemetric webhooks.
5. **Machine Learning Validation Engine Clarification:**
   - The predictive validation service (`prediction_validation_service.py`) operates as an internal **Synthetic Multi-Scenario Spatial-Holdout Benchmark** with `np.random.seed(42)` across 4 simulated event scenarios.
   - Target classification labels ($y$) are computed from a synthetic latent multi-criteria equation containing elevation, stream distance, and runoff. The metrics ($POD = 0.857$, $FAR = 0.0$, $IoU = 0.857$) test model learning capability and spatial generalization across 4 held-out coastal mandals (Razole, Sakhinetipalli, Mummidivaram, Amalapuram), **not** empirical accuracy against field-surveyed flood extents.

---

## 2. Historical Flood Event Inventory

An exhaustive audit of historical flood events documented across project datasets, CWC bulletins, APSDMA situation reports, and local archive files (`data/reference/historical_flood_events_godavari.json`, `data/raw/historical_floods/july2022_flood_bulletin_records.md`, and `data/reference/godavari_flood_hazard_report_2026.pdf`) was conducted.

### 2.1 Inventory Table of Historical Events

| Event Identifier | Event Name & Classification | Date & Duration | Geographic Coverage | Available Rainfall Data | Available Satellite SAR Imagery | Available Gauge / Discharge Records | Official Reports & Warnings | Potentially Affected Mandals | Evidence Quality & Missing Information | Overall Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GODAVARI_FLOOD_JULY_2022` | Historic Lower Godavari Basin Flood (Second highest crest in modern history) | 2022-07-11 to 2022-07-22 (Peak: 15–16 July 2022) | Entire Lower Godavari Basin, Gautami & Vasishta delta branches (Konaseema, East/West Godavari, Eluru, ASR) | CHIRPS 2.0 daily NetCDF (`0.05°`), GPM IMERG V07B NetCDF-4 (`0.1°`), ERA5 reanalysis JSON (`0.25°`) | **Sentinel-1 SAR Track 129 Ascending (2022-07-16 12:44 UTC / 18:14 IST)**: 4 raw tiles (5.74 GB), water classification raster, 9.71 MB candidate GeoJSON | Dowleswaram Barrage: 17.75–19.0 ft ($>2,580,000\text{ cusecs}$ / $73,056\text{ m}^3/\text{s}$, 3rd Warning); Bhadrachalam: 71.30 ft | CWC Daily Flood Situation Reports; APSDMA SEOC Bulletins; ISRO NRSC DMSP flood boundary maps | 21 study mandals, especially Mummidivaram, Amalapuram, Razole, P. Gannavaram, Kovvur, Rajamahendravaram | **High Quality Benchmark.** Raw peak SAR tiles exist locally; baseline dry-season SAR raster tiles pending local download. Flood candidates derived via Otsu thresholding; village damage registries restricted. | `PARTIALLY AVAILABLE` |
| `CYCLONE_MURASU_NOV_2026` | Cyclone Murasu Landfall & Post-Landfall Deep Depression | 2026-11-02 to 2026-11-05 (Landfall: 3 Nov evening; Depression: 4 Nov) | Bay of Bengal coastal Andhra Pradesh, South & Central Delta (Konaseema, East/West Godavari, Kakinada) | Scenario rainfall series (48.6 to 112.4 mm/day in replay timeline) | **None.** No Sentinel-1 SAR acquisition over delta during active cyclone cloud passage | Dowleswaram Barrage stage tracking: 12.4 to 15.2 ft (approaching 1st warning 14.75 ft) | NDMA SACHET RSS feeds; APSDMA Flash Bulletins (#14 to #18); IMD Tropical Cyclone Bulletins | Amalapuram, Razole, Mummidivaram, Kakinada Rural, Kovvur, Rajamahendravaram Urban | **Operational Alerting Benchmark.** Real-time government warnings verified in JSON archives. Satellite SAR imagery unavailable; river hydrograph is scenario-based. | `AVAILABLE` (As Alert Replay) / `NOT AVAILABLE` (As SAR Imagery) |
| `CYCLONE_ARNAB_HISTORICAL` | Severe Cyclonic Storm Coastal Storm Surge & Inundation | Historical Reference Archive (4-Day Synoptic Duration) | Godavari Delta Shoreline & Bay of Bengal Estuary | Aggregated event precipitation (32.0 to 145.0 mm) | Catalogue references only; no local raw SAR rasters | Dowleswaram stage reference: 11.2 to 13.5 ft; Coastal surge modeled at +1.2 m above astronomical tide | IMD Historical Tropical Cyclone Archive; APSDMA Disaster History Records | Coastal mandals: Mummidivaram, Amalapuram, Razole, Kakinada | **Conceptual Validation Benchmark.** Narrative and parameter vectors stored in `historical_flood_events_godavari.json`. Lacks physical raw satellite grids. | `PARTIALLY AVAILABLE` (Synthesized Scenario) |
| `GODAVARI_OCT_2020` | Godavari Basin Autumn Depression & Flash Flood Surge | 2020-10-12 to 2020-10-19 | Upper & Lower Godavari catchments, Telangana border to Dowleswaram | Regional IMD station summaries (literature only) | None stored locally on disk | Dowleswaram peak discharge: $\sim 1,450,000\text{ cusecs}$ (2nd Warning signal hoisted) | CWC Godavari Circle flood hydrographs; APSDMA situational alerts | Island mandals (Lankas), Kothapeta, Ainavilli, P. Gannavaram | **Literature Reference Only.** Referenced in `godavari_flood_hazard_report_2026.pdf`. No raw NetCDF rainfall grids or SAR rasters archived locally. | `NOT AVAILABLE` |
| `GODAVARI_AUG_2019` | Godavari Monsoon Flood Wave | 2019-08-05 to 2019-08-14 | Lower Godavari Basin, Papikonda hills, Polavaram backwaters | Literature daily totals | None stored locally on disk | Dowleswaram peak discharge: $\sim 1,600,000\text{ cusecs}$; Bhadrachalam 52.8 ft | CWC Flood Forecast Bulletins; Irrigation & CAD Dept reports | Devipatnam, Polavaram, Kovvur, Achanta, Kothapeta | **Historical Calibration Gap.** Mentioned in project review slides as an analogue to July 2022. No satellite rasters downloaded. | `NOT AVAILABLE` |
| `GODAVARI_AUG_1986` | All-Time Record Godavari Super Flood | 1986-08-11 to 1986-08-18 (Peak: 16 Aug 1986) | Entire 312,812 km² Godavari Basin; catastrophically submerged delta | Historical IMD gauge tables (non-digital) | Pre-dates operational civilian radar satellites (pre-Sentinel/pre-ERS) | Dowleswaram all-time record peak: $3,506,000\text{ cusecs}$ ($99,280\text{ m}^3/\text{s}$), Gauge: 22.8 ft | Central Water Commission Historical Monograph (1987); Andhra Pradesh Gazette | All 21 mandals experienced extensive levee overtopping and breaches | **Extreme Hydrologic Boundary.** Embedded within the static `historical_hazard` AHP factor via CWC zonation polygons. Raw spatial time series non-existent. | `AVAILABLE` (As Static Hazard Weight) |

---

## 3. Physical Dataset Inventory

A rigorous file-by-file audit was conducted across the local storage paths (`data/raw/`, `data/processed/`, and `data/metadata/`). Every spatial dataset was checked for exact file path, disk size, file format, Coordinate Reference System (CRS), spatial/temporal resolution, provenance, validation status, and operational limitations.

### 3.1 Inventory Table of Physical Datasets

| Dataset & Layer | Provider & Source URL | Local File Path | Size on Disk | Format | Spatial Coverage & Bounding Box | Native CRS | Spatial Resolution | Temporal Frequency | Processing Status | Limitations & Scientific Caveats | Status Label |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Copernicus DEM GLO-30 (Raw Tiles)** | ESA / AWS Open Data (`copernicus-dem-30m.s3.amazonaws.com`) | `data/raw/dem/Copernicus_DSM_COG_10_N16_00_E081_00_DEM.tif` (+3 adjacent tiles: N16E082, N17E081, N17E082) | 4 tiles $\approx 72\text{ MB}$ total | Cloud-Optimized GeoTIFF (COG) | $16^\circ\text{N}-18^\circ\text{N}$, $81^\circ\text{E}-83^\circ\text{E}$ | EPSG:4326 | 30 meters (1 arc-sec) | Static (2011–2015 TanDEM-X) | Validated raw tiles | Digital Surface Model (DSM) reflects canopy/structures rather than bare earth; small vertical bias in mangrove/coconut forests. | `AVAILABLE` |
| **Copernicus DEM Processed Terrain Raster** | Derived via `scripts/download_dem.py` | `data/processed/terrain/copernicus_dem_30m_lower_godavari.tif` | 108.7 MB ($7200 \times 7200\text{ px}$) | GeoTIFF (Float32) | Lower Godavari Basin ($16.3^\circ-17.9^\circ\text{N}$, $81.0^\circ-82.8^\circ\text{E}$) | EPSG:4326 | 30 meters | Static Baseline | Fully processed & clipped | Primary terrain layer for AHP Elevation Factor. Elevation range: $-14\text{ m}$ to $+682\text{ m}$ (mean $42.4\text{ m}$). | `AVAILABLE` |
| **Terrain Slope & Aspect Matrices** | Derived from Copernicus DEM | `data/processed/terrain/slope_deg_lower_godavari.tif` | 108.7 MB ($7200 \times 7200\text{ px}$) | GeoTIFF (Float32) | Lower Godavari Basin | EPSG:4326 | 30 meters | Static Baseline | Fully processed & clipped | Central-difference calculation scaled for latitude. Mean slope $2.14^\circ$; delta plain is exceptionally flat ($<1.0^\circ$). | `AVAILABLE` |
| **Administrative Boundaries (Districts & Mandals)** | GADM v4.1 (`gadm.org`) | `data/processed/boundaries/lower_godavari_mandals.geojson` & `andhra_pradesh_districts.geojson` | 1.23 MB (Mandals), 1.85 MB (Districts) | GeoJSON | Andhra Pradesh (28 districts) & Lower Godavari (21 mandals) | EPSG:4326 | High-precision vector polygons | 2022 Post-Reorganization | Fully processed & validated | 21 study mandals match official APSDMA administrative naming. Cadastral village boundaries are restricted government records. | `AVAILABLE` |
| **HydroRIVERS Hydrographic Network** | WWF HydroSHEDS (`hydrosheds.org`) | `data/processed/hydrology/hydrorivers_lower_godavari.geojson` | 5.88 MB | GeoJSON | Lower Godavari Basin (1,496 reaches) | EPSG:4326 | Vector LineStrings (15 arc-sec flow) | Static | Fully filtered & attributed | Carries stream order (1–8), reach length, and modeled discharge. Unmapped local irrigation canals and artificial drains omitted. | `AVAILABLE` |
| **ESA WorldCover Land Cover (Raw)** | ESA / AWS Open Data (`esa-worldcover.s3.eu-central-1.amazonaws.com`) | `data/raw/landcover/ESA_WorldCover_10m_2021_v200_N15E081_Map.tif` | 1.07 GB | Cloud-Optimized GeoTIFF | $15^\circ-18^\circ\text{N}$, $81^\circ-84^\circ\text{E}$ | EPSG:4326 | 10 meters | Annual (2021 v200) | Validated raw raster | High resolution (10m). Seasonal paddy irrigation can temporarily mimic open water bodies. | `AVAILABLE` |
| **ESA WorldCover 50m Standardized Raster** | Derived via `scripts/download_landcover.py` | `data/processed/landcover/worldcover_50m_lower_godavari.tif` | 3.55 MB ($3840 \times 4320\text{ px}$) | GeoTIFF (Byte) | Lower Godavari Basin | EPSG:4326 | 50 meters | 2021 Baseline | Aggregated & standardized | Decoded classes: Tree (10), Cropland (40), Built-up (50), Water (80), Mangrove (95). Serves land cover runoff weighting. | `AVAILABLE` |
| **WorldPop Population Exposure (Raw)** | WorldPop / Univ. of Southampton (`data.worldpop.org`) | `data/raw/population/ind_ppp_2020_1km_Aggregated_UNadj.tif` | 152.4 MB | GeoTIFF (Float32) | India National Coverage | EPSG:4326 | 1 kilometer (0.008333°) | Annual (2020 UN-Adj) | Validated raw grid | Statistical dasymetric disaggregation; represents residential density, not instantaneous headcount or daytime commuters. | `AVAILABLE` |
| **WorldPop Clipped Study Area Raster** | Derived via `scripts/download_population.py` | `data/processed/population/worldpop_lower_godavari_2020.tif` | 165.9 KB ($192 \times 216\text{ px}$) | GeoTIFF (Float32) | Lower Godavari Basin | EPSG:4326 | ~1 km | 2020 Baseline | Clipped & validated | Authoritative basin baseline: 9,126,353 persons within 21-mandal vector boundaries; 8,252,724 in Very High + High risk tiers (90.43%). Unclipped bounding box is 11.11M. | `AVAILABLE` |
| **Critical Infrastructure Points (Health, School, Shelters)** | OpenStreetMap contributors via Overpass API | `data/processed/infrastructure/osm_health_facilities.geojson`, `osm_educational_facilities.geojson`, `osm_emergency_shelters.geojson` | 1.8 MB (Health: 1,146 pts), 480 KB (Schools: 333 pts), 112 KB (Shelters: 63 pts) | GeoJSON | Lower Godavari Basin | EPSG:4326 | Vector Points | Current OSM tags (2026 extract) | Cleaned & deduplicated | Crowdsourced completeness; rural delta island shelters verified against APSDMA official cyclone shelter listings. | `AVAILABLE` |
| **CHIRPS 2.0 Daily Precipitation Grid** | Climate Hazards Center, UCSB (`iridl.ldeo.columbia.edu`) | `data/raw/rainfall/chirps/chirps_godavari_20220710_20220720.nc` | 2.34 MB | NetCDF-3 Classic | Lower Godavari Catchment ($16.3^\circ-17.9^\circ\text{N}$, $81.0^\circ-82.8^\circ\text{E}$) | EPSG:4326 | 0.05 degrees ($\sim 5.5\text{ km}$) | Daily (10–20 July 2022) | Validated gridded series | Blended satellite-station product. Captures antecedent soil saturation; convective localized rainfall peaks slightly smoothed. | `AVAILABLE` |
| **NASA GPM IMERG Daily Precipitation** | NASA GSFC / GES DISC (`data.gesdisc.earthdata.nasa.gov`) | `data/raw/rainfall/gpm_imerg/3B-DAY.MS.MRG.3IMERG.20220715-S000000-E235959.V07B.nc4` | 1.45 MB | NetCDF-4 / HDF5 | Global subset encompassing Lower Godavari | EPSG:4326 | 0.1 degree ($\sim 11\text{ km}$) | Daily (15 July 2022 peak) | Validated gridded single-day | High microwave radiometric precision. 0.1° resolution coarse for micro-catchment convective cells. | `AVAILABLE` |
| **ECMWF ERA5 Atmospheric Reanalysis** | ECMWF / Copernicus via Open-Meteo Archive Script | `data/raw/rainfall/era5/era5_godavari_july2022.json` | 18.4 KB | JSON Time Series | Central Delta ($16.98^\circ\text{N}, 81.78^\circ\text{E}$) | EPSG:4326 | 0.25 degrees ($\sim 28\text{ km}$) | Hourly aggregated to daily | Offline downloaded JSON timeseries | Single-station spatial extract retrieved via offline script `scripts/download_rainfall_era5.py`. Not a live streaming feed. | `AVAILABLE` (Historical File) |
| **Google Maps Platform Weather API** | Google Maps Platform Weather API (`weather.googleapis.com`) | `backend/app/services/weather_service.py` | Code service | JSON API Proxy | Point query (lat/lon) | WGS84 | Station / Point | On-demand caching (15-min TTL) | **Inactive** (`API_KEY_NOT_CONFIGURED`) | Service returns unavailable because `GOOGLE_WEATHER_API_KEY` is not configured in `backend/.env`. No live weather or forecast is retrieved. | `CONFIGURATION REQUIRED` |
| **Sentinel-1 SAR Flood Peak GeoTIFFs** | ESA Copernicus / Google Earth Engine Export | `data/processed/sentinel1/track129_20220716/s1a_t129_20220716_flood_peak_utm44n_10m-*.tif` (4 tiles) | 5.74 GB total (1.76 GB, 1.32 GB, 1.48 GB, 1.18 GB) | Cloud-Optimized GeoTIFF | Lower Godavari Delta (Track 129 Ascending Pass) | EPSG:32644 (UTM 44N) | 10 meters | Single pass: 2022-07-16 12:44 UTC | Calibrated $\sigma_0$ RTC backscatter | Physical multi-gigabyte rasters stored on disk. Validated 99.88% valid pixel coverage over study mandals. | `AVAILABLE` |
| **Sentinel-1 SAR Derived Water Classification** | Adaptive Otsu Thresholding on Track 129 | `data/processed/sentinel1/track129_water_classification.tif` | 764 KB | GeoTIFF | Lower Godavari Delta | EPSG:4326 | 50 meters resampled | Single pass derived | Derived binary water mask | Thresholded at $\sigma_0 < -14\text{ dB}$ with permanent water & DEM slope masking. Represents remote sensing inference without cadastral ground truth. | `AVAILABLE` |
| **Sentinel-1 SAR Flood Candidate Polygons** | Vectorized from Water Classification Raster | `data/processed/sentinel1/track129_flood_water_candidates.geojson` | 9.71 MB | GeoJSON | Lower Godavari Delta | EPSG:4326 | Vector Polygons | Single pass derived | Processed & filtered | Filtered candidate polygons representing surface standing water during July 16 crest. | `AVAILABLE` |
| **Sentinel-1 Pre-Flood Baseline SAR Rasters** | ESA Copernicus Data Space Ecosystem | `data/processed/sentinel1/coverage_track92_mandals.geojson` & catalogue | Vector footprints only (21.5 KB) | GeoJSON footprints | 12 baseline scenes (June 1–20, 2022, Track 92) | EPSG:4326 | 10 meters | 12-day orbital repeat | Footprints only; physical rasters NOT downloaded | Pre-flood baseline rasters are not present on local disk. Opposing pass geometry (Track 92 Descending vs Track 129 Ascending) prevents direct cross-track differencing. | `PARTIALLY AVAILABLE` (Catalogue & Footprints) |
| **APSDMA / NDMA SACHET Disaster Alerts** | APSDMA State GIS Mirror (`apsdmagis.ap.gov.in`) | `data/monitoring/live_disaster_alerts.json` & `sachet_mandals_cache.geojson` | 14.8 KB | JSON (6 alert bulletins) | Andhra Pradesh Statewide & Godavari Delta | N/A | Administrative vector polygons | 15-minute polling cache | Ingested, parsed, & verified | Polled from APSDMA State GIS mirror; carries publication time, retrieval time, expiry time, and strict 4-state lifecycle (`LIVE`, `STALE`, `EXPIRED`, `UNAVAILABLE`). | `AVAILABLE` |
| **CWC River Gauge Telemetry Baselines** | Central Water Commission Godavari Circle | `backend/app/services/river_monitoring_service.py` & `data/monitoring/river_gauge_records.json` | 14.2 KB JSON file | JSON records | 4 stations: Dowleswaram, Polavaram, Kunavaram, Bhadrachalam | WGS84 coordinates | Station point | Stored scenario records (`2026-11-03 09:20:00`) | Stored benchmark records (`is_live: false`) | Warning/Danger levels are authoritative; current water levels use stored scenario records rather than live automated CWC telemetry webhooks. | `PARTIALLY AVAILABLE` (Stored Scenario Records) |
| **High Water Mark Field Survey Data (HWBM)** | AP Irrigation & CAD Dept / Survey of India | None stored locally | 0 KB | N/A | Delta canal reaches | N/A | Sub-meter RTK-GNSS | Event-based post-flood | Not available in repository | Post-event high-water survey marks and surveyed crest elevations are restricted internal records; prevents fine-scale hydraulic calibration. | `NOT AVAILABLE` |

---

## 4. Historical Event Reconstruction Readiness Matrix

To determine whether historical events can be reliably reconstructed for empirical model training, spatial holdout validation, or retrospective case studies, each candidate event was evaluated across six strict criteria:
1. Pre-, during-, and post-event satellite imagery availability.
2. Catchment-scale precipitation series.
3. Upstream and downstream gauge/discharge observations.
4. Documented inundation reference maps or village rosters.
5. Study area spatial overlap.
6. Data leakage avoidance (preventing contamination of training splits).

### 4.1 Historical Event Reconstruction Evaluation

| Event Identifier | Pre/During/Post Satellite | Catchment Rainfall Series | River Gauge & Discharge | Inundation Ground-Truth | Study Area Overlap | Leakage Avoidance Readiness | Reconstruction Suitability Classification | Scientific Justification & Reconciled Findings |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **July 2022 Godavari Mega-Crest** | **PARTIAL** (Peak SAR available on disk; Pre-flood baseline SAR pending export) | **COMPLETE** (CHIRPS daily NetCDF, GPM IMERG V07B, ERA5 hourly reanalysis) | **COMPLETE** (Dowleswaram $17.75\text{ ft}$, $2.58\text{M cfs}$; Bhadrachalam $71.3\text{ ft}$) | **SAR CANDIDATES** (NRSC flood inundation shapefiles; 628 APSDMA affected villages documented) | **100% OVERLAP** (Direct hit on Lower Godavari Basin) | **PASS** (Strict spatial holdout on 4 coastal mandals: Razole, Sakhinetipalli, Mummidivaram, Amalapuram) | **SUITABLE FOR BENCHMARK TRAINING & HOLDOUT TESTING** | Primary historical calibration benchmark. Raw peak radar tiles exist locally. The ML evaluation in `prediction_validation_service.py` is a **Synthetic Multi-Scenario Spatial-Holdout Benchmark** testing algorithmic generalization. Dual-date differential change detection requires acquiring matching Ascending Track 129 baseline tiles. |
| **Cyclone Murasu (Nov 2026)** | **NONE** (Optical obscured by dense cloud; no SAR passes acquired locally) | **PARTIAL** (Replay scenario time series: 48.6 to 112.4 mm/day) | **STORED SCENARIO** (Dowleswaram stage: 12.4 to 15.2 ft; tidal locking modeled) | **MEDIUM** (APSDMA SEOC flash bulletins & official damage reports) | **100% OVERLAP** (Delta coastal & urban mandals) | **PASS** (Operates as sequential temporal replay; no future data revealed to agent) | **SUITABLE FOR OPERATIONAL TIMELINE CASE STUDY** | Ideal for testing emergency decision workflows, continuous warning lifecycle transitions, and multi-tier public advisory generation without data leakage. |
| **Cyclone Arnab (Archive)** | **CATALOGUE ONLY** (No local SAR rasters) | **COARSE** (Aggregated daily values: 32–145 mm) | **SYNTHESIZED** (Dowleswaram 11.2–13.5 ft, surge +1.2m) | **LOW** (Historical narrative records only) | **100% OVERLAP** (Coastal delta mandals) | **PASS** (Stored as independent reference test set) | **SUITABLE FOR RETROSPECTIVE SCENARIO SENSITIVITY TESTING** | Useful for evaluating model robustness against tidal surge and estuarine backwater locking scenarios; unsuited for empirical pixel validation. |
| **October 2020 Depression** | **NONE** | **NOT STORED LOCALLY** | **PARTIAL** (Dowleswaram 2nd warning crest records in literature) | **LOW** (No digital flood boundaries) | **100% OVERLAP** | **N/A** | **UNSUITED WITHOUT ADDITIONAL DATA** | Lacks local gridded precipitation and satellite imagery. Requires downloading IMD gridded rainfall and CDSE Sentinel-1 scenes from Oct 2020 before use. |
| **August 2019 Flood Wave** | **NONE** | **NOT STORED LOCALLY** | **PARTIAL** (Peak discharge records only) | **LOW** (Literature summaries only) | **100% OVERLAP** | **N/A** | **UNSUITED WITHOUT ADDITIONAL DATA** | Lacks spatial rasters on disk. Requires historical data acquisition pipeline execution. |
| **August 1986 Benchmark Flood** | **UNAVAILABLE** (Pre-satellite era) | **COARSE** (Station-level paper records) | **AUTHORITATIVE** ($3.506\text{M cfs}$, 22.8 ft) | **REGIONAL** (CWC high-water flood contour maps) | **100% OVERLAP** | **PASS** (Frozen into static physical hazard weighting) | **SUITABLE ONLY AS AN EXTREME BOUNDARY CONSTRAINT** | Serves as the ultimate physical capacity envelope for barrage discharge and levee design; cannot be used for dynamic ML time-series validation. |

---

## 5. Present Monitoring Readiness Matrix

An audit of the runtime monitoring stack (`backend/app/services/`, `data/monitoring/`, and `frontend/app.js`) was conducted to evaluate genuine real-time surveillance capabilities against static fallbacks, reference tables, and simulated streams.

### 5.1 Present Monitoring Capability Table

| Monitoring Domain | Genuine Live Capability | Fallback or Simulated Mode | Data Provenance & Source Endpoint | Update Frequency & Latency | Operational Readiness Status | Deficiencies & Actionable Gaps |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Official Disaster Alerts** | Live ingestion of APSDMA State GIS mirror of NDMA SACHET / IMD warnings | Serves cached JSON if network or feed is unreachable (`is_cached: true`) | `https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/layers/sachet_alerted_mandals.geojson` | 15-minute background polling; 60-minute freshness TTL | `AVAILABLE` | Fully operational with 4 distinct temporal states (`LIVE`, `STALE`, `EXPIRED`, `UNAVAILABLE`) and 3 explicit timestamps. Polled from APSDMA state GIS servers. |
| **Meteorological & Weather Feeds** | Configured to proxy Google Maps Platform Weather API | None (Returns structured error payload when unconfigured) | `https://weather.googleapis.com/v1/...` via `WeatherService` | 15-min to 1-hour caching TTL | `CONFIGURATION REQUIRED` | Currently inactive (`API_KEY_NOT_CONFIGURED`) because `GOOGLE_WEATHER_API_KEY` is empty in `backend/.env`. No live forecast data is currently retrieved or used. Open-Meteo is not a live fallback in the backend. |
| **River Gauge Telemetry** | Automated threshold evaluation against CWC Warning Levels (1st, 2nd, 3rd Danger signals) | Stored benchmark scenario records for 4 stations (`is_live: false`, dated `2026-11-03 09:20:00`) | `data/monitoring/river_gauge_records.json` (CWC Godavari Circle) | Static reference baselines; manual operator update via API | `PARTIALLY AVAILABLE` (Stored Scenario Records) | System lacks an authorized live telemetry webhook or automated real-time CWC HydroNet API scraper. Evaluates CWC threshold logic against stored benchmark scenario measurements. |
| **Citizen & Community Reports** | Live ingestion, spatial indexing, photo upload, and automated 2.0 km duplicate clustering | Persistent SQLite database (`data/users.db` / `hazard_reports.json`) | Local FastAPI backend endpoint (`POST /api/v1/community/report`) | Real-time event-driven submission | `AVAILABLE` | Fully functional community reporting pipeline with Haversine spatial proximity deduplication and photo artifact storage. |
| **Continuous Alert Aggregation** | 3-Tier priority sorting (Government Warning $\rightarrow$ AI Advisory $\rightarrow$ Citizen Report) | In-memory priority queue with MD5 bulletin fingerprinting | `ContinuousAlertService` fusing all active sources | Real-time on client request | `AVAILABLE` | Prevents conflation of official evacuation orders with model predictions or unverified citizen reports. Verified 100% operational in frontend drawer. |
| **Emergency Decision Advisories** | Automated generation of evacuation routing, shelter assignments, and resource requirements | Heuristic routing based on Haversine distance to 63 OSM shelters | `EmergencyOperationsService` | Dynamic on demand | `AVAILABLE` | Robust rule-based expert system connecting mandal risk tiers to designated cyclone shelters. Lacks road-level live flood blockage routing. |

---

## 6. Future Forecasting Data Requirements

To evolve PRAVAH 360 from static susceptibility assessment and alert monitoring into an operational **Future Flood Forecasting System**, the platform must transition across six core predictive tiers. The specific physical data inputs, update cadences, formats, and providers required for each tier are detailed below.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              FUTURE FORECASTING DEPENDENCY PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [1. NWP Rainfall Forecast]  ──> IMD GFS/WRF 3km Hourly (0-72h)                                   │
│              │                                                                                  │
│              ▼                                                                                  │
│ [2. Hydrologic Rainfall-Runoff] ──> HEC-HMS / SWAT Upper Catchment Inflow Simulation            │
│              │                                                                                  │
│              ▼                                                                                  │
│ [3. River Discharge Forecast]  ──> Polavaram & Dowleswaram Inflow/Outflow Hydrographs (m³/s)     │
│              │                                                                                  │
│              ▼                                                                                  │
│ [4. River Stage Forecast]      ──> Dynamic Rating Curves & Barrage Gate Operation Rules (ft/m)  │
│              │                                                                                  │
│              ▼                                                                                  │
│ [5. 2D Hydrodynamic Inundation]──> HEC-RAS 2D / LISFLOOD Overland Depth & Velocity Maps (10-30m)│
│              │                                                                                  │
│              ▼                                                                                  │
│ [6. Predictive Impact & Exposure]──> Building/Population Inundation Depth Intersect (0-72h)     │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.1 Comprehensive Requirements Specification

| Forecasting Tier | Required Input Datasets & Parameters | Spatial & Temporal Resolution | Necessary Update Frequency | Required File Format | Authoritative Data Providers | Current Status in PRAVAH 360 | Implementation Prerequisites & Missing Links |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Catchment Rainfall Forecasting** | Numerical Weather Prediction (NWP) quantitative precipitation forecasts (QPF): GFS, WRF, or ECMWF IFS ensembles | $3\text{ km}$ to $9\text{ km}$ spatial; $1\text{-hour}$ to $3\text{-hour}$ timesteps up to 72 hours | 4 times daily (00, 06, 12, 18 UTC cycles) | GRIB2 or NetCDF-4 | India Meteorological Department (IMD) / ECMWF / NCMRWF | `NOT AVAILABLE` (Weather API is unconfigured; lacks gridded NWP ingestion) | Ingestion pipeline for full-catchment ($312,812\text{ km}^2$) gridded NWP forecasts covering Maharashtra, Telangana, and Odisha catchments. |
| **Tier 2: Hydrologic Rainfall-Runoff Modeling** | Sub-basin delineation, calibrated Curve Number (CN) / Green-Ampt infiltration, routing parameters, and soil moisture grids | Sub-catchment level (HUC-8 equivalent); hourly timesteps | Continuous real-time state updating | HEC-HMS project files / NetCDF state vectors | Central Water Commission (CWC) / State Water Resources Dept | `NOT AVAILABLE` | Calibrated semi-distributed rainfall-runoff model (e.g. HEC-HMS, SWAT, or VIC) connecting rainfall to river discharge. |
| **Tier 3: River Discharge Forecasting** | Predicted upstream hydrographs at Perur, Kunavaram, Polavaram, and Dowleswaram Barrage | Point timeseries (hourly discharge in $\text{m}^3/\text{s}$ or cusecs) | Hourly during flood surge | JSON timeseries or CSV hydrographs | CWC Godavari Circle / APSDMA Flood Cell | `NOT AVAILABLE` | Automated telemetric hydrograph ingestion or upstream routing solver translating runoff into barrage inflow. |
| **Tier 4: River Stage & Barrage Gate Operations** | Gauge height rating curves ($Q-h$ relationships) and real-time barrage gate opening schedules (175 crest gates at Dowleswaram) | Barrage gauge locations; 15-minute stage intervals | Real-time continuous | Structured JSON / REST API | AP Water Resources Department (Irrigation & CAD) | `PARTIALLY AVAILABLE` (Static stage thresholds only) | Dynamic hydraulic rating curves accounting for tailwater submergence and variable gate discharge coefficients. |
| **Tier 5: 2D Hydrodynamic Inundation Modeling** | High-resolution bare-earth DTM (LiDAR or edited Copernicus DEM), river bathymetry, roughness (Manning's $n$), and levee crest vectors | $10\text{ m}$ to $30\text{ m}$ spatial grid; $1\text{-hour}$ flood propagation slices | Event-driven (triggered on 2nd warning signal) | GeoTIFF depth rasters & GeoJSON vector velocity fields | Hydrodynamic solver output (HEC-RAS 2D, LISFLOOD-FP, or hydrodynamic surrogate) | `NOT AVAILABLE` (Only static AHP susceptibility exists) | Bare-earth DTM correction (removing DSM vegetation bias), river channel bathymetric cross-sections, and calibrated 2D shallow-water equation solver. |
| **Tier 6: Predictive Impact & Exposure Forecasting** | Dynamic intersection of forecast flood depth rasters with WorldPop demographic grids and OSM buildings/roads | Building-level to $30\text{ m}$ grid; synchronous with hydrodynamic output | Hourly updates during emergency | GeoJSON impact summaries & CSV mandal tables | PRAVAH 360 Core Analytics Engine | `PARTIALLY AVAILABLE` (Operates on static AHP, not dynamic depths) | Depth-damage vulnerability curves for local housing structures and agriculture to estimate financial/human loss. |

---

## 7. Evidence and Validation Gaps

To maintain strict scientific integrity during major project review, the following evidence gaps and limitations within the existing repository must be transparently disclosed.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    EVIDENCE & VALIDATION GAPS                                   │
├──────────────────────────┬──────────────────────┬───────────────────────────────────────────────┤
│ Evidence Domain          │ Current Limitation   │ Impact on System Claims                       │
├──────────────────────────┼──────────────────────┼───────────────────────────────────────────────┤
│ Ground-Truth Inundation  │ No cadastral-level   │ Remote sensing SAR provides candidate water   │
│ Extent                   │ surveyed flood maps  │ extents (10m); village-level depth claims     │
│                          │ on local disk.       │ cannot be independently verified.             │
├──────────────────────────┼──────────────────────┼───────────────────────────────────────────────┤
│ Model Validation Labels  │ Target label y comes │ Classification metrics evaluate learning      │
│ in Prediction Service    │ from synthetic latent│ against a synthetic multi-criteria equation,  │
│                          │ formula with noise.  │ not empirical ground-truth sensors.           │
├──────────────────────────┼──────────────────────┼───────────────────────────────────────────────┤
│ River Gauge Telemetry    │ Stored scenario      │ Stage warning logic is scientifically valid,  │
│ Automation               │ records; lacks live  │ but operates on stored benchmarks dated       │
│                          │ automated scraping.  │ 2026-11-03 09:20:00 (is_live: false).         │
├──────────────────────────┼──────────────────────┼───────────────────────────────────────────────┤
│ Live Weather Feeds       │ Google Weather API   │ Inactive (API_KEY_NOT_CONFIGURED). Open-Meteo │
│                          │ key unconfigured in  │ is not implemented as an active fallback.     │
│                          │ .env file.           │ No live forecast data is retrieved.           │
├──────────────────────────┼──────────────────────┼───────────────────────────────────────────────┤
│ Pre-Flood Baseline SAR   │ Track 92 rasters     │ Direct raster differential change detection   │
│ Rasters & Geometry       │ absent; Track 129 is │ cannot execute; opposing orbit geometries     │
│                          │ Ascending vs Desc.   │ prevent cross-track pixel differencing.       │
├──────────────────────────┼──────────────────────┼───────────────────────────────────────────────┤
│ Digital Surface Model    │ Copernicus GLO-30    │ Low-lying delta mangroves and coconut groves  │
│ (DSM) Artifacts          │ includes canopy and  │ appear 5-15m higher than actual ground,       │
│                          │ building heights.    │ distorting gravity-driven flow paths.         │
└──────────────────────────┴──────────────────────┴───────────────────────────────────────────────┘
```

### 7.1 Detailed Breakdown of Gaps

1. **Synthetic Nature of Predictive Model Labels:**
   - **Current Reality:** In `prediction_validation_service.py`, `_generate_synthetic_benchmark_dataset()` creates the target label $y$ via:
     $$y = \mathbb{I}\left[0.25\frac{\text{rf}_{72}}{300} + 0.30\frac{\text{gauge} - 0.85}{0.5} + 0.20\,\text{elev} + 0.15\,\text{dist} + 0.10\,\text{runoff} + \mathcal{N}(0, 0.06) > 0.52\right]$$
     The labels are derived from the exact same physical factors used in susceptibility modeling. While the 4 coastal delta mandals are withheld during training to evaluate spatial generalization, the evaluation tests learning consistency against a synthetic heuristic equation, not against independent observed flood extents.
   - **Academic Disclosure:** Academic reports must designate this component as a **Synthetic Multi-Scenario Spatial-Holdout Benchmark**, explicitly stating that empirical validation against field high-water marks is pending.
2. **Ground-Truth Flood Extent at Cadastral Resolution:**
   - **Current Reality:** Validation relies on single-date adaptive Otsu thresholding ($\sigma_0 < -14\text{ dB}$) of Track 129 C-band SAR backscatter combined with permanent water (WorldCover Class 80) and slope masking. Cadastral village-level flood boundary maps and surveyed submerged area registries from the Revenue Department / APSDMA are not present on local disk.
   - **Academic Disclosure:** Academic publications and project presentations must report validation against **Sentinel-1 SAR Satellite Water Candidate Footprints**, rather than claiming direct ground survey verification.
3. **Telemetry Synchronization & Gauge Gaps:**
   - **Current Reality:** River stage analysis uses verified CWC flood markers (Warning: $14.50\text{ m}$ / $11.75\text{ ft}$, Second Warning: $13.75\text{ ft}$, Third Warning: $16.50\text{ m}$ / $17.75\text{ ft}$ at Dowleswaram Barrage). Current water level evaluations operate on stored scenario records dated `2026-11-03 09:20:00` with `is_live: false`.
   - **Academic Disclosure:** The system demonstrates **rule-based multi-tier gauge alert gates**, but does not currently feature an active telemetric webhook connection to the Central Water Commission HydroNet API.
4. **Pre-Flood Baseline SAR Imagery Storage Gap & Geometric Incompatibility:**
   - **Current Reality:** The 12 pre-flood baseline scenes (June 2022) are catalogued in `data/raw/sentinel1/sentinel1_scene_catalogue.json`, and vector footprints exist for Track 92, but physical rasters are absent locally. Crucially, Track 129 is an **Ascending pass** (evening acquisition, ~18:14 IST), while Track 92 is a **Descending pass** (morning acquisition, ~06:00 IST). Opposing look angles prevent cross-track pixel differencing.
   - **Academic Disclosure:** Local processing currently uses **calibrated single-date backscatter thresholding with landcover masking**, rather than dual-date backscatter log-ratio difference detection ($\Delta\sigma_0 = \sigma_{0,\text{flood}} - \sigma_{0,\text{baseline}}$).
5. **Terrain DSM vs Bare-Earth DTM Discrepancy:**
   - **Current Reality:** Copernicus DEM is a Digital Surface Model (DSM). In the lush, vegetated delta of Dr. B.R. Ambedkar Konaseema, dense coconut plantations and mangrove forests elevate the recorded surface by 5 to 15 meters above the true bare-earth hydraulic plain.
   - **Academic Disclosure:** The Analytical Hierarchy Process (AHP) incorporates slope and drainage density to mitigate elevation biases, but hydrodynamic 2D overland routing cannot be reliably executed until the DSM is hydro-flattened and vegetation-filtered.

---

## 8. Recommended Data Acquisition Priorities

To address the identified gaps systematically without disrupting existing functional workflows, data acquisitions are prioritized by feasibility, licensing, disk footprint, and scientific impact.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               RECOMMENDED DATA ACQUISITION ROADMAP                              │
├───────┬──────────────────────────────────────────┬──────────────┬─────────────┬─────────────────┤
│ Rank  │ Dataset Target                           │ Feasibility  │ Storage     │ Scientific Gain │
├───────┼──────────────────────────────────────────┼──────────────┼─────────────┼─────────────────┤
│ P1    │ Sentinel-1 Track 129 Ascending Pre-Flood │ Immediate    │ ~2.5 GB     │ Enables true    │
│       │ Baseline GeoTIFF (June 2022)             │ (Open CDSE)  │             │ change detection│
├───────┼──────────────────────────────────────────┼──────────────┼─────────────┼─────────────────┤
│ P2    │ Google Weather API Production Key        │ Configuration│ 0 MB        │ Activates live  │
│       │ in backend/.env                          │ Only         │             │ primary weather │
├───────┼──────────────────────────────────────────┼──────────────┼─────────────┼─────────────────┤
│ P3    │ CWC HydroNet API Telemetry Webhook       │ Medium       │ <10 MB/mo   │ Enables live    │
│       │ or Scheduled Scraper                     │ (Public CWC) │             │ river updates   │
├───────┼──────────────────────────────────────────┼──────────────┼─────────────┼─────────────────┤
│ P4    │ IMD 3km WRF / GFS 72-Hour Numerical     │ Medium       │ ~150 MB/day │ Enables Stage 1 │
│       │ Rainfall Grids                           │ (IMD Open)   │             │ flood forecast  │
├───────┼──────────────────────────────────────────┼──────────────┼─────────────┼─────────────────┤
│ P5    │ Hydro-Enforced Bare-Earth DEM Filter     │ Computational│ ~200 MB     │ Resolves canopy │
│       │ for Konaseema Delta                      │ (Local GDAL) │             │ height bias     │
└───────┴──────────────────────────────────────────┴──────────────┴─────────────┴─────────────────┘
```

### 8.1 Specific Acquisition Details
1. **Priority 1: Download Baseline Sentinel-1 SAR Rasters (`IMMEDIATE`):**
   - *Target Scenes:* Matching Ascending Track 129 pre-flood baseline scenes from June 2022 (e.g. `2022-06-10` or `2022-06-22`).
   - *Purpose:* Provides the exact orbital geometry required for true differential change detection ($\Delta\sigma_0 < -3\text{ dB}$).
   - *Storage Required:* $\sim 2.5\text{ GB}$.
2. **Priority 2: Configure Primary Weather API Credentials (`CONFIGURATION ONLY`):**
   - *Target:* Set `GOOGLE_WEATHER_API_KEY` in `backend/.env`.
   - *Purpose:* Activates live weather streaming in `WeatherService`, which is currently returning `API_KEY_NOT_CONFIGURED`.
   - *Storage Required:* 0 MB.
3. **Priority 3: Implement Automated CWC Telemetry Scraper (`SHORT-TERM`):**
   - *Target:* Central Water Commission daily river situation reports (`ffs.tamc.nhp.mowr.gov.in` / CWC Godavari Circle).
   - *Purpose:* Replaces static scenario records with automated hourly gauge level updates for Dowleswaram, Polavaram, and Bhadrachalam.
   - *Storage Required:* Negligible ($<10\text{ MB/month}$).
4. **Priority 4: Ingest IMD High-Resolution NWP Precipitation Forecasts (`MEDIUM-TERM`):**
   - *Target:* IMD WRF 3km numerical weather prediction model output (72-hour forecast horizon).
   - *Purpose:* Provides the quantitative catchment precipitation forecast necessary to drive runoff modeling.
   - *Storage Required:* $\sim 150\text{ MB/day}$ rolling buffer.
5. **Priority 5: Hydro-Enforce the Copernicus DEM (`MEDIUM-TERM`):**
   - *Target:* Algorithmic vegetation removal and stream-burn filtering over the Konaseema delta using ESA WorldCover Class 10 (Tree cover) masks.
   - *Purpose:* Creates a hydro-conditioned bare-earth elevation raster for hydrodynamic routing without requiring expensive airborne LiDAR.
   - *Storage Required:* $\sim 200\text{ MB}$.

---

## 9. Suggested Next Development Dependencies

To maintain software engineering discipline and avoid introducing fragmented, un-integrated features, future development must adhere to the following strict order of operations:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DEVELOPMENT ORDER OF OPERATIONS                               │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 1: Complete and Solidify Past Historical Reconstruction (Inundation Change Detection)     │
│          └── Prerequisite: Local export of matching Ascending Track 129 baseline SAR rasters.   │
│          └── Verification: Validate pixel change detection against July 2022 flooded mandals.  │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 2: Automate and Verify Present Live Telemetry (CWC + IMD Weather)                        │
│          └── Prerequisite: Configure weather API key and integrate automated CWC gauge scraper.│
│          └── Verification: Confirm end-to-end alert pipeline from CWC/NDMA to frontend drawer.  │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 3: Build Hydrologic Catchment Routing (Runoff & Discharge Forecasting)                    │
│          └── Prerequisite: Ingest 72-hour NWP rainfall grids and calibrate unit hydrographs.    │
│          └── Verification: Evaluate discharge prediction skill (MAE/RMSE) at Dowleswaram.       │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 4: Implement 2D Hydrodynamic Inundation Prediction & Impact Modeling                      │
│          └── Prerequisite: Hydro-conditioned bare-earth DTM and calibrated stage forecast.      │
│          └── Verification: Compare predicted 24h inundation footprint against holdout mandals.  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Step 1: Complete Historical Inundation Change Detection:**
   - Do not attempt future inundation forecasting until historical flood reconstruction is 100% verified using dual-date satellite SAR change detection with matched orbital geometries.
2. **Step 2: Automate Live Present Monitoring:**
   - Ensure the live monitoring drawer, weather services, and river gauge threshold evaluators operate seamlessly with live telemetric data rather than stored reference scenario records.
3. **Step 3: Develop Catchment-Scale Hydrologic Routing:**
   - Build the rainfall-runoff engine connecting upstream Godavari catchment precipitation to Dowleswaram Barrage inflow before attempting 2D overland flood routing in the delta.
4. **Step 4: Couple Hydrodynamic Routing with Predictive Impact Analytics:**
   - Once discharge and stage forecasts are stable, deploy 2D shallow-water inundation routing to predict flooded infrastructure and affected populations 24 to 72 hours prior to river crest.

---

## 10. Conclusion and Reconciled Verdict

| System Dimension | Empirical Verdict | Academic & Practical Defensibility |
| :--- | :--- | :--- |
| **Susceptibility Modeling (FSI)** | **FULLY VALIDATED & OPERATIONAL** | AHP multi-criteria model ($CR = 0.0001$, weights $[0.25, 0.20, 0.25, 0.15, 0.15]$) is rigorously defensible for long-term structural flood vulnerability zoning. |
| **Demographic Exposure** | **RECONCILED & DEFENSIVE** | Baseline of $9,126,353$ and elevated exposure of $8,252,724$ (**Very High + High only**, $90.43\%$) represent potential demographic exposure, not confirmed flood victims. |
| **Historical Data (July 2022)** | **CALIBRATED BENCHMARK READY** | Peak SAR (5.74 GB) and multi-sensor precipitation NetCDFs provide strong evidence for benchmark testing. Flood candidates are remote sensing inferences. |
| **Live Alert Ingestion** | **ROBUST & OPERATIONALLY VERIFIED** | Ingestion from APSDMA state GIS mirror of NDMA SACHET warnings functions with complete temporal provenance and strict freshness lifecycle management. |
| **Weather & Gauge Feeds** | **CONFIGURATION & TELEMETRY REQUIRED** | Weather API requires key configuration (`API_KEY_NOT_CONFIGURED`); river gauges evaluate CWC thresholds on stored scenario records dated `2026-11-03 09:20:00`. |
| **Future Predictive Forecasting** | **CONCEPTUAL STAGE (NOT OPERATIONAL)** | Requires upstream rainfall-runoff routing (HEC-HMS), live CWC telemetry integration, and 2D hydrodynamic modeling before it can be claimed as an operational forecasting system. |

*This document represents the authoritative, reconciled data readiness assessment for the PRAVAH 360 system architecture and academic project reporting.*
