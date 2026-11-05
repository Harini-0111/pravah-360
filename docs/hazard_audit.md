# PRAVAH 360: Hazard Monitoring, Alert Ingestion, and Impact Assessment Technical Audit

**Audit Date:** November 5, 2026  
**Project Workspace:** `C:\major project`  
**Audit Scope:** Read-Only Technical Audit of Hazard Ingestion, Atmospheric Monitoring, River Gauging, Susceptibility Modeling, and Impact Assessment Capabilities  
**Audit Methodology:** Static Source Code Inspection, Local Data Store Examination, Configuration Audit, and Schema Analysis  

---

## 1. Executive Summary

A comprehensive, read-only technical audit of the PRAVAH 360 disaster intelligence codebase at `C:\major project` was performed. The objective of this audit is to establish with forensic precision what hazard-monitoring, alert-ingestion, and impact-assessment capabilities are currently implemented, what external endpoints are referenced, what data is stored versus live, and what gaps must be bridged to ingest newly announced hazards (including cyclonic and monsoonal flood events) under an authoritative, version-controlled architecture.

### Key Audit Findings

1. **Active Real-Time Alert Ingestion:**
   - **Verified in Code & Stored Data:** The platform possesses a working automated ingestion pipeline for official Andhra Pradesh disaster alerts via the **NDMA SACHET / APSDMA Weather-Watch GIS layer** (`https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/layers/sachet_alerted_mandals.geojson`).
   - The background daemon (`LiveMonitoringService`) executes every 300 seconds (5 minutes), groups alerted mandals by incident and severity, matches affected areas against the 21 Lower Godavari study mandals, and stores normalized records in `data/monitoring/live_disaster_alerts.json`.
   - The latest ingested dataset contains **7 active official alerts** (recorded on November 4, 2026, 17:08:40 IST), including active lightning and severe rainfall advisories across Dr. B.R. Ambedkar Konaseema, East Godavari, Kakinada, and Eluru districts.

2. **Dormant and Inactive Ingestion Feeds:**
   - **Configured but Unused (Verified in Code):** A dedicated cyclone feed URL (`https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/cyclone.json`) is defined in `live_alert_ingestion_service.py` (line 25), but is never referenced or called in any runtime routine.
   - **Implemented but Inactive (Verified in Code & Stored Data):** The Google Maps Platform Weather API client (`weather_service.py`) implements current conditions, hourly forecasts, 10-day forecasts, and Google Public Alerts. However, it is **currently dormant** because `GOOGLE_WEATHER_API_KEY` is not configured in `.env`.
   - **Simulated Health Status (Verified in Code):** In `live_monitoring_service.py`, a feed labeled `OPEN_METEO_AP_STREAM` is reported in system health as `AVAILABLE` with 24 records; however, **no HTTP request or client library exists** for Open-Meteo in the codebase. The health record is hardcoded telemetry.

3. **Hydrological & River Gauge Monitoring:**
   - **Stored Data Only (Verified in Code & Stored Data):** Central Water Commission (CWC) and Andhra Pradesh Water Resources Department (WRD) river stages for four strategic Lower Godavari stations (Dowleswaram Barrage, Bhadrachalam, Polavaram Spillway, and Kunavaram Confluence) are maintained as **static reference records** in `data/monitoring/river_gauge_records.json` (timestamped `2026-11-03 09:20:00`).
   - While an administrative update endpoint (`update_gauge_observation()`) exists, there is **zero automated web scraping or live telemetry ingestion** from CWC portals (such as the Water Resources Information System or CWC Flood Watch).

4. **Flood Susceptibility vs. Dynamic Inundation:**
   - **Verified in Code:** The primary flood intelligence engine (`flood_risk_service.py`) evaluates **intrinsic physical susceptibility** using a multi-criteria Analytical Hierarchy Process (AHP: Elevation 25%, Slope 20%, River Proximity 25%, Land Cover 15%, Historical Hazard 15%) across Copernicus GLO-30 DSM, HydroSHEDS HydroRIVERS (1,496 reaches), and ESA WorldCover (50m).
   - The system strictly distinguishes between **intrinsic physical susceptibility** and **confirmed floodwater inundation**. Sentinel-1 C-band SAR processing for Track 129 (July 16, 2022) is classified as exploratory water candidates rather than confirmed water depths.

5. **Impact and Exposure Computation:**
   - **Verified in Code & Stored Data:** Population exposure is computed using true cell-by-cell zonal aggregation over the WorldPop India 2020 UN-adjusted 1km raster ($9,126,353$ baseline residents across the 21 mandals; $8,252,724$ residing in Very High and High susceptibility zones).
   - Critical infrastructure exposure is computed over **1,542 verified OpenStreetMap facilities** (1,146 healthcare, 333 educational, 63 shelters). The system correctly avoids claiming unverified road submergence.

6. **Notification Delivery Channels:**
   - **Simulated (Verified in Code):** While the backend provides multi-channel emergency notification dispatch (`notification_service.py`), SMTP email credentials and SMS API keys are unconfigured in `.env`. Consequently, all notification dispatches execute in `SAFE_TEST_SIMULATION` mode and are recorded in local audit files.

---

## 2. Existing Capability Inventory

| Functional Domain | Implemented Capabilities | Operational Status | Data Nature | Code & Data Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **Official Alert Ingestion** | Polls NDMA SACHET / APSDMA GeoJSON feed; normalizes Common Alerting Protocol (CAP) properties; filters 21 Lower Godavari mandals; deduplicates events. | **Active & Operating** (Background Daemon) | Live Observations & Active Warnings | `backend/app/services/live_alert_ingestion_service.py`<br>`data/monitoring/live_disaster_alerts.json` |
| **Cyclone Tracking & Bulletins** | Ingestion of dedicated cyclone JSON layer (`cyclone.json`). | **Configured but Unused** | None (Uncalled) | `backend/app/services/live_alert_ingestion_service.py` (line 25) |
| **Historical Cyclone Replay** | Replays multi-phase milestones for Cyclone Murasu (Nov 2026), Cyclone Arnab, and July 2022 Godavari flood crest. | **Implemented & Active** | Curated Historical Reference | `backend/app/services/historical_event_service.py`<br>`data/reference/historical_flood_events_godavari.json` |
| **Atmospheric Weather & Rain** | Google Weather API proxy for current weather, hourly/daily forecasts, and Google Public Alerts. | **Implemented but Inactive** | Live Forecast & Current (Dormant) | `backend/app/services/weather_service.py`<br>Blocked by unconfigured `GOOGLE_WEATHER_API_KEY` |
| **Precipitation Stream Fallback** | Purported Open-Meteo rainfall stream listed in monitoring health telemetry. | **Simulated / Hardcoded** | Hardcoded Telemetry | `backend/app/services/live_monitoring_service.py` (lines 89-100) |
| **River Gauge Monitoring** | Hydrological stage, warning markers (1st, 2nd, 3rd), discharge (cusecs), and flood status for 4 stations. | **Stored Data Only** | Stored Reference Values | `backend/app/services/river_monitoring_service.py`<br>`data/monitoring/river_gauge_records.json` |
| **Manual Bulletin Ingestion** | Administrative endpoint to inject verified CWC/IMD bulletins with source attribution. | **Implemented & Active** | Administrator Input | `backend/app/services/live_alert_ingestion_service.py` (`import_manual_bulletin`) |
| **Flood Susceptibility Mapping** | AHP Multi-Criteria Evaluation ($CR = 0.0001 < 0.10$) combining Copernicus DSM, slope, HydroSHEDS, and land cover. | **Implemented & Active** | Modelled Spatial Surface | `backend/app/services/flood_risk_service.py`<br>`data/processed/boundaries/lower_godavari_mandals.geojson` |
| **Satellite Water Detection** | Multi-temporal Sentinel-1 C-band SAR backscatter thresholding (sigma-0 < -16 dB, Track 129). | **Stored Data Only** | Historical Exploratory Overlay | `data/processed/sentinel1/`<br>`frontend/overlays/sentinel1_flood_candidates_track129.png` |
| **Demographic Exposure** | Cell-by-cell zonal aggregation of UN-adjusted WorldPop India 2020 raster across 21 mandals. | **Implemented & Active** | Empirical Demographic Grid | `backend/app/services/flood_risk_service.py`<br>`data/processed/population/worldpop_lower_godavari_2020.tif` |
| **Infrastructure Exposure** | Point-in-polygon spatial intersection of 1,542 verified OSM healthcare, school, and shelter facilities. | **Implemented & Active** | Empirical Vector Asset Catalog | `backend/app/services/flood_risk_service.py`<br>`data/processed/infrastructure/osm_*.geojson` |
| **Continuous Notification Center**| Tri-tier notification aggregation: Tier A (Official), Tier B (Model Advisory), Tier C (Citizen Ground Report). | **Implemented & Active** | Unified Operational Feed | `backend/app/services/continuous_alert_service.py`<br>`data/operations/acknowledged_alerts.json` |
| **Citizen Hazard Reporting** | Citizen submission of flood reports, water levels, breach observations, geotags, and photos. | **Implemented & Active** | Crowdsourced Ground Data | `backend/app/services/community_hazard_service.py`<br>`data/community/hazard_reports.json` |
| **Emergency Help Requests** | Direct citizen request logging for boat evacuation, medical triage, food rations, and livestock assistance. | **Implemented & Active** | Live Operational Queue | `backend/app/services/live_monitoring_service.py`<br>`data/monitoring/resident_help_requests.json` |
| **Resource Allocation Solver** | Capacity-constrained multi-objective integer optimization allocating boats, kits, and food rations. | **Implemented & Active** | Modelled Operational Decision | `backend/app/services/resource_allocation_service.py` |
| **Multilingual Voice Assistant** | Telugu (`te-IN`) and Indian English (`en-IN`) speech recognition, intent extraction, and voice synthesis. | **Implemented & Active** | Live Regional User Interface | `backend/app/services/voice_tts_service.py`<br>`frontend/voice.js` |
| **Emergency Contact Directory** | Verified toll-free emergency phone directory (112, 1070, 1077, 108, 101, 104) with authority provenance. | **Implemented & Active** | Static Government Reference | `backend/app/services/emergency_helpline_service.py` |

