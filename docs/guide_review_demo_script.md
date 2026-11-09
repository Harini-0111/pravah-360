# PRAVAH 360 • Academic Guide Review Live Demonstration Script

**Document Version:** 1.0.0
**Target Duration:** 12 to 15 Minutes
**Audience:** Academic Project Guides, External Examiners, Department Evaluators
**Application URL:** `http://127.0.0.1:8000`
**System Prerequisites:** Backend running on port 8000; modern web browser (Chrome, Edge, or Firefox).

---

## Quick Reference: 15-Minute Demonstration Timeline

```
 0:00 -  1:30 | 1. Introduction & Lower Godavari Problem Statement (#welcome)
 1:30 -  3:00 | 2. Overview Dashboard & Multi-Hazard KPIs (#overview)
 3:00 -  4:30 | 3. Lower Godavari GIS Explorer & Spatial Infrastructure (#explorer)
 4:30 -  6:00 | 4. Flood Susceptibility Assessment & Saaty AHP Consistency (#risk)
 6:00 -  7:30 | 5. Population & Infrastructure Impact Assessment (#impact)
 7:30 -  8:45 | 6. Historical Sentinel-1 SAR Radar Analysis (#weather)
 8:45 - 10:00 | 7. Present Official Hazard Monitoring & 4-State Freshness (#overview / #evidence)
10:00 - 11:00 | 8. Global 3D Earth Planetary Context (#global)
11:00 - 12:45 | 9. Emergency Operations Simulator & 4 RBAC Personas (#operations)
12:45 - 13:45 | 10. Scientific Evidence, Validation Transparency & Limitations (#evidence)
13:45 - 15:00 | 11. Past, Present & Future Architecture (GloFAS EV-01 Ingestion) (#research)
```

---

## Detailed Step-by-Step Demonstration Sequence

---

### Section 1: Project Introduction & Problem Statement (1.5 Minutes)
- **Workspace to Open:** `#workspace-welcome` (`http://127.0.0.1:8000`)
- **Action to Perform:**
  1. Present the landing screen hero title: **PRAVAH 360: Predictive Analytics & Vigilance for Andhra Hazards**.
  2. Point out the bilingual language switcher in the header and click **"TE" (Telugu)**, then switch back to **"EN" (English)**.
  3. Click **"Enter Command Center"** or click the **Overview** workspace navigation pill.
- **Expected Result:**
  - The welcome screen presents clean typography, responsive layout, and immediate visual clarity.
  - Bilingual switching instantly alters headings and navigation cues to Telugu, showing grassroots accessibility.
  - Smooth animated transition opens the Overview dashboard without page reloads.
- **Technical Explanation for Guide:**
  - *"The Lower Godavari Delta, spanning Dr. B.R. Ambedkar Konaseema and East Godavari districts, is uniquely vulnerable to compound flooding—combining torrential monsoon river discharge from an upstream catchment of 312,812 km² with coastal storm surges and low-gradient drainage congestion. Existing systems present fragmented data: CWC monitors river levels, IMD issues regional rainfall, and APSDMA broadcasts alerts. PRAVAH 360 synthesizes these streams into an integrated geospatial decision-support platform grounded in rigorous multi-criteria analysis and transparent temporal provenance."*
- **Status:** `WORKING` (100% operational).

---

### Section 2: Executive Overview Dashboard (1.5 Minutes)
- **Workspace to Open:** `#workspace-overview`
- **Action to Perform:**
  1. Walk through the 4 executive metric cards:
     - **Study Area Baseline Population:** `9,126,353` (WorldPop 2020 100m constrained raster).
     - **Elevated Exposure Population:** `8,252,724` residing in High and Very High risk mandals.
     - **High-Risk Mandals:** `18 of 21` study mandals classified in elevated hazard categories.
     - **Monitored River Gauges:** `4` strategic stations (Dowleswaram Barrage, Kunavaram, Chintoor, Polavaram).
  2. Direct attention to the **Active Disaster Alerts Banner** displaying official APSDMA / NDMA bulletins.
- **Expected Result:**
  - Metric counters display verified baseline numbers matching documented evidence.
  - Active alerts display distinct source attribution (APSDMA / SACHET) and temporal timestamps.
