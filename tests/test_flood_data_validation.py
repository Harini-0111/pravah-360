"""
Automated Test Suite for Flood Data Validation & Analysis (Phase 3).
Tests the reproducibility and integrity of Sentinel-1 catalogue validation,
rainfall cross-comparison (GPM, CHIRPS, ERA5), terrain DSM, and exposure layers.
"""

import unittest
import os
import numpy as np

from scripts.validate_flood_data import FloodDataValidator, parse_netcdf3_classic

class TestFloodDataValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = FloodDataValidator()
        cls.results = cls.validator.run_all()

    def test_gpm_imerg_daily_validation(self):
        """Verify NASA GPM IMERG Daily NetCDF-4/HDF5 structure, units, and stats."""
        gpm = self.results["rainfall_datasets"].get("gpm_imerg")
        self.assertIsNotNone(gpm, "GPM IMERG validation result should exist.")
        self.assertEqual(gpm["status"], "VALID")
        self.assertEqual(gpm["units"], "mm/day")
        self.assertEqual(gpm["date"], "2022-07-15")
        self.assertIn("precipitation", gpm["variables"])
        self.assertIn("randomError", gpm["variables"])
        self.assertGreater(gpm["max_mm_day"], 20.0)
        self.assertGreater(gpm["mean_mm_day"], 2.0)
        self.assertLess(gpm["mean_mm_day"], 6.0)

    def test_chirps_daily_validation(self):
        """Verify CHIRPS 2.0 NetCDF-3 Classic parsing and temporal series."""
        chirps = self.results["rainfall_datasets"].get("chirps")
        self.assertIsNotNone(chirps, "CHIRPS validation result should exist.")
        self.assertEqual(chirps["status"], "VALID")
        self.assertEqual(len(chirps["full_daily_series"]), 11)
        # Check peak antecedent storm date (July 11)
        self.assertIn("2022-07-11", chirps["event_peak_date"])
        # July 15 stats
        j15 = chirps["july15_stats"]
        self.assertEqual(j15["date"], "2022-07-15")
        self.assertGreater(j15["mean_mm"], 3.0)
        self.assertLess(j15["mean_mm"], 6.0)

    def test_era5_rainfall_validation(self):
        """Verify ERA5 reanalysis series and antecedent 72-hour precipitation sum."""
        era5 = self.results["rainfall_datasets"].get("era5")
        self.assertIsNotNone(era5, "ERA5 validation result should exist.")
        self.assertEqual(era5["status"], "VALID")
        self.assertGreater(era5["total_11day_mm"], 140.0)
        self.assertGreater(era5["antecedent_3day_peak_mm"], 90.0)
        self.assertIn("100.5 mm", era5["antecedent_3day_window"])

    def test_cross_product_rainfall_agreement(self):
        """Verify that GPM IMERG and CHIRPS show strong consistency for July 15, 2022."""
        comp = self.results.get("cross_product_rainfall_comparison")
        self.assertIsNotNone(comp)
        gpm_mean = comp["gpm_imerg_daily_mean_mm"]
        chirps_mean = comp["chirps_daily_mean_mm"]
        self.assertIsNotNone(gpm_mean)
        self.assertIsNotNone(chirps_mean)
        # Difference between GPM and CHIRPS basin-wide mean on July 15 should be < 2.0 mm/day
        diff = abs(gpm_mean - chirps_mean)
        self.assertLess(diff, 2.0, "GPM and CHIRPS basin mean should agree closely (<2mm diff).")
        self.assertEqual(comp["consistency_verdict"], "STRONG SCIENTIFIC AGREEMENT")

    def test_copernicus_dem_dsm_integrity(self):
        """Verify Copernicus DEM elevation, slope, aspect, and DSM classification."""
        rasters = self.results["spatial_rasters"]
        elev = rasters.get("Copernicus DEM Processed Elevation")
        self.assertIsNotNone(elev)
        self.assertEqual(elev["status"], "VALID")
        self.assertEqual(elev["dimensions"], [3600, 3600])
        self.assertIn("DSM", elev["model_type"])

        slope = rasters.get("Copernicus DEM Slope (deg)")
        self.assertIsNotNone(slope)
        self.assertEqual(slope["status"], "VALID")
        self.assertGreater(slope["max"], 30.0)

        aspect = rasters.get("Copernicus DEM Aspect (deg)")
        self.assertIsNotNone(aspect)
        self.assertEqual(aspect["status"], "VALID")

    def test_worldcover_landcover_classes(self):
        """Verify ESA WorldCover discrete class codes in 10m raw and 50m clipped rasters."""
        rasters = self.results["spatial_rasters"]
        lc10 = rasters.get("ESA WorldCover 10m Raw Tile")
        lc50 = rasters.get("ESA WorldCover 50m Godavari")
        self.assertIsNotNone(lc10)
        self.assertIsNotNone(lc50)
        self.assertEqual(lc10["status"], "VALID")
        self.assertEqual(lc50["status"], "VALID")
        # Ensure key classes exist (10: Tree, 40: Cropland, 50: Built-up, 80: Water, 95: Mangroves)
        for expected_class in [10, 40, 50, 80, 95]:
            self.assertIn(expected_class, lc50["unique_classes"])

    def test_worldpop_population_baseline(self):
        """Verify WorldPop clipped baseline total population (~11.11 million persons)."""
        rasters = self.results["spatial_rasters"]
        wpop = rasters.get("WorldPop Lower Godavari Clipped")
        self.assertIsNotNone(wpop)
        self.assertEqual(wpop["status"], "VALID")
        self.assertEqual(wpop["dimensions"], [192, 216])
        pop_sum = wpop["total_population_sum"]
        self.assertGreater(pop_sum, 1.0e7, "Lower Godavari population should exceed 10 million.")
        self.assertLess(pop_sum, 1.2e7, "Lower Godavari population should be under 12 million.")

    def test_sentinel1_sar_catalogue_and_raster_status(self):
        """Verify Sentinel-1 catalogue scenes and transparently verify local raster presence."""
        s1 = self.results.get("sentinel1_sar")
        self.assertIsNotNone(s1)
        self.assertTrue(s1["catalogue_found"])
        self.assertEqual(s1["flood_peak_scenes_count"], 8)
        self.assertEqual(s1["baseline_scenes_count"], 12)
        # Orbit geometry match verified
        compat = s1.get("orbit_geometry_compatibility", {})
        self.assertTrue(compat.get("identical_relative_orbit_pair_found"))
        # Transparent check: reflects actual state on disk (downloaded/processed vs pre-export catalogue)
        if s1["local_rasters_present"]:
            self.assertEqual(s1["status"], "VALID_WITH_LOCAL_RASTERS")
            self.assertGreater(len(s1["local_raster_files"]), 0)
        else:
            self.assertEqual(s1["status"], "CATALOGUE_VALID_RASTERS_NOT_DOWNLOADED")
            self.assertIn("limitation_note", s1)

    def test_vector_layers_integrity(self):
        """Verify all 8 vector layers are valid with 100% valid geometries."""
        vectors = self.results["vector_layers"]
        self.assertEqual(len(vectors), 8)
        for name, v in vectors.items():
            self.assertEqual(v["status"], "VALID", f"Vector layer {name} should be valid.")
            self.assertEqual(v["valid_geometries_count"], v["feature_count"], f"All geometries in {name} must be valid.")

    def test_scientific_readiness_assessment(self):
        """Verify the synthesized assessment answers the core user question."""
        verdict = self.results.get("scientific_readiness_assessment")
        self.assertIsNotNone(verdict)
        self.assertEqual(verdict["rainfall_datasets_status"], "READY & FULLY VALIDATED")
        self.assertEqual(verdict["overall_phase3_verdict"], "PARTIALLY READY FOR PHASE 4")


if __name__ == "__main__":
    unittest.main()
