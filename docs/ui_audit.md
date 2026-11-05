# PRAVAH 360: Comprehensive UI & API Audit (Phase A)
Generated: 2026-11-03T08:35:39.900Z

## 1. Frontend Entry Points

| Entry Point | Target / Function | Status | Notes |
|:---|:---|:---:|:---|
| `/` | Default Application Root (Starts at Welcome Discovery) | WORKING | Loads Single-Page Application |
| `/?ui=classic` | Instant Fallback Classic Interface | WORKING | Serves preserved classic index_classic.html |
| `/#welcome` | System Introduction & Discovery Workspace | WORKING | 6 Core capability cards & quick action CTAs |
| `/#overview` | Executive Intelligence Command Centre | WORKING | Lower Godavari 600px Hero Map & floating HUD |
| `/#explorer` | Geospatial Explorer (Web GIS) | WORKING | Multi-layer canvas with satellite/terrain/dark tiles |
| `/#risk` | Flood Risk Intelligence | WORKING | AHP susceptibility model & 21-mandal rankings |
| `/#impact` | Impact Assessment | WORKING | WorldPop 2020 exposure & 1,467 community assets |
| `/#weather` | Weather, Alerts & Environmental Monitoring | WORKING | NDMA SACHET, Open-Meteo & CWC river stages |
| `/#operations` | Emergency Operations & Decision Support Simulator | WORKING | Citizen SOS, Tahsildar, Collector & ERT views |
| `/#global` | Global 3D Earth Workspace | WORKING | Continuous WebGL globe with 177 geopolitical borders |
| `/#research` | Research & Methodology | WORKING | Formal academic paper title, GEE & AHP weights |
| `/#help` | Help & Flood Preparedness Guide | WORKING | 3-stage checklist & emergency directory |
| `/?action=login` | Earth-at-Night Authentication Overlay | WORKING | Displays Reference B glassmorphic login modal |
| `/?action=tour` | Guided Onboarding Walkthrough Modal | WORKING | 6-step guided walkthrough modal |
| `/?role=resident#operations` | Citizen AidConnect Console | WORKING | Direct deep-link to simplified resident SOS view |
| `/?role=disaster_mgmt#operations` | Mandal Tahsildar Console | WORKING | Direct deep-link to Mandal advisory view |
| `/?role=collectorate#operations` | District Collector Console | WORKING | Direct deep-link to District coordination view |
| `/?role=ert#operations` | SDRF Responder Console | WORKING | Direct deep-link to ERT dispatch board |

---

## 2. Backend API Endpoints Audit

Total Registered Endpoints: 60