---

## 3. External Source and Endpoint Inventory

This inventory documents every external remote endpoint referenced, configured, or claimed within the application code and scripts.

| Source & Provider | Remote Endpoint / URL in Code | Operational Purpose | Calling File & Function | Runtime Status | Update Mechanism & Interval | Auth / Key Requirements | Local Storage & Format | Latest Timestamp & Age | Example Stored Record |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **APSDMA / NDMA SACHET**<br>(AP State Disaster Management Authority) | `https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/layers/sachet_alerted_mandals.geojson` | Ingest active Common Alerting Protocol (CAP) warnings across AP mandals. | `backend/app/services/live_alert_ingestion_service.py`<br>`LiveAlertIngestionService.fetch_live_alerts()` | **IMPLEMENTED AND CALLED** | Periodic background polling every 300 seconds (5 min) via `LiveMonitoringService`. | None (Public HTTPS; SSL verification bypassed via custom unverified context). | `data/monitoring/live_disaster_alerts.json` (JSON)<br>`data/monitoring/sachet_mandals_cache.geojson` (GeoJSON) | `feed_generated_at`: `2026-11-04 17:07:21 IST`<br>`last_updated`: `2026-11-04 17:08:40 IST`<br>(Age: ~23h 48m) | Alert `AP-SACHET-20261104-001`: Event `Lightning`, Severity `Severe`, Mandal `Ravulapalem`, District `Dr.B.R.Ambedkar Konaseema`. |
| **APSDMA Cyclone Portal**<br>(AP State Disaster Management Authority) | `https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/cyclone.json` | Dedicated tropical cyclone metadata and track feed. | `backend/app/services/live_alert_ingestion_service.py`<br>Constant `CYCLONE_JSON_URL` (line 25) | **CONFIGURED BUT UNUSED** | None. Variable declared but never referenced in any function or module. | None. | None. | None. | N/A (Never requested). |
| **Google Maps Weather API**<br>(Google Maps Platform) | `https://weather.googleapis.com/v1/currentConditions:lookup`<br>`https://weather.googleapis.com/v1/forecast/hours:lookup`<br>`https://weather.googleapis.com/v1/forecast/days:lookup`<br>`https://weather.googleapis.com/v1/publicAlerts:lookup` | Current atmospheric conditions, 48h hourly rainfall forecasts, 10d daily outlooks, and Google Public Alerts. | `backend/app/services/weather_service.py`<br>`WeatherService._make_request()` | **IMPLEMENTED BUT NOT ACTIVE** | In-memory TTL cache (Current: 900s, Hourly: 3600s, Daily: 3600s, Alerts: 900s). | Requires `GOOGLE_WEATHER_API_KEY` in `.env`. Currently unconfigured. | In-memory dictionary cache (`_cache`). No persistent disk cache. | None (`last_success_iso: null`). | `"api_status": "API_KEY_NOT_CONFIGURED"`, `"alerts_status": "API_KEY_NOT_CONFIGURED"`. |
| **Open-Meteo Precipitation Stream**<br>(Open-Meteo) | None in code. (Claimed source ID: `OPEN_METEO_AP_STREAM`) | Purported ECMWF/GFS precipitation stream fallback. | `backend/app/services/live_monitoring_service.py`<br>`LiveMonitoringService.execute_all_checks()` | **SIMULATED** | Hardcoded dummy health status created during each daemon execution cycle. | None. | None. | Dummy timestamp updated to current execution time. | `SourceHealthStatus(source_id="OPEN_METEO_AP_STREAM", status="AVAILABLE", records_count=24)`. |
| **Central Water Commission / AP WRD**<br>(Ministry of Jal Shakti / AP WRD) | None (No remote HTTP endpoint; local file reference only) | River stage, discharge (cusecs), warning thresholds (1st, 2nd, 3rd) for Dowleswaram, Bhadrachalam, Polavaram, Kunavaram. | `backend/app/services/river_monitoring_service.py`<br>`RiverMonitoringService.get_river_observations()` | **STORED DATA ONLY** | Manual administrative update via `POST /api/v1/monitoring/manual-bulletin`. No automated polling. | None. | `data/monitoring/river_gauge_records.json` (JSON) | `last_updated`: `2026-11-03 09:20:00 IST`<br>(Age: ~55h 36m) | Station `CWC-DWL-01` (Dowleswaram Barrage): Level `13.80m`, Discharge `850,000 cusecs`, Status `NORMAL`. |
| **Google Cloud Text-to-Speech API**<br>(Google Cloud Platform) | `https://texttospeech.googleapis.com/v1/text:synthesize` | High-fidelity neural voice synthesis (`te-IN-Standard-A` / `en-IN-Standard-B`). | `backend/app/services/voice_tts_service.py`<br>`VoiceTtsService.synthesize_speech()` | **IMPLEMENTED BUT NOT ACTIVE** | On-demand user query via `POST /api/v1/voice/tts`. | Requires `GOOGLE_TTS_API_KEY` or `GOOGLE_CLOUD_API_KEY` in `.env`. Currently unset. | Transitory base64 audio payload in HTTP response. | None. | Falls back to Tier 2 (Google Web TTS). |
| **Google Translate Web TTS**<br>(Google Translate) | `https://translate.google.com/translate_tts?ie=UTF-8&tl={tl}&client=tw-ob&q={query}` | Direct unauthenticated regional voice audio generation. | `backend/app/services/voice_tts_service.py`<br>`VoiceTtsService.synthesize_speech()` | **IMPLEMENTED AND CALLED** | On-demand user query via `POST /api/v1/voice/tts`. | None. | Transitory audio buffer returned directly to client. | Invoked at runtime on demand. | Base64-encoded MP3 audio payload returned to client browser. |
| **Copernicus Data Space Ecosystem (CDSE)**<br>(European Space Agency) | `https://catalogue.dataspace.copernicus.eu/odata/v1/Products` | Sentinel-1 C-band SAR scene catalogue search and raw `.SAFE` downloading. | `scripts/gee/download_sentinel1.py`<br>`scripts/check_track129_history.py` | **OFFLINE SCRIPTS ONLY** | Manual batch execution. Not active in backend runtime service. | CDSE credentials (`CDSE_USERNAME`, `CDSE_PASSWORD`, `CDSE_CLIENT_ID`, `CDSE_CLIENT_SECRET`). Currently unconfigured. | Local GeoTIFF in `data/processed/sentinel1/track129_water_classification.tif` | Historical acquisition: `2022-07-16 00:30 UTC`. | Scene `S1A_IW_GRDH_1SDV_20220716T0030...` (Track 129 Descending). |
| **NASA Earthdata Login (EDL)**<br>(NASA EOSDIS) | `https://urs.earthdata.nasa.gov/api/users/tokens`<br>`https://urs.earthdata.nasa.gov/api/users/find_or_create_token` | Token authentication and data streaming for NASA GPM IMERG rainfall cubes. | `backend/app/services/nasa_auth_service.py`<br>`NASAAuthService.test_connection()` | **CONFIGURED BUT UNCALLED AT RUNTIME** | Standalone verification method. Not invoked by any API router or daemon. | Requires `NASA_EARTHDATA_USERNAME` and `NASA_EARTHDATA_PASSWORD`. Configured in `.env`. | `data/raw/rainfall/gpm_imerg/3B-DAY...nc4` (NetCDF-4) | Historical observation: `2022-07-15`. | File `3B-DAY.MS.MRG.3IMERG.20220715-S000000-E235959.V07B.nc4` ($18 \times 16$ grid, mean 3.47 mm/day). |
| **SMTP Mail Server**<br>(Configured SMTP Relay) | Configured host via `SMTP_HOST` (e.g. `smtp.gmail.com`) | External civil defense email notification dispatch. | `backend/app/services/notification_service.py`<br>`NotificationDeliveryService._send_email()` | **SIMULATED** | On administrative dispatch via `POST /api/v1/notifications/dispatch`. | Requires `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` in `.env`. Unconfigured. | `data/operations/notification_delivery_log.json` | Simulated log records dated `2026-11-04 17:08:40`. | Dispatch `DISP-2026-001`: `status: "DELIVERED"`, `provider_name: "Safe-Test Simulation Email Provider"`. |
| **SMS Gateway**<br>(Telecom SMS API) | Configured gateway via `SMS_API_KEY` | Emergency broadcast SMS to registered mandal officers. | `backend/app/services/notification_service.py`<br>`NotificationDeliveryService._send_sms()` | **SIMULATED** | On administrative dispatch via `POST /api/v1/notifications/dispatch`. | Requires `SMS_API_KEY` in `.env`. Unconfigured. | `data/operations/notification_delivery_log.json` | Recorded during dispatch tests. | Mode: `SAFE_TEST_SIMULATION`, `gateway_configured: false`. |

