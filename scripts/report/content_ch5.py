# Chapter 5: Dataset and Data Processing

CH5_CONTENT = {
    "num": "5",
    "title": "DATASET AND DATA PROCESSING",
    "sections": [
        {
            "num": "5.1",
            "title": "Case Study Area Characterization: Lower Godavari Basin",
            "level": 2,
            "paragraphs": [
                "The Lower Godavari Basin, situated in the coastal state of Andhra Pradesh, India, constitutes one of the most hydrologically vital and disaster-vulnerable deltaic regions in South Asia. Originating at Brahmagiri in Maharashtra and draining a vast catchment of over 312,812 square kilometers across central India, the Godavari River transits the Eastern Ghats gorge before bifurcating into two primary distributaries at Sir Arthur Cotton Barrage (Dowleswaram Barrage) near Rajahmundry: the eastern Gautami Godavari and the western Vasishta Godavari.",
                "1. Administrative Scope and Territorial Coverage:",
                "   - The primary case study covers 21 administrative mandals spanning an authoritative physical area of 18,498.23 square kilometers in Universal Transverse Mercator (UTM Zone 44N) projection (18,571.12 square kilometers geodesic WGS84 area).",
                "   - These 21 mandals encompass the six reorganized districts of Andhra Pradesh: East Godavari, West Godavari, Dr. B.R. Ambedkar Konaseema, Kakinada, Eluru, and Alluri Sitharama Raju.",
                "   - Note on Administrative Boundaries: An earlier preliminary draft transcribed an erroneous figure of 9,008.8 square kilometers from census revenue sub-divisions; the authoritative physical GADM polygon geometries have always covered 18,498.23 square kilometers.",
                "2. Topographic & Geomorphological Profile:",
                "   - The region exhibits extreme topographic contrast, transitioning rapidly from rugged upland hills in Polavaram and Rampachodavaram (elevations exceeding 1,200 meters above mean sea level) to the hyper-flat alluvial delta and coastal marshlands of Konaseema and West Godavari (elevations between 0.5 and 5.0 meters).",
                "   - Central Delta Lanka Islands: A distinctive physiographic feature is the presence of numerous inhabited riverine silt islands ('Lankas') within the bifurcated channels. During severe flood discharges exceeding 2.0 to 2.5 million cubic feet per second (cusecs) at Dowleswaram, these Lanka habitations become entirely marooned, with land transport completely severed.",
                "3. Historical Flood Vulnerability:",
                "   - The basin experiences severe recurrent flooding driven by the combined effects of intense Southwest Monsoon catchment rainfall, Bay of Bengal cyclonic storm surges, and downstream tidal backwater choking.",
                "   - In July 2022, an unprecedented flood wave transited the basin, peaking at a discharge of over 2.58 million cusecs at Dowleswaram Barrage, inundating over 628 delta villages and displacing hundreds of thousands of residents. This catastrophic event serves as our primary historical benchmark."
            ]
        },
        {
            "num": "5.2",
            "title": "Copernicus GLO-30 Digital Elevation Model (DSM)",
            "level": 2,
            "paragraphs": [
                "Topographic relief is the single most decisive physical determinant governing gravity-driven flood accumulation and inundation depth.",
                "1. Technical Specifications:",
                "   - Source: European Space Agency (ESA) Copernicus WorldDEM programme.",
                "   - Product: GLO-30 Cloud-Optimized GeoTIFF (COG), 1.0 arc-second (~30-meter ground pixel resolution).",
                "   - Coverage: Four raw tiles (N16E081, N16E082, N17E081, N17E082) covering Lat 16.0-18.0 N, Lon 81.0-83.0 E, seamlessly mosaicked into a 7200 x 7200 pixel continuous raster.",
                "   - Coordinate System: WGS84 Geographic (EPSG:4326), vertical datum EGM2008 geoid.",
                "2. Scientific Distinction - DSM vs. DTM:",
                "   - Crucially, the Copernicus GLO-30 product is a Digital Surface Model (DSM) rather than a bare-earth Digital Terrain Model (DTM). It captures the elevations of the uppermost reflective surface, including dense agricultural vegetation canopies (sugarcane, coconut palms, paddy fields) and urban settlement structures.",
                "   - While this can introduce slight elevation over-estimations in dense tree canopies, its high spatial fidelity provides an outstanding representation of flood barriers, embankments, and road bunds.",
                "3. Derived Topographic Metrics:",
                "   - From the continuous elevation raster, the first derivative (topographic slope in degrees) was computed using a 3x3 Sobel kernel with cell spacing dx = dy = 30 meters.",
                "   - Slope values across the delta floor range from 0.0 to 1.5 degrees, indicating extreme susceptibility to prolonged surface water ponding."
            ]
        },
        {
            "num": "5.3",
            "title": "HydroSHEDS HydroRIVERS Reaches and Hydrological Topography",
            "level": 2,
            "paragraphs": [
                "The hydrographic network defines the physical conduits through which floodwaters travel and overflow into adjacent floodplains.",
                "1. Source & Extraction:",
                "   - Ingested from the global HydroSHEDS HydroRIVERS database (developed by the World Wildlife Fund and McGill University).",
                "   - Extracted 1,496 river reaches within the bounding envelope of the Lower Godavari Basin.",
                "2. Hydrological Attributes:",
                "   - Attributes include Strahler stream order (ranging from 1 for headwater rivulets up to 9 for the primary Godavari stem), upstream catchment area (sq km), and long-term naturalized discharge estimates.",
                "3. Distance Transform & Proximity Buffering:",
                "   - All 1,496 reaches were converted into multi-segment LineStrings and indexed in memory using Shapely's STRtree.",
                "   - A continuous Euclidean distance raster was derived, quantifying the metric proximity of every terrestrial point to the nearest active river channel, with distance tiers defined at <= 500m, 500m-2km, 2km-5km, 5km-10km, and >10km."
            ]
        },
        {
            "num": "5.4",
            "title": "ESA WorldCover 2021 v200 Land Cover Classification",
            "level": 2,
            "paragraphs": [
                "Surface land cover governs infiltration capacity, surface runoff generation, and hydraulic flow resistance (Manning's roughness coefficient n).",
                "1. Product Details:",
                "   - Ingested from the European Space Agency (ESA) WorldCover 2021 v200 global land cover map, generated from Sentinel-1 and Sentinel-2 multi-spectral observations at 10-meter resolution, downsampled to a 50-meter grid (3840 x 4320 pixels) for regional analysis.",
                "2. Land Cover Distribution in the Lower Godavari:",
                "   - Class 10 (Tree Cover / Forests): Predominates in northern upland mandals (Polavaram, Rampachodavaram); high infiltration, low runoff generation.",
                "   - Class 40 (Cropland / Irrigated Paddy): Dominates >65% of the central delta floor (Amalapuram, Mummidivaram, Kothapeta); clay-rich alluvial soils with saturated standing water, highly vulnerable to prolonged ponding.",
                "   - Class 50 (Built-Up / Urban Settlements): Rajahmundry, Kakinada, Bhimavaram; impermeable concrete surfaces with high runoff coefficients and dense human exposure.",
                "   - Classes 80, 90, 95 (Permanent Water, Herbaceous Wetland, Mangroves): Coastal estuaries and river reaches; intrinsic high water presence."
            ]
        },
        {
            "num": "5.5",
            "title": "WorldPop India 2020 High-Resolution Population Density",
            "level": 2,
            "paragraphs": [
                "To evaluate human exposure, fine-scale demographic distribution data is essential.",
                "1. Source & Processing:",
                "   - Ingested from WorldPop India 2020 UN-adjusted population count raster at 30 arc-second (~1 km) resolution.",
                "   - Clipped and projected to the Lower Godavari administrative boundaries without synthetic extrapolation.",
                "2. Authoritative Population Baseline:",
                "   - The cell-by-cell zonal sum yields a verified baseline population of 9,126,353 residents across the 21 mandals.",
                "   - Highly populated urban and peri-urban centers include Rajahmundry Urban (over 450,000 residents) and Kakinada, while delta agricultural mandals maintain dense rural densities ranging from 600 to 1,200 persons per square kilometer."
            ]
        },
        {
            "num": "5.6",
            "title": "OpenStreetMap Mapped Critical Infrastructure",
            "level": 2,
            "paragraphs": [
                "Critical infrastructure assets represent essential lifelines during disaster response operations.",
                "1. Asset Ingestion:",
                "   - Queried via the Overpass API from OpenStreetMap (OSM) and validated through topological point containment within the 21 mandal boundary polygons.",
                "2. Authoritative Facility Counts:",
                "   - Exactly 1,542 critical facilities fall strictly within the 21 study mandals:",
                "     * Healthcare Infrastructure: 1,146 verified facilities (including government general hospitals, community health centers, primary health clinics, and emergency dispensaries).",
                "     * Educational Infrastructure: 333 facilities (schools, junior colleges, and university campuses capable of serving as emergency relief camps).",
                "     * Emergency Shelters: 63 designated cyclone and flood shelters constructed under the National Cyclone Risk Mitigation Project (NCRMP).",
                "3. Data Availability Caveat:",
                "   - Mapped road and bridge vector geometries were found incomplete in rural open datasets; in strict compliance with research integrity standards, road network vulnerability was omitted rather than synthetically fabricated."
            ]
        },
        {
            "num": "5.7",
            "title": "Multi-Source Precipitation Datasets (GPM IMERG, CHIRPS, ERA5)",
            "level": 2,
            "paragraphs": [
                "To investigate meteorological drivers during the July 2022 catastrophic flood, three independent precipitation products were ingested and harmonized across an 11-day observation window (July 10-20, 2022):",
                "1. NASA GPM IMERG Daily (3B-DAY-V07B): High-resolution multi-satellite precipitation estimates on a 0.1-degree grid. On July 15, 2022 (peak flood crest), GPM recorded a basin-mean daily rainfall of 3.47 mm/day (maximum 27.54 mm/day).",
                "2. CHIRPS 2.0 (Climate Hazards Group InfraRed Precipitation with Station Data): 0.05-degree quasi-global daily rainfall. On July 15, CHIRPS recorded a basin-mean daily rainfall of 4.59 mm/day (maximum 29.89 mm/day).",
                "3. ECMWF ERA5 Reanalysis: Daily surface precipitation series at 16.97 N, 81.80 E, recording 0.0 mm directly over the delta on July 15.",
                "4. Critical Meteorological Finding:",
                "   - Cross-product comparison reveals strong scientific agreement across GPM, CHIRPS, and ERA5: localized rainfall over the delta on July 15 was low to moderate (3-5 mm/day).",
                "   - However, the multi-day antecedent time series reveals extreme catchment-wide storm rainfall between July 11 and July 13 (over 100.5 mm in 72 hours across the upper and middle Godavari catchments in Maharashtra, Telangana, and Chhattisgarh).",
                "   - This conclusively demonstrates that catastrophic Lower Godavari floods are driven by upstream transiting flood waves converging at Dowleswaram Barrage rather than localized delta cloudbursts."
            ]
        },
        {
            "num": "5.8",
            "title": "Sentinel-1 C-Band Synthetic Aperture Radar (SAR)",
            "level": 2,
            "paragraphs": [
                "Synthetic Aperture Radar (SAR) provides cloud-penetrating day-and-night active microwave imaging, making it the premier satellite instrument for surface water detection during monsoonal storm events.",
                "1. Orbit & Scene Catalogue:",
                "   - A comprehensive catalogue of 8 peak-flood scenes (July 14 and 16, 2022) and 12 pre-flood baseline scenes (June 2022) was compiled.",
                "   - Relative Orbit Compatibility: Identical track geometry is mandatory to eliminate terrain-induced backscatter variance. The July 14, 2022 descending pass (Track 129, 00:30 UTC) pairs identically with the June 8, 2022 descending baseline scene (an exact 36-day 3-cycle repeat).",
                "2. Processing Status and Integrity Rule:",
                "   - Local processing of Track 129 generated exploratory water candidate masks (reflecting low backscatter coefficient sigma-nought < -16 dB in VV polarization).",
                "   - Scientific Policy: Because field ground-truth depth gauges and coincident high-resolution aerial optical surveys were unavailable during the July 16 peak pass, these SAR layers are designated as exploratory surface water candidates rather than verified inundation depths."
            ]
        },
        {
            "num": "5.9",
            "title": "Spatial Alignment, Resampling, and CRS Unification",
            "level": 2,
            "paragraphs": [
                "All vector and raster layers were unified under a standardized geospatial pipeline:",
                "1. Coordinate Reference Systems:",
                "   - Presentation & Storage: World Geodetic System 1984 (WGS84, EPSG:4326).",
                "   - Analytical & Distance Computations: Universal Transverse Mercator Zone 44 North (UTM Zone 44N, EPSG:32644), which minimizes planar projection distortion across the 81-83 E meridian.",
                "2. Boundary Topological Buffering:",
                "   - Administrative polygon boundaries often suffer from minor slivers and edge discrepancies against coastal shorelines. An 80-meter outward buffer was applied during raster zonal extraction to guarantee full coverage of coastal settlements without introducing artificial data truncation."
            ]
        },
        {
            "num": "5.10",
            "title": "Spatial Data Validation, Quality Checks, and Sentinel Values",
            "level": 2,
            "paragraphs": [
                "Rigorous automated data validation scripts were executed across all ingested layers:",
                "1. Completeness & Integrity Checks: All 21 mandal polygons verified as topologically valid MultiPolygons without self-intersections or unclosed rings.",
                "2. Coordinate Bounds Enforcement: Geometries strictly bounded within Lat [16.20, 17.80] and Lon [81.30, 82.50].",
                "3. Missing Data Sentinel Handling: Explicit sentinel values of -9999.0 enforced across all raster readers; any zero or uninitialized values were caught and rejected prior to model ingestion."
            ]
        }
    ]
}
