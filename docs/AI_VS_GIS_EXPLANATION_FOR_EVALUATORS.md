# PRAVAH 360 · Evaluator Guide: Distinguishing AI, GIS & Conventional Logic
## Prepared for Professors, Viva Voce Evaluators, and Technical Reviewers

---

### 1. The Core Scientific Distinction

When presenting PRAVAH 360, evaluators often ask:
> *"Is this really Artificial Intelligence, or is it an advanced Geographic Information System (GIS)?"*

**The Defensible Academic Answer:**
> "PRAVAH 360 is an **AI-Enabled Environmental Decision Support System (EDSS)**. In modern computer science and environmental engineering, AI encompasses both **Knowledge-Based / Expert Systems (Symbolic AI)** and **Data-Driven Machine Learning (Subsymbolic AI)**. PRAVAH 360 integrates remote sensing image processing, multi-criteria spatial reasoning, deterministic rule engines, and natural language voice parsing to transform raw geospatial data into actionable civil defense decisions."

---

### 2. Detailed Technical Comparison Table

| Feature in PRAVAH 360 | Claimed Paradigm | What the Code Actually Executes | Academic Classification | Why It Is NOT Just a "Simple Dashboard" |
|---|---|---|---|---|
| **Sentinel-1 Flood Water Detection** | Remote Sensing / Vision | `extract_sentinel1_water.py`: Multi-polarization (VH/VV) decibel conversion, adaptive Otsu bimodal histogram thresholding, speckle filter, WorldCover masking. | **Computer Vision & Statistical Remote Sensing** | Evaluates radar backscatter physics in all-weather clouds to isolate smooth water surfaces from rough terrain. |
| **Flood Susceptibility Index (FSI)** | Multi-Criteria Evaluation | `flood_risk_service.py`: 5 physical environmental criteria weighted using Saaty's Analytic Hierarchy Process. Calculated $\lambda_{\max}=5.0006, CR=0.0001$. | **Knowledge-Based Expert System (MCE/AHP)** | Enforces mathematical transitivity and consistency checks across conflicting criteria (elevation, slope, stream distance, LULC, rainfall). |
| **WorldPop Demographic Overlay** | Spatial Demography | Cell-by-cell raster intersection of $100\text{ m}$ constrained WorldPop 2020 grids with FSI polygon contours using `STRtree` spatial indexing. | **Spatial Data Science / Disaggregation** | Avoids coarse census area averaging by calculating true physical population distribution within elevated risk polygons ($8,252,724$). |
| **Hydrological Thresholds** | Operational Rule Engine | Compares CWC river gauge meters against 3-stage warning/danger datums and slope trends (`RISING`, `FALLING`, `STEADY`). | **Deterministic Expert System Rule Engine** | Translates raw water levels into legally recognized emergency operational states. |
| **Emergency Triage & Nearest Facility** | Operations Research | Haversine metric matrix computation finding the top-$k$ nearest shelters/hospitals outside the inundation perimeter. | **Algorithmic Spatial Heuristic (k-NN)** | Ensures displaced citizens are not directed towards shelters located inside the flood zone. |
| **Telugu Voice Assistant** | Natural Language Interface | Web Speech API speech-to-text + semantic intent classification mapping Telugu queries to real-time API states + Text-to-Speech synthesis. | **Applied NLP & Speech Recognition** | Democratizes disaster access for rural residents with limited digital literacy. |
| **Citizen Ground Hazard Reporting** | Crowdsourced Ground Truth | Citizen image upload, Base64 handling, location extraction, and 4-tier admin review state machine (`SUBMITTED` $\to$ `RESOLVED`). | **Participatory GIS & Triage Workflow** | Bridges orbital sensor latency with real-time ground truth observations. |

---

### 3. Evaluation Defense Points: Answering Common Evaluator Questions

#### Q1: "Why didn't you train a Deep Neural Network (e.g. CNN / ResNet) on flood images?"
> **Answer:** "In an emergency decision support system for the Lower Godavari delta, **explainability and auditability are critical**. While black-box deep learning models can suffer from spatial overfitting or hallucination when generalizing across deltaic agricultural backwaters, our Sentinel-1 adaptive thresholding and AHP MCE framework are fully transparent, mathematically verifiable ($CR < 0.10$), and aligned with National Disaster Management Authority (NDMA) guidelines. Furthermore, deep learning SAR models require large ground-truth training datasets (like Sen1Floods11), which we have identified as a natural follow-up research milestone."

#### Q2: "Can you change the criteria weights in real-time?"
> **Answer:** "Yes. The backend API `/api/v1/flood-risk/basin-assessment` accepts custom weight vectors and immediately recalculates the basin risk profile and sensitivity scenarios. This enables disaster managers to simulate extreme climate scenarios (e.g., doubling the rainfall weight during an atmospheric depression)."

#### Q3: "How is population exposure calculated?"
> **Answer:** "We do not use uniform census distribution. We execute cell-by-cell intersection of the WorldPop 2020 high-resolution constrained building-footprint raster with our FSI high-susceptibility polygon boundary, proving that 8,252,724 individuals reside within terrain susceptible to seasonal monsoon inundation."
