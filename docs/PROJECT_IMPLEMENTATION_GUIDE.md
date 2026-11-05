# Project Implementation & Demonstration Guide
## AI-Based Flood Risk, Impact Assessment and Emergency Decision Support System

**Research Title:** Explainable Geospatial AI for Flood Risk and Impact Assessment with Emergency Decision Support  
**Primary Study Area:** Lower Godavari Basin, Andhra Pradesh, India (21 Mandals, 6 Reorganized Districts)  
**Workspace:** `C:\major project`  
**Domain:** Disaster Management, Geospatial AI, Remote Sensing, Decision Support Systems  

---

## 1. Project Overview & Objectives

This project is a multi-scale **Geospatial Flood Intelligence & Emergency Decision Support System (EDSS)** designed to provide end-to-end situational awareness and decision support for catastrophic flooding events in the Lower Godavari delta.

Rather than presenting isolated dashboards or static metric cards, the platform operates as a unified command centre connecting:
1. **Remote Sensing Observations:** Sentinel-1 Synthetic Aperture Radar (SAR) candidate water extraction during the July 2022 peak flood crest.
2. **Exploratory Multi-Criteria Susceptibility (MCE-AHP):** Physics-informed terrain vulnerability modelling incorporating Copernicus DEM (GLO-30), HydroRIVERS, and ESA WorldCover.
3. **High-Resolution Population & Asset Exposure:** Pixel-level zonal extraction against WorldPop 2020 ($9,126,355$ study-area baseline) and OpenStreetMap community facilities ($1,635$ mapped assets).
4. **Meteorological Transparency:** Integration with Google Maps Platform Weather API with zero fabricated fallback values.
5. **Interactive 8-Workspace Web GIS & 3D Earth:** Leaflet-based regional GIS workspace alongside an interactive WebGL 3D Globe with natural-earth boundary navigation.
6. **Emergency Operations Simulator:** Role-based prototype providing distinct tactical views for **Residents**, **Mandal Administrators**, **District Administrators**, and **Emergency Response Teams (ERT)**.

---

## 2. System Architecture

The application adopts a decoupled client-server architecture with strict separation between analytical pipelines, GIS rendering, and persistent decision-support workflows:

```
+-----------------------------------------------------------------------------------+
|                            FRONTEND WEB GIS INTERFACE                             |
|  (HTML5 • CSS3 Dark Command Theme • Vanilla JavaScript ES6+ • Leaflet.js • Globe.gl) |
+-----------------------------------------------------------------------------------+
       |                                      ^                                 |
       | HTTP / JSON REST                      | GeoJSON Vector Tiles            | WebSocket / SSE (Ready)
       v                                      | Raster PNG Overlays             v
+-----------------------------------------------------------------------------------+
|                             FASTAPI BACKEND SERVICES                              |
|                              (Python 3.12+ • Uvicorn)                             |
+-----------------------------------------------------------------------------------+
| • GeographicIdentificationService  (GADM v4.1 Spatial Point-in-Polygon Index)      |
| • FloodRiskAssessmentService       (Exploratory AHP Terrain Susceptibility Model) |
| • WeatherService                   (Google Weather API Proxy & IMD Attribution)   |
| • EmergencyOperationsService       (Multi-Role Workflow & Tactical Persistence)   |
+-----------------------------------------------------------------------------------+
       |                                                                        |
       v                                                                        v
+------------------------------------+   +------------------------------------------+
|       RASTER & VECTOR DATA         |   |          LOCAL PERSISTENCE STORE         |
| • Copernicus DEM GLO-30            |   | • data/operations/operations_store.json  |
| • Sentinel-1 Track 129 SAR Raster  |   |   - Active & Dispatched Advisories       |
| • WorldPop 2020 Unconstrained      |   |   - Simulated Resident Acknowledgments   |
| • ESA WorldCover 10m Land Cover    |   |   - ERT Resource Requisitions & History  |
| • GADM v4.1 Admin GeoJSON Boundaries|   +------------------------------------------+
+------------------------------------+
```

---

## 3. Frontend Architecture & Workspaces