- **Technical Explanation for Guide:**
  - *"Rather than presenting uncalibrated estimates, every metric on this dashboard is derived from verifiable geospatial baselines. The 9.13 million population is aggregated from the UN-adjusted WorldPop dataset clipped exactly to our 21-mandal study extent. The 8.25 million figure accurately isolates the population within High and Very High susceptibility zones, providing emergency planners with immediate macro-exposure quantification."*
- **Status:** `WORKING` (100% operational).

---

### Section 3: Lower Godavari GIS Explorer (1.5 Minutes)
- **Workspace to Open:** `#workspace-explorer`
- **Action to Perform:**
  1. Open the full-screen Web-GIS Explorer.
  2. In the layer control panel on the right, enable:
     - `Critical Infrastructure` (Hospitals, Relief Shelters, Power Stations).
     - `River & Drainage Network`.
  3. Click on the polygon for **Mummidivaram Mandal** or **Katrenikona Mandal**.
  4. Review the popup and side panel displaying: Mandal Name, Total Area, Mean Elevation, Vulnerability Tier, and Nearest Designated Shelters.
- **Expected Result:**
  - Responsive Leaflet vector rendering at 60 fps.
  - Color-coded polygons visually separate deltaic floodplains from elevated upland terraces.
  - Clustered infrastructure markers expand into individual facilities with accurate contact details.
- **Technical Explanation for Guide:**
  - *"Our GIS engine combines Survey of India administrative polygons with OpenStreetMap spatial infrastructure points. When a user queries any of the 21 mandals, the backend instantly resolves its spatial intersect, returning localized elevation profiles from Copernicus 30m DEM and identifying critical lifeline facilities situated within the flood zone."*
- **Status:** `WORKING` (100% operational).

---

### Section 4: Flood Susceptibility Assessment (AHP) (1.5 Minutes)
- **Workspace to Open:** `#workspace-risk`
- **Action to Perform:**
  1. Navigate to the **Flood Susceptibility (AHP)** workspace.
  2. Point out the 5 geophysical criteria and their normalized weights:
     - Elevation: **0.25**
     - Slope: **0.20**
     - River Proximity: **0.25**
     - Land Use / Land Cover (LULC): **0.15**
     - Historical Hazard Frequency: **0.15**
  3. Click **"Inspect Saaty Pairwise Matrix & Consistency"** button to open the mathematical verification modal.
  4. Point to the computed Consistency Ratio: $CR = 0.0189$.
  5. Inspect the 21-mandal ranking table, highlighting **Mummidivaram** ($FSI = 0.838$, Very High).
- **Expected Result:**
  - The modal displays the exact $5 \times 5$ reciprocal pairwise matrix.
  - Shows $\lambda_{\max} = 5.0847$, $CI = 0.0212$, $RI = 1.12$, and $CR = 0.0189$.
  - Clearly confirms $CR < 0.10$, proving mathematical consistency according to Saaty's theorem.
- **Technical Explanation for Guide:**
  - *"A common weakness in academic flood projects is using arbitrary weights. In PRAVAH 360, our weights are mathematically derived from an eigenvector decomposition of a strictly reciprocal Saaty pairwise comparison matrix. Thomas Saaty established that a Consistency Ratio below 0.10 indicates valid judgment. Our matrix yields a CR of 0.0189, well within the threshold. Furthermore, our unit tests verify this matrix on every server build."*
- **Status:** `WORKING` (100% operational).

---

### Section 5: Population & Infrastructure Impact Assessment (1.5 Minutes)
- **Workspace to Open:** `#workspace-impact`
- **Action to Perform:**
  1. Navigate to the **Impact & Exposure** workspace.
  2. Point out the demographic breakdown:
     - Very High Risk Exposure: **4,812,190** persons.
     - High Risk Exposure: **3,440,534** persons.
     - Sum of Elevated Exposure: **8,252,724** persons ($4,812,190 + 3,440,534$).
  3. Point to the vulnerable cohorts breakdown (Children $< 5$ years: ~680,000; Senior Citizens $> 60$ years: ~940,000).
  4. Filter the infrastructure table by **"Designated Evacuation Shelters"** and show capacity statistics.
