"""
Authoritative Population Exposure & Susceptibility Audit Script (Phase 4.3.2)
==============================================================================
Reproduces the EXACT production calculations from FloodRiskAssessmentService:
- Exact CRS and WGS84 coordinate transformations
- Actual HydroSHEDS HydroRIVERS LineString geometries and STRtree spatial queries
- Exact geodesic distance calculations (in km)
- Honest missing-data handling (preserving DEM gaps without artificial zero-filling)
- Exact cell-by-cell multi-criteria FSI calculation
- Identical classification thresholds (Very High: >= 0.72, High: >= 0.58, Moderate: >= 0.44, Low: < 0.44)
- Reports both raw unrounded floating-point totals and rounded integer categories
"""
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.flood_risk_service import FloodRiskAssessmentService

def run_authoritative_audit():
    t0 = time.time()
    print("=" * 115)
    print("PHASE 4.3.2: AUTHORITATIVE POPULATION EXPOSURE AUDIT - LOWER GODAVARI BASIN")
    print("=" * 115)
    print("Initializing production FloodRiskAssessmentService (authoritative calculation engine)...")
    service = FloodRiskAssessmentService()
    t_init = time.time() - t0
    print(f"Service loaded and raster overlay completed in {t_init:.2f}s.\n")

    basin = service.get_basin_assessment()
    
    print("-" * 115)
    print(f"{'Mandal Name':20s} | {'Raw Total':12s} | {'Rnd Total':10s} | {'Very High':10s} | {'High':10s} | {'Moderate':10s} | {'Low':10s} | {'Exp (VH+H)':11s} | {'Pct':6s} | {'DEM Conf':11s}")
    print("-" * 115)

    mandals_sorted = sorted(basin.mandals, key=lambda m: m.mandal_name)

    for m in mandals_sorted:
        prof = service.mandal_profiles[m.mandal_name]
        raw_tot = prof.get("raw_total_pop", 0.0)
        rnd_tot = m.baseline_population_2020
        vh = m.population_very_high_risk or 0
        h = m.population_high_risk or 0
        mod = m.population_moderate_risk or 0
        low = m.population_low_risk or 0
        exp = m.potentially_exposed_population
        pct = m.exposed_population_pct
        conf = m.dem_coverage_confidence or m.confidence_level

        print(f"{m.mandal_name:20s} | {raw_tot:12.2f} | {rnd_tot:10,d} | {vh:10,d} | {h:10,d} | {mod:10,d} | {low:10,d} | {exp:11,d} | {pct:5.1f}% | {conf:11s}")

    print("-" * 115)
    
    # 1. Raw Floating-Point Basin Totals
    raw_vh = sum(p.get("raw_pop_very_high", 0.0) for p in service.mandal_profiles.values())
    raw_h = sum(p.get("raw_pop_high", 0.0) for p in service.mandal_profiles.values())
    raw_mod = sum(p.get("raw_pop_moderate", 0.0) for p in service.mandal_profiles.values())
    raw_low = sum(p.get("raw_pop_low", 0.0) for p in service.mandal_profiles.values())
    raw_total = sum(p.get("raw_total_pop", 0.0) for p in service.mandal_profiles.values())
    raw_exp = raw_vh + raw_h
    raw_pct = (raw_exp / raw_total * 100) if raw_total > 0 else 0.0

    print(f"{'RAW BASIN TOTAL':20s} | {raw_total:12.2f} | {'N/A':10s} | {raw_vh:10.1f} | {raw_h:10.1f} | {raw_mod:10.1f} | {raw_low:10.1f} | {raw_exp:11.1f} | {raw_pct:5.2f}% | {'BASIN-WIDE':11s}")

    # 2. Rounded Mandal-by-Mandal Sums
    rnd_vh = sum(m.population_very_high_risk or 0 for m in basin.mandals)
    rnd_h = sum(m.population_high_risk or 0 for m in basin.mandals)
    rnd_mod = sum(m.population_moderate_risk or 0 for m in basin.mandals)
    rnd_low = sum(m.population_low_risk or 0 for m in basin.mandals)
    rnd_total = sum(m.baseline_population_2020 for m in basin.mandals)
    rnd_exp = rnd_vh + rnd_h
    rnd_pct = (rnd_exp / rnd_total * 100) if rnd_total > 0 else 0.0

    print(f"{'ROUNDED MANDAL SUM':20s} | {'N/A':12s} | {rnd_total:10,d} | {rnd_vh:10,d} | {rnd_h:10,d} | {rnd_mod:10,d} | {rnd_low:10,d} | {rnd_exp:11,d} | {rnd_pct:5.2f}% | {'BASIN-WIDE':11s}")
    
    # 3. Overall Rounded Totals (Direct round of unrounded floats)
    glob_rnd_vh = int(round(raw_vh))
    glob_rnd_h = int(round(raw_h))
    glob_rnd_mod = int(round(raw_mod))
    glob_rnd_low = int(round(raw_low))
    glob_rnd_total = int(round(raw_total))
    glob_rnd_exp = int(round(raw_exp))
    glob_rnd_pct = (glob_rnd_exp / glob_rnd_total * 100)

    print(f"{'DIRECT ROUNDED SUM':20s} | {'N/A':12s} | {glob_rnd_total:10,d} | {glob_rnd_vh:10,d} | {glob_rnd_h:10,d} | {glob_rnd_mod:10,d} | {glob_rnd_low:10,d} | {glob_rnd_exp:11,d} | {glob_rnd_pct:5.2f}% | {'BASIN-WIDE':11s}")
    print("=" * 115)

    print("\nMATHEMATICAL & ROUNDING CONSISTENCY VERIFICATION:")
    print(f"1. Raw float unrounded population sum : {raw_total:.4f}")
    print(f"2. Overall rounded total (round(raw)) : {glob_rnd_total:,d}")
    print(f"3. Sum of 21 rounded mandals           : {rnd_total:,d}")
    print(f"4. Rounding discrepancy (Mandal - Raw): {rnd_total - glob_rnd_total} persons")
    print(f"5. Combined elevated exposure (VH + H): {rnd_exp:,d} persons ({rnd_pct:.2f}%)")
    print(f"6. Phase 4.3 baseline exposure value  : 8,252,724 persons (Match: {rnd_exp == 8252724})")
    print(f"7. Phase 4.3 baseline population value: 9,126,355 persons (Match: {rnd_total == 9126355})")

if __name__ == "__main__":
    run_authoritative_audit()