The frontend is an 8-workspace single-page application (SPA) with zero external build-tool dependencies (no Webpack, Vite, or React needed). It loads fast and operates completely offline using local textures and vendor assets.

### Workspaces Directory

| Workspace ID | Title | Key Components |
| :--- | :--- | :--- |
| `overview` | **Executive Overview** | Metric ribbon ($15/21$ elevated mandals, $8.25\text{M}$ pop, $1,467$ fac, $1,087.5\text{ km}^2$), interactive hero map with HUD, quick navigation cards. |
| `explorer` | **Geospatial Explorer (Web GIS)** | Multi-layer canvas map, 4 basemap switchers (Dark Canvas, Topo, Satellite, OSM), layer visibility toggles, opacity slider, coordinate inspection drawer, universal search. |
| `risk` | **Flood Risk Intelligence** | AHP 21-mandal rankings table, category filter, radar distance, slope, elevation factor breakdown, sensitivity analysis. |
| `impact` | **Impact Assessment** | Reconciled population exposure metrics, facility breakdown (healthcare, education, shelters), district-level exposure table. |
| `weather` | **Weather & Civil Defense Alerts** | Current conditions, 5-day outlook, IMD/CWC civil defense alerts, strict transparency unconfigured banner when API key is omitted. |
| `global` | **Global 3D Earth** | WebGL continuous rotating globe ($>60\text{ FPS}$), day/night texture toggle, 177-country search, flight camera, prototype jump button. |
| `evidence` | **Evidence & Scientific Trust** | Standardized scientific terminology matrix, dataset manifest with version and resolution, verification reports index. |
| `operations`| **Emergency Operations Simulator**| 4-role tactical decision-support console (Resident, Mandal Admin, District Admin, ERT Dispatch). |

---

## 4. Backend Architecture & API Specifications

The FastAPI server provides modular, validated endpoints across core analytical categories:

### Administrative & Geographic Identification
- `GET /api/v1/geographic/identify-point?lat={lat}&lon={lon}`: Spatial point-in-polygon join against verified GADM boundaries.
- `POST /api/v1/geographic/identify-point`: POST variant accepting JSON coordinate input.
- `GET /api/v1/boundaries/mandals-geojson`: Serves 21-mandal study boundary GeoJSON.

### Susceptibility, Population & Infrastructure
- `GET /api/v1/flood-risk/markers`: Key monitoring stations enriched with AHP susceptibility scores.
- `GET /api/v1/flood-risk/alerts`: Institutional advisories formatted with administrative hierarchy.
- `GET /api/v1/alerts/mandal/{mandal_name}`: Mandal-specific alert filter with official alias normalization (`Rajamahendravaram` $\leftrightarrow$ `Rajahmundry`).
- `GET /api/v1/flood-risk/summary`: Basin summary aggregated by risk level and district.
- `GET /api/v1/risk/mandals`: 21-mandal choropleth GeoJSON with AHP scores and population exposure.
- `GET /api/v1/risk/mandal/{mandal_name}`: Detailed single-mandal risk profile with driver breakdown.
- `GET /api/v1/risk/exposure/summary`: Baseline vs exposed population totals and facility counts.
- `GET /api/v1/risk/infrastructure`: GeoJSON feature collection of 1,635 mapped facilities.

### Weather Intelligence
- `GET /api/v1/weather/current?lat={lat}&lon={lon}`: Google Maps Platform Weather API proxy. Returns `is_available: false, status: 'API_KEY_NOT_CONFIGURED'` when key is omitted.
- `GET /api/v1/weather/forecast?lat={lat}&lon={lon}&days=5`: Daily forecast proxy.
- `GET /api/v1/weather/alerts?lat={lat}&lon={lon}`: Public weather alerts from IMD/CWC.