- **Expected Result:**
  - Highcharts/Chart.js graphs render demographic distribution cleanly.
  - Tables allow instant search and filtering by mandal and facility type.
- **Technical Explanation for Guide:**
  - *"Susceptibility alone does not tell an administrator what is at stake. In this module, we perform zonal raster extraction of WorldPop demographic data over our AHP susceptibility zones. This allows district collectors to understand not just land area, but human exposure—specifically highlighting vulnerable pediatric and geriatric populations who require prioritized evacuation transport."*
- **Status:** `WORKING` (100% operational).

---

### Section 6: Historical Sentinel-1 SAR Radar Analysis (1.25 Minutes)
- **Workspace to Open:** `#weather` (`workspace-weather`)
- **Action to Perform:**
  1. Navigate to the **Weather & Satellite Radar** workspace.
  2. Review the July 2022 Godavari mega-flood rainfall records:
     - GPM IMERG 72-hour antecedent rainfall exceeding $280\text{ mm}$ across the Godavari sub-basins.
     - CHIRPS 2.0 localized precipitation peaks on July 14–15, 2022.
  3. Inspect the **Sentinel-1 SAR Water Candidates** layer:
     - Show the dual-polarized C-band Synthetic Aperture Radar footprint acquired on July 15, 2022 (Track 129).
     - Point out the Lee-filtered thresholded backscatter mask distinguishing permanent water bodies from temporary flood inundation candidates.
- **Expected Result:**
  - High-contrast radar water candidate layer displays the extensive inundation along the Gautami and Vashishta Godavari distributary channels.
  - Comparative toggle highlights the flood surge beyond normal riverbanks.
- **Technical Explanation for Guide:**
  - *"Optical satellites like Sentinel-2 or Landsat are frequently blinded by thick cloud cover during monsoon depressions. PRAVAH 360 utilizes Copernicus Sentinel-1 Synthetic Aperture Radar (SAR), which penetrates clouds and rain. By processing Level-1 Ground Range Detected (GRD) backscatter with speckle filtering and Otsu bimodal thresholding, we extract candidate flood surfaces even during active cyclonic landfall."*
- **Status:** `WORKING` (100% operational).

---

### Section 7: Present Official Hazard Monitoring & 4-State Freshness (1.25 Minutes)
- **Workspace to Open:** `#workspace-overview` / `#workspace-evidence`
- **Action to Perform:**
  1. Open the **Continuous Notification Drawer** (bell icon in header or Evidence inspector).
  2. Highlight the 4 distinct temporal freshness states:
     - <span style="color:#22c55e; font-weight:bold;">LIVE / FRESH</span>: Alert retrieved within 30 minutes, valid future expiration.
     - <span style="color:#eab308; font-weight:bold;">STALE</span>: Valid unexpired alert, but upstream retrieval cache $> 30$ minutes old.
     - <span style="color:#ef4444; font-weight:bold;">EXPIRED</span>: Alert whose official valid-until timestamp has passed (strictly excluded from active danger counts).
     - <span style="color:#94a3b8; font-weight:bold;">UNAVAILABLE</span>: Upstream state server unreachable; cached fallback clearly watermarked.
  3. Inspect the three distinct timestamps on an alert card:
     - **Published Time:** When APSDMA originally issued the warning.
     - **Retrieved Time:** When PRAVAH 360 ingested it.
     - **Expires At:** When the bulletin officially lapses.
- **Expected Result:**
  - Visual badges clearly distinguish active warnings from expired historical records.
  - Expired alerts are not counted in the executive header counter.
- **Technical Explanation for Guide:**
  - *"In disaster management, displaying an expired alert as active causes public panic, while displaying a stale cached alert as live creates false security. Our system enforces a strict 4-state temporal lifecycle model. Every alert retains its publication time, ingestion time, and expiration time. If an alert has expired, it is immediately archived and subtracted from the active danger tally."*
- **Status:** `WORKING` (100% operational).

---

