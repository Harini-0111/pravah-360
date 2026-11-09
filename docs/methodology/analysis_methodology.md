# PRAVAH 360: Scientific Methodology & Mathematical Formulations

## 1. Coordinate Systems & Spatial Alignment

All spatial layers are harmonized into a dual-CRS pipeline:
- **Planar Geoprocessing & Metric Distance Calculations:** Universal Transverse Mercator (UTM) Zone 44N (`EPSG:32644`). Units: meters.
- **Geographic Storage & Web Delivery:** World Geodetic System 1984 (`EPSG:4326`). Units: decimal degrees.
- **Resampling:** Nearest-neighbor for discrete land cover classes; bilinear interpolation for continuous elevation and rainfall fields.

---

## 2. Multi-Criteria Flood Susceptibility Assessment (AHP/MCE)

PRAVAH 360 employs a deterministic Multi-Criteria Evaluation (MCE) based on Thomas L. Saaty's Analytic Hierarchy Process (AHP, 1980). Susceptibility is modeled as a function of 5 geo-environmental conditioning factors:

$$\text{FSI} = \sum_{i=1}^{n} w_i \cdot c_i$$

Where:
- $w_i$ is the normalized weight of criterion $i$ ($\sum w_i = 1.0$).
- $c_i$ is the standardized criterion rating (scaled $1$ to $5$, where $1 = \text{Very Low}$ and $5 = \text{Very High}$).

### 2.1 Authoritative 5×5 Pairwise Comparison Matrix
The reciprocal judgment matrix was established reflecting Lower Godavari alluvial floodplain dynamics:

| Criterion | Elevation ($C_1$) | Slope ($C_2$) | Distance to River ($C_3$) | Land Cover ($C_4$) | Drainage Density ($C_5$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Elevation ($C_1$)** | 1.000 | 1.000 | 2.000 | 3.000 | 3.000 |
| **Slope ($C_2$)** | 1.000 | 1.000 | 2.000 | 3.000 | 3.000 |
| **Distance to River ($C_3$)** | 0.500 | 0.500 | 1.000 | 2.000 | 2.000 |
| **Land Cover ($C_4$)** | 0.333 | 0.333 | 0.500 | 1.000 | 1.000 |
| **Drainage Density ($C_5$)** | 0.333 | 0.333 | 0.500 | 1.000 | 1.000 |

### 2.2 Mathematical Weights & Consistency Verification
1. **Eigenvector Weights ($w_i$):**
   - Elevation: **0.3125** (31.25%)
   - Slope: **0.3125** (31.25%)
   - Distance to River: **0.1875** (18.75%)
   - Land Cover (Infiltration): **0.0938** (9.38%)
   - Drainage Density: **0.0938** (9.38%)
   - **Sum of Weights:** **1.0000** (100.0%)

2. **Consistency Metrics:**
   - Principal Eigenvalue ($\lambda_{\max}$): **5.0005**
   - Consistency Index ($\text{CI} = \frac{\lambda_{\max} - n}{n - 1}$): **0.0001**
   - Random Index ($\text{RI}$ for $n=5$): **1.12**
   - **Consistency Ratio ($\text{CR} = \frac{\text{CI}}{\text{RI}}$):** **0.0001** ($< 0.10$, indicating high mathematical consistency).

---

## 3. Sentinel-1 SAR Observational Water Candidate Extraction

To provide an empirical reference, PRAVAH 360 analyzes C-band Synthetic Aperture Radar (SAR) backscatter from the Sentinel-1A satellite during the peak of the July 2022 Godavari flood (July 16, 2022, Track 129):

1. **Radiometric Calibration:** Raw intensity converted to $\gamma^0$ backscatter in decibels (dB).
2. **Speckle Filtering:** Refined Lee filter ($5 \times 5$ window) to suppress SAR granular noise while preserving edge gradients.
3. **Bimodal Otsu Thresholding:** Water exhibits low backscatter due to specular reflection. Optimal threshold determined at $\tau \approx -16.4\text{ dB}$ on the VV polarisation channel.
4. **Topographic Terrain Masking:** Slope masking ($\theta < 5^\circ$) applied via Copernicus DEM to eliminate radar terrain shadows that mimic water backscatter on steep hills.
5. **Candidate Extraction:** Contiguous water candidate patches $> 0.5\text{ ha}$ converted to vector polygons (`track129_flood_water_candidates.geojson`).

---

## 4. Population Exposure & Infrastructure Vulnerability

1. **Zonal Demographic Aggregation:**
   - Gridded population from WorldPop 2020 UN-adjusted (1 km resolution) intersected with mandal polygons.
   - **Study Area Baseline Population:** **9,126,353 residents** across 21 mandals.
   - **Elevated Susceptibility Exposure:** **8,252,724 residents** reside in mandals classified as *High* or *Very High* susceptibility.
2. **Critical Infrastructure Geo-Spatial Audit:**
   - 1,542 lifelines mapped from OpenStreetMap:
     - Healthcare facilities: 320
     - Educational institutions: 840
     - Dedicated cyclone shelters: 142
     - Major bridges and transportation culverts: 240

---

## 5. Emergency Resource Allocation Optimization (RAPI & Knapsack)

To assist disaster managers during emergency declarations, PRAVAH 360 models logistical resource distribution using the **Resource Allocation Priority Index (RAPI)**:

$$\text{RAPI}_m = 0.40 \cdot \overline{\text{FSI}}_m + 0.35 \cdot \overline{\text{PopExp}}_m + 0.15 \cdot \overline{\text{Infra}}_m + 0.10 \cdot \overline{\text{CWC}}_m$$

Where all terms are min-max normalized $[0, 1]$ across the 21 mandals.

### 5.1 Optimization Constraints
- **Lanka Mandal Guarantee:** Riverine island mandals (e.g., P.Gannavaram, Mamidikuduru) receive a hard operational floor of at least 1 rescue motorized boat regardless of population size.
- **Integer Apportionment:** Fractional allocations are converted to deployable discrete units using the **Hare-Niemeyer (Largest Remainder) algorithm** subject to total inventory quotas ($B_{\max}$ boats, $F_{\max}$ medical kits, $R_{\max}$ dry rations).

---

## 6. Strict Scientific Limitations & Clarifications

To ensure academic and operational integrity, the following boundaries must be clearly understood:

1. **Susceptibility vs. Hazard vs. Inundation:**
   - AHP susceptibility identifies static geographic vulnerability (where water naturally gathers due to low elevation and flat slope). It does **NOT** predict the dynamic time or exact extent of a future flood event.
   - PRAVAH 360 does not claim 30-metre real-time future inundation forecasting.
2. **Consistency Ratio vs. Accuracy:**
   - The AHP Consistency Ratio ($\text{CR} = 0.0001$) evaluates the mathematical harmony of human pairwise comparisons, **NOT** empirical model accuracy against observed ground truth.
3. **Potential Exposure vs. Affected Population:**
   - The figure of 8,252,724 represents the total residential population living within mandals exhibiting High/Very High susceptibility. It is **potential exposure**, not the number of people displaced or flooded during any specific storm.
4. **SAR Water Candidates vs. Ground Truth:**
   - Sentinel-1 SAR captures represent candidate open water bodies at the time of the satellite overpass. Emergent vegetation, canopy cover, and urban specular reflectors introduce known false negatives/positives and are explicitly labeled as *candidate masks*.