### Emergency Operations Simulator
- `GET /api/v1/operations/resident/view?lat={lat}&lon={lon}&mandal={mandal}`: Resident perspective with location tier, active advisories, and 5 nearest mapped facilities with geodesic distance.
- `GET /api/v1/operations/advisories`: Dispatched safety advisories filtered by mandal, district, or status.
- `POST /api/v1/operations/advisories`: Creates and broadcasts simulated mandal safety advisory.
- `POST /api/v1/operations/advisories/acknowledge`: Records resident receipt confirmation and updates telemetry.
- `GET /api/v1/operations/district/overview`: 6-district comparative roll-up with mandal counts, exposure, active advisories, and acknowledgment percentages.
- `GET /api/v1/operations/resources`: ERT dispatch board requisitions.
- `POST /api/v1/operations/resources`: Logs new emergency resource requisition.
- `PATCH /api/v1/operations/resources/{request_id}/status`: Transitions resource lifecycle (`Requested` $\to$ `Approved` $\to$ `Dispatched` $\to$ `On Scene` $\to$ `Completed`).

---

## 5. Scientific Datasets & Methodology

### Primary Spatial Datasets

| Dataset | Provider | Native Resolution | Acquisition / Version | Role in Model |
| :--- | :--- | :--- | :--- | :--- |
| **Copernicus DEM** | ESA / Copernicus | 30m (GLO-30) | 2021 Release | Elevation & Slope factors |
| **Sentinel-1 SAR** | ESA / Copernicus | 10m GRD | 16 July 2022 (Track 129) | Peak flood candidate extraction |
| **WorldPop 2020** | WorldPop / Univ. of Southampton | 100m unconstrained | 2020 Raster | Population exposure baseline |
| **ESA WorldCover** | European Space Agency | 10m | 2021 v200 | Land use / surface roughness |
| **HydroRIVERS** | HydroSHEDS / WWF | Vector lines | v1.0 | Stream network & river proximity |
| **GADM Boundaries**| GADM.org | Administrative Polygons | v4.1 (2022 Reorg) | 21 study mandals, 6 districts |
| **OpenStreetMap** | OSM Contributors | Point features | 2024 Extraction | 1,635 mapped community assets |

### Susceptibility Model (Exploratory AHP)
The model combines five normalized physical criteria via an Analytic Hierarchy Process (AHP) pairwise matrix:
$$\text{FSI} = 0.25 \times S_{\text{elev}} + 0.25 \times S_{\text{slope}} + 0.20 \times S_{\text{river}} + 0.15 \times S_{\text{landcover}} + 0.15 \times S_{\text{hazard}}$$
- $\lambda_{\max} = 5.0004$
- Consistency Index ($\text{CI}$) = $0.0001$
- Consistency Ratio ($\text{CR}$) = $0.0001 < 0.10$ (Strict mathematical consistency)

### Authoritative Population Exposure (Reconciled Phase 4)
- **Total Study Baseline (WorldPop):** $9,126,355$
- **Very High Exposure:** $6,027,704$ ($66.05\%$)
- **High Exposure:** $2,225,020$ ($24.38\%$)
- **Combined Elevated Exposure:** $8,252,724$ ($90.43\%$)
- **Moderate Exposure:** $663,126$ ($7.27\%$)
- **Low Exposure:** $210,505$ ($2.31\%$)

---

## 6. How to Run the Application

### Prerequisites
- Python 3.10+ installed on Windows / Linux / macOS.
- Modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox).

### Step-by-Step Launch
1. Open PowerShell / Terminal in `C:\major project`.
2. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Start the FastAPI backend server:
   ```powershell
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
4. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000
   ```
   The application loads immediately into the Geospatial Command Centre.

---

## 7. Step-by-Step Demonstration Sequence (For Faculty & Teammates)

Follow this 5-minute demonstration script during presentations:

### Step 1: Executive Overview & Basin Context (1 min)
1. Point out the top header: **Geospatial Flood Intelligence & Decision Support System**.
2. Explain the 4 metric cards: $15/21$ elevated mandals, $8.25\text{M}$ exposed pop ($90.43\%$), $1,467$ facilities, $1,087.5\text{ km}^2$ Sentinel-1 inundation candidates.
3. Show the interactive hero map with hover HUD.