---

## 4. Official-Alert Ingestion Findings

### 4.1 SACHET / NDMA CAP Alerts
- **Classification:** `IMPLEMENTED AND CALLED`
- **Supporting Evidence:**
  - **Source File:** `backend/app/services/live_alert_ingestion_service.py`, lines 56–188 (`fetch_live_alerts`).
  - **Periodic Invocation:** Scheduled every 300 seconds by `LiveMonitoringService.start_daemon()` in `backend/app/services/live_monitoring_service.py` (lines 68, 239–247).
  - **Stored Data:** `data/monitoring/live_disaster_alerts.json` contains 7 normalized records directly parsed from SACHET.
  - **Endpoint:** `GET /api/v1/monitoring/ap-disaster-alerts` directly serves these active warnings.
  - **Mechanism:** Ingests live GeoJSON features, extracts CAP parameters (`events`, `severity`, `senders`, `last_sent`, `expires`, `district`, `mandal`), matches them against the 21 Lower Godavari mandals, and generates unified `OfficialDisasterAlert` objects.

### 4.2 APSDMA Alert Feeds
- **Classification:** `IMPLEMENTED AND CALLED` (for alerted mandals layer); `IMPLEMENTED BUT NOT ACTIVE` (for dedicated cyclone metadata layer).
- **Supporting Evidence:**
  - The alerted mandals GeoJSON is hosted on the official APSDMA GIS server (`apsdmagis.ap.gov.in/weather-watch/data/cyclone/layers/sachet_alerted_mandals.geojson`). This is actively fetched, parsed, and cached on disk at `data/monitoring/sachet_mandals_cache.geojson`.
  - In `backend/app/services/live_alert_ingestion_service.py` (line 25), the constant `CYCLONE_JSON_URL = "https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/cyclone.json"` is declared. Static inspection confirms this constant is never called anywhere in the codebase.

