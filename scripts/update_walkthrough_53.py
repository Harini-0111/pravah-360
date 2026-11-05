with open(r'C:\Users\harini\.gemini\antigravity\brain\c788c5c0-c2d6-4368-89fb-fb5804766273\walkthrough.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Update header statuses
header_old = "**Phase 5.2.1 Status**: **COMPLETE** (Scientific Reconciliation & Live GIS Verification)"
header_new = """**Phase 5.2.1 Status**: **COMPLETE** (Scientific Reconciliation & Live GIS Verification)  
**Phase 5.3 Status**: **COMPLETE** (Visual Transformation, Immersive Web GIS & Global 3D Globe)"""
text = text.replace(header_old, header_new)

# Add Phase 5.3 Summary before Documentation & Reports
summary_old = "## 25. Documentation & Reports"
summary_new = """## 25. Phase 5.3 Summary: Visual Transformation, Immersive Web GIS & Global 3D Globe
- **Geographic Intelligence Hero:** Replaced text-heavy overview layout with an interactive 480px Lower Godavari Basin hero map featuring live hover HUD, thematic layer chips (Overlays, SAR Floodwater, Susceptibility, River Reaches), and glowing analytical metric cards (15/21 mandals, 8.25M exposed, 1,467 facilities, 1,087.5 km² candidate inundation).
- **High-Contrast Web GIS:** Resolved the unlabelled "grey map" defect by pairing `Esri World Dark Gray Base` with `Esri World Dark Gray Reference` (zIndex 420), restoring crisp coastlines and settlement labels (Rajahmundry, Kakinada, Bhimavaram, Eluru, Tanuku). Added `Esri Topographic` basemap, floating toolbars (🎯 Fit Basin), and vibrant symbology legend.
- **Zero-CDN Offline Architecture:** Cached all Leaflet CSS, JS, and marker images locally in `frontend/leaflet/` alongside `frontend/globe.gl.min.js`, ensuring 100% offline resilience and zero CDN latency or blockage.
- **Structural DOM Integrity:** Repaired premature `</div>` closure at line 547 of `index.html`, restoring all 7 workspaces as direct children of `.workspaces-container` and enabling seamless tab transitions across all 7 views.
- **Immersive Global 3D Planetarium:** Deployed local high-resolution Earth textures (`earth-blue-marble.jpg`, `earth-night.jpg`, `earth-topology.png`, `night-sky.png`) with dynamic cyan atmosphere, 3D pulse ring marker for the Lower Godavari delta prototype, Day/Night texture toggle, and verified 79.4–88.4 measured FPS auto-rotation.
- **Authoritative Metrics Strictly Preserved:** Total baseline population ($9,126,355$), elevated exposure ($8,252,724$, $90.43\%$), AHP exploratory susceptibility weights ($25\\%$, $25\\%$, $20\\%$, $15\\%$, $15\\%$), and $1,467$ facilities in elevated zones.
- **Automated Verification:** 70/70 passing tests (64 backend unit tests + 6 workspace acceptance tests) and 11 high-resolution screenshots in `docs/screenshots/`.
- Documented in [PHASE_5_3_VISUAL_TRANSFORMATION_REPORT.md](file:///c:/major%20project/PHASE_5_3_VISUAL_TRANSFORMATION_REPORT.md).

---

## 26. Documentation & Reports"""
text = text.replace(summary_old, summary_new)

# Add report link to Documentation & Reports
doc_entry = "- [PHASE_5_3_VISUAL_TRANSFORMATION_REPORT.md](file:///c:/major%20project/PHASE_5_3_VISUAL_TRANSFORMATION_REPORT.md): Phase 5.3 visual transformation, immersive Web GIS, and global 3D Earth report.\n"
text = text.replace("- [PHASE_5_2_1_VERIFICATION_REPORT.md](file:///c:/major%20project/PHASE_5_2_1_VERIFICATION_REPORT.md): Phase 5.2.1 scientific reconciliation and live GIS verification report.\n", "- [PHASE_5_2_1_VERIFICATION_REPORT.md](file:///c:/major%20project/PHASE_5_2_1_VERIFICATION_REPORT.md): Phase 5.2.1 scientific reconciliation and live GIS verification report.\n" + doc_entry)

with open(r'C:\Users\harini\.gemini\antigravity\brain\c788c5c0-c2d6-4368-89fb-fb5804766273\walkthrough.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated walkthrough.md successfully.")
