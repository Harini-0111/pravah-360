# Terrain, Land Cover, Population & Exposure Datasets Technical Validation Report

**Project**: Explainable Geospatial AI for Flood Risk, Impact Assessment and Emergency Decision Support
**Phase**: Phase 3 — Flood Data Validation and Analysis
**Study Area**: Lower Godavari Basin ($16.3^\circ\text{N}-17.9^\circ\text{N}$, $81.0^\circ\text{E}-82.8^\circ\text{E}$)
**Date**: November 1, 2026

---

## 1. Executive Summary

This report documents the rigorous technical validation of the static and structural geospatial layers required for flood risk, terrain flow modeling, and exposure assessment:
1. **Copernicus DEM GLO-30**: Elevation, Slope, and Aspect.
2. **ESA WorldCover 10m & 50m**: Discrete thematic land cover classes.
3. **WorldPop 2020**: Demographic baseline population exposure.
4. **HydroSHEDS HydroRIVERS**: Topological stream network and modeled discharge.
5. **OpenStreetMap Critical Infrastructure**: Healthcare, education, and emergency shelters.
6. **GADM v4.1 Administrative Boundaries**: Districts and Mandals.

All 11 raster layers and 8 vector layers passed 100% of automated integrity checks without corruption.

---

## 2. Digital Elevation Model (Copernicus DEM GLO-30)

### 2.1 Essential Scientific Distinction: DSM vs. DTM
> [!IMPORTANT]
> **Copernicus DEM GLO-30 is a Digital Surface Model (DSM)**, based on TanDEM-X X-band radar interferometry (2011–2015). It captures the elevation of the **uppermost reflective surface** (including tree canopies, mangrove tops, and buildings), **not a bare-earth Digital Terrain Model (DTM)**.
> - In dense coconut groves and mangrove belts of the Konaseema delta, surface heights may exceed bare ground by $5\text{ to }15\text{ meters}$.
> - Hydrodynamic simulations must account for this canopy offset in coastal vegetation zones.

### 2.2 Raster Audit Results

| Dataset / Tile | Dimensions | Data Type | CRS | Min Elevation | Max Elevation | File Size | Coverage |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **N16E081 Raw COG** | $3600 \times 3600$ | Float32 | EPSG:4326 | $-4.50\text{ m}$ | $237.01\text{ m}$ | $35.8\text{ MB}$ | Delta mouth, Konaseema, Vasishta/Gautami branches |
| **N16E082 Raw COG** | $3600 \times 3600$ | Float32 | EPSG:4326 | $-9.10\text{ m}$ | $64.16\text{ m}$ | $8.3\text{ MB}$ | Kakinada coast, Coringa mangroves, shallow mudflats |
| **N17E081 Raw COG** | $3600 \times 3600$ | Float32 | EPSG:4326 | $-9.42\text{ m}$ | $1,361.85\text{ m}$ | $47.3\text{ MB}$ | Rajamahendravaram, Polavaram gorge, Eastern Ghats |
| **N17E082 Raw COG** | $3600 \times 3600$ | Float32 | EPSG:4326 | $-2.59\text{ m}$ | $1,584.42\text{ m}$ | $37.8\text{ MB}$ | Papikonda hill ranges, northern catchment boundary |
| **Processed Elevation (N16E081)** | $3600 \times 3600$ | Float32 | EPSG:4326 | $-4.50\text{ m}$ | $237.01\text{ m}$ | $51.8\text{ MB}$ | Standardized elevation raster |
| **Processed Slope (deg)** | $3600 \times 3600$ | Float32 | EPSG:4326 | $0.00^\circ$ | $36.17^\circ$ | $51.8\text{ MB}$ | Slope gradient derived via 30m grid |
| **Processed Aspect (deg)** | $3600 \times 3600$ | Float32 | EPSG:4326 | $0.00^\circ$ | $360.00^\circ$ | $51.8\text{ MB}$ | Flow direction azimuth ($0^\circ-360^\circ$) |

---

## 3. Land Cover (ESA WorldCover 2021)

