"""
Phase 5.2 Preservation Inventory & Baseline Audit
Records checksums, sizes, and paths of authoritative scientific outputs,
services, and datasets before Phase 5.2 GIS transformation.
"""

import os
import sys
import json
import hashlib
from pathlib import Path

WORKSPACE = Path(r"C:\major project")

def get_file_info(p):
    path = WORKSPACE / p
    if not path.exists():
        return None
    size = path.stat().st_size
    # Compute sha256 for files under 20MB
    sha = "SKIPPED_LARGE_FILE"
    if size < 20 * 1024 * 1024:
        with open(path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
    return {"path": str(p), "size_bytes": size, "sha256": sha}

def main():
    critical_files = [
        # Authoritative Phase 4 reports & datasets
        "data/processed/population/worldpop_lower_godavari_2020.tif",
        "data/processed/dem/copernicus_dem_elevation_N16E081.tif",
        "data/processed/landcover/esa_worldcover_lower_godavari_50m.tif",
        "data/processed/boundaries/lower_godavari_mandals.geojson",
        "data/processed/boundaries/lower_godavari_districts.geojson",
        "data/processed/rivers/lower_godavari_hydrorivers.geojson",
        "data/processed/sentinel1/track129_water_classification.tif",
        "data/processed/sentinel1/track129_flood_water_candidates.geojson",
        "data/metadata/phase3_3_mandal_water_candidates.json",
        "data/metadata/sentinel1_png_overlay_metadata.json",
        "backend/app/services/flood_risk_service.py",
        "backend/app/services/geographic_identification_service.py",
        "backend/app/services/weather_service.py",
        "backend/app/api/endpoints.py",
        "PHASE_4_FINAL_POPULATION_RECONCILIATION.md",
        "PHASE_3_3_AND_WEATHER_INTEGRITY_REVIEW.md",
        "PHASE_5_1_FRONTEND_INTEGRATION_REPORT.md",
        "docs/frontend_contract.md"
    ]

    inventory = {
        "timestamp": "2026-11-02T21:18:00Z",
        "project": "AI-Based Flood Risk, Impact Assessment and Emergency Decision Support System",
        "case_study": "Lower Godavari Basin, Andhra Pradesh (21 Mandals)",
        "phase": "Phase 5.2 - GIS-First Web App Transformation + Global 3D Earth",
        "authoritative_reconciled_population": {
            "raw_baseline": 9126354.9793,
            "rounded_baseline": 9126355,
            "elevated_exposure": 8252723.5482,
            "elevated_exposure_rounded": 8252724,
            "elevated_exposure_pct": 90.43
        },
        "sentinel1_historical_observation": {
            "track": 129,
            "date": "2022-07-16",
            "candidate_floodwater_km2": 1087.5,
            "permanent_water_km2": 1018.3,
            "ambiguous_wetsoil_km2": 214.4
        },
        "preserved_assets": []
    }

    for cf in critical_files:
        info = get_file_info(cf)
        if info:
            inventory["preserved_assets"].append(info)
            print(f"[PRESERVED] {cf:60s} | {info['size_bytes']:9,d} bytes")
        else:
            print(f"[MISSING]   {cf}")

    out_file = WORKSPACE / "data" / "metadata" / "phase_5_2_preservation_inventory.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)

    print(f"\n[+] Preservation inventory generated: {out_file}")

if __name__ == "__main__":
    main()
