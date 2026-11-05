# Frontend GIS & 3D Earth Architecture Documentation

**System:** AI-Based Flood Risk, Impact Assessment and Emergency Decision Support System  
**Version:** 5.2.0 (Phase 5.2 GIS-First Web Application)  
**Workspace:** `c:\major project\frontend`  

---

## 1. Overview & Architectural Philosophy

The frontend is architected as a **GIS-First Web Application** designed for rapid geospatial exploration, analytical flood susceptibility modeling, and global contextual awareness. 

### Key Architectural Tenets:
- **Zero Node Build Dependency:** Written in clean, modern vanilla JavaScript (ES6+), CSS3, Leaflet, and Globe.gl. Can be served by any standard HTTP/ASGI server without compilation, bundlers, or Babel/Webpack overhead.
- **Client-Side Workspace Routing:** A lightweight state machine coordinates 7 dedicated workspaces within a persistent application shell, eliminating full-page reloads and preserving Map/Globe canvas contexts.
- **Canvas-Accelerated Spatial Rendering:** Map containers utilize Leaflet's `preferCanvas: true` mode to efficiently display thousands of vectorized river reaches, administrative boundaries, and community facilities at 60 FPS.
- **Lazy Map Initialization:** Sub-workspaces (`#overview-map`, `#risk-map`, `#impact-map`) are initialized only upon their first activation, preventing off-screen dimension calculation defects and optimizing initial load times.
- **Unified Location State:** Changes to the active inspected location (via map clicks, universal search, country flight, or ranking table selection) immediately propagate to all relevant views and drawers through `appState.selectedLocation`.

---

## 2. Directory Layout & Key Files

```
frontend/
├── index.html            # Unified application shell containing all 7 workspace DOM sections
├── styles.css            # Geospatial dark intelligence design system & responsive layout
├── app.js                # Core controller: workspace router, Leaflet manager, Globe.gl manager
├── globe.gl.min.js       # Localized WebGL 3D Globe library (1.0 MB, zero CDN dependency)
├── data/                 # Localized static vector datasets
│   ├── world_countries.geojson             # Natural Earth 110m countries (177 countries, 293 KB)
│   ├── lower_godavari_study_area.geojson   # Dissolved study area perimeter (750 B)
│   ├── lower_godavari_districts.geojson    # 6 district boundary polygons (80.5 KB)
│   └── lower_godavari_hydrorivers.geojson  # HydroRIVERS reach vectors (1.33 MB)
└── overlays/             # Lightweight Sentinel-1 SAR Web PNG overlays
    ├── metadata.json
    ├── sentinel1_flood_candidates_track129.png
    ├── sentinel1_permanent_water.png
    └── sentinel1_ambiguous_wetsoil.png
```

---

## 3. Workspace State Machine & Lifecycle

The client controller coordinates 7 workspaces:

```
[Overview] <--> [Geospatial Explorer] <--> [Flood Risk] <--> [Impact] <--> [Weather] <--> [Global 3D] <--> [Evidence]
```

### Tab Switching Mechanics (`switchWorkspace(workspaceId)`):
1. **DOM Visibility:** Removes `.active` from previous `.workspace` and adds it to `#workspace-{id}`.
2. **Navigation Indication:** Updates `.nav-item.active` on the left sidebar.
3. **Utility Header Sync:** Updates `#currentWorkspaceHeading` and `#currentWorkspaceSubheading`.
4. **Map Viewport Invalidation:** Dispatches `map.invalidateSize()` after a 60ms delay to ensure Leaflet recalculates pixel dimensions accurately when containers become visible.
5. **Lazy Initializer Hook:**
   - `explorer` -> `initExplorerMap()`
   - `overview` -> `initOverviewMap()`
   - `risk` -> `initRiskMap()`
   - `impact` -> `initImpactMap()`
   - `weather` -> `loadWeatherData()`
   - `global` -> `initGlobalEarth()`

---

## 4. Map & Basemap Providers

### Keyless Basemap Configuration:
To prevent API key watermarks (such as CARTO's unauthenticated watermark defect), the system uses keyless, reliable providers:

```javascript
// Esri World Dark Gray Canvas (Default)
const esriDark = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
  attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
  maxZoom: 16
});

// Esri World Imagery (Satellite)
const esriSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
  attribution: 'Tiles &copy; Esri',
  maxZoom: 18
});

// OpenStreetMap Standard
const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors',
  maxZoom: 19
});
```

The active basemap is controlled dynamically via radio inputs in the GIS Layer Catalogue (`input[name="basemapRadio"]`).

---

## 5. Global 3D Earth Integration (`Globe.gl`)

The Global 3D Earth workspace uses a locally hosted build of `Globe.gl` running in WebGL:

### Features:
- **Geometry & Rendering:** Uses Natural Earth 110m GeoJSON polygons (`/static/data/world_countries.geojson`) rendered as 3D extruded polygons with ambient night atmospheric textures.
- **Continuous Auto-Rotation:** Enabled via `globeInstance.controls().autoRotate = true; autoRotateSpeed = 0.6;`. Can be toggled on/off via the top toolbar button (`#btnToggleGlobeRotation`).
- **Smooth Flight Transitions:** Clicking any country polygon or selecting a search result executes `globeInstance.pointOfView({ lat, lng, altitude: 1.6 }, 1400)` to smoothly orient the planetarium towards that nation.
- **Regional Transition Bridge:** When India is selected, the floating country card displays an action button `Zoom to Regional Prototype (Lower Godavari Basin)` which invokes `switchWorkspace('explorer')` and flies the 2D Leaflet camera directly to Rajahmundry.

---

## 6. API Service Contracts & Endpoints

| Endpoint URL | HTTP Method | Function | Description |
| :--- | :---: | :--- | :--- |
| `/api/v1/health` | `GET` | `health_check` | System status and active study area identifier. |
| `/api/v1/boundaries/mandals-geojson` | `GET` | `get_mandals_geojson` | 21-mandal boundary polygons (GADM v4.1 / 2022 AP). |
| `/api/v1/flood-risk/basin-assessment` | `GET` | `get_basin_assessment_alias` | AHP rankings, scores, and zonal demographics for 21 mandals. |
| `/api/v1/flood-risk/mandal/{name}` | `GET` | `get_mandal_risk_alias` | Detailed factor breakdown and drivers for a single mandal. |
| `/api/v1/flood-risk/point-assessment` | `GET/POST` | `evaluate_point_risk_get` | Real-time coordinate inspection (elevation, slope, river dist). |
| `/api/v1/infrastructure/facilities` | `GET` | `get_facilities_alias` | 1,635 OSM community facilities (healthcare, schools, shelters). |
| `/api/v1/water-levels/stations` | `GET` | `get_water_level_stations_alias` | 10 hydrometric river monitoring stations. |
| `/api/v1/alerts/feed` | `GET` | `get_alerts_feed_alias` | Active decision advisories and susceptibility bulletins. |
| `/api/v1/weather/current` | `GET` | `get_current_weather` | Real-time atmospheric conditions (temp, humidity, wind). |
| `/api/v1/weather/forecast` | `GET` | `get_weather_forecast_alias` | 5-day daily precipitation and temperature forecast. |