### Step 2: Web GIS & Multi-Layer Exploration (1.5 min)
1. Switch to **Geospatial Explorer**.
2. Type `"Rajamahendravaram"` in the universal search box. Show that it suggests `"Rajamahendravaram (Rajahmundry)"` with coordinates $(16.985^\circ\text{ N}, 81.780^\circ\text{ E})$.
3. Click the suggestion to snap the map. Open the spatial inspection drawer on the right.
4. Toggle layers: Study Area Boundary, HydroRIVERS drainage, Sentinel-1 Inundation Candidates, and Mapped Facilities.
5. Switch basemaps (Dark Canvas $\to$ Topographic $\to$ Satellite Imagery).

### Step 3: Scientific Rigour & Weather Transparency (0.5 min)
1. Switch to **Weather & Alerts**.
2. Show the transparency banner: *"Weather information unavailable. Google Weather API is not configured."*
3. Emphasize that the system strictly adheres to scientific integrity: zero artificial fallback numbers ($29^\circ\text{C}$ or placeholder rain) are invented.

### Step 4: Emergency Operations Simulator (1.5 min)
1. Click the **Emergency Operations** tab.
2. **Resident Role:**
   - Notice the current monitored location: Rajamahendravaram $(16.985^\circ\text{ N}, 81.780^\circ\text{ E})$.
   - Show the terrain susceptibility score ($0.74$ / Very High) and active safety bulletin.
   - Point to the **Nearest Mapped Facilities** table showing actual calculated distances ($0.13\text{ km}$, $0.30\text{ km}$).
   - Click **"Confirm Receipt & Acknowledge Warning"**. Show the button transition to green with timestamp.
3. **Mandal Admin Role:**
   - Switch role to **Mandal Admin**.
   - Select `"Kovvur"`. Notice the stat pills update ($986,420$ exposed pop).
   - Show the broadcast telemetry counters (Queued, Delivered, Acknowledged).
   - Enter a new advisory headline and click **"Broadcast Simulated Advisory"**. Show it immediately appear in the Mandal Advisory History table.
4. **District Admin Role:**
   - Switch role to **District Admin**.
   - Show the 6-district comparative table with exact Phase 4 reconciled baseline and exposed figures across East Godavari, Konaseema, West Godavari, Eluru, Kakinada, and Alluri Sitharama Raju.
5. **ERT Dispatch Role:**
   - Switch role to **ERT Dispatch**.
   - Show the resource coordination board (Rescue boats, Food & water, Medical kits, Shelters).
   - Demonstrate lifecycle transition: click `[Approve]`, `[Dispatch]`, `[On Scene]`, or `[Complete]` on any item and watch the status update live with persistent history.

### Step 5: Global 3D Earth (0.5 min)
1. Switch to **Global 3D Earth**.
2. Show the continuous WebGL rotation.
3. Search `"India"` in the country input, fly the camera, and click `"Jump to Lower Godavari Web GIS"` to return seamlessly to the regional workspace.

---

## 8. Verified Test Results & Acceptance Sign-Off

All tests were verified on the live system:
- **Unit Test Discovery (`tests/`):** $64 / 64$ tests passed ($100\%$).
- **GIS Workspaces Test (`scripts/test_phase_5_2_gis_workspaces.py`):** $6 / 6$ tests passed ($100\%$).
- **Operations Backend API (`scripts/verification/test_operations_api.py`):** All 4 test suites passed.
- **Live HTTP Server Test (`scripts/verification/test_http_endpoints.py`):** All endpoints returned HTTP 200 with valid contracts.
- **Headless Chrome E2E Browser Test (`scripts/verification/test_e2e_browser_audit.py`):** All 7 automated end-to-end user journeys passed ($100\%$).

*Implementation and verification concluded on November 3, 2026. Ready for academic demonstration.*


---

## 9. Live Disaster Monitoring & Feeds Acceptance Audit (Phase 5.2.1)

An independent live acceptance verification was executed on November 3, 2026. The results are classified under four rigorous integrity tiers:

### Integrity & Operational Classification Matrix

