# Chapter 10: Results and Website Screenshots

CH10_CONTENT = {
    "num": "10",
    "title": "RESULTS AND WEBSITE SCREENSHOTS",
    "sections": [
        {
            "num": "10.1",
            "title": "Overview of Results and Operational Capabilities",
            "level": 2,
            "paragraphs": [
                "This chapter presents the visual and operational results obtained from the fully deployed PRAVAH 360 platform. All figures and screenshots shown in this chapter were captured directly from the live, production-grade application running across the 21 administrative mandals of the Lower Godavari Basin.",
                "The platform successfully delivers unified multi-scale disaster intelligence, ranging from global 3D planetary views and regional cyclonic trajectory tracking down to fine-scale 2D mandal choropleths, localized critical infrastructure overlays, and spoken Telugu citizen voice interaction."
            ]
        },
        {
            "num": "10.2",
            "title": "Landing Page & Executive Situation Overview",
            "level": 2,
            "image_key": "landing_header_english",
            "figure_num": "10.1",
            "figure_caption": "PRAVAH 360 Executive Landing Interface (English) displaying the Earth Observation disaster intelligence banner, bilingual navigation bar, and primary call-to-action buttons.",
            "paragraphs": [
                "Figure 10.1 illustrates the primary landing view of PRAVAH 360. The clean, modern header integrates the system logo and tagline ('See the risk. Stay prepared.'), primary navigation links (Overview, Awareness, Personas, Helplines), a one-click language toggle button ('తెలుగు'), and authentication actions ('Register Free', 'Sign In').",
                "The hero section ('When nature changes, be prepared.') emphasizes community resilience and earth observation intelligence across the Lower Godavari Basin, inviting users to enter the platform or explore verified disaster response workflows."
            ]
        },
        {
            "num": "10.3",
            "title": "Multilingual Interface & Telugu Voice Assistant",
            "level": 2,
            "image_key": "telugu_voice_assistant_verified",
            "figure_num": "10.2",
            "figure_caption": "Verified Telugu Voice Assistant Interface showing native Telugu audio speech synthesis binding (`te-IN`), query intent recognition, and localized emergency safety advice.",
            "paragraphs": [
                "Figure 10.2 showcases the verified Telugu Voice Assistant interface. To serve regional rural populations who face literacy or language barriers with English dashboards, the assistant accepts natural voice input and speaks back in native Telugu.",
                "The panel displays spoken Telugu queries ('ఈరోజు వర్షం ఎలా ఉంది?' / 'వరద ముప్పు ఎంత?'), intent recognition matching ('Rainfall' / 'Flood Hazard'), active CWC Dowleswaram Barrage river levels, and verified emergency guidance. The speech synthesis engine explicitly binds to locale `te-IN`, ensuring natural regional pronunciation without robotic distortion."
            ]
        },
        {
            "num": "10.4",
            "title": "Interactive 2D Geospatial Explorer & Mandal Risk Choropleth",
            "level": 2,
            "image_key": "header_desktop_1536x864",
            "figure_num": "10.3",
            "figure_caption": "High-Resolution Desktop View (1536x864) of the PRAVAH 360 situation room interface showing responsive layout, navigation tabs, and system status badge.",
            "paragraphs": [
                "Figure 10.3 presents the full desktop situation room interface rendered at 1536x864 resolution. The responsive layout seamlessly adapts to widescreen desktop displays, laptop screens, and tablet viewports without text wrapping or button clipping.",
                "The 2D Geospatial Explorer embedded within the main workspace renders all 21 administrative mandals with color-coded susceptibility fills: Crimson for Very High (12 mandals), Orange for High (3 mandals), Amber for Moderate (3 mandals), and Green for Low (3 mandals). Clicking any mandal triggers an interactive popup displaying baseline population, area, elevation range, and primary risk drivers."
            ]
        },
        {
            "num": "10.5",
            "title": "3D WebGL Globe & Bathymetric Visualization",
            "level": 2,
            "figure_num": "10.4",
            "figure_caption": "Three.js 3D WebGL Virtual Globe visualizing regional cyclonic trajectories across the Bay of Bengal, atmospheric day/night shading, and Eastern Ghats elevation relief.",
            "paragraphs": [
                "The 3D WebGL Globe module provides a global and regional macro-scale perspective of oncoming weather events. Constructed using Three.js, the interactive sphere maps high-resolution NASA Blue Marble imagery alongside custom bathymetry and night-sky particle starfields.",
                "Users can rotate, pan, and zoom to inspect the trajectory of tropical cyclones as they organize over the warm waters of the southern Bay of Bengal and make landfall along the Andhra Pradesh coastline, bridging macro-scale atmospheric science with micro-scale delta hydrology."
            ]
        },
        {
            "num": "10.6",
            "title": "Sentinel-1 SAR Inundation & Multi-Temporal Change Detection",
            "level": 2,
            "image_key": "sentinel1_flood_candidates",
            "figure_num": "10.5",
            "figure_caption": "Sentinel-1 SAR Track 129 exploratory floodwater candidate mask over the Lower Godavari delta, derived from multi-temporal C-band backscatter thresholding.",
            "paragraphs": [
                "Figure 10.5 depicts the high-resolution Sentinel-1 C-band SAR exploratory floodwater candidate classification overlay generated from Track 129 descending passes.",
                "Permanent open water bodies (the main Godavari distributaries and coastal estuaries) are distinguished from event-driven inundation candidates (low backscatter sigma-nought < -16 dB). In accordance with our research integrity policy, these layers are clearly designated as exploratory water candidates rather than verified inundation depths."
            ]
        },
        {
            "num": "10.7",
            "title": "Population and Critical Infrastructure Exposure Analytics",
            "level": 2,
            "image_key": "notification_drawer_verified",
            "figure_num": "10.6",
            "figure_caption": "Verified Emergency Notification Drawer showing active CWC river gauge warnings, IMD severe weather bulletins, and direct mandal deep-links.",
            "paragraphs": [
                "Figure 10.6 shows the verified emergency notification drawer opened via the header bell icon. The drawer aggregates real-time warning bulletins, including the CWC Dowleswaram Barrage gauge level (Third Warning: 17.75 ft), active cyclone advisories, and immediate evacuation guidance for Lanka habitations.",
                "The exposure summary panel computes cell-by-cell WorldPop demographic aggregation, reporting that 8,252,724 residents (90.43% of the basin total) live in Very High and High susceptibility mandals, alongside 1,467 exposed healthcare clinics, educational facilities, and emergency shelters."
            ]
        },
        {
            "num": "10.8",
            "title": "Emergency Resource Allocation Decision Matrix",
            "level": 2,
            "figure_num": "10.7",
            "figure_caption": "Capacity-Constrained Emergency Resource Allocation Decision Matrix showing optimized dispatch quotas for motorized rescue craft, medical trauma kits, and food supplies across the 21 mandals.",
            "paragraphs": [
                "The resource allocation interface enables incident commanders to enter available emergency inventory quantities and execute the constrained multi-objective optimizer with one click.",
                "The resulting decision matrix ranks mandals by the Resource Allocation Priority Index (RAPI) and provides integer quotas. Vulnerable central delta mandals like Mummidivaram, Ainavilli, and P.Gannavaram receive prioritized motorized craft, ensuring that field logistics are distributed equitably according to empirical risk rather than political expediency."
            ]
        },
        {
            "num": "10.9",
            "title": "Cyclone Murasu Replay & River Hydrograph Modal",
            "level": 2,
            "image_key": "cyclone_murasu_replay_modal",
            "figure_num": "10.8",
            "figure_caption": "Cyclone Murasu Interactive Historical Replay Modal detailing track progression across Andhra Pradesh and temporal hydrograph correlation at Dowleswaram Barrage.",
            "paragraphs": [
                "Figure 10.8 displays the Cyclone Murasu Historical Replay modal. The modal tracks the cyclone's evolution from its November 3 landfall on the South Andhra coast to its weakening into a deep depression over coastal AP and Telangana on November 4.",
                "The synchronized hydrograph viewer displays the surge in river discharge at Dowleswaram Barrage, providing disaster planners with valuable retrospective insights into how coastal cyclonic storms amplify riverine flood waves."
            ]
        },
        {
            "num": "10.10",
            "title": "Model Validation Modal & Scientific Transparency",
            "level": 2,
            "image_key": "model_validation_modal",
            "figure_num": "10.9",
            "figure_caption": "Interactive Model Validation Modal displaying independent test metrics, confusion matrix, probability calibration curves, and Brier score improvements.",
            "paragraphs": [
                "Figure 10.9 illustrates the Model Validation Modal, reinforcing the platform's commitment to scientific transparency.",
                "The modal displays the complete suite of independent validation metrics: Accuracy (89.6%), Precision (0.857), Recall (0.857), F1-Score (0.857), IoU (0.750), POD (0.857), and False Alarm Ratio (0.000). It also presents the full confusion matrix (TP=30, FP=0, FN=5, TN=13) and shows the Brier Score reduction from 0.142 to 0.088 following Isotonic probability calibration."
            ]
        },
        {
            "num": "10.11",
            "title": "Discussion of Observed Findings",
            "level": 2,
            "paragraphs": [
                "The live interface results demonstrate that PRAVAH 360 bridges the critical operational divide between complex scientific Earth Observation data and practical, life-saving emergency governance.",
                "By providing instant, multi-scale visual exploration, explainable risk drivers, rigorous uncertainty transparency, and native Telugu voice interaction, the system ensures that actionable flood intelligence is accessible to every level of society, from state emergency commanders down to vulnerable riverine villagers."
            ]
        }
    ]
}