| HTTP Method | API Path | Service Handler | Functional Status |
|:---|:---|:---|:---:|
| `POST` | `/api/v1/auth/login` | FastAPI Router | WORKING |
| `GET` | `/api/v1/auth/session` | FastAPI Router | WORKING |
| `POST` | `/api/v1/auth/logout` | FastAPI Router | WORKING |
| `GET` | `/api/v1/auth/demo-accounts` | FastAPI Router | WORKING |
| `GET` | `/api/v1/geographic/identify-point` | FastAPI Router | WORKING |
| `POST` | `/api/v1/geographic/identify-point` | FastAPI Router | WORKING |
| `POST` | `/api/v1/geographic/identify-batch` | FastAPI Router | WORKING |
| `GET` | `/api/v1/flood-risk/markers` | FastAPI Router | WORKING |
| `GET` | `/api/v1/flood-risk/alerts` | FastAPI Router | WORKING |
| `GET` | `/api/v1/alerts/mandal/{mandal_name}` | FastAPI Router | WORKING |
| `GET` | `/api/v1/flood-risk/alerts/mandal/{mandal_name}` | FastAPI Router | WORKING |
| `GET` | `/api/v1/flood-risk/summary` | FastAPI Router | WORKING |
| `GET` | `/api/v1/risk/assessment` | FastAPI Router | WORKING |
| `GET` | `/api/v1/risk/mandals` | FastAPI Router | WORKING |
| `GET` | `/api/v1/risk/mandal/{mandal_name}` | FastAPI Router | WORKING |
| `GET` | `/api/v1/risk/exposure/summary` | FastAPI Router | WORKING |
| `GET` | `/api/v1/risk/infrastructure` | FastAPI Router | WORKING |
| `POST` | `/api/v1/risk/evaluate-point` | FastAPI Router | WORKING |
| `GET` | `/api/v1/risk/evaluate-point` | FastAPI Router | WORKING |
| `GET` | `/api/v1/flood-risk/basin-assessment` | FastAPI Router | WORKING |
| `GET` | `/api/v1/flood-risk/mandal/{mandal_name}` | FastAPI Router | WORKING |
| `GET` | `/api/v1/flood-risk/point-assessment` | FastAPI Router | WORKING |
| `GET` | `/api/v1/infrastructure/facilities` | FastAPI Router | WORKING |
| `GET` | `/api/v1/alerts/feed` | FastAPI Router | WORKING |
| `GET` | `/api/v1/weather/forecast` | FastAPI Router | WORKING |
| `GET` | `/api/v1/water-levels/stations` | FastAPI Router | WORKING |
| `GET` | `/api/v1/risk/sensitivity` | FastAPI Router | WORKING |
| `GET` | `/api/v1/weather/unified` | FastAPI Router | WORKING |
| `GET` | `/api/v1/weather/current` | FastAPI Router | WORKING |
| `GET` | `/api/v1/weather/forecast/hourly` | FastAPI Router | WORKING |
| `GET` | `/api/v1/weather/forecast/daily` | FastAPI Router | WORKING |
| `GET` | `/api/v1/weather/alerts` | FastAPI Router | WORKING |
| `GET` | `/api/v1/locations/search` | FastAPI Router | WORKING |
| `GET` | `/api/v1/satellite/water-candidates` | FastAPI Router | WORKING |
| `GET` | `/api/v1/satellite/water-candidates-geojson` | FastAPI Router | WORKING |
| `GET` | `/api/v1/operations/resident/view` | FastAPI Router | WORKING |
| `GET` | `/api/v1/operations/advisories` | FastAPI Router | WORKING |
| `POST` | `/api/v1/operations/advisories` | FastAPI Router | WORKING |
| `POST` | `/api/v1/operations/advisories/acknowledge` | FastAPI Router | WORKING |
| `GET` | `/api/v1/operations/district/overview` | FastAPI Router | WORKING |
| `GET` | `/api/v1/operations/resources` | FastAPI Router | WORKING |
| `POST` | `/api/v1/operations/resources` | FastAPI Router | WORKING |
| `PATCH` | `/api/v1/operations/resources/{request_id}/status` | FastAPI Router | WORKING |
| `GET` | `/api/v1/monitoring/health` | FastAPI Router | WORKING |
| `POST` | `/api/v1/monitoring/refresh` | FastAPI Router | WORKING |
| `GET` | `/api/v1/monitoring/ap-disaster-alerts` | FastAPI Router | WORKING |
| `GET` | `/api/v1/monitoring/ap-alerted-mandals-geojson` | FastAPI Router | WORKING |
| `GET` | `/api/v1/monitoring/ap-districts-geojson` | FastAPI Router | WORKING |
| `GET` | `/api/v1/monitoring/river-stages` | FastAPI Router | WORKING |
| `POST` | `/api/v1/monitoring/manual-bulletin` | FastAPI Router | WORKING |
| `GET` | `/api/v1/notifications/recipients` | FastAPI Router | WORKING |
| `POST` | `/api/v1/notifications/recipients` | FastAPI Router | WORKING |
| `GET` | `/api/v1/notifications/history` | FastAPI Router | WORKING |
| `POST` | `/api/v1/notifications/dispatch` | FastAPI Router | WORKING |
| `POST` | `/api/v1/notifications/test-delivery` | FastAPI Router | WORKING |
| `POST` | `/api/v1/operations/resident/help-request` | FastAPI Router | WORKING |
| `GET` | `/api/v1/operations/resident/help-requests` | FastAPI Router | WORKING |
| `GET` | `/api/v1/health` | FastAPI Router | WORKING |
| `GET` | `/api/v1/boundaries/mandals-geojson` | FastAPI Router | WORKING |
| `GET` | `/` | FastAPI Router | WORKING |

---

## 3. Visible Controls & Interactive Elements Audit