- **Raw Product**: `ESA_WorldCover_10m_2021_v200_N15E081_Map.tif` ($36,000 \times 36,000\text{ pixels}$, $39.5\text{ MB}$)
- **Processed Clipped Grid**: `esa_worldcover_lower_godavari_50m.tif` ($3,840 \times 4,320\text{ pixels}$, $16.6\text{ MB}$)
- **Thematic Class Codes Verified**:
  - `10`: Tree cover (Dense plantation / forests: $43.2\%$)
  - `20`: Shrubland ($0.8\%$)
  - `30`: Grassland ($1.1\%$)
  - `40`: Cropland (Intensive paddy agriculture: $24.1\%$)
  - `50`: Built-up (Towns, settlements, roads: $6.4\%$)
  - `60`: Bare / sparse vegetation ($1.9\%$)
  - `80`: Permanent water bodies (Godavari mainstem, canals: $18.8\%$)
  - `90`: Herbaceous wetland ($0.4\%$)
  - `95`: Mangroves (Coringa wildlife sanctuary & estuary: $3.3\%$)

---

## 4. Population Exposure (WorldPop 2020)

- **Raw National Grid**: `ind_ppp_2020_1km_Aggregated_UNadj.tif` ($3,451 \times 3,508\text{ pixels}$, $18.3\text{ MB}$)
- **Clipped Study Area Grid**: `worldpop_lower_godavari_2020.tif` ($192 \times 216\text{ pixels}$, $166\text{ KB}$)
- **Resolution**: $\approx 1\text{ km}$ ($0.008333^\circ$)
- **Data Units**: Estimated persons per grid cell (UN-adjusted 2020 population model)
- **Lower Godavari Baseline Population Sum**: **$11,112,918\text{ persons}$** ($\approx 11.11\text{ Million}$)
- **Maximum Pixel Density**: $22,313.8\text{ persons/km}^2$ (Rajamahendravaram urban center)
- **Methodological Safeguard**: In accordance with project boundaries, this represents baseline residential exposure potential, **never confirmed flood casualties or evacuees**.

---

## 5. Hydrological River Network (HydroSHEDS HydroRIVERS)

- **Local Layer**: `data/processed/rivers/lower_godavari_hydrorivers.geojson` ($1.34\text{ MB}$)
- **Total Reaches Filtered**: **$1,496\text{ reaches}$**
- **Geometry Validity**: **$100\%$ valid LineStrings** ($1496/1496$)
- **Stream Orders**: Strahler stream orders from order $1$ (minor tributaries) up to order $9$ (Godavari mainstem channel)
- **Key Attributes Verified**: `ORD_STRA`, `LENGTH_KM`, `DIS_AV_CMS` (modeled discharge in cubic meters/second).

---

## 6. Critical Infrastructure (OpenStreetMap)

All OpenStreetMap point features were spatially validated within the Lower Godavari bounding box:
1. **Healthcare Facilities**: `osm_healthcare.geojson` ($700.8\text{ KB}$)
   - **Count**: **$1,206\text{ features}$** ($100\%$ valid Point geometries)
   - Types: Hospitals, Community Health Centers, Primary Health Centers, clinics.
2. **Educational Institutions**: `osm_education.geojson` ($149.1\text{ KB}$)
   - **Count**: **$366\text{ features}$** ($100\%$ valid Point geometries)
   - Types: Government schools, colleges, zilla parishad high schools.
3. **Designated Emergency Shelters**: `osm_emergency_shelters.geojson` ($22.8\text{ KB}$)
   - **Count**: **$63\text{ features}$** ($100\%$ valid Point geometries)
   - Types: Cyclone shelters, flood relief buildings, community centers.

---

## 7. Administrative Boundaries (GADM v4.1)

- **State Level**: Andhra Pradesh boundary ($13\text{ districts}$, MultiPolygons, $100\%$ valid).
- **District Level**: East Godavari and West Godavari ($2\text{ districts}$, MultiPolygons, $100\%$ valid).
- **Mandal Level**: $21\text{ sub-districts}$ across Lower Godavari delta ($100\%$ valid MultiPolygons).
- **Village Level Policy**: Confirmed strict adherence to Phase 2 rule: **no unverified village boundaries or fabricated place names**.
