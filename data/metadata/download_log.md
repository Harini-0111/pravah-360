# Dataset Download & Acquisition Log

**Execution Timestamp**: 2026-11-01 (NASA Earthdata Authentication Reverification)
**Study Area**: Lower Godavari Basin, Andhra Pradesh, India
**Benchmark Flood Event**: Historic July 2022 Godavari flood (Discharge >2.58M cusecs at Dowleswaram Barrage)

---

## 1. Automated Direct Downloads (Completed Successfully)
| Dataset | Source / Protocol | Local Path | Size | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Copernicus DEM GLO-30** | AWS S3 HTTPS (Public) | `data/raw/dem/*.tif` | 129.2 MB (4 tiles) | SUCCESS |
| **WorldPop India 2020** | WorldPop Open CDN | `data/raw/population/*.tif` | 18.3 MB | SUCCESS |
| **ESA WorldCover 10m 2021** | AWS S3 HTTPS (Public) | `data/raw/landcover/*.tif` | 39.5 MB | SUCCESS |
| **HydroSHEDS HydroRIVERS** | HydroSHEDS Portal | `data/raw/rivers/*.zip` | 90.5 MB | SUCCESS |
| **GADM v4.1 Admin Boundaries** | GADM Geodata CDN | `data/raw/boundaries/*` | 3.7 MB | SUCCESS |
| **CHIRPS 2.0 Daily Precipitation** | Columbia IRI REST API | `data/raw/rainfall/chirps/*.nc` | 52.2 KB | SUCCESS |
| **ECMWF ERA5 Daily Rainfall** | Open-Meteo / Copernicus | `data/raw/rainfall/era5/*.json` | 1.2 KB | SUCCESS |
| **OSM Infrastructure Features** | Overpass REST API | `data/processed/infrastructure/*.geojson` | ~1.8 MB | SUCCESS |

---

## 2. Satellite Scenes Catalogued with Automated Pipeline Ready
- **Sentinel-1 SAR GRD (IW, VV+VH)**: 8 scenes during flood peak (July 14–18, 2022) and 12 baseline scenes (June 2022) catalogued in `data/raw/sentinel1/sentinel1_scene_catalogue.json`. Reusable GEE extraction script prepared in `scripts/gee/download_sentinel1.py`.

---

## 3. NASA Earthdata Reverification & GPM IMERG Status
- **Authentication**: **PASS** (HTTP 200). Username `har***9` verified against official Earthdata Login token endpoint.
- **Data Endpoint**: **VERIFIED** on Earthdata Cloud at `https://data.gesdisc.earthdata.nasa.gov/data/GPM_L3/GPM_3IMERGDF.07/2022/07/3B-DAY.MS.MRG.3IMERG.20220715-S000000-E235959.V07B.nc4`.
- **Authorization & EULA**: **ACTION REQUIRED**. Earthdata Cloud egress returns HTTP 403 `EULA Acceptance Failure`.
- **Resolution Step**: Visit `https://urs.earthdata.nasa.gov/approve_app?client_id=e2WVk8Pw6weeLUKZYOxvTQ` in browser and click "Agree".
- **Download Automation**: `scripts/download_rainfall_gpm.py` is configured with automated Bearer token retrieval and HDF5 spatial/variable validation for Lower Godavari Basin.