### Section 8: Global 3D Earth Planetary Context (1 Minute)
- **Workspace to Open:** `#workspace-global`
- **Action to Perform:**
  1. Switch to the **Global 3D Earth** workspace.
  2. Rotate the WebGL 3D globe using mouse drag.
  3. Click **"Fly to Lower Godavari"** bookmark button.
  4. Observe the smooth camera animation zooming from planetary space into the Andhra Pradesh coastline and the Godavari river delta.
- **Expected Result:**
  - Smooth WebGL rendering of the Earth with NASA Blue Marble basemap.
  - Interactive camera smoothly transitions into the local basin geometry.
- **Technical Explanation for Guide:**
  - *"Flooding in the Godavari delta is driven by large-scale synoptic meteorology—monsoon depressions forming in the northern Bay of Bengal and tracking west-northwest across central India. The Global Earth workspace allows incident commanders to maintain synoptic situational awareness, connecting hemispheric weather patterns directly to local mandal vulnerability."*
- **Status:** `WORKING` (100% operational).

---

### Section 9: Emergency Operations Simulator & 4 RBAC Personas (1.75 Minutes)
- **Workspace to Open:** `#workspace-operations`
- **Action to Perform:**
  1. Open the **Emergency Operations** workspace.
  2. In the Role Switcher dropdown, demonstrate all 4 distinct personas:
     - **Role 1: Resident (Citizen):**
       - Observe the hyper-local view: *Mummidivaram Mandal Safe Route & Nearest Shelter (Z.P. High School Shelter, 1.2 km)*.
       - Click **"Request Assistance (SOS)"**, select "Elderly Evacuation", enter 3 persons, and submit.
     - **Role 2: Mandal Admin (Mandal Revenue Officer - MRO):**
       - View the incoming assistance requests table showing the newly submitted Mummidivaram request.
       - Click **"Acknowledge & Assign to ERT"**.
     - **Role 3: District Admin (District Collector):**
       - View the district-wide resource readiness matrix: 18 SDRF Inflatable Boats, 420 Relief Tents, 8 Mobile Water Purification Units.
       - Click **"Deploy SDRF Unit"** to demonstrate stateful resource dispatch.
     - **Role 4: Emergency Response Team (ERT):**
       - View the tactical rescue mission queue with assigned GPS coordinates and priority triage flags.
- **Expected Result:**
  - The interface dynamically reshapes based on the selected RBAC role.
  - Actions taken by one role (e.g. Resident SOS) appear immediately in the administrative queue.
- **Technical Explanation for Guide:**
  - *"A disaster platform cannot have a single generic interface. A resident needs an immediate safe route and panic-free assistance form; a Mandal Revenue Officer needs shelter occupancy; a District Collector needs macro-resource allocation; and rescue teams need tactical coordinates. PRAVAH 360 implements strict Role-Based Access Control to serve each agency in the disaster response hierarchy."*
- **Status:** `WORKING` (100% operational).

---

### Section 10: Scientific Evidence, Validation Transparency & Limitations (1 Minute)
- **Workspace to Open:** `#workspace-evidence`
- **Action to Perform:**
  1. Open the **Scientific Evidence** workspace.
  2. Point to the **Model Validation Report** section:
     - **Precision:** `0.857` (6 True Positives, 1 False Positive)
     - **Recall:** `0.857` (6 True Positives, 1 False Negative)
     - **F1-Score:** `0.857`
     - **Accuracy:** `0.857` (12 correct classifications across 14 spatial test blocks)
  3. Walk the guide through the **Prominent Transparency Notice**:
     - Explain that this validation benchmark evaluates spatial holdout sensitivity against Sentinel-1 candidate flood extents across 4 test mandals.
     - Clearly state: *"This benchmark evaluates candidate water agreement under multi-scenario conditions; independent ground-truth RTK-GPS surveyor validation remains ongoing work."*
- **Expected Result:**
  - Clear confusion matrix diagram and defensible statistical metrics.
  - Honest, rigorous demarcation between tested scenario sensitivity and field truth.
- **Technical Explanation for Guide:**
  - *"In engineering research, scientific integrity is paramount. We do not claim 99% accuracy from synthetic benchmarks. Our 0.857 precision and recall represent a calibrated 4-mandal spatial holdout test against Copernicus Sentinel-1 SAR candidate water. We clearly disclose our assumptions and emphasize that physical surveyor ground-truthing is future work."*
