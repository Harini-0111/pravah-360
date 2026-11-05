"""
Comprehensive Test Suite for Phase 4: Flood Risk and Impact Assessment
========================================================================
Project: AI-Based Flood Risk, Impact Assessment and Emergency Decision Support
Study Area: Lower Godavari Basin (21 Mandals), Andhra Pradesh, India
"""

import unittest
from typing import Dict, Any
from fastapi import HTTPException
from shapely.geometry import Point

from backend.app.services.flood_risk_service import (
    FloodRiskAssessmentService,
    DEFAULT_WEIGHTS,
    CLASSIFICATION_THRESHOLDS
)
from backend.app.schemas.flood_risk import (
    BasinRiskAssessmentSummary,
    MandalRiskAssessment,
    PointRiskEvaluation,
    PointRiskEvaluationInput,
    SensitivityAnalysisResult
)
from backend.app.api import endpoints


class TestFloodRiskAssessmentService(unittest.TestCase):
    """Unit tests for FloodRiskAssessmentService calculations and datasets."""

    @classmethod
    def setUpClass(cls):
        cls.service = FloodRiskAssessmentService()

    def test_service_initialization(self):
        """Verify that all required datasets and spatial indices are loaded."""
        self.assertEqual(len(self.service.mandals_by_name), 21, "Must contain exactly 21 mandals.")
        self.assertEqual(len(self.service.mandal_profiles), 21, "Must precompute profiles for all 21 mandals.")
        self.assertIsNotNone(self.service.dem_mosaic, "DEM mosaic must be assembled.")
        self.assertEqual(self.service.dem_mosaic.shape, (7200, 7200), "DEM mosaic must be 7200x7200 pixels.")
        self.assertIsNotNone(self.service.slope_mosaic, "Slope mosaic must be computed.")
        self.assertIsNotNone(self.service.river_tree, "River spatial STRtree index must exist.")
        self.assertGreater(len(self.service.river_geoms), 1000, "Must contain HydroRIVERS reaches.")
        self.assertGreater(len(self.service.healthcare_facilities), 1000, "Must load healthcare facilities.")
        self.assertGreater(len(self.service.education_facilities), 300, "Must load education facilities.")
        self.assertGreater(len(self.service.emergency_shelters), 50, "Must load emergency shelters.")

    def test_factor_normalization_bounds(self):
        """Verify that all factor normalization functions output strictly between 0.0 and 1.0."""
        # Elevation
        self.assertEqual(self.service.normalize_elevation_score(0.0), 1.0)
        self.assertEqual(self.service.normalize_elevation_score(5.0), 1.0)
        self.assertLess(self.service.normalize_elevation_score(30.0), 1.0)
        self.assertGreater(self.service.normalize_elevation_score(30.0), 0.0)
        self.assertLessEqual(self.service.normalize_elevation_score(500.0), 0.15)

        # Slope
        self.assertEqual(self.service.normalize_slope_score(0.5), 1.0)
        self.assertLess(self.service.normalize_slope_score(4.0), 1.0)
        self.assertGreater(self.service.normalize_slope_score(4.0), 0.0)
        self.assertEqual(self.service.normalize_slope_score(35.0), 0.05)

        # River distance
        self.assertEqual(self.service.normalize_river_distance_score(0.2), 1.0)
        self.assertLess(self.service.normalize_river_distance_score(3.0), 1.0)
        self.assertGreater(self.service.normalize_river_distance_score(3.0), 0.0)
        self.assertEqual(self.service.normalize_river_distance_score(15.0), 0.10)

        # Land cover
        self.assertEqual(self.service.normalize_landcover_score(80), 1.0)  # Water
        self.assertEqual(self.service.normalize_landcover_score(90), 1.0)  # Wetland
        self.assertEqual(self.service.normalize_landcover_score(40), 0.8)  # Cropland
        self.assertEqual(self.service.normalize_landcover_score(10), 0.15) # Forest

    def test_weights_normalization(self):
        """Verify that factor weights are strictly normalized to sum to 1.0."""
        custom_w = {"elevation": 5.0, "slope": 5.0, "river_proximity": 5.0, "landcover": 5.0, "historical_hazard": 5.0}
        norm_w = self.service._normalize_weights(custom_w)
        self.assertAlmostEqual(sum(norm_w.values()), 1.0, places=3)
        self.assertAlmostEqual(norm_w["elevation"], 0.20, places=2)

    def test_classification_thresholds(self):
        """Verify the 4-tier risk classification logic."""
        self.assertEqual(self.service.classify_risk(0.85), "Very High")
        self.assertEqual(self.service.classify_risk(0.72), "Very High")
        self.assertEqual(self.service.classify_risk(0.65), "High")
        self.assertEqual(self.service.classify_risk(0.58), "High")
        self.assertEqual(self.service.classify_risk(0.50), "Moderate")
        self.assertEqual(self.service.classify_risk(0.44), "Moderate")
        self.assertEqual(self.service.classify_risk(0.35), "Low")
        self.assertEqual(self.service.classify_risk(0.10), "Low")

    def test_population_zonal_statistics(self):
        """Verify that baseline population estimates are realistic and preserve units."""
        basin = self.service.get_basin_assessment()
        self.assertGreater(basin.total_population, 8_000_000, "Total baseline population should exceed 8M.")
        self.assertLess(basin.total_population, 12_000_000, "Total baseline population should not exceed 12M.")
        
        # Verify no double-counting: sum of mandal populations must equal basin total
        mandal_sum = sum(m.baseline_population_2020 for m in basin.mandals)
        self.assertEqual(mandal_sum, basin.total_population, "Mandal population sum must equal basin total.")

        # Potentially exposed population must be strictly less than or equal to total population
        self.assertLessEqual(basin.total_potentially_exposed_population, basin.total_population)
        self.assertGreater(basin.total_potentially_exposed_population, 0)

    def test_infrastructure_facility_counts(self):
        """Verify that infrastructure facilities are properly counted and mapped."""
        basin = self.service.get_basin_assessment()
        self.assertGreater(basin.total_mapped_facilities, 1000)
        
        # Sum of facilities by risk must equal total
        fac_sum = sum(basin.facilities_by_risk.values())
        self.assertEqual(fac_sum, basin.total_mapped_facilities)

    def test_mandal_risk_geographical_consistency(self):
        """Verify that known low-lying delta mandals have elevated risk compared to agency hills."""
        ama = self.service.assess_mandal_risk("Amalapuram")
        bhm = self.service.assess_mandal_risk("Bhimavaram")
        rcp = self.service.assess_mandal_risk("RampaChodavaram")
        add = self.service.assess_mandal_risk("Addatigala")

        # Delta mandals must have higher susceptibility score than upland hill mandals
        self.assertIn(ama.risk_level, ("Very High", "High"))
        self.assertIn(bhm.risk_level, ("Very High", "High"))
        self.assertEqual(rcp.risk_level, "Low")
        self.assertEqual(add.risk_level, "Low")
        self.assertGreater(ama.susceptibility_score, rcp.susceptibility_score)
        self.assertGreater(bhm.susceptibility_score, add.susceptibility_score)

        # Delta mandal mean elevation must be significantly lower than hills
        self.assertLess(ama.factors.elevation_m, 20.0)
        self.assertGreater(rcp.factors.elevation_m, 200.0)

    def test_explainability_generation(self):
        """Verify that plain-English explanations and primary risk drivers are generated."""
        ama = self.service.assess_mandal_risk("Amalapuram")
        self.assertGreater(len(ama.primary_risk_drivers), 0)
        self.assertIn("Amalapuram", ama.plain_english_explanation)
        self.assertIn("Susceptibility", ama.plain_english_explanation)
        self.assertGreater(len(ama.scientific_limitations), 2)

    def test_point_risk_evaluation(self):
        """Test coordinate-level susceptibility evaluation inside and outside the study area."""
        # Point in Dowleswaram / Kovvur lowlands (16.942, 81.776)
        pt_in = self.service.evaluate_point(16.942, 81.776)
        self.assertTrue(pt_in.is_inside_study_area)
        self.assertIsNotNone(pt_in.mandal)
        self.assertIn(pt_in.risk_level, ("High", "Very High"))
        self.assertGreater(pt_in.susceptibility_score, 0.5)

        # Point outside Andhra Pradesh (e.g. Bangalore: 12.97, 77.59)
        pt_out = self.service.evaluate_point(12.97, 77.59)
        self.assertFalse(pt_out.is_inside_study_area)
        self.assertIsNone(pt_out.mandal)

    def test_sensitivity_analysis_execution(self):
        """Verify that sensitivity analysis tests multiple scenarios without failure."""
        res = self.service.run_sensitivity_analysis()
        self.assertIsInstance(res, SensitivityAnalysisResult)
        self.assertEqual(len(res.scenarios), 4)
        for sc in res.scenarios:
            self.assertEqual(sum(sc.risk_distribution.values()), 21)
            self.assertGreater(len(sc.scenario_name), 0)
        self.assertGreater(len(res.conclusion), 20)

    def test_phase_4_1_raster_population_overlay_not_fixed_multipliers(self):
        """Verify that population exposure is derived from raster cell overlay, not heuristic multipliers."""
        basin = self.service.get_basin_assessment()
        
        # Verify basin total exposed population matches cell-by-cell sum across mandals
        self.assertEqual(basin.total_potentially_exposed_population, 8_252_724)
        self.assertAlmostEqual(basin.exposed_population_pct, 90.43, places=1)

        # Verify mandal exposures are NOT simple fixed percentages (85%, 65%, 35%, 10%)
        fixed_percentages = {0.85, 0.65, 0.35, 0.10}
        for mandal in basin.mandals:
            ratio = mandal.potentially_exposed_population / mandal.baseline_population_2020
            # Ensure none match the simplistic fixed percentages exactly
            for fp in fixed_percentages:
                self.assertNotAlmostEqual(ratio, fp, places=4, 
                    msg=f"Mandal {mandal.mandal_name} must use true raster overlay, not fixed {fp*100}% heuristic.")
            
            # Verify breakdown sums to total
            vh = mandal.population_very_high_risk or 0
            h = mandal.population_high_risk or 0
            m = mandal.population_moderate_risk or 0
            l = mandal.population_low_risk or 0
            self.assertEqual(vh + h + m + l, mandal.baseline_population_2020)

    def test_phase_4_1_ahp_consistency_ratio(self):
        """Verify that AHP pairwise comparison matrix has Consistency Ratio CR < 0.10."""
        self.assertLess(self.service.ahp_consistency_ratio, 0.10, "AHP matrix must be mathematically consistent.")
        self.assertAlmostEqual(self.service.ahp_consistency_ratio, 0.0001, places=3)
        self.assertEqual(len(self.service.ahp_matrix), 5)
        # Verify reciprocal symmetry a_ij = 1 / a_ji
        for i in range(5):
            for j in range(5):
                self.assertAlmostEqual(self.service.ahp_matrix[i][j] * self.service.ahp_matrix[j][i], 1.0, places=2)

    def test_phase_4_1_dem_coverage_and_river_distances(self):
        """Verify exact per-mandal DEM coverage reporting and distinct stream vs major river distances."""
        for name, m in self.service.mandal_profiles.items():
            self.assertIn("dem_coverage_pct", m)
            self.assertIn("mean_major_river_distance_km", m)
            if name == "Chintalapudi":
                self.assertAlmostEqual(m["dem_coverage_pct"], 74.74, places=1)
            elif name == "Eluru":
                self.assertAlmostEqual(m["dem_coverage_pct"], 97.36, places=1)
            else:
                self.assertGreaterEqual(m["dem_coverage_pct"], 99.9)
            self.assertGreaterEqual(m["mean_major_river_distance_km"], m["mean_stream_distance_km"] - 0.001)
            
            # Also test the Pydantic assessment output
            ass = self.service.assess_mandal_risk(name)
            self.assertEqual(ass.factors.dem_coverage_pct, m["dem_coverage_pct"])
            self.assertIsNotNone(ass.factors.major_river_distance_km)

    def test_phase_4_1_point_level_facility_exposure(self):
        """Verify that facility risk is evaluated at exact point coordinates."""
        basin = self.service.get_basin_assessment()
        self.assertEqual(basin.facilities_by_risk["Very High"], 876)
        self.assertEqual(basin.facilities_by_risk["High"], 591)
        self.assertEqual(basin.facilities_by_risk["Moderate"], 72)
        self.assertEqual(basin.facilities_by_risk["Low"], 3)
        elevated_facilities = basin.facilities_by_risk["Very High"] + basin.facilities_by_risk["High"]
        self.assertEqual(elevated_facilities, 1467)
        self.assertEqual(basin.total_mapped_facilities, 1542)

    def test_phase_4_2_study_area_reconciliation(self):
        """Phase 4.2 Audit: Verify true study area size (~18,500 km2) and refute the 9,008.8 km2 transcription error."""
        basin = self.service.get_basin_assessment()
        total_mandal_area = sum(m.area_sq_km for m in basin.mandals)
        self.assertGreater(total_mandal_area, 18_000.0, "Total 21-mandal area must exceed 18,000 km2.")
        self.assertLess(total_mandal_area, 19_000.0, "Total 21-mandal area must be ~18,500 km2.")
        self.assertAlmostEqual(total_mandal_area, 18_523.0, delta=50.0)

    def test_phase_4_2_dem_no_artificial_clamping(self):
        """Phase 4.2 Audit: Verify that sampling outside 81.0E-83.0E returns None without artificial clamping."""
        # Point west of 81.0E (e.g. 80.90E, 17.0N in western Chintalapudi)
        e, s = self.service._sample_dem_at(80.90, 17.0)
        self.assertIsNone(e, "Uncovered DEM coordinates must return None.")
        self.assertIsNone(s, "Uncovered DEM coordinates must return None.")

        # Coordinate evaluation at gap point
        pt_eval = self.service.evaluate_point(17.0, 80.90)
        self.assertIn("DEM Gap", pt_eval.explanation)
        self.assertIn("1.88%", pt_eval.limitation_note)

    def test_phase_4_2_mapped_facility_totals_reconciliation(self):
        """Phase 4.2 Audit: Verify mapped facility terminology and exact category reconciliation."""
        basin = self.service.get_basin_assessment()
        # All facilities by risk sum to total mapped
        risk_sum = sum(basin.facilities_by_risk.values())
        self.assertEqual(risk_sum, basin.total_mapped_facilities)
        self.assertEqual(basin.total_mapped_facilities, 1542)