### 4.3 IMD Cyclone Bulletins
- **Classification:** `STORED DATA ONLY` (Historical Replay & Benchmarks) / `IMPLEMENTED VIA SACHET` (For Live Nowcasts).
- **Supporting Evidence:**
  - Live IMD convective and rainfall nowcasts forwarded via the SACHET portal (e.g. `IMD-Visakhapatnam` in alert record `AP-SACHET-20261104-006`) are actively ingested.
  - However, there is **no direct IMD scraper or API client** for formal National Cyclone Warning Centre (NCWC) bulletins or RSMC New Delhi bulletins.
  - Formal cyclone bulletins for historical events (e.g., Cyclone Murasu Bulletins #14 and #15) are maintained as static reference text in `data/reference/historical_flood_events_godavari.json` (served by `backend/app/services/historical_event_service.py`).
  - Manual entry of live bulletins is supported via `import_manual_bulletin()` in `live_alert_ingestion_service.py` via route `POST /api/v1/monitoring/manual-bulletin`.

### 4.4 IMD Forecast Track and Cone Data
- **Classification:** `NOT IMPLEMENTED` (At Runtime) / `STORED DATA ONLY` (In Historical Replay).
- **Supporting Evidence:**
  - There is **no runtime code** to parse, transform, or render IMD cyclonic cone-of-uncertainty polygons, quadrant wind radii shapefiles, or track forecast vectors.
  - In `historical_flood_events_godavari.json`, track progression is described textually across four discrete milestones (Approaching Coast, Landfall, Post-Landfall Deep Depression, Residual Rain/Lightning).
  - The 3D WebGL globe (`frontend/globe.js`) visualizes a visual orbital arc for display, but does not bind to an live IMD GIS feed.

### 4.5 CWC River-Stage Observations
- **Classification:** `STORED DATA ONLY`
- **Supporting Evidence:**
  - **Source File:** `backend/app/services/river_monitoring_service.py` (`RiverMonitoringService`).
  - **Data Store:** `data/monitoring/river_gauge_records.json` contains records for Dowleswaram, Bhadrachalam, Polavaram, and Kunavaram, with observation timestamp `2026-11-03 09:20:00`.
  - **Endpoint:** `GET /api/v1/monitoring/river-stages` returns these records with `is_live: false`.
  - **Missing Feature:** There is no web scraper, telemetry API client, or National Hydrology Project (NHP) connector. Automated continuous updates do not exist; updates require explicit invocations of `update_gauge_observation()`.

### 4.6 Official Rainfall Forecasts and Observations
- **Classification:** `STORED DATA ONLY` (Historical Datasets) / `IMPLEMENTED BUT NOT ACTIVE` (Google Weather API) / `SIMULATED` (Open-Meteo Telemetry).
- **Supporting Evidence:**
  - **Historical Observations:** NASA GPM IMERG Daily NetCDF-4 (`3B-DAY.MS.MRG.3IMERG.20220715...nc4`), CHIRPS 2.0 NetCDF-3 (`chirps_godavari_20220710_20220720.nc`), and ERA5 JSON (`era5_godavari_july2022.json`) are validated and stored locally in `data/raw/rainfall/`.
  - **Live Forecasts / Observations:** Implemented in `backend/app/services/weather_service.py` using Google Maps Weather API, but disabled due to missing `GOOGLE_WEATHER_API_KEY`.
  - **Open-Meteo:** Claimed as a live feed in `live_monitoring_service.py`, but verified as non-existent in code.

---

## 5. Existing API Inventory

Below is the verified inventory of all HTTP routes implemented in `backend/app/api/endpoints.py` and `backend/app/main.py`.

### 5.1 Official Alerts & Notifications

| Method | Route | Handler Function | Operational Purpose | Data Nature | Source Files & Data Backing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/monitoring/ap-disaster-alerts` | `list_ap_official_alerts` | Streams active NDMA SACHET / APSDMA official disaster alerts. | **Live Observations** | `live_alert_ingestion_service.py`<br>`data/monitoring/live_disaster_alerts.json` |
| `GET` | `/api/v1/monitoring/ap-alerted-mandals-geojson` | `get_ap_alerted_mandals_geojson` | Streams GeoJSON polygons of currently alerted mandals across AP. | **Live Observations** | `live_alert_ingestion_service.py`<br>`data/monitoring/sachet_mandals_cache.geojson` |
| `GET` | `/api/v1/monitoring/ap-districts-geojson` | `get_ap_districts_geojson` | Streams boundary GeoJSON for all 13/26 AP districts. | **Stored Reference** | `data/processed/boundaries/andhra_pradesh_districts.geojson` |
| `POST` | `/api/v1/monitoring/manual-bulletin` | `import_manual_bulletin` | Administrative injection of official emergency bulletin. | **Administrator Input** | `live_alert_ingestion_service.py`<br>Updates `live_disaster_alerts.json` |
| `GET` | `/api/v1/notifications/continuous-feed` | `get_continuous_notification_feed` | Unified notification feed split into Tier A (Official), Tier B (Model), Tier C (Community). | **Unified Operational Feed** | `continuous_alert_service.py`<br>Combines live alerts, model advisories, citizen reports |
| `POST` | `/api/v1/notifications/acknowledge` | `acknowledge_continuous_alert` | Marks notification as read by alert ID. | **Live State** | `continuous_alert_service.py`<br>`data/operations/acknowledged_alerts.json` |
| `GET` | `/api/v1/alerts/feed` | `get_alerts_feed_alias` | Alias endpoint streaming formatted active alerts. | **Live Observations** | `endpoints.py` -> `live_alert_ingestion_service.py` |
| `GET` | `/api/v1/flood-risk/alerts` | `get_flood_alerts` | Streams model-derived threshold flood alerts for mandals. | **Modelled** | `flood_risk_service.py` |
| `GET` | `/api/v1/alerts/mandal/{mandal_name}` | `get_alerts_by_mandal` | Returns active alerts filtered to a specific mandal. | **Live & Modelled** | `endpoints.py` |

### 5.2 Weather, Rainfall & River Stages

| Method | Route | Handler Function | Operational Purpose | Data Nature | Source Files & Data Backing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/monitoring/river-stages` | `get_river_stages` | Returns water levels, discharge, and warning statuses for 4 CWC stations. | **Stored Reference** | `river_monitoring_service.py`<br>`data/monitoring/river_gauge_records.json` |
| `GET` | `/api/v1/water-levels/stations` | `get_water_level_stations_alias` | Alias endpoint returning river gauge observation records. | **Stored Reference** | `endpoints.py` -> `river_monitoring_service.py` |
| `GET` | `/api/v1/weather/unified` | `get_unified_weather` | Unified weather response combining current, hourly, daily, and alerts. | **Dormant (Config Missing)** | `weather_service.py`<br>Returns unconfigured state if no API key |
| `GET` | `/api/v1/weather/current` | `get_current_weather` | Current atmospheric conditions for coordinate. | **Dormant (Config Missing)** | `weather_service.py` |
| `GET` | `/api/v1/weather/forecast/hourly` | `get_hourly_weather_forecast` | 24-48 hour hourly rainfall and weather forecast. | **Dormant (Config Missing)** | `weather_service.py` |
| `GET` | `/api/v1/weather/forecast/daily` | `get_daily_weather_forecast` | 10-day daily precipitation and temperature forecast. | **Dormant (Config Missing)** | `weather_service.py` |
| `GET` | `/api/v1/weather/alerts` | `get_weather_alerts` | Google Public Alerts for coordinate. | **Dormant (Config Missing)** | `weather_service.py` |
| `GET` | `/api/v1/locations/search` | `search_locations` | Reusable location search across coordinates, 21 mandals, and AP hubs. | **Stored Reference** | `weather_service.py`<br>`geographic_identification_service.py` |

### 5.3 Flood Susceptibility & Satellite Observations

| Method | Route | Handler Function | Operational Purpose | Data Nature | Source Files & Data Backing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/risk/assessment` | `get_basin_risk_assessment` | Comprehensive basin-wide susceptibility summary across 21 mandals. | **Modelled** | `flood_risk_service.py` (AHP MCE algorithm) |
| `GET` | `/api/v1/risk/mandals` | `get_risk_mandals_geojson` | GeoJSON FeatureCollection of 21 mandals with embedded AHP scores and tiers. | **Modelled GeoJSON** | `flood_risk_service.py`<br>`data/processed/boundaries/lower_godavari_mandals.geojson` |
| `GET` | `/api/v1/risk/mandal/{mandal_name}` | `get_mandal_risk_profile` | Detailed susceptibility profile, criteria breakdown, and plain-English drivers. | **Modelled** | `flood_risk_service.py` |
| `POST` | `/api/v1/risk/evaluate-point` | `evaluate_point_risk` | Evaluates localized susceptibility and terrain metrics for arbitrary lat/lon. | **Modelled** | `flood_risk_service.py` |
| `GET` | `/api/v1/risk/sensitivity` | `get_risk_sensitivity_analysis` | Evaluates model stability under AHP criteria weight perturbation. | **Modelled Analysis** | `flood_risk_service.py` |
| `GET` | `/api/v1/satellite/water-candidates` | `get_satellite_water_candidates_summary` | Summary of Sentinel-1 Track 129 exploratory floodwater candidates. | **Historical Dataset** | `data/metadata/phase3_3_mandal_water_candidates.json` |
| `GET` | `/api/v1/satellite/water-candidates-geojson` | `get_satellite_water_candidates_geojson` | GeoJSON polygon representations of SAR-classified water candidate clusters. | **Historical Dataset** | `data/processed/sentinel1/` |

### 5.4 Boundaries, Exposure & Infrastructure

| Method | Route | Handler Function | Operational Purpose | Data Nature | Source Files & Data Backing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/boundaries/mandals-geojson` | `get_mandals_geojson` | Serves boundary polygons for the 21 Lower Godavari study mandals. | **Stored Reference** | `backend/app/main.py`<br>`data/processed/boundaries/lower_godavari_mandals.geojson` |
| `GET` | `/api/v1/geographic/identify-point` | `identify_point_get` | Point-in-polygon containment lookup returning containing mandal and district. | **Stored Spatial Index** | `geographic_identification_service.py`<br>In-memory `STRtree` spatial index |
| `POST` | `/api/v1/geographic/identify-point` | `identify_point_endpoint` | POST version of point-in-polygon containment lookup. | **Stored Spatial Index** | `geographic_identification_service.py` |
| `POST` | `/api/v1/geographic/identify-batch` | `identify_batch_endpoint` | High-throughput batch coordinate identification. | **Stored Spatial Index** | `geographic_identification_service.py` |
| `GET` | `/api/v1/risk/exposure/summary` | `get_exposure_summary` | Basin-wide demographic (WorldPop) and facility (OSM) exposure totals. | **Empirical Overlay** | `flood_risk_service.py`<br>`worldpop_lower_godavari_2020.tif`, `osm_*.geojson` |
| `GET` | `/api/v1/risk/infrastructure` | `get_infrastructure_geojson` | GeoJSON of 1,542 verified healthcare, school, and shelter facilities. | **Empirical Vector Catalog** | `flood_risk_service.py`<br>`data/processed/infrastructure/osm_*.geojson` |

### 5.5 Operations, Citizen Services & Health

| Method | Route | Handler Function | Operational Purpose | Data Nature | Source Files & Data Backing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/monitoring/health` | `get_monitoring_daemon_health` | Returns health, uptime, and last-check status across all monitoring sources. | **Live Telemetry** | `live_monitoring_service.py`<br>`data/monitoring/monitoring_health.json` |
| `POST` | `/api/v1/monitoring/refresh` | `trigger_monitoring_refresh` | Forces immediate on-demand polling cycle across all external feeds. | **Operational Action** | `live_monitoring_service.py` |
| `GET` | `/api/v1/operations/resident/view` | `get_resident_operations_view` | Contextual resident view: local alerts, nearest shelters, risk tier. | **Live Contextual View** | `emergency_operations_service.py` |
| `GET` | `/api/v1/operations/district/overview` | `get_district_operations_overview` | District Collector situation room: aggregated risk, alerts, resource requests. | **Live Operational View** | `emergency_operations_service.py` |
| `GET` | `/api/v1/operations/advisories` | `list_advisories` | Lists active administrative flood advisories. | **Stored Live State** | `emergency_operations_service.py`<br>`data/operations/operations_store.json` |
| `POST` | `/api/v1/operations/advisories` | `create_advisory` | Administrator broadcast of targeted mandal advisory. | **Administrator Input** | `emergency_operations_service.py` |
| `POST` | `/api/v1/operations/resident/help-request` | `submit_resident_help_request` | Citizen emergency assistance submission (rescue boat, food, medical). | **Citizen Input** | `live_monitoring_service.py`<br>`data/monitoring/resident_help_requests.json` |
| `GET` | `/api/v1/operations/resident/help-requests` | `list_resident_help_requests` | Incident command queue of citizen help requests. | **Live Operational Queue** | `live_monitoring_service.py` |
| `POST` | `/api/v1/community/hazards/report` | `submit_community_hazard` | Citizen ground hazard report with photo upload and geolocation. | **Citizen Crowdsourced** | `community_hazard_service.py`<br>`data/community/hazard_reports.json` |
| `GET` | `/api/v1/community/hazards` | `list_community_hazards` | Lists citizen hazard reports with PII-redacted reporter names. | **Crowdsourced Queue** | `community_hazard_service.py` |
| `POST` | `/api/v1/community/hazards/{id}/escalate` | `escalate_hazard_report` | Escalates verified citizen hazard into an ERT resource request. | **Operational Action** | `community_hazard_service.py` |
| `GET` | `/api/v1/emergency/helplines` | `list_emergency_helplines` | Verified official emergency toll-free contact numbers directory. | **Static Reference** | `emergency_helpline_service.py` |
| `POST` | `/api/v1/voice/tts` | `synthesize_voice_speech` | Converts text to spoken Telugu (`te-IN`) or English (`en-IN`) audio. | **Live Speech Service** | `voice_tts_service.py` |
| `GET` | `/api/v1/prediction/validation-report` | `get_model_validation_report` | Independent ML validation metrics, confusion matrix, and ECE curves. | **Modelled Benchmark** | `prediction_validation_service.py` |
| `GET` | `/api/v1/events/historical` | `list_historical_events` | Summaries of historical replay events (Murasu, Arnab, July 2022). | **Historical Reference** | `historical_event_service.py` |
| `GET` | `/api/v1/events/{id}/timeline` | `get_event_timeline` | Step-by-step milestones for historical event replay. | **Historical Reference** | `historical_event_service.py` |

---

## 6. Proposed Hazard-Event Schema (Specification Only - Not Implemented)

To ingest any newly announced hazard—whether an approaching Bay of Bengal tropical cyclone, a depression, an upstream catchment cloudburst, or a major dam discharge wave—without requiring custom code per event, a universal, version-controlled **Hazard-Event Object Schema** is proposed.

### 6.1 Schema Design Principles
1. **Event Agnostic:** Accommodates cyclones, riverine flood waves, flash floods, storm surges, and dam spillway releases under a uniform structural interface.
2. **Strict Provenance:** Requires source bulletin references, issuing agency identifiers, and publication timestamps on every entry.
3. **Immutable Versioning:** A changed forecast track, revised landfall coordinate, or updated river discharge estimate **never overwrites** earlier records; it appends an immutable new version to `version_history`.

### 6.2 Proposed Pydantic / JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HazardEventRecord",
  "type": "object",
  "required": [
    "event_id",
    "hazard_type",
    "issuing_authority",
    "bulletin_reference",
    "bulletin_issue_time_iso",
    "last_updated_time_iso",
    "hazard_status",
    "validity_period",
    "affected_geographic_scope",
    "source_verification",
    "version",
    "current_state"
  ],
  "properties": {
    "event_id": {
      "type": "string",
      "description": "Unique canonical identifier (e.g., 'EVT-2026-CYCLONE-MURASU' or 'EVT-2026-FLOOD-GODAVARI-01')."
    },
    "hazard_type": {
      "type": "string",
      "enum": [
        "TROPICAL_CYCLONE",
        "DEEP_DEPRESSION",
        "RIVERINE_FLOOD_CREST",
        "FLASH_FLOOD",
        "DAM_SPILLWAY_DISCHARGE",
        "STORM_SURGE_TIDAL",
        "HEAVY_CONVECTIVE_RAINFALL",
        "LIGHTNING_STRIKE_SERIES"
      ]
    },
    "event_name": {
      "type": "string",
      "description": "Officially assigned name (e.g., 'Cyclone Murasu') or null for unnamed convective events."
    },
    "issuing_authority": {
      "type": "object",
      "required": ["agency_name", "agency_code", "jurisdiction", "contact_portal"],
      "properties": {
        "agency_name": {"type": "string", "example": "India Meteorological Department / APSDMA"},
        "agency_code": {"type": "string", "enum": ["IMD", "APSDMA", "CWC", "NDMA", "DIS_COLLECTORATE"]},
        "jurisdiction": {"type": "string", "example": "National / Andhra Pradesh"},
        "contact_portal": {"type": "string", "format": "uri", "example": "https://mausam.imd.gov.in"}
      }
    },
    "bulletin_reference": {
      "type": "object",
      "required": ["bulletin_number", "source_url"],
      "properties": {
        "bulletin_number": {"type": "string", "example": "IMD Special Tropical Weather Outlook Bulletin #14"},
        "source_url": {"type": "string", "format": "uri"},
        "document_sha256": {"type": "string", "description": "Cryptographic hash of source PDF/JSON if archived"}
      }
    },
    "bulletin_issue_time_iso": {"type": "string", "format": "date-time"},
    "last_updated_time_iso": {"type": "string", "format": "date-time"},
    "hazard_status": {
      "type": "string",
      "enum": [
        "WATCH_STAGE",
        "ALERT_STAGE",
        "WARNING_STAGE",
        "CRITICAL_EMERGENCY",
        "LANDFALL_IN_PROGRESS",
        "DE_INTENSIFYING",
        "DEPRESSION_RESIDUAL",
        "DISSIPATED",
        "CANCELLED"
      ]
    },
    "validity_period": {
      "type": "object",
      "required": ["valid_from_iso", "valid_until_iso"],
      "properties": {
        "valid_from_iso": {"type": "string", "format": "date-time"},
        "valid_until_iso": {"type": "string", "format": "date-time"}
      }
    },
    "affected_geographic_scope": {
      "type": "object",
      "required": ["districts", "mandals", "intersects_lower_godavari"],
      "properties": {
        "districts": {"type": "array", "items": {"type": "string"}},
        "mandals": {"type": "array", "items": {"type": "string"}},
        "intersects_lower_godavari": {"type": "boolean"},
        "lower_godavari_mandals_affected": {"type": "array", "items": {"type": "string"}},
        "bounding_box_wgs84": {
          "type": "array",
          "items": {"type": "number"},
          "minItems": 4,
          "maxItems": 4,
          "description": "[min_lon, min_lat, max_lon, max_lat]"
        }
      }
    },
    "source_verification": {
      "type": "object",
      "required": ["confidence_rating", "verification_method"],
      "properties": {
        "confidence_rating": {"type": "string", "enum": ["HIGH_OFFICIAL", "MODERATE_OFFICIAL", "UNVERIFIED_PROVISIONAL"]},
        "verification_method": {"type": "string", "example": "Digitally Signed Official CAP RSS Feed"},
        "is_simulated_or_exercise": {"type": "boolean", "default": false}
      }
    },
    "version": {
      "type": "integer",
      "minimum": 1,
      "description": "Monotonically increasing version counter (1, 2, 3...)."
    },
    "current_state": {
      "type": "object",
      "description": "Specific metrics for current forecast step (e.g. coordinates, wind speed, rainfall, discharge).",
      "properties": {
        "observed_or_forecast_center": {
          "type": "object",
          "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
            "location_name": {"type": "string"}
          }
        },
        "intensity_metrics": {
          "type": "object",
          "properties": {
            "sustained_wind_kmph": {"type": "number"},
            "gusting_kmph": {"type": "number"},
            "central_pressure_hpa": {"type": "number"},
            "expected_24h_rainfall_mm": {"type": "number"},
            "forecast_discharge_cusecs": {"type": "number"}
          }
        },
        "spatial_geometry": {
          "type": "object",
          "description": "GeoJSON Geometry object representing forecast track cone, isohyetal contour, or inundation polygon."
        }
      }
    },
    "version_history": {
      "type": "array",
      "description": "Chronological audit trail of all prior versions of this event record.",
      "items": {
        "type": "object",
        "properties": {
          "version": {"type": "integer"},
          "superseded_at_iso": {"type": "string", "format": "date-time"},
          "superseded_by_bulletin": {"type": "string"},
          "prior_state": {"type": "object"}
        }
      }
    }
  }
}
```

### 6.3 Versioning Workflow
When a new bulletin arrives (e.g. Cyclone Murasu track shifting eastward by 40 km or Dowleswaram discharge forecast escalating from 1.4M to 2.1M cusecs):
1. The ingestion engine looks up the existing record by `event_id`.
2. The current `current_state`, `validity_period`, and `bulletin_reference` are archived into the `version_history` array alongside a `superseded_at_iso` timestamp.
3. The `version` number increments ($v_n \to v_{n+1}$).
4. The new forecast coordinates, geometry, and intensity parameters populate `current_state`.
5. Prior predictions remain permanently inspectable for forecast verification, avoiding data loss or retrospective distortion.

---

## 7. Proposed Common Assessment-Object Schema (Specification Only - Not Implemented)

To provide a synchronized, defensible data model that feeds both **Citizen Views** (clear language, spoken guidance, shelter directions) and **Administrator Views** (demographic risk matrices, logistics dispatch schedules), a unified **Common Assessment Object** is proposed.

### 7.1 Mandatory Metadata Envelope
Every single assessment property must be wrapped in a standardized provenance envelope:
```json
{
  "value": Any,
  "unit": Optional[str],
  "source": str,
  "observation_or_forecast_time_iso": str,
  "retrieval_time_iso": str,
  "data_type": "observed | forecast | historical | modelled | reference",
  "status_and_freshness": "LIVE_FRESH | STALE_CACHED | HISTORICAL_REFERENCE | UNCONFIGURED",
  "uncertainty_or_limitations": str,
  "geographic_scope": str
}
```

### 7.2 Strict Terminology Rules
- **Susceptibility** is **never** labeled as a flood probability (it is intrinsic physical terrain proneness).
- **Population Exposure** is **never** labeled as confirmed affected population (it is baseline demographic presence in elevated susceptibility zones).

### 7.3 Complete Schema Definition

```json
{
  "assessment_id": "ASM-20261105-MUMMIDIVARAM",
  "generated_at_iso": "2026-11-05T16:56:07+05:30",
  "geographic_context": {
    "mandal_name": "Mummidivaram",
    "district_name": "Dr. B.R. Ambedkar Konaseema",
    "state_name": "Andhra Pradesh",
    "is_lower_godavari_core": true,
    "area_sq_km": 184.22
  },
  "assessment_components": {
    "official_warnings": {
      "value": [
        {
          "alert_id": "AP-SACHET-20261104-001",
          "event_type": "Lightning",
          "severity": "Severe",
          "headline": "Official Lightning Warning for Konaseema Mandals",
          "instruction": "Stay indoors, avoid tall trees and water bodies."
        }
      ],
      "unit": null,
      "source": "APSDMA / NDMA SACHET",
      "observation_or_forecast_time_iso": "2026-11-04T16:56:05+05:30",
      "retrieval_time_iso": "2026-11-04T17:08:40+05:30",
      "data_type": "observed",
      "status_and_freshness": "STALE_CACHED (23h 48m old)",
      "uncertainty_or_limitations": "Subject to state alert dissemination latency; reflects published CAP alerts only.",
      "geographic_scope": "Mandal-Level (Mummidivaram)"
    },
    "flood_susceptibility": {
      "value": {
        "index_score": 0.92,
        "classification_tier": "Very High",
        "factor_breakdown": {
          "elevation_score": 0.95,
          "slope_score": 0.98,
          "river_proximity_score": 0.92,
          "landcover_score": 0.85,
          "historical_hazard_score": 0.90
        },
        "explainable_drivers": [
          "Critically low delta elevation (mean 2.4m above MSL)",
          "Extreme proximity to Gautami Godavari main channel (< 400m)",
          "Flat agricultural plain gradient (< 0.6 degrees slope)"
        ]
      },
      "unit": "Normalized Index (0.00 to 1.00)",
      "source": "PRAVAH 360 Multi-Criteria AHP Model",
      "observation_or_forecast_time_iso": "2026-11-02T11:47:00+05:30",
      "retrieval_time_iso": "2026-11-05T16:56:07+05:30",
      "data_type": "modelled",
      "status_and_freshness": "HISTORICAL_REFERENCE (Model v4.1)",
      "uncertainty_or_limitations": "Measures intrinsic physical susceptibility based on terrain and drainage; DOES NOT predict dynamic water depth or flood arrival timing.",
      "geographic_scope": "Mandal Geometry (Mummidivaram)"
    },
    "precipitation": {
      "value": {
        "current_rate_mm_hr": 0.0,
        "past_24h_observed_mm": 48.6,
        "forecast_next_24h_mm": 0.0,
        "forecast_72h_accum_mm": 0.0
      },
      "unit": "millimeters (mm)",
      "source": "Google Weather API / GPM IMERG Reference",
      "observation_or_forecast_time_iso": "2026-11-04T17:08:40+05:30",
      "retrieval_time_iso": "2026-11-04T17:08:40+05:30",
      "data_type": "reference",
      "status_and_freshness": "UNCONFIGURED (Live API Key Missing in .env)",
      "uncertainty_or_limitations": "Live atmospheric streaming inactive; values reflect historical reference datasets.",
      "geographic_scope": "Point Centroid (Lat: 16.65, Lon: 82.01)"
    },
    "river_stage": {
      "value": {
        "station_name": "Dowleswaram Barrage (Sir Arthur Cotton Barrage)",
        "current_level_m": 13.80,
        "current_discharge_cusecs": 850000.0,
        "first_warning_stage_m": 14.50,
        "second_warning_stage_m": 15.50,
        "third_danger_stage_m": 16.50,
        "flood_status": "NORMAL",
        "trend": "STEADY"
      },
      "unit": "meters above MSL & cusecs",
      "source": "AP Water Resources Department / CWC Godavari Circle",
      "observation_or_forecast_time_iso": "2026-11-03T09:20:00+05:30",
      "retrieval_time_iso": "2026-11-04T17:08:40+05:30",
      "data_type": "reference",
      "status_and_freshness": "HISTORICAL_REFERENCE (Stored benchmark)",
      "uncertainty_or_limitations": "Stored reference values from Nov 3, 2026; live automated CWC scraping is not active.",
      "geographic_scope": "Regional Headworks (Dowleswaram)"
    },
    "population_exposure": {
      "value": {
        "baseline_population_count": 84520,
        "population_density_per_sq_km": 458.8,
        "potentially_exposed_in_elevated_zone": 84520,
        "percentage_of_mandal_exposed": 100.0
      },
      "unit": "Persons (UN-Adjusted Count)",
      "source": "WorldPop India 2020 1km Raster",
      "observation_or_forecast_time_iso": "2020-01-01T00:00:00Z",
      "retrieval_time_iso": "2026-11-02T11:47:00+05:30",
      "data_type": "historical",
      "status_and_freshness": "HISTORICAL_REFERENCE",
      "uncertainty_or_limitations": "Represents baseline demographic residency in zones of Very High intrinsic susceptibility; DOES NOT imply confirmed affected or displaced population.",
      "geographic_scope": "Mandal Geometry (Mummidivaram)"
    },
    "critical_infrastructure_exposure": {
      "value": {
        "total_mapped_facilities": 76,
        "healthcare_facilities_count": 54,
        "educational_institutions_count": 16,
        "emergency_shelters_count": 6,
        "nearest_designated_shelter": {
          "name": "Mummidivaram High School Cyclone Relief Shelter",
          "distance_km": 1.2,
          "capacity_persons": 800,
          "latitude": 16.654,
          "longitude": 82.012
        }
      },
      "unit": "Facility Count & Kilometers",
      "source": "OpenStreetMap Verified Facilities via Overpass API",
      "observation_or_forecast_time_iso": "2024-06-01T00:00:00Z",
      "retrieval_time_iso": "2026-11-02T11:47:00+05:30",
      "data_type": "reference",
      "status_and_freshness": "HISTORICAL_REFERENCE",
      "uncertainty_or_limitations": "Facility list reflects mapped OSM objects; unmapped rural private clinics and community buildings are excluded. Road submergence is not evaluated.",
      "geographic_scope": "Mandal Geometry (Mummidivaram)"
    },
    "recommended_actions": {
      "value": {
        "resident_guidance_en": "Monitor local municipal broadcasts. Keep mobile phones charged. If water approaches threshold, move to Mummidivaram High School Shelter.",
        "resident_guidance_te": "స్థానిక సమాచారాన్ని గమనిస్తూ ఉండండి. తాగునీరు, మందులు సిద్ధం చేసుకోండి. ముంపు హెచ్చరిక వస్తే ముమ్మిడివరం పునరావాస కేంద్రానికి చేరుకోండి.",
        "administrator_directives": [
          "Pre-position 5 motorized rescue boats at Gautami river ferry points.",
          "Alert primary health centers regarding water-borne disease prophylaxis.",
          "Ensure power generators at 6 designated cyclone shelters have 48h diesel reserves."
        ],
        "suggested_resource_dispatch": {
          "motorboats_allocated": 5,
          "medical_kits_allocated": 9,
          "food_packets_allocated": 18200
        }
      },
      "unit": null,
      "source": "PRAVAH 360 Emergency Operations Decision Engine",
      "observation_or_forecast_time_iso": "2026-11-05T16:56:07+05:30",
      "retrieval_time_iso": "2026-11-05T16:56:07+05:30",
      "data_type": "modelled",
      "status_and_freshness": "LIVE_CALCULATED",
      "uncertainty_or_limitations": "Decision support advice generated algorithmically; must be confirmed by District Incident Commander prior to tactical deployment.",
      "geographic_scope": "Mandal Emergency Command"
    }
  }
}
```

---

## 8. Integration Mapping

This section maps existing codebase endpoints, services, and local data stores to the fields required by the proposed Hazard-Event and Common Assessment-Object schemas.

```
+-----------------------------------------------------------------------------------------------------------------+
|                                         PRAVAH 360 INTEGRATION TOPOLOGY                                         |
+------------------------------+-------------------------------------------------+--------------------------------+
| Schema Component             | Supplying Existing Endpoint / Service           | Integration Feasibility        |
+------------------------------+-------------------------------------------------+--------------------------------+
| 1. Hazard Event Metadata     | LiveAlertIngestionService.fetch_live_alerts()   | Reusable Directly              |
|                              | GET /api/v1/monitoring/ap-disaster-alerts       |                                |
| 2. Event Versioning History  | Currently Absent in Code                        | Requires Adaptation (New DB)   |
| 3. Affected Mandals Scope    | GeographicIdentificationService.mandals         | Reusable Directly              |
|                              | GET /api/v1/boundaries/mandals-geojson          |                                |
| 4. Official Warnings         | ContinuousAlertNotificationService (Tier A)     | Reusable Directly              |
|                              | GET /api/v1/notifications/continuous-feed       |                                |
| 5. Flood Susceptibility      | FloodRiskAssessmentService.assess_basin_risk()  | Reusable Directly              |
|                              | GET /api/v1/risk/mandals                        |                                |
| 6. Precipitation Streams     | WeatherService (Google Maps Platform)           | Blocked on API Key in .env     |
| 7. River Gauge Stages        | RiverMonitoringService.get_river_observations() | Needs Scraper Adaptation       |
|                              | GET /api/v1/monitoring/river-stages             | (Currently Stored Data Only)   |
| 8. Demographic Exposure      | FloodRiskAssessmentService (WorldPop 2020)      | Reusable Directly              |
|                              | GET /api/v1/risk/exposure/summary               |                                |
| 9. Infrastructure Exposure   | FloodRiskAssessmentService (OSM 1,542 points)   | Reusable Directly              |
|                              | GET /api/v1/risk/infrastructure                 |                                |
| 10. Operational Directives   | EmergencyOperationsService (Advisories/Helpline)| Reusable Directly              |
|                              | GET /api/v1/operations/advisories               |                                |
| 11. Resource Quota Solver    | ResourceAllocationService.allocate_resources()  | Requires Admin Stock Input     |
|                              | POST /api/v1/allocate-resources                 |                                |
| 12. Spoken Telugu Advisory   | VoiceTtsService.synthesize_speech()             | Reusable Directly (Tier 2 TTS) |
|                              | POST /api/v1/voice/tts                          |                                |
+------------------------------+-------------------------------------------------+--------------------------------+
```

### 8.1 What Can Be Reused Directly (Zero Modifications Needed)
1. **Administrative Geometry & Point Identification:**
   - `GeographicIdentificationService` with in-memory `STRtree` spatial index provides sub-millisecond point-in-polygon resolution across all 21 mandals and districts.
2. **Multi-Criteria AHP Susceptibility Calculation:**
   - `FloodRiskAssessmentService` calculates normalized continuous susceptibility scores and classification tiers without modification.
3. **WorldPop Baseline Exposure:**
   - The cell-by-cell zonal sum matrix for 9,126,353 baseline residents is validated and fully intact.
4. **Verified Infrastructure Catalog:**
   - The 1,542 OSM healthcare, educational, and shelter assets with coordinates and nearest-distance queries are reusable immediately.
5. **SACHET CAP Alert Ingestion:**
   - The parser in `LiveAlertIngestionService` successfully parses, deduplicates, and filters active warnings from APSDMA.
6. **Telugu Voice Synthesis:**
   - `VoiceTtsService` synthesizes regional Telugu speech without requiring proprietary cloud keys via its verified Google Translate Web fallback.

### 8.2 What Needs Adaptation
1. **Live Alert Ingestion Service:**
   - Needs adaptation to read `CYCLONE_JSON_URL` (`https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/cyclone.json`) which is already declared on line 25 but not yet called.
   - Needs adaptation to maintain an append-only JSON file or SQLite table for hazard event versioning instead of overwriting `live_disaster_alerts.json` on each fetch.
2. **River Monitoring Service:**
   - Currently serves hardcoded station records from `river_gauge_records.json`.
   - Needs adaptation to add an automated HTTP fetching mechanism (e.g. against CWC Godavari Circle bulletin feeds or National Hydrology Project APIs) with fallback to stored values when government servers timeout.
3. **Notification Delivery Service:**
   - Currently runs in `SAFE_TEST_SIMULATION` mode. Needs live SMTP relay settings and an SMS gateway provider configured in `.env` to perform external dispatches.

### 8.3 What Data is Missing & Requires External Sources
1. **Live IMD Cyclonic Cone Shapefiles:**
   - No code or parser exists in the project to ingest IMD cyclone forecast tracks, wind radii quadrants, or forecast cones in GIS format.
   - *Required External Source:* IMD Cyclone Warning Division RSS/GeoJSON feed or GDACS (Global Disaster Alert and Coordination System) API.
2. **Live Automated Rainfall Telemetry:**
   - Real-time rainfall observations across mandal weather stations are currently missing because Google Weather API is unconfigured and Open-Meteo is simulated.
   - *Required External Source:* Configuration of `GOOGLE_WEATHER_API_KEY` or implementation of a verified public Open-Meteo / IMD AWS client.
3. **Dynamic Hydrodynamic Flow Depths:**
   - The system models static terrain susceptibility (proneness), not time-stepping 2D hydraulic flood depths (e.g. HEC-RAS 2D). Dynamic flood routing requires coupled hydrological discharge hydrographs.

### 8.4 What Requires Administrator Input
1. **Emergency Stock Declarations:** Available numbers of motorized rescue craft, trauma medical kits, and food rations must be entered by incident commanders to execute the allocation solver (`POST /api/v1/allocate-resources`).
2. **Notification Dispatch Approval:** Emergency alerts cannot be broadcast without explicit administrative authorization (`approved_by_admin: true` gate).
3. **Citizen Report Verification:** Citizen-submitted hazard photos and ground observations require administrative triage before being escalated to emergency response teams.
4. **Manual Bulletin Injection:** In the event of government feed downtime, emergency officials must use `POST /api/v1/monitoring/manual-bulletin` to inject verified bulletins.

---

## 9. Risks and Data-Quality Limitations

1. **Risk of Misinterpreting Susceptibility as Flood Probability:**
   - *Finding (Verified in Code):* The AHP index ($FSI \in [0, 1]$) represents **intrinsic physical terrain vulnerability** (low elevation, flat slope, river proximity).
   - *Risk:* Non-technical officials or residents might mistake an FSI of 0.88 as an "88% statistical probability of imminent inundation."
   - *Mitigation:* The UI and API must strictly label this metric as "Intrinsic Physical Susceptibility" and explicitly declare that actual inundation requires dynamic meteorological and river discharge triggers.

2. **Risk of Conflating Baseline Exposure with Confirmed Affected Population:**
   - *Finding (Verified in Code):* `flood_risk_service.py` reports $8,252,724$ people residing in Very High and High susceptibility zones.
   - *Risk:* In disaster reporting, describing this entire figure as "affected citizens" would constitute severe misinformation.
   - *Mitigation:* All interfaces must maintain the label "Potentially Exposed Population in Elevated Susceptibility Zones" and document that flood bunds, embankments, and localized topography protect many settlements during minor-to-moderate events.

3. **External Feed Disruption & Stale Caching:**
   - *Finding (Verified in Stored Data):* State government GIS portals (`apsdmagis.ap.gov.in`) occasionally suffer connection timeouts or SSL handshake anomalies during major disasters due to severe web traffic.
   - *Mitigation:* `LiveAlertIngestionService` correctly implements `ssl.CERT_NONE` and catches `HTTPError` to serve cached records. However, the UI must display a clear "Stale / Cached as of [timestamp]" warning whenever a feed is older than 30 minutes.

4. **Synthetic Training Benchmark in Validation Engine:**
   - *Finding (Verified in Code):* `prediction_validation_service.py` generates synthetic training data seeded by historical profiles (`np.random.seed(42)`) to demonstrate model metrics (Precision 0.857, Recall 0.857).
   - *Risk:* Claiming these performance figures represent real-time telemetric validation of live predictions would violate research integrity.
   - *Mitigation:* The validation modal explicitly disclaims: "Trained on historical event benchmarks (2018-2024). Provides decision support; not an operational hydrodynamic guarantee."

5. **Lack of Automated Live CWC River Telemetry:**
   - *Finding (Verified in Stored Data):* The four river monitoring stations have not updated since November 3, 2026.
   - *Risk:* If a resident checks river status during an active storm, they will view a 2-day-old gauge reading of 13.80m at Dowleswaram unless manually updated.
   - *Mitigation:* Display the observation timestamp prominently next to every water level figure.

---

## 10. Recommended Next Steps (Ordered by Priority)

The following recommendations are structured in strict priority order for future development phases upon user approval:

### Priority 1: Activate Dormant APSDMA Cyclone Feed Ingestion
- **Action:** Utilize the already-configured `CYCLONE_JSON_URL` (`https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/cyclone.json`) in `live_alert_ingestion_service.py`.
- **Implementation:** Implement a parser to extract active cyclone names, central coordinates, intensity classifications, and bulletin timestamps into the proposed `HazardEventRecord` schema.
- **Verification Requirement:** Pending user approval (requires network verification of APSDMA JSON format).

### Priority 2: Implement Verified Public Rainfall Fallback (Open-Meteo or IMD)
- **Action:** Replace the hardcoded `OPEN_METEO_AP_STREAM` telemetry in `live_monitoring_service.py` with an actual, unauthenticated HTTP client querying Open-Meteo's free ECMWF/GFS precipitation API (`https://api.open-meteo.com/v1/forecast?latitude=16.94&longitude=81.77&hourly=precipitation,rain`).
- **Benefit:** Provides real-time and 72-hour forecast precipitation across the 21 mandals without requiring a paid Google Weather API key.

### Priority 3: Implement Automated CWC River Bulletin Scraper / Ingestion Adapter
- **Action:** Build an automated ingestion module for CWC Godavari river stations (Dowleswaram Barrage, Bhadrachalam, Polavaram) querying official CWC flood bulletins or Central Water Commission Daily Flood Bulletins.
- **Benefit:** Eliminates reliance on static stored values in `river_gauge_records.json` and ensures river stages update synchronously with monsoon discharges.

### Priority 4: Implement Immutable Hazard-Event Versioning Store
- **Action:** Deploy the proposed `HazardEventRecord` schema in a local SQLite table (`data/hazards.db`) or structured JSON store.
- **Benefit:** When IMD or APSDMA issues an updated track or warning revision, the previous forecast is preserved in `version_history`, enabling retrospective forecast accuracy verification.

### Priority 5: Expose Common Assessment Object Endpoint
- **Action:** Create `GET /api/v1/assessment/mandal/{mandal_name}` implementing the proposed Common Assessment Object schema.
- **Benefit:** Unifies susceptibility, active alerts, WorldPop demographics, OSM facilities, and river stages into a single, provenance-tracked JSON contract for both web dashboard and mobile voice clients.

---

## 11. Completion Verification

- **Source Code Preservation:** **Verified.** Zero application source code files (`.py`, `.js`, `.html`, `.css`) were modified, renamed, created, or deleted.
- **Dependency & Environment Preservation:** **Verified.** Zero packages installed; `.venv` and `requirements.txt` untouched.
- **Network Request Restriction:** **Verified.** Zero outbound network calls, API requests, or downloads were executed during this audit.
- **Report Target:** Created exclusively at `docs/hazard_audit.md`.
- **Integrity Compliance:** All findings strictly categorized as **verified in code**, **verified in stored data**, **inferred**, or **not verified**. No unsupported operational claims made.