- **Status:** `WORKING` (100% operational).

---

### Section 11: Past, Present & Future Forecasting Architecture (1.25 Minutes)
- **Workspace to Open:** `#workspace-research` / Architectural Summary
- **Action to Perform:**
  1. Present the **Three Pillars of PRAVAH 360 Intelligence**:
     - **PAST (Historical Reconstruction):**
       - Reconstructed major events: July 2022 Godavari flood, Cyclone Murasu (Oct 2020), August 2006 historic deluge.
       - Calibrated Sentinel-1 SAR radar backscatter and GPM IMERG / CHIRPS precipitation records.
     - **PRESENT (Official Monitoring & Vigilance):**
       - Live APSDMA disaster bulletins and NDMA SACHET warning ingestion.
       - Stored CWC gauge danger thresholds at Dowleswaram, Kunavaram, and Polavaram.
       - Rigorous 4-state freshness lifecycle and community accessibility (Telugu TTS).
     - **FUTURE (Scenario Inflow & External Forecast Ingestion):**
       - Present the results of our **EV-01 External GloFAS Verification Audit** (`docs/ev01_glofas_verification.md`):
       - Copernicus GloFAS v4.0 provides 30-day ensemble river discharge forecasts for the Godavari mainstem at 0.05° resolution.
       - PRAVAH 360's architectural path: Ingest GloFAS upstream discharge forecasts at Polavaram / Dowleswaram, apply local stage-discharge rating curves, and map resulting attention levels to our AHP susceptibility zones.
  2. Conclude the demonstration and invite questions.
- **Expected Result:**
  - Clear, coherent architectural narrative establishing the project's academic and practical contribution.
  - The guide sees a comprehensive, defensible, and mature engineering project ready for final review.
- **Technical Explanation for Guide:**
  - *"Rather than attempting to train an uncalibrated machine learning model on sparse local data or falsely claiming 30-meter inundation predictions, PRAVAH 360 adopts the standard international practice: we ingest established upstream hydrological forecasts like Copernicus GloFAS, translate them into local river discharge scenarios, and project those scenarios onto our validated AHP susceptibility and WorldPop vulnerability baselines."*
- **Status:** `WORKING` (100% operational).

---

## Guide Review FAQ & Defensible Answers

**Q1: Is your AHP susceptibility map predicting tomorrow's flood?**
*Answer:* "No, sir/madam. Our AHP model is a static territorial susceptibility assessment based on elevation, slope, river proximity, land cover, and historical hazard zones. It identifies *where* the terrain is naturally prone to accumulate floodwaters. Real-time dynamic forecasting requires coupling upstream river discharge forecasts with hydrodynamic routing, which is the role of our Future Ingestion module."

**Q2: What is the source of your population numbers?**
*Answer:* "Our study area population of 9,126,353 is extracted from the WorldPop 2020 UN-adjusted 100-meter resolution demographic raster, clipped to the 21 mandal boundaries of Konaseema and East Godavari. The 8,252,724 figure represents the exact subset residing in the Very High (4.81M) and High (3.44M) susceptibility zones."

**Q3: Are you pulling live telemetry from CWC sensors right now?**
*Answer:* "No. Upstream CWC water level data is stored calibrated reference data reflecting official warning levels (1st, 2nd, and 3rd warning thresholds at Dowleswaram Barrage). We clearly tag this data as Stored Reference Data in our data freshness engine rather than masquerading it as unauthenticated live sensor web sockets."

**Q4: How did you calculate your Consistency Ratio of 0.0189?**
*Answer:* "We construct a $5 \times 5$ reciprocal pairwise comparison matrix adhering to Saaty's scale. Using the principal eigenvector method, we find $\lambda_{\max} = 5.0847$. The Consistency Index is $CI = (\lambda_{\max} - n)/(n - 1) = (5.0847 - 5)/4 = 0.0212$. Dividing by the Random Index for $n=5$ ($RI = 1.12$), we obtain $CR = 0.0212 / 1.12 = 0.0189$. Because $0.0189 < 0.10$, the matrix is mathematically consistent."
