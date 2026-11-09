# Geospatial Dataset Sources & Provider Directory

This document details every provider, data access protocol, licensing, and citation for the **AI-Based Flood Risk, Impact Assessment and Emergency Decision Support System** (Lower Godavari Basin, Andhra Pradesh).

## Copernicus DEM GLO-30 (Raw Tiles)
- **Provider**: European Space Agency (ESA) / AWS Open Data
- **Source URL**: [https://copernicus-dem-30m.s3.amazonaws.com/](https://copernicus-dem-30m.s3.amazonaws.com/)
- **Product & Version**: Copernicus Digital Elevation Model (DSM) (GLO-30 (2020 release))
- **Temporal Vintage / Acquisition**: 2011-2015 (TanDEM-X radar)
- **Spatial Resolution**: 30 meters (1 arcsec) | **CRS**: EPSG:4326 (WGS84)
- **License**: Copernicus WorldDEM-30 Open License
- **Attribution**: European Space Agency (ESA), Airbus, DLR
- **Intended Use**: Hydrological terrain modeling, slope, aspect, low-lying coastal flood vulnerability
- **Documented Limitations**: Digital Surface Model (DSM) capturing canopy/buildings rather than bare earth; small vertical bias in dense vegetation

---

## Copernicus DEM Processed Terrain Indicators
- **Provider**: Derived from ESA Copernicus DEM GLO-30
- **Source URL**: [Local calculation via scripts/download_dem.py](Local calculation via scripts/download_dem.py)
- **Product & Version**: Elevation, Slope (degrees), Aspect (degrees) (1.0)
- **Temporal Vintage / Acquisition**: 2011-2015
- **Spatial Resolution**: 30 meters | **CRS**: EPSG:4326 (WGS84)
- **License**: Copernicus WorldDEM-30 Open License
- **Attribution**: ESA / AI Flood Intelligence System
- **Intended Use**: Hydrodynamic routing, gravity drainage impediment analysis, flood retention zone mapping
- **Documented Limitations**: Derived on geographic grid using central differences with latitude-scaled cell metric

---

## WorldPop India Population 2020 (Raw)
- **Provider**: WorldPop / University of Southampton
- **Source URL**: [https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/2020/IND/ind_ppp_2020_1km_Aggregated_UNadj.tif](https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/2020/IND/ind_ppp_2020_1km_Aggregated_UNadj.tif)
- **Product & Version**: WorldPop UN-adjusted Global Population Density (v1.0 (2020))
- **Temporal Vintage / Acquisition**: 2020
- **Spatial Resolution**: 1 kilometer (0.008333 deg) | **CRS**: EPSG:4326 (WGS84)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Attribution**: WorldPop, University of Southampton
- **Intended Use**: Macro-demographic exposure baseline
- **Documented Limitations**: Statistical disaggregation model; not an official census head count

---

## WorldPop Lower Godavari Clipped Population Grid
- **Provider**: WorldPop / Extracted via scripts/download_population.py
- **Source URL**: [https://data.worldpop.org/](https://data.worldpop.org/)
- **Product & Version**: Lower Godavari Population Exposure Baseline (2020 UN-adj)
- **Temporal Vintage / Acquisition**: 2020
- **Spatial Resolution**: ~1 km (192 x 216 pixels) | **CRS**: EPSG:4326 (WGS84)
- **License**: CC BY 4.0
- **Attribution**: WorldPop / System Processed
- **Intended Use**: Exposure and humanitarian impact assessment for flood scenarios
- **Documented Limitations**: Must never be reported as confirmed affected persons; represents residential exposure potential

---

## ESA WorldCover 10m 2021 (Raw)
- **Provider**: European Space Agency (ESA) / AWS Open Data
- **Source URL**: [https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N15E081_Map.tif](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N15E081_Map.tif)
- **Product & Version**: ESA WorldCover 10 m 2021 (v200)
- **Temporal Vintage / Acquisition**: 2021
- **Spatial Resolution**: 10 meters | **CRS**: EPSG:4326 (WGS84)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Attribution**: ESA WorldCover project / VITO Remote Sensing
- **Intended Use**: Distinguishing agricultural cropland, built-up settlements, water bodies, and mangroves
- **Documented Limitations**: Paddy crop cycles can cause seasonal misclassification between shallow water and cropland

---

## ESA WorldCover 50m Lower Godavari Standardized Raster
- **Provider**: ESA / Processed via scripts/download_landcover.py
- **Source URL**: [Local derivation](Local derivation)
- **Product & Version**: Lower Godavari Land Cover Map (v200)
- **Temporal Vintage / Acquisition**: 2021
- **Spatial Resolution**: 50 meters | **CRS**: EPSG:4326 (WGS84)
- **License**: CC BY 4.0
- **Attribution**: ESA / VITO / Project Extract
- **Intended Use**: Vulnerability weighting and sectoral damage modeling
- **Documented Limitations**: Aggregated 5x stride from 10m raw product

---

## HydroRIVERS Asia River Network (Raw)
- **Provider**: World Wildlife Fund (WWF) / HydroSHEDS
- **Source URL**: [https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_as_shp.zip](https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_as_shp.zip)
- **Product & Version**: HydroRIVERS v1.0 (1.0)
- **Temporal Vintage / Acquisition**: Derived from HydroSHEDS DEM
- **Spatial Resolution**: 15 arc-sec flow routing | **CRS**: EPSG:4326 (WGS84)
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Attribution**: Lehner, B., Grill G. (2013) / HydroSHEDS
- **Intended Use**: Topological river network analysis, stream order hierarchy, proximity to river channels
- **Documented Limitations**: Does not represent real-time hydrodynamics or anthropogenic bunds/levees

---

## Lower Godavari Basin River Reaches (Processed)
- **Provider**: HydroSHEDS / Filtered via scripts/filter_rivers.py
- **Source URL**: [Local extraction](Local extraction)
- **Product & Version**: Lower Godavari Reaches (1.0)
- **Temporal Vintage / Acquisition**: Static
- **Spatial Resolution**: Vector LineStrings | **CRS**: EPSG:4326 (WGS84)
- **License**: CC BY 4.0
- **Attribution**: HydroSHEDS / AI Flood Intelligence System
- **Intended Use**: River distance buffers, flood propagation path analysis
- **Documented Limitations**: Represents natural channel vectors, unmapped local irrigation drainage channels omitted

---

## CHIRPS 2.0 Daily Precipitation (July 2022 Flood)
- **Provider**: Climate Hazards Center (CHC), UCSB / IRI Data Library
- **Source URL**: [https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.daily-improved/.global/.0p05/.prcp/](https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.daily-improved/.global/.0p05/.prcp/)
- **Product & Version**: CHIRPS v2.0 Daily Rainfall (2.0)
- **Temporal Vintage / Acquisition**: 2022-07-10 to 2022-07-20
- **Spatial Resolution**: 0.05 degrees (~5.5 km) | **CRS**: EPSG:4326 (WGS84)
- **License**: Public Domain (Open Data)
- **Attribution**: Funk et al. (2015), Scientific Data, UCSB Climate Hazards Center
- **Intended Use**: Catchment precipitation antecedent conditioning and flood event tracking
- **Documented Limitations**: Satellite-gauge blended product; extreme local convective peaks may be smoothed

---

## Administrative Boundaries (AP Districts & Mandals)
- **Provider**: Global Administrative Areas (GADM v4.1)
- **Source URL**: [https://gadm.org/download.html](https://gadm.org/download.html)
- **Product & Version**: GADM India Admin Level 2 (Districts) and Level 3 (Mandals/Taluks) (4.1)
- **Temporal Vintage / Acquisition**: 2022 release
- **Spatial Resolution**: Vector Polygons | **CRS**: EPSG:4326 (WGS84)
- **License**: GADM license (free for academic and non-commercial research)
- **Attribution**: GADM project (University of California, Davis)
- **Intended Use**: Administrative impact aggregation (reporting flooded area per mandal and district)
- **Documented Limitations**: Cadastral village boundaries require Survey of India / APSDMA restricted portal login

---

## OpenStreetMap Emergency Infrastructure (Healthcare, Education, Shelters)
- **Provider**: OpenStreetMap Contributors via Overpass API
- **Source URL**: [https://overpass-api.de/api/interpreter](https://overpass-api.de/api/interpreter)
- **Product & Version**: OSM Healthcare, Education, and Emergency Shelters (Live OSM extract)
- **Temporal Vintage / Acquisition**: 2026 (Historical tags preserved)
- **Spatial Resolution**: Vector Points | **CRS**: EPSG:4326 (WGS84)
- **License**: Open Data Commons Open Database License (ODbL)
- **Attribution**: © OpenStreetMap contributors
- **Intended Use**: Emergency decision support, evacuation routing, critical asset inundation risk
- **Documented Limitations**: Crowdsourced data; coverage in remote rural delta islands may be incomplete

---

## Sentinel-1 SAR Satellite Imagery Catalogue (July 2022 Benchmark Flood)
- **Provider**: European Space Agency (ESA) / Copernicus Data Space Ecosystem (CDSE)
- **Source URL**: [https://catalogue.dataspace.copernicus.eu/odata/v1/Products](https://catalogue.dataspace.copernicus.eu/odata/v1/Products)
- **Product & Version**: Sentinel-1 IW GRDH (VV + VH) (Level-1 GRD)
- **Temporal Vintage / Acquisition**: 2022-07-14 and 2022-07-16 (Peak flood) / 2022-06-01 to 2022-06-15 (Baseline)
- **Spatial Resolution**: 10 meters | **CRS**: EPSG:4326 (WGS84)
- **License**: Copernicus Open Access Policy (Free and open)
- **Attribution**: European Space Agency (ESA) / Copernicus Sentinel-1
- **Intended Use**: SAR backscatter water thresholding and flood inundation extent mapping
- **Documented Limitations**: Wind-induced surface roughness and emergent vegetation in paddy fields can cause SAR backscatter ambiguity

---