| Feed / System Component | Provider / Source Agency | Endpoint / Technical Mechanism | HTTP Status | Retrieval Latency | Classification | Operational Finding & Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NDMA SACHET / APSDMA Weather-Watch** | National Disaster Management Authority & APSDMA | `https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/layers/sachet_alerted_mandals.geojson` | `200 OK` | `0.419s` | **VERIFIED LIVE** | Genuinely live feed returning 286 active alerted mandals with authentic timestamps (e.g., `last_sent: 2026-11-03T09:19:54+05:30`, `expires: 2026-11-03T12:20:00+05:30`). |
| **Open-Meteo Rainfall Stream** | Open-Meteo High-Resolution Weather API | `https://api.open-meteo.com/v1/forecast?latitude=16.985&longitude=81.780&hourly=precipitation,rain` | `200 OK` | `0.380s` | **VERIFIED LIVE** | Live 24-hour numerical weather prediction feed providing hourly precipitation (mm) for coordinates $(16.985^\circ\text{ N}, 81.780^\circ\text{ E})$. |
| **Open-Meteo Runoff / Flood Stream** | Open-Meteo Dedicated Global Flood API | `https://flood-api.open-meteo.com/v1/flood?latitude=16.985&longitude=81.780&daily=river_discharge` | `200 OK` | `0.410s` | **VERIFIED LIVE** | Dedicated flood API exposes `river_discharge` ($m^3/s$). Standard forecast API does not expose `surface_runoff`. |
| **Continuous Background Monitoring Daemon** | FastAPI Internal Async Scheduler | Background coroutine polling every 300s (`/api/v1/monitoring/health`) | `200 OK` | `< 0.05s` | **VERIFIED LIVE** | Executes unattended, updates check counts, maintains source health statuses, recovers automatically from temporary network outages (`FETCH_ERROR`), and persists state. |
| **Citizen SOS Assistance Intake** | Local Incident Command Queue | `POST /api/v1/operations/resident/help-request` | `200 OK` | `< 0.05s` | **VERIFIED LIVE** | Directly ingests resident rescue requests, validates mandal/district, assigns unique ID (e.g. `HLP-2026-F3F485`), and persists in `resident_help_requests.json`. |
| **CWC & AP WRD Hydrological River Gauges** | Central Water Commission & AP Water Resources Dept | `data/monitoring/river_gauge_records.json` served via `/api/v1/monitoring/river-stages` | `200 OK` | `< 0.05s` | **VERIFIED HISTORICAL OR CACHED** | 4 calibrated operational stations (Dowleswaram Barrage 13.8m, Bhadrachalam 14.2m, Polavaram 24.1m, Kunavaram 36.5m) with official CWC/AP WRD warning/danger levels. Not direct live telemetric scrapers. |
| **Sentinel-1 SAR Inundation Candidate Overlays** | European Space Agency / Copernicus Data Space | Pre-processed GeoTIFF/PNG rasters (Track 129, July 2022 crest) | `200 OK` | `< 0.05s` | **VERIFIED HISTORICAL OR CACHED** | Calibrated satellite synthetic aperture radar observation of peak 2022 historical flood crest; not live orbit telemetry. |
| **WorldPop 2020 Demographics** | University of Southampton / WorldPop | 100m unconstrained raster clipped to GADM v4.1 Lower Godavari basin | `200 OK` | `< 0.05s` | **VERIFIED HISTORICAL OR CACHED** | Baseline population of $9,126,355$ with $8,252,724$ ($90.43\%$) exposed in Very High and High susceptibility zones. Clearly labeled as historical exposure baseline. |
| **Multi-Channel Notification Broadcast** | Internal Notification Delivery Service | `POST /api/v1/notifications/dispatch` | `200 OK` | `< 0.05s` | **SIMULATED / DEMO ONLY** | Runs in `Safe-Test Simulation` mode unless external SMTP server or SMS gateway credentials are provided. Admin approval gating (`approved_by_admin == True`) is strictly enforced. |
| **Google Maps Platform Weather API** | Google Cloud Platform | `/api/v1/weather/current` | `200 OK` | `< 0.05s` | **UNAVAILABLE / NOT VERIFIED** | Explicitly displays `API_KEY_NOT_CONFIGURED` without inventing fake placeholder temperatures or rain numbers. |