class TestFloodRiskAPIEndpoints(unittest.TestCase):
    """Integration tests for Phase 4 FastAPI endpoints."""

    def test_get_basin_risk_assessment_endpoint(self):
        """GET /api/v1/risk/assessment"""
        res = endpoints.get_basin_risk_assessment()
        self.assertIsInstance(res, BasinRiskAssessmentSummary)
        self.assertEqual(res.total_mandals, 21)
        self.assertIn("Very High", res.risk_distribution)

    def test_get_risk_mandals_geojson_endpoint(self):
        """GET /api/v1/risk/mandals"""
        res = endpoints.get_risk_mandals_geojson()
        self.assertEqual(res["type"], "FeatureCollection")
        self.assertEqual(len(res["features"]), 21)
        # Verify required properties for map rendering
        p = res["features"][0]["properties"]
        self.assertIn("susceptibility_score", p)
        self.assertIn("risk_level", p)
        self.assertIn("baseline_population", p)
        self.assertIn("potentially_exposed_population", p)

    def test_get_mandal_risk_profile_endpoint_valid_and_invalid(self):
        """GET /api/v1/risk/mandal/{mandal_name}"""
        # Valid mandal
        res = endpoints.get_mandal_risk_profile("Rajahmundry")
        self.assertEqual(res.mandal_name, "Rajahmundry")
        self.assertEqual(res.district_name, "East Godavari")

        # Invalid mandal must raise 404
        with self.assertRaises(HTTPException) as ctx:
            endpoints.get_mandal_risk_profile("NonExistentMandal123")
        self.assertEqual(ctx.exception.status_code, 404)

    def test_get_exposure_summary_endpoint(self):
        """GET /api/v1/risk/exposure/summary"""
        res = endpoints.get_exposure_summary()
        self.assertIn("total_population", res)
        self.assertIn("total_potentially_exposed_population", res)
        self.assertIn("population_by_risk", res)
        self.assertIn("facilities_by_risk", res)
        self.assertIn("district_summaries", res)

    def test_get_infrastructure_geojson_endpoint(self):
        """GET /api/v1/risk/infrastructure"""
        res = endpoints.get_infrastructure_geojson()
        self.assertEqual(res["type"], "FeatureCollection")
        self.assertGreater(len(res["features"]), 1000)
        p = res["features"][0]["properties"]
        self.assertIn("facility_type", p)
        self.assertIn("host_risk_level", p)

    def test_evaluate_point_risk_endpoint_valid_and_invalid(self):
        """POST /api/v1/risk/evaluate-point"""
        # Valid point
        inp = PointRiskEvaluationInput(latitude=16.5557, longitude=82.0156)
        res = endpoints.evaluate_point_risk(inp)
        self.assertIsInstance(res, PointRiskEvaluation)
        self.assertEqual(res.latitude, 16.5557)
        self.assertEqual(res.longitude, 82.0156)

        # Invalid coordinate (out of range lat)
        bad_inp = PointRiskEvaluationInput(latitude=999.0, longitude=82.0)
        with self.assertRaises(HTTPException) as ctx:
            endpoints.evaluate_point_risk(bad_inp)
        self.assertEqual(ctx.exception.status_code, 400)

    def test_get_risk_sensitivity_endpoint(self):
        """GET /api/v1/risk/sensitivity"""
        res = endpoints.get_risk_sensitivity_analysis()
        self.assertIsInstance(res, SensitivityAnalysisResult)
        self.assertEqual(len(res.scenarios), 4)

    def test_phase_4_3_no_synthetic_depth_or_probability_in_markers(self):
        """Phase 4.3 Task 1 & Phase 4.3.1 Task 4: Verify markers present null depth and explicit NOT_OBSERVED status."""
        markers = endpoints.get_flood_risk_markers()
        self.assertEqual(len(markers), 10)
        for m in markers:
            # Must not show legacy hardcoded depth 3.85m or prob 0.94
            self.assertNotEqual(m.water_depth_est_m, 3.85, "Synthetic depth 3.85m must be removed.")
            self.assertIsNone(m.water_depth_est_m, "Unobserved water depth must be null (None) to avoid -9999 calculation errors.")
            self.assertIsNone(m.water_depth_m, "Unobserved water depth must be null (None).")
            self.assertIsNotNone(m.water_depth_status)
            self.assertIn("NOT_OBSERVED", m.water_depth_status)
            # Physical susceptibility score must be present
            self.assertIsNotNone(m.susceptibility_score)
            self.assertGreaterEqual(m.susceptibility_score, 0.0)
            self.assertLessEqual(m.susceptibility_score, 1.0)

    def test_phase_4_3_alerts_are_susceptibility_advisories(self):
        """Phase 4.3 Task 2: Verify alerts are framed as susceptibility advisories without false emergency claims."""
        alerts = endpoints.get_flood_alerts()
        self.assertGreater(len(alerts), 0)
        for a in alerts:
            self.assertIn("SUSCEPTIBILITY ADVISORY", a.title)
            self.assertNotIn("Estimated water depth: 3.85m", a.summary)
            self.assertIn("In-situ water depth is NOT observed", a.summary)
            self.assertIn("Mandal", a.human_readable_location)

    def test_phase_4_3_confidence_level_enforcement(self):
        """Phase 4.3.1 Task 3: Verify 4-tier machine-readable confidence_level (HIGH, MEDIUM, PROVISIONAL, NODATA)."""
        # 1. Mandal confidence
        prof_rjy = endpoints.get_mandal_risk_profile("Rajahmundry")
        self.assertEqual(prof_rjy.confidence_level, "HIGH", "Rajahmundry with 100.0% DEM coverage must be HIGH.")

        prof_eluru = endpoints.get_mandal_risk_profile("Eluru")
        self.assertEqual(prof_eluru.confidence_level, "MEDIUM", "Eluru with 97.36% DEM coverage (90-99%) must be MEDIUM.")

        prof_chin = endpoints.get_mandal_risk_profile("Chintalapudi")
        self.assertEqual(prof_chin.confidence_level, "PROVISIONAL", "Chintalapudi with 74.74% DEM coverage (50-90%) must be PROVISIONAL.")

        # 2. Point evaluation confidence
        pt_good = endpoints.evaluate_point_risk(PointRiskEvaluationInput(latitude=17.0, longitude=81.8))
        self.assertEqual(pt_good.confidence_level, "HIGH", "Inside study area with valid DEM must be HIGH.")

        pt_gap = endpoints.evaluate_point_risk(PointRiskEvaluationInput(latitude=17.05, longitude=80.95))
        self.assertEqual(pt_gap.confidence_level, "PROVISIONAL", "Inside study area but in western DEM gap must be PROVISIONAL.")

        pt_out = endpoints.evaluate_point_risk(PointRiskEvaluationInput(latitude=20.0, longitude=85.0))
        self.assertEqual(pt_out.confidence_level, "NODATA", "Outside study area boundary must be NODATA.")

    def test_phase_4_3_population_partitioning_and_invariant_exposure(self):
        """Phase 4.3 Task 3: Verify population partitioning without double counting and invariant exposure."""
        summary = endpoints.get_basin_risk_assessment()
        # Sum of categories strictly partitions total baseline population
        sum_bins = sum(summary.population_exposure_by_risk.values())
        self.assertEqual(sum_bins, summary.total_population)
        # Invariant elevated exposure
        self.assertEqual(summary.total_potentially_exposed_population, 8252724)
        self.assertAlmostEqual(summary.exposed_population_pct, 90.43, places=2)
        # Sum of VH + H matches total exposed
        vh_h_sum = summary.population_exposure_by_risk["Very High"] + summary.population_exposure_by_risk["High"]
        self.assertEqual(vh_h_sum, 8252724)

    def test_phase_4_3_2_dem_coverage_confidence_and_overall_unrated(self):
        """Phase 4.3.2 Task 2: Verify dem_coverage_confidence is distinguished from overall model confidence."""
        # Mandal confidence
        prof_rjy = endpoints.get_mandal_risk_profile("Rajahmundry")
        self.assertEqual(prof_rjy.dem_coverage_confidence, "HIGH")
        self.assertIn("UNRATED", prof_rjy.overall_assessment_confidence)

        prof_eluru = endpoints.get_mandal_risk_profile("Eluru")
        self.assertEqual(prof_eluru.dem_coverage_confidence, "MEDIUM")
        self.assertIn("UNRATED", prof_eluru.overall_assessment_confidence)

        prof_chin = endpoints.get_mandal_risk_profile("Chintalapudi")
        self.assertEqual(prof_chin.dem_coverage_confidence, "PROVISIONAL")
        self.assertIn("UNRATED", prof_chin.overall_assessment_confidence)

        # Dataset limitations documented
        self.assertGreaterEqual(len(prof_rjy.scientific_limitations), 6)
        self.assertTrue(any("Copernicus DEM" in lim for lim in prof_rjy.scientific_limitations))
        self.assertTrue(any("HydroRIVERS" in lim for lim in prof_rjy.scientific_limitations))
        self.assertTrue(any("WorldCover" in lim for lim in prof_rjy.scientific_limitations))
        self.assertTrue(any("WorldPop" in lim for lim in prof_rjy.scientific_limitations))

    def test_phase_4_3_2_nodata_and_gap_handling_cases(self):
        """Phase 4.3.2 Task 3: Verify NoData handling across 4 specific spatial test cases."""
        # Case A: Inside a fully covered mandal (Rajahmundry)
        res_a = endpoints.evaluate_point_risk(PointRiskEvaluationInput(latitude=17.0005, longitude=81.8040))
        self.assertTrue(res_a.is_inside_study_area)
        self.assertEqual(res_a.mandal, "Rajahmundry")
        self.assertIsNotNone(res_a.elevation_m)
        self.assertGreater(res_a.elevation_m, 0.0)
        self.assertIsNotNone(res_a.slope_deg)
        self.assertIsNotNone(res_a.susceptibility_score)
        self.assertEqual(res_a.dem_coverage_confidence, "HIGH")

        # Case B: Inside Eluru's partial DEM coverage
        res_b = endpoints.evaluate_point_risk(PointRiskEvaluationInput(latitude=16.7100, longitude=81.1000))
        self.assertTrue(res_b.is_inside_study_area)
        self.assertEqual(res_b.mandal, "Eluru")
        self.assertIsNotNone(res_b.elevation_m)
        self.assertIsNotNone(res_b.slope_deg)
        self.assertIsNotNone(res_b.susceptibility_score)
        self.assertEqual(res_b.dem_coverage_confidence, "MEDIUM")
        self.assertIn("97.36%", res_b.limitation_note)

        # Case C: Inside Chintalapudi's DEM coverage gap (west of 81.0E)
        res_c = endpoints.evaluate_point_risk(PointRiskEvaluationInput(latitude=17.0500, longitude=80.9500))
        self.assertTrue(res_c.is_inside_study_area)
        self.assertEqual(res_c.mandal, "Chintalapudi")
        # Missing DEM must NOT become 0.0 elevation
        self.assertIsNone(res_c.elevation_m, "Missing DEM sample must not become 0.0 elevation.")
        self.assertIsNone(res_c.slope_deg, "Missing slope sample must not become 0.0 slope.")
        # Missing values must NOT receive fabricated terrain scores
        self.assertIsNone(res_c.susceptibility_score, "Missing terrain factors must not receive fabricated susceptibility score.")
        self.assertEqual(res_c.risk_level, "Unavailable (DEM Coverage Gap)")
        self.assertEqual(res_c.dem_coverage_confidence, "PROVISIONAL")
        self.assertIn("1.88%", res_c.limitation_note)

        # Case D: Outside Lower Godavari study boundary
        res_d = endpoints.evaluate_point_risk(PointRiskEvaluationInput(latitude=20.0, longitude=85.0))
        self.assertFalse(res_d.is_inside_study_area, "Outside points must remain distinguishable from internal NoData points.")
        self.assertIsNone(res_d.mandal)
        self.assertIsNone(res_d.district)
        self.assertIsNone(res_d.elevation_m)
        self.assertIsNone(res_d.susceptibility_score)
        self.assertEqual(res_d.risk_level, "Outside Study Area")
        self.assertEqual(res_d.dem_coverage_confidence, "NODATA")

    def test_phase_4_3_2_population_reporting_consistency(self):
        """Phase 4.3.2 Task 4: Verify raw floating-point totals, rounded totals, and zero rounding discrepancy."""
        summary = endpoints.get_basin_risk_assessment()
        self.assertIsNotNone(summary.raw_total_population)
        self.assertAlmostEqual(summary.raw_total_population, 9126354.98, delta=1.0)
        self.assertEqual(summary.total_population, 9126355)
        self.assertEqual(summary.total_potentially_exposed_population, 8252724)
        self.assertEqual(summary.rounding_discrepancy, 0)
        
        # Verify raw fields on individual mandal
        prof_rjy = endpoints.get_mandal_risk_profile("Rajahmundry")
        self.assertIsNotNone(prof_rjy.raw_baseline_population)
        self.assertGreater(prof_rjy.raw_baseline_population, 916000.0)


if __name__ == "__main__":
    unittest.main()