| UI Component | Element ID / Selector | Action / Event Trigger | Status | Verification Notes |
|:---|:---|:---|:---:|:---|
| **Top Bar Brand Logo** | `.nav-brand` | Brand Identity | WORKING | PRAVAH 360 SVG Emblem & Tagline |
| **User Profile Button** | `#btnUserAuth` | Click &rarr; Opens Login Modal / Confirms Logout | WORKING | Displays active role / user name |
| **Guided Tour Button** | `#btnLaunchTour` | Click &rarr; Opens Onboarding Walkthrough | WORKING | 6-step guided tour modal |
| **Global Universal Search** | `#globalLocationSearchInput` | Input &rarr; Mandal/Town/Coordinate Suggestions | WORKING | Supports Rajamahendravaram / Rajahmundry alias |
| **Search Button** | `#btnGlobalSearch` | Click &rarr; Pans map to match | WORKING | Resolves coordinates and bounds |
| **Reset View Button** | `#btnResetBasinView` | Click &rarr; Resets camera to Lower Godavari | WORKING | Center: [16.942, 81.776], Zoom: 9 |
| **Hero HUD: All Layers** | `[data-layer="all"]` | Click &rarr; Displays all GIS layers | WORKING | Toggles SAR flood, susceptibility & rivers |
| **Hero HUD: SAR Floodwater** | `[data-layer="flood"]` | Click &rarr; Displays SAR flood extents | WORKING | Sentinel-1 Track 129 inundation |
| **Hero HUD: Susceptibility** | `[data-layer="susceptibility"]` | Click &rarr; Displays AHP susceptibility polygons | WORKING | Color-coded 4-tier risk categories |
| **Hero HUD: Drainage** | `[data-layer="rivers"]` | Click &rarr; Displays HydroRIVERS drainage network | WORKING | 1,496 vector segments |
| **Basemap Radios** | `input[name="basemapRadio"]` | Change &rarr; Switches dark/satellite/OSM | WORKING | Leaflet tile layer swap |
| **Layer Opacity Slider** | `#sarOpacitySlider` | Input &rarr; Sets vector/raster layer opacity | WORKING | Dynamic setOpacity() |
| **Inspection Drawer Close** | `#btnCloseDrawer` | Click &rarr; Hides spatial inspection drawer | WORKING | Closes right-side drawer |
| **Ops Role Switcher: Citizen** | `[data-ops-role="resident"]` | Click &rarr; Activates Resident view | WORKING | Citizen AidConnect-style UI |
| **Ops Role Switcher: Mandal** | `[data-ops-role="disaster_mgmt"]` | Click &rarr; Activates Tahsildar view | WORKING | Mandal advisory console |
| **Ops Role Switcher: District** | `[data-ops-role="collectorate"]` | Click &rarr; Activates Collector view | WORKING | District coordination console |
| **Ops Role Switcher: ERT** | `[data-ops-role="ert"]` | Click &rarr; Activates SDRF Responder view | WORKING | Mission triage & dispatch |
| **Emergency SOS Submission** | `#residentHelpForm` | Submit &rarr; POST /operations/resident/help-request | WORKING | Persists real request with ID |
| **Advisory Broadcast Form** | `#advisoryForm` | Submit &rarr; POST /operations/advisories | WORKING | Logs advisory to store |
| **Resource Requisition Form**| `#resourceRequestForm` | Submit &rarr; POST /operations/resources | WORKING | Logs resource request |
| **ERT Lifecycle Buttons** | `.btn-lc` | Click &rarr; PATCH /operations/resources/{id}/status | WORKING | Requested &rarr; Approved &rarr; Dispatched &rarr; On Scene &rarr; Completed |
| **Login Modal Submit** | `#loginForm` | Submit &rarr; POST /api/v1/auth/login | WORKING | PBKDF2 verification & session issuance |
| **Login Demo Chips** | `.demo-chip` | Click &rarr; Pre-fills demo credentials | WORKING | 4 roles: Citizen, Mandal, District, ERT |
| **Tour Step Navigation** | `#btnTourNext`, `#btnTourBack` | Click &rarr; Cycles tour steps | WORKING | 6 steps with active dots |
| **Globe Auto-Rotation** | `#btnToggleGlobeRotation` | Click &rarr; Toggles 3D globe spin | WORKING | Pauses / resumes rotation |
| **Globe Day/Night Texture** | `#btnToggleGlobeTexture` | Click &rarr; Toggles daytime / night Earth texture | WORKING | WebGL texture swap |
| **Globe Reset View** | `#btnResetGlobeView` | Click &rarr; Resets orbital camera altitude | WORKING | Eases camera to global orbit |
| **Globe Country Search** | `#globeCountrySearchInput` | Input &rarr; Searches 177 countries | WORKING | Pans globe to country centroid |

---

## 4. Audit Conclusion & Baseline Status
- **Baseline Unit Tests:** 72 / 72 Passing (100% OK)
- **Functional Endpoints:** All existing endpoints respond with valid schemas.
- **Frontend Syntax & Rendering:** 0 syntax errors, 0 unhandled promise rejections on load.
- **Safety Backups:** Fully preserved in `backups/2026-11-03/` and classic fallback verified at `frontend/index_classic.html`.
