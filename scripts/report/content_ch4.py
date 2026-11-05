# Chapter 4: System Design and Architecture

CH4_CONTENT = {
    "num": "4",
    "title": "SYSTEM DESIGN AND ARCHITECTURE",
    "sections": [
        {
            "num": "4.1",
            "title": "Overall System Architecture",
            "level": 2,
            "paragraphs": [
                "The PRAVAH 360 platform is designed as an end-to-end, uncertainty-calibrated geospatial artificial intelligence and emergency decision-support system. Unlike legacy flood monitoring systems that operate solely on discrete point river gauges or isolated post-event satellite imagery, PRAVAH 360 integrates multi-source physical and environmental observations, statistical machine learning models, calibrated uncertainty quantification, and resource-constrained emergency optimization into a unified, modular architecture.",
                "The core engineering philosophy prioritizes three fundamental architectural tenets:",
                "1. Scientific Integrity and Separation of Concerns: Clear, non-negotiable boundaries are enforced between physical baseline flood susceptibility (intrinsic terrain vulnerability), dynamic meteorological forcing (rainfall and river discharge), and post-event satellite water detection (SAR backscatter difference). Inundation is never falsely claimed or fabricated without local ground-truth calibration.",
                "2. Asynchronous High-Throughput Processing: The backend services utilize non-blocking asynchronous I/O architectures powered by Python's asyncio and FastAPI, guaranteeing that intensive spatial bounding-box intersections, multi-criteria evaluations, and live API queries execute with sub-50ms latency.",
                "3. Multilingual Accessibility & Explainable Transparency: Every risk prediction is accompanied by a mathematically sound uncertainty metric and a plain-language narrative in both English and native Telugu, ensuring that decisions are fully interpretable by citizens, field personnel, and senior administrative commanders alike."
            ]
        },
        {
            "num": "4.2",
            "title": "High-Level Architecture (5-Tier Layered Framework)",
            "level": 2,
            "paragraphs": [
                "The system is organized into a formal five-tier architectural hierarchy, ensuring strict decoupling, maintainability, and horizontal scalability:",
                "1. Tier 1: Geospatial Data Ingestion Layer:",
                "   - Interfaces directly with external Earth Observation catalogues, open meteorological APIs, and authoritative governmental hydrographic feeds.",
                "   - Ingests Copernicus GLO-30 DSM elevation rasters, HydroSHEDS HydroRIVERS hydrography, ESA WorldCover land use maps, WorldPop 2020 UN-adjusted population grids, OpenStreetMap essential facility vectors, NASA GPM IMERG / CHIRPS precipitation cubes, and Sentinel-1 SAR orbital imagery.",
                "2. Tier 2: Spatial Harmonization & Preprocessing Pipeline Layer:",
                "   - Reprojects all heterogeneous datasets to unified spatial reference systems (WGS84 EPSG:4326 for web vector serving and UTM Zone 44N EPSG:32644 for metric Euclidean distance and slope calculations).",
                "   - Implements bilinear and nearest-neighbor raster resampling, nodata masking with -9999.0 sentinels, boundary topology healing (80m buffering), and R-tree spatial indexing via Shapely STRtree.",
                "3. Tier 3: Geospatial AI & Uncertainty Calibration Layer:",
                "   - Encapsulates the core analytical models: Analytical Hierarchy Process (AHP) multi-criteria evaluation, Random Forest ensemble classifier, and Platt / Isotonic regression probability calibration.",
                "   - Computes normalized Flood Susceptibility Indices (FSI), prediction confidence intervals, and Expected Calibration Error (ECE) metrics.",
                "4. Tier 4: Emergency Decision Support & Optimization Layer:",
                "   - Synthesizes susceptibility surfaces with population exposure and infrastructure density.",
                "   - Formulates and solves a multi-objective capacity-constrained knapsack optimization problem to generate the Resource Allocation Priority Index (RAPI) and optimal resource dispatch quotas (rescue boats, medical personnel, food rations).",
                "   - Generates plain-language explainable risk drivers for each administrative unit.",
                "5. Tier 5: Presentation & Multilingual Interaction Layer:",
                "   - Delivers an interactive, dark-themed Single Page Application (SPA).",
                "   - Integrates 2D Leaflet slippy maps, 3D WebGL planetary globes, real-time alert tickers, role-based administrative dashboards, and a native Web Speech API voice assistant supporting Telugu (`te-IN`) and English (`en-IN`)."
            ]
        },
        {
            "num": "4.3",
            "title": "Data Pipeline & Harmonization Architecture",
            "level": 2,
            "paragraphs": [
                "A foundational challenge in multi-source geospatial AI is the severe spatial and temporal heterogeneity of Earth Observation datasets. The data pipeline implements rigorous harmonization protocols to convert disparate data formats into synchronized analysis-ready data (ARD):",
                "1. Spatial Indexing & Boundary Harmonization:",
                "   - The 21 administrative mandals of the Lower Godavari Basin exhibit complex riverine geometries, islands, and estuary boundaries. Boundary topologies are normalized and indexed in memory using a two-dimensional R-tree (`shapely.strtree.STRtree`).",
                "   - When querying point coordinates (latitude/longitude), the system executes a bounding-box pre-filter in O(log N) time, followed by exact ray-casting point-in-polygon containment, completing point lookups in under 1.2 milliseconds.",
                "2. Raster Normalization & Resolution Bridging:",
                "   - The Copernicus DEM (30m), ESA WorldCover (10m/50m), and WorldPop (1km) rasters operate at differing cell resolutions. The harmonization engine resamples continuous elevation and slope fields using bilinear interpolation to preserve gradient continuity, while categorical land-cover classes are resampled using nearest-neighbor assignment to preserve discrete class labels.",
                "   - River proximity rasters are generated by computing exact Euclidean distance transforms from the 1,496 HydroSHEDS river reach vectors to each pixel centroid.",
                "3. Missing Data Sentinel Handling:",
                "   - In strict compliance with scientific standards, missing or invalid spatial data cells are assigned an explicit float32 sentinel value of -9999.0. Imputation or synthetic value generation is prohibited across all hydrological feature extractors."
            ]
        },
        {
            "num": "4.4",
            "title": "Geospatial AI & Uncertainty Calibration Architecture",
            "level": 2,
            "paragraphs": [
                "The intelligence layer operates through a complementary dual-model paradigm consisting of an empirical Multi-Criteria Evaluation (MCE-AHP) pipeline and a supervised Machine Learning (Random Forest) classifier augmented with uncertainty calibration:",
                "1. Multi-Criteria AHP Engine:",
                "   - Constructs a 5x5 pairwise comparison matrix across elevation, slope, river proximity, land cover, and historical hazard.",
                "   - Calculates the principal eigenvalue and normalized eigenvector weights via power iteration. Automatically verifies Saaty's Consistency Ratio (CR = 0.0001 << 0.10) to ensure mathematical stability and transitivity of expert weighting.",
                "2. Supervised Learning & Random Forest Ensemble:",
                "   - Trains a multi-tree ensemble on verified flood presence/absence ground-truth samples derived from historical flood events.",
                "   - Evaluates tree-level prediction variance to quantify epistemic model uncertainty across spatial zones.",
                "3. Probability Calibration Architecture:",
                "   - Raw classification probabilities from decision tree ensembles are notoriously uncalibrated, tending to produce overconfident predictions near 0.0 and 1.0.",
                "   - An empirical calibration post-processor applies Isotonic Regression and Platt Scaling over validation holdout sets, aligning output probabilities with true empirical flood frequencies and reducing the Brier Score."
            ]
        },
        {
            "num": "4.5",
            "title": "Emergency Decision Support & Resource Allocation Architecture",
            "level": 2,
            "paragraphs": [
                "Predictive flood intelligence achieves operational value only when translated into actionable emergency response directives. The decision support architecture integrates three algorithmic subsystems:",
                "1. Composite Spatial Risk Synthesis:",
                "   - Combines hazard susceptibility (FSI), population exposure (WorldPop 2020), and critical infrastructure vulnerability (OpenStreetMap healthcare and school density) into an overarching composite risk metric:",
                "   $$\\text{Risk}_m = \\text{FSI}_m \\times \\left( \\alpha \\cdot \\frac{\\text{Pop}_m}{\\max(\\text{Pop})} + \\beta \\cdot \\frac{\\text{Infra}_m}{\\max(\\text{Infra})} \\right)$$",
                "2. Constrained Resource Allocation Solver:",
                "   - Disaster management authorities operate under severe, unavoidable resource constraints. Given total available quantities of rescue assets (motorized boats $B$, medical trauma kits $M$, food ration packs $R$), the engine formulates a constrained multi-objective allocation problem.",
                "   - Evaluates the Resource Allocation Priority Index (RAPI) for each mandal and assigns integer resource quotas through proportional apportionment weighted by susceptibility tier, ensuring that high-risk riverine and island settlements receive prioritized logistics before stocks deplete.",
                "3. Explainable Risk Driver Generation:",
                "   - To prevent administrative skepticism of automated algorithms, an automated natural-language explanation generator evaluates the constituent feature contributions of each mandal and outputs human-readable risk summaries in English and Telugu."
            ]
        },
        {
            "num": "4.6",
            "title": "Backend Microservice & API Architecture",
            "level": 2,
            "paragraphs": [
                "The backend service layer is implemented in Python using FastAPI, structured into decoupled, modular service classes under `backend/app/`:",
                "1. `GeographicIdentificationService` (`services/geographic_identification_service.py`):",
                "   - Manages territorial GeoJSON boundaries, polygon containment queries, mandal centroid extraction, and coordinate bounding-box evaluations.",
                "2. `FloodRiskService` (`services/flood_risk_service.py`):",
                "   - Executes the AHP multi-criteria scoring algorithm, calculates population and infrastructure exposure statistics, generates explainable risk narratives, and manages model validation metrics.",
                "3. `ResourceAllocationService` (`services/resource_allocation_service.py`):",
                "   - Ingests emergency stock parameters and computes optimal dispatch quotas across mandals using capacity-constrained optimization.",
                "4. RESTful API Endpoints (`api/endpoints.py`):",
                "   - Exposes standardized, versioned endpoints (`/api/v1/...`) supporting both JSON payload exchanges and GeoJSON feature collection streaming. Complete endpoints include `/health`, `/identify/point`, `/mandals`, `/flood-risk/summary`, `/flood-risk/mandals`, `/exposure/summary`, `/allocate-resources`, `/validation/metrics`, `/weather/current`, and `/alerts/active`."
            ]
        },
        {
            "num": "4.7",
            "title": "Frontend Architecture & Interactive GIS Stack",
            "level": 2,
            "paragraphs": [
                "The user interface is constructed as a lightweight, high-performance responsive web application adhering to modern Single Page Application (SPA) principles without heavy external framework bloat:",
                "1. Modular Client Scripting:",
                "   - JavaScript logic is partitioned into dedicated operational modules: `app.js` (application state and navigation routing), `map.js` (Leaflet GIS map controller, choropleth rendering, layer switching), `globe.js` (Three.js WebGL 3D virtual globe with orbital controls), `voice.js` (Web Speech API recognition and Telugu/English speech synthesis), and `notifications.js` (emergency alert drawer management).",
                "2. Dual-Layer Visualization (2D GIS + 3D Globe):",
                "   - The 2D Geospatial Explorer uses Leaflet.js with customized CartoDB Dark Matter tiles, rendering vector mandal boundaries with color-coded risk classifications (Low: Green, Moderate: Amber, High: Orange, Very High: Crimson).",
                "   - The 3D WebGL Globe presents a dynamic planetary sphere mapped with NASA Blue Marble textures, animated night-time illumination, and East Coast cyclonic track trajectories.",
                "3. Regional Language Engine:",
                "   - Supports instant bi-directional language toggling between English and Telugu (`te-IN`). All interface labels, alert notifications, and voice interactions switch synchronously without page reloads."
            ]
        },
        {
            "num": "4.8",
            "title": "Data Flow Diagrams (DFD Level 0, Level 1, Level 2)",
            "level": 2,
            "paragraphs": [
                "System data movements are formalized across three hierarchical Data Flow Diagram levels:",
                "1. DFD Level 0 (Context Diagram):",
                "   - External Entities: Citizens/Residents, Mandal/District Emergency Administrators, Earth Observation Satellites (Copernicus/Sentinel), Meteorological Agencies (IMD/CWC).",
                "   - Core System: PRAVAH 360 Geospatial AI Platform.",
                "   - Data Flows: Ingests raw satellite rasters, hydrographic vectors, and weather feeds; outputs interactive maps, prioritized resource allocations, alert feeds, and regional voice advisories.",
                "2. DFD Level 1 (Macro-Processes):",
                "   - Process 1.0 (Data Ingestion & Preprocessing): Transforms raw rasters and GeoJSON vectors into synchronized spatial arrays.",
                "   - Process 2.0 (Spatial Intelligence & Susceptibility Modeling): Computes AHP weights, Random Forest predictions, and calibrated uncertainty scores.",
                "   - Process 3.0 (Exposure & Impact Assessment): Overlays susceptibility rasters with WorldPop and OSM infrastructure grids.",
                "   - Process 4.0 (Resource Optimization): Solves constrained multi-objective resource dispatch problems.",
                "   - Process 5.0 (Visualization & Multilingual Delivery): Renders 2D/3D maps, manages notification drawers, and synthesizes Telugu voice responses.",
                "3. DFD Level 2 (Decomposition of Process 2.0 - Susceptibility Modeling):",
                "   - Sub-process 2.1: Extract normalized criteria values (elevation, slope, river proximity, land cover, hazard index) for each pixel/mandal.",
                "   - Sub-process 2.2: Compute pairwise comparison matrix and verify Consistency Ratio (CR < 0.10).",
                "   - Sub-process 2.3: Generate continuous Flood Susceptibility Index (FSI).",
                "   - Sub-process 2.4: Execute Isotonic Regression calibration to produce calibrated uncertainty bounds."
            ]
        },
        {
            "num": "4.9",
            "title": "Sequence Diagrams",
            "level": 2,
            "paragraphs": [
                "Interaction sequences model the chronological message flow between actors and system objects:",
                "1. Sequence 1: Citizen Hazard Query & Telugu Voice Guidance:",
                "   - Step 1: Citizen clicks the voice interface button and speaks a query in Telugu ('ఈరోజు వరద హెచ్చరికలు ఏమిటి?').",
                "   - Step 2: Browser Web Speech API captures speech and dispatches phonetic transcript to `voice.js`.",
                "   - Step 3: `voice.js` matches intent and calls `/api/v1/weather/current` and `/api/v1/alerts/active`.",
                "   - Step 4: FastAPI backend queries live meteorological cache and river gauge stage at Dowleswaram Barrage.",
                "   - Step 5: Backend returns structured JSON containing active alert levels, rainfall, and nearest shelter coordinates.",
                "   - Step 6: Frontend maps response into formatted Telugu text and invokes `window.speechSynthesis` with locale `te-IN`.",
                "   - Step 7: System audibly plays spoken Telugu guidance to the resident while updating the map view to display shelter locations.",
                "2. Sequence 2: Administrator Constrained Resource Dispatch:",
                "   - Step 1: District Collector opens Emergency Operations module and specifies total available motorboats (50), medical kits (100), and food supplies (200,000).",
                "   - Step 2: Frontend dispatches HTTP POST request to `/api/v1/allocate-resources` with asset quantities.",
                "   - Step 3: FastAPI endpoint delegates payload to `ResourceAllocationService`.",
                "   - Step 4: Service retrieves mandal susceptibility ratings, population exposure, and critical facility counts.",
                "   - Step 5: Optimization algorithm executes capacity-constrained apportionment and computes the Resource Allocation Priority Index (RAPI) for each of the 21 mandals.",
                "   - Step 6: Endpoint responds with complete allocation matrix, priority ranks, and dispatch quotas.",
                "   - Step 7: Frontend renders interactive data table and choropleth overlay highlighting prioritized logistics routes."
            ]
        },
        {
            "num": "4.10",
            "title": "Security, Authentication & Role-Based Access Control",
            "level": 2,
            "paragraphs": [
                "Emergency disaster intelligence systems handle sensitive public safety data and require robust protection against unauthorized tampering or spoofed alert broadcasts:",
                "1. Role-Based Access Control (RBAC):",
                "   - Public Resident: Unrestricted access to public situation overviews, regional hazard maps, live alert tickers, emergency shelter locators, and Telugu voice queries. Administrative functions are hidden.",
                "   - Mandal Revenue Officer (MRO): Authenticated access via secure credentials to input field observation reports, submit local shelter status updates, and request resource quotas.",
                "   - District Collector / SDMA Officer: Elevated authorization allowing basin-wide resource allocation solving, alert threshold modification, and historical replay inspection.",
                "   - System Administrator: Full administrative access for API key management, service health monitoring, and data catalogue updates.",
                "2. Token-Based Authentication & Transport Security:",
                "   - Authentication is governed by industry-standard JSON Web Tokens (JWT) implementing HMAC-SHA256 signatures and automated expiration.",
                "   - All client-server communications are enforced over Transport Layer Security (TLS 1.3 / HTTPS), preventing man-in-the-middle packet inspection.",
                "   - Backend input validation leverages Pydantic strict schemas to neutralize injection attacks, buffer overruns, and malformed spatial payloads."
            ]
        },
        {
            "num": "4.11",
            "title": "System Operational Workflow",
            "level": 2,
            "paragraphs": [
                "The end-to-end operational workflow of PRAVAH 360 operates in four continuous stages:",
                "1. Stage 1 - Ingestion & Spatial Monitoring: Continuous background monitoring of CWC Dowleswaram Barrage gauge readings, IMD cyclonic storm advisories, and satellite data feeds.",
                "2. Stage 2 - AI Susceptibility & Uncertainty Quantification: Automated re-evaluation of susceptibility surfaces whenever updated hydrological parameters or seasonal boundary conditions are ingested.",
                "3. Stage 3 - Decision Optimization: Instant calculation of emergency resource quotas and explainable risk narratives upon administrative command.",
                "4. Stage 4 - Multi-Channel Dissemination: Immediate, synchronized broadcasting of visual choropleths, tabular dispatches, notification drawer badges, and spoken audio advisories across all connected web clients."
            ]
        }
    ]
}
