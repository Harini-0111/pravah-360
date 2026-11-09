# PRAVAH 360 Major Project Report: Enhancement & QA Audit Report

**Date of Execution:** 08 November 2026
**Target Documents Generated:**
1. **Editable DOCX:** [`C:\major project\PRAVAH360_Final_Formatted_Report.docx`](PRAVAH360_Final_Formatted_Report.docx) (8.55 MB)
2. **Final Typeset PDF:** [`C:\major project\PRAVAH360_Final_Formatted_Report.pdf`](PRAVAH360_Final_Formatted_Report.pdf) (3.41 MB, 86 Pages)
3. **Diagram Assets Directory:** [`C:\major project\report_diagrams\`](report_diagrams) (10 High-Resolution 300 DPI PNG diagrams)
4. **Screenshot Assets Directory:** [`C:\major project\report_screenshots_final\`](report_screenshots_final) (9 Distinct Verified Application PNG screenshots)

---

## 1. Executive Summary

In accordance with academic standards and guidelines derived from the reference major project report (*AI-Powered Interview Assistant*), the PRAVAH 360 Major Project Report has undergone a comprehensive visual and structural enhancement.

Key milestones accomplished:
1. **Chapter 4 Architecture Diagrams:** All 10 requested high-resolution, colourful architecture diagrams, data flow diagrams (DFDs), sequence diagrams, and end-to-end operational workflows have been programmatically generated at 300 DPI and typeset directly into their respective Chapter 4 sections.
2. **Chapter 2 Literature Survey Citations:** Formatted to adhere strictly to formal IEEE surname citation conventions (**Surname et al. [X]** / **Surname [X]**).
3. **Chapter 10 Application Screenshots Overhaul:** All duplicate placeholder screenshots were permanently eliminated. 9 completely distinct, verified, high-resolution application screenshots were captured directly from the live application and embedded into Chapter 10 with exact mathematical pagination across the Table of Contents and List of Figures.
4. **Scientific Integrity Preservation:** 100% of the project's original technical claims, case study baseline figures (9,126,353 population, 1,542 critical facilities, 21 Lower Godavari mandals, 18,498.23 sq km UTM area), model evaluation metrics (89.6% accuracy, 0.088 Brier score, 0.034 ECE), student details, supervisor credentials, and passing test suites have been preserved without alteration.

---

## 2. Chapter 4 Diagram Enhancement Audit

All 10 diagrams were engineered with vector-quality clarity at 300 DPI using a unified, professional academic palette (Navy Blue `#1B4F72`, Dark Teal `#0E6655`, Emerald Green `#1E8449`, Amber `#B9770E`, Crimson `#922B21`, Royal Purple `#512E5F`, and neutral card fills `#F8F9F9`, `#EBF5FB`, `#E8F8F5`).

| Section | Figure Number & Title | File Asset | Dimensions & DPI | Core Technical Elements Illustrated |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | **Figure 4.1:** Multi-Layer System Architecture of PRAVAH 360 | `fig4_1_system_architecture.png` | 3600 x 3000 (300 DPI) | 6 decoupled architectural layers: Layer 1 (Multi-Source Data Acquisition: DEM, WorldCover, WorldPop, HydroSHEDS, OSM, SAR, GPM/CHIRPS, CWC/IMD); Layer 2 (Harmonization: EPSG:4326/32644, STRtree indexing, -9999.0 sentinels); Layer 3 (Geospatial AI: AHP 5x5 matrix, Random Forest, Isotonic calibration); Layer 4 (Decision Support: RAPI, knapsack solver); Layer 5 (FastAPI backend); Layer 6 (Leaflet 2D GIS, 3D WebGL Globe, Telugu Voice Assistant, Notification Drawer). |
| **4.6** | **Figure 4.2:** Modular FastAPI Backend Architecture and API Service Routing | `fig4_2_backend_architecture.png` | 3300 x 2550 (300 DPI) | Asynchronous FastAPI architecture (`main.py`), CORS middleware, lifespan management, 10 versioned REST endpoints (`/api/v1/*`), decoupled domain service classes (`GeographicIdentificationService`, `FloodRiskService`, `ResourceAllocationService`, `AlertMonitoringService`), Pydantic models, and GeoJSON streaming. |
| **4.7** | **Figure 4.3:** Frontend Single Page Application and Interactive GIS Architecture | `fig4_3_frontend_architecture.png` | 3300 x 2550 (300 DPI) | Client viewport (`index.html`, `styles.css`), master state & router (`app.js`), 2D Leaflet.js explorer (`map.js`), 3D Three.js WebGL globe (`globe.js`), W3C Web Speech API Telugu voice engine (`voice.js`), sliding emergency drawer (`notifications.js`), and non-blocking asynchronous `fetch()` API bridge. |
| **4.8** | **Figure 4.4:** Data Flow Diagram Level 0 (Context Level Diagram) | `fig4_4_dfd_level_0.png` | 3000 x 2250 (300 DPI) | Central system `0.0 PRAVAH 360` exchanging bidirectional data flows with 5 external entities: Citizens/Residents, District/Mandal Administrators, Emergency Responders (NDRF/SDRF), Earth Observation catalogues, and CWC/IMD hydrographic telemetry. |
| **4.8** | **Figure 4.5:** Data Flow Diagram Level 1 (Macro-Process Decomposition) | `fig4_5_dfd_level_1.png` | 3300 x 2550 (300 DPI) | 5 macro-processes (1.0 Ingestion, 2.0 Susceptibility Modeling, 3.0 Exposure Assessment, 4.0 Resource Optimization, 5.0 Visualization & Delivery) interacting across 5 standardized data stores (D1 Harmonized Rasters, D2 Susceptibility Store, D3 Demographics & OSM Store, D4 Resource Quotas, D5 Telemetry Cache). |
| **4.8** | **Figure 4.6:** Data Flow Diagram Level 2 (Decomposition of Flood Susceptibility and Exposure Assessment) | `fig4_6_dfd_level_2.png` | 3300 x 2550 (300 DPI) | Granular decomposition of sub-processes: 2.1 Feature extraction, 2.2 AHP pairwise evaluation (CR=0.0001), 2.3 FSI calculation, 2.4 Tier classification, 3.1 WorldPop zonal aggregation, 3.2 Critical facility extraction (1,542 assets), 3.3 Bilingual driver synthesis, 3.4 Payload delivery. |
| **4.9** | **Figure 4.7:** UML Sequence Diagram: Resident Geospatial Risk Query and Voice Guidance | `fig4_7_sequence_resident_query.png` | 3300 x 2550 (300 DPI) | End-to-end message sequence across 6 lifelines (Resident, Browser, `voice.js`, FastAPI, STRtree Spatial Index, MCE Engine) showing Telugu query capture, coordinate lookup (<1.2ms), FSI evaluation, and localized `te-IN` audio speech synthesis. |
| **4.9** | **Figure 4.8:** UML Sequence Diagram: Emergency Resource Allocation and Logistics Dispatch | `fig4_8_sequence_resource_coordination.png` | 3300 x 2550 (300 DPI) | Message exchange across 5 lifelines (Collector, Dashboard, FastAPI, Knapsack Solver, Mandal Store) modeling stockpile ingestion (50 boats, 100 kits, 200k rations), RAPI scoring, Lanka 1-boat guarantee, and Hare-Niemeyer integer apportionment. |
| **4.9** | **Figure 4.9:** UML Sequence Diagram: Real-Time Hydrographic Alert and Freshness Ingestion | `fig4_9_sequence_alert_monitoring.png` | 3300 x 2550 (300 DPI) | Ingestion sequence across 6 lifelines (CWC/IMD Feeds, Ingestion Worker, Alert Cache, FastAPI, Notification Drawer, Incident Commander) modeling automated polling, timestamp auditing, freshness calculation, and Stage 3 (17.75 ft) emergency auto-trigger. |
| **4.11** | **Figure 4.10:** End-to-End System Operational Workflow and Decision Logic | `fig4_10_operational_workflow.png` | 3300 x 3000 (300 DPI) | Comprehensive flowchart detailing the full lifecycle: user launch, persona selection, spatial boundary validation decision diamond, Telugu voice branch, administrative credential check, CWC gauge threshold branching (10.0ft, 13.75ft, 17.75ft), and continuous monitoring loop. |

---

## 3. Literature Survey (Chapter 2) Citation Audit

In-text citations in Chapter 2 have been reconciled with the authoritative 25-item bibliography, enforcing the academic convention:
- **Multiple Authors:** `[First Author Surname] et al. [Ref]`
- **Single Author / Organization:** `[Author Surname / Acronym] [Ref]`

### Verified Author Attributions Applied:
1. **Section 2.1 (Primary Reference):**
   - *Previous:* Generic paper title.
   - *Corrected:* **Adnan et al. [1]** investigated *"A Novel Framework for Addressing Uncertainties in Machine Learning-Based Geospatial Approaches for Flood Prediction"* (*Journal of Environmental Management*, Elsevier, 2023).
2. **Table 2.1 (Row 1):**
   - *Attribution:* **Adnan et al. [1]** (Uncertainties in ML Flood Prediction, 2023).
3. **Table 2.1 (Row 8):**
   - *Attribution:* **Central Water Commission (CWC) [3]** & Google Flood Hub Collaboration (2020–2025).
4. **Section 2.2 Subsection 1 (Multi-Criteria Frameworks):**
   - *Attribution:* Analytic Hierarchy Process formulated by **Saaty [2]**; bivariate statistical frameworks established by **Tehrany et al. [19]**.
5. **Section 2.2 Subsection 2 (Deep Sequential Models):**
   - *Attribution:* Classical hydrological formulations by **Ramirez [24]** and **Chow et al. [25]**.
6. **Section 2.2 Subsection 3 (Spatial Topology & GNNs):**
   - *Attribution:* Machine learning uncertainty characterization by **Adnan et al. [1]** and climate risk perspectives by **Merz et al. [20]**.
7. **Section 2.2 Subsection 4 (Operational Deployments):**
   - *Attribution:* **Central Water Commission (CWC) [3]** national gauge telemetry.

### Unverified Literature Entries Flagged for Faculty Review:
The following six comparative benchmark entries from Table 2.1 were surveyed as general domain benchmarks in the case study region but do not have separate individual entries in the 25-item bibliography:
1. *GIS-based AHP Flood Risk Assessment, Lower Godavari Basin (2024)* (Regional conference paper)
2. *Flood Detection in Upper Krishna Basin using AHP, FR & SI (2024)* (Monsoonal comparative study)
3. *Multivariate Multi-Step LSTM for Flood Runoff, Godavari Basin (2023)* (Catchment runoff study)
4. *Systematic Review of Flood Susceptibility in Data-Scarce Catchments (2025)* (Domain review)
5. *State-Wide Flash-Flood Susceptibility using GNNs (2026)* (arXiv preprint)
6. *Graph Attention Network for Pluvial Flood Susceptibility (2023)* (Urban inundation study)

*Status:* Preserved in Table 2.1 for comparative completeness without fabricating fictional author surnames.

---

## 4. Chapter 10 Application Screenshots Verification Audit

In response to the audit finding that previous versions of Chapter 10 contained duplicate and missing screenshot figures, all screenshots were completely overhauled. The PRAVAH 360 FastAPI server and frontend were executed live, and targeted headless/CDP automation scripts captured high-resolution, pixel-perfect screenshots of each specific feature and modal.

All 9 figures in Chapter 10 are **100% unique**, backed by verified cryptographic MD5 hashes, authentic dimensions, and exact page numbers:

| Figure No. | Caption Title | Image File | Size (Bytes) | MD5 Hash | Body Page | PDF Page | Feature Verified |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Figure 10.1** | PRAVAH 360 Executive Landing Interface (English) | `fig10_1.png` | 609,455 | `82f37f07f2...` | 53 | 66 | Executive landing page with KPI metrics, Godavari hydrographic gauge status, and dual-language selector. |
| **Figure 10.2** | Verified Telugu Voice Assistant Interface with te-IN Speech Synthesis | `fig10_2.png` | 874,384 | `ae09809cf8...` | 54 | 67 | Verified Telugu Voice Assistant drawer active with bilingual transcript, query chips, and `te-IN` audio synthesizer. |
| **Figure 10.3** | High-Resolution Desktop Situation Room View (1536x864) | `fig10_3.png` | 701,690 | `c63957f978...` | 54 | 67 | 2D Interactive GIS Situation Room with 21-mandal choropleth, layer toggles, and AHP susceptibility breakdown. |
| **Figure 10.4** | 3D WebGL Virtual Globe Bathymetric View and Cyclone Trajectory Tracking | `fig10_4.png` | 1,039,243 | `9d7c94b18b...` | 55 | 68 | Three.js WebGL 3D Globe with digital elevation relief, cloud cover, and Cyclone Murasu trajectory track. |
| **Figure 10.5** | Sentinel-1 SAR Track 129 Exploratory Floodwater Candidate Mask | `fig10_5.png` | 229,797 | `eb43c1f594...` | 56 | 69 | Calibrated Sentinel-1 SAR Track 129 floodwater candidate footprint across Konaseema coastal mandals. |
| **Figure 10.6** | Verified Emergency Notification Drawer and Multi-Mandal Alert Feed | `fig10_6.png` | 724,385 | `c000740064...` | 57 | 70 | Sliding Emergency Notification Drawer displaying real-time alert feed, source freshness badges, and CWC levels. |
| **Figure 10.7** | Emergency Resource Allocation Decision Matrix and Logistics Dispatch Interface | `fig10_7.png` | 321,653 | `76b40e5f20...` | 57 | 70 | Role-based ERT operations dashboard with RAPI prioritization scores, SDRF dispatch tables, and inventory tracking. |
| **Figure 10.8** | Cyclone Murasu Interactive Historical Replay Modal and River Hydrograph Surge | `fig10_8.png` | 366,119 | `9cfc35846c...` | 58 | 71 | Historical Replay Modal with live hydrograph canvas surge curves (17.85m peak), discharge rates, and mandal timeline. |
| **Figure 10.9** | Interactive Model Validation Modal Displaying Contingency Metrics and Calibration Curves | `fig10_9.png` | 367,328 | `6a810e7868...` | 59 | 72 | Model Validation Modal with full contingency matrix (TP=18, FP=2, FN=3, TN=25), Brier score, and calibration curves. |

**Integrity Verification:**
- Total Chapter 10 images in PDF: **9**
- Unique MD5 image stream hashes: **9 (Zero duplicates, 100% distinct)**
- All captions formatted in bold Times New Roman 11pt, centered, with `keep_with_next = True`.

---

## 5. Preservation & Document Integrity Verification

| Document Attribute | Target Requirement | Status in Final Output | Verification Evidence |
| :--- | :--- | :--- | :--- |
| **Project Title** | UNCERTAINTY-CALIBRATED GEOSPATIAL AI FOR FLOOD SUSCEPTIBILITY AND EMERGENCY RESOURCE ALLOCATION | **Preserved 100%** | Cover, Certificate, Declaration, Abstract, and Headings match identically. |
| **Team Details** | P. Harini (23A81A4348), P. Likhitha (23A81A4349), D. J.S.L.P.Durga (23A81A4311), K. Mokshagna Sai Teja (23A81A4321) | **Preserved 100%** | Verified across preliminary pages ii, iii, iv. |
| **Guide & Institutional Leadership** | Mr. M. V. Raghavendra Rao (Guide), Dr. G. Loshma (HOD), Dr. Ch. Rambabu (Principal), Sri Vasavi Eng. College | **Preserved 100%** | Sign-off blocks on Certificate and Acknowledgement preserved intact. |
| **Study Area Baseline** | 21 Mandals, 18,498.23 sq km UTM 44N area, 9,126,353 baseline population, 1,542 critical facilities | **Preserved 100%** | All numbers in Chapter 5, Chapter 8, and Appendix B remain exact. |
| **AI Model & Calibration Metrics** | Accuracy 89.6%, Precision 0.857, Recall 0.857, FAR 0.000, Brier 0.088, ECE 0.034 | **Preserved 100%** | Table 9.2 and Table 9.3 preserved without alteration. |
| **Automated Test Results** | 87 tests passed across 6 modules (100% pass rate in 21.96s) | **Preserved 100%** | Table 9.1 and Section 9.2 preserved exactly. |
| **Unrelated Chapters** | Chapters 1, 3, 5, 6, 7, 8, 9, 10, 11, References, Appendices A–F | **Preserved 100%** | Zero textual deletions or unwanted modifications. |

---

## 6. Pagination and Layout Verification

- **Section 1 (Preliminary Pages):** Roman numerals (`ii` to `xiii`). Cover page unnumbered (`differentFirstPage`).
- **Section 2 (Main Chapters & Body):** Decimal numerals starting at `1` on Chapter 1 and running continuously to `73` on Appendix F.
- **Total Paginated Extent:** **86 Pages** in Microsoft Word and compiled PDF.
- **Double-Line Borders:** Standardized double border (`<w:pgBorders w:val="double" w:sz="12" w:space="24"/>`) active on all 86 pages.
- **Table of Contents & List of Figures:** Dynamically synchronized with exact page locations via Word COM two-pass pagination. All 20 figures and 13 tables are listed with their precise page numbers matching the printed PDF.
