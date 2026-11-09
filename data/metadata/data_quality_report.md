# Geospatial Data Quality, Integrity, and Limitations Report

## 1. Executive Summary
All downloaded datasets have been systematically audited for file integrity, Coordinate Reference System (CRS) compliance, spatial intersection with the study area, attribute validity, and data-type correctness. All 13 primary raster/gridded datasets and 8 vector layers passed integrity tests without corruption.

---

## 2. Gridded and Raster Data Quality Audit
| Dataset | Format | Dimensions | CRS | Resolution | Intersects Study Area | Value Range / Units |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NASA GPM IMERG Daily (V07B)** | NetCDF-4/HDF5 | 1 x 3600 x 1800 | EPSG:4326 | 0.1° (~11 km) | **YES** | 0.0 to 27.5 mm/day (Godavari) |
| **Copernicus DEM (N16E081)** | COG | 3600 x 3600 | EPSG:4326 | 30m | **YES** | -4.5m to 237.0m |
| **Copernicus DEM Slope** | GeoTIFF | 3600 x 3600 | EPSG:4326 | 30m | **YES** | 0.0° to 36.2° |
| **Copernicus DEM Aspect** | GeoTIFF | 3600 x 3600 | EPSG:4326 | 30m | **YES** | 0.0° to 360.0° |
| **WorldPop India Raw** | GeoTIFF | 3451 x 3508 | EPSG:4326 | ~1 km | **YES** | 0 to 45,000+ persons/km² |
| **WorldPop Lower Godavari** | GeoTIFF | 192 x 216 | EPSG:4326 | ~1 km | **YES** | ~11.11M baseline persons |
| **ESA WorldCover 10m Raw** | COG | 36000 x 36000 | EPSG:4326 | 10m | **YES** | Classes 10–100 |
| **ESA WorldCover 50m Clipped** | GeoTIFF | 3840 x 4320 | EPSG:4326 | 50m | **YES** | Cropland 24%, Water 19%, Tree 43% |
| **CHIRPS 2.0 Daily Precipitation** | NetCDF3 | 36 x 32 x 11 | EPSG:4326 | 0.05° (~5.5 km) | **YES** | 0 to 125+ mm/day |
| **ECMWF ERA5 Daily Reanalysis** | JSON / Series | 11 daily timesteps | WGS84 | Point/Basin | **YES** | 100.5 mm 72-hr antecedent storm |

---

## 3. Vector Layer Quality Audit
- **Lower Godavari Study Area Polygon**: EPSG:4326, valid closed bounding polygon enclosing $16.3^\circ\text{N}-17.9^\circ\text{N}$, $81.0^\circ\text{E}-82.8^\circ\text{E}$.
- **Andhra Pradesh Districts**: 13 districts from GADM v4.1; valid MultiPolygons.
- **Lower Godavari Mandals / Taluks**: 21 subdistricts across East & West Godavari (Amalapuram, Kakinada, Rajamahendravaram, Mummidivaram, Kothapeta, etc.); geometries valid.
- **HydroRIVERS Godavari Reaches**: 1,496 reaches filtered from 1.42 million Asian river reaches; contains Strahler stream orders 1 through 9, channel length, and modeled discharge.
- **OpenStreetMap Infrastructure**: 1,206 healthcare centers, 366 educational institutions, and 63 emergency shelters; all point geometries verified within study bounding box.

---

## 4. GPM IMERG Daily File Schema & Schema Reconciliation
- **Schema Model**: NetCDF-4 Classic/Enhanced Data Model (NetCDF 4.7.1 / HDF5 1.10.5).
- **Group Hierarchy**: Root-level datasets (`/`). Unlike GPM Half-Hourly products (`3B-HHR`), which nest datasets under `/Grid/`, the official GPM Final Daily product (`3B-DAY`) stores variables directly at root.
- **Variable Nomenclature**: Calibrated daily rainfall is stored as `precipitation` (`long_name: Daily mean precipitation rate (combined microwave-IR) estimate. Formerly precipitationCal.`).
- **Validation Resolution**: Corrected validation logic to inspect root-level variables and verified full spatial and temporal integrity.
