"""
Phase 5.2 GIS-First Workspaces & Global 3D Earth Acceptance Test Suite.
Verifies all 7 workspaces, static asset integrity, endpoint contracts,
basemap configurations, and scientific figure integrity.
"""
import unittest
import json
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.main import app, serve_frontend_root, get_mandals_geojson
from backend.app.api import endpoints

class TestPhase52GisWorkspaces(unittest.TestCase):

    def test_01_index_html_structure_and_7_workspaces(self):
        """Verify frontend/index.html defines all 7 workspaces, navigation, and 3D globe elements."""
        index_path = os.path.join("frontend", "index.html")
        self.assertTrue(os.path.exists(index_path), "frontend/index.html must exist")

        with open(index_path, "r", encoding="utf-8") as f:
            html = f.read()

        workspaces = [
            "workspace-overview",
            "workspace-explorer",
            "workspace-risk",
            "workspace-impact",
            "workspace-weather",
            "workspace-global",
            "workspace-evidence"
        ]
        for ws in workspaces:
            self.assertIn(f'id="{ws}"', html, f"Missing workspace container: {ws}")

        nav_targets = ["overview", "explorer", "risk", "impact", "weather", "global", "evidence"]
        for target in nav_targets:
            self.assertIn(f'data-workspace="{target}"', html, f"Missing nav button for {target}")

        # Scripts & stylesheets
        self.assertIn('/static/globe.gl.min.js', html)
        self.assertIn('/static/app.js', html)
        self.assertIn('/static/styles.css', html)

        # 3D Earth UI elements
        self.assertIn('id="globe-container"', html)
        self.assertIn('id="btnToggleGlobeRotation"', html)
        self.assertIn('id="btnResetGlobeView"', html)
        self.assertIn('id="globeCountrySearchInput"', html)
        self.assertIn('id="globeCountryCard"', html)
        self.assertIn('id="globeOsintPanel"', html)

        # Explorer GIS elements
        self.assertIn('id="explorer-map"', html)
        self.assertIn('id="gisLayerPanel"', html)
        self.assertIn('id="gisFloatingLegend"', html)
        self.assertIn('id="gisInspectionDrawer"', html)
        self.assertIn('name="basemapRadio"', html)

    def test_02_static_data_files_exist_and_valid(self):
        """Verify all static data files exist and have valid JSON content."""
        files_to_check = {
            "frontend/data/world_countries.geojson": 170, # min features
            "frontend/data/lower_godavari_study_area.geojson": 1,
            "frontend/data/lower_godavari_districts.geojson": 1,
            "frontend/data/lower_godavari_hydrorivers.geojson": 5
        }
        for path, min_features in files_to_check.items():
            self.assertTrue(os.path.exists(path), f"Missing file: {path}")
            self.assertGreater(os.path.getsize(path), 100, f"File too small: {path}")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data.get("type"), "FeatureCollection", f"{path} must be FeatureCollection")
            features = data.get("features", [])
            self.assertGreaterEqual(len(features), min_features, f"{path} has fewer than {min_features} features")

        # Specific check for world_countries.geojson containing India
        with open("frontend/data/world_countries.geojson", "r", encoding="utf-8") as f:
            world = json.load(f)
        india = next((f for f in world["features"] if (f["properties"].get("name") == "India" or f["properties"].get("NAME") == "India")), None)
        self.assertIsNotNone(india, "India must be present in world_countries.geojson")

    def test_03_satellite_overlays_and_globe_gl(self):
        """Verify all satellite PNG overlays and globe.gl script exist and are non-empty."""
        png_files = [
            "frontend/overlays/sentinel1_flood_candidates_track129.png",
            "frontend/overlays/sentinel1_permanent_water.png",
            "frontend/overlays/sentinel1_ambiguous_wetsoil.png"
        ]
        for p in png_files:
            self.assertTrue(os.path.exists(p), f"Missing overlay: {p}")
            self.assertGreater(os.path.getsize(p), 10000, f"Overlay too small: {p}")

        # Check globe.gl.min.js
        globe_script = "frontend/globe.gl.min.js"
        self.assertTrue(os.path.exists(globe_script), "globe.gl.min.js must exist")
        self.assertGreater(os.path.getsize(globe_script), 500000, "globe.gl.min.js size too small")

    def test_04_api_endpoint_contracts(self):
        """Verify endpoint functions return valid schemas without error."""
        # 1. Mandals GeoJSON
        m_resp = get_mandals_geojson()
        self.assertIsInstance(m_resp, dict)
        self.assertEqual(m_resp.get("type"), "FeatureCollection")
        self.assertEqual(len(m_resp.get("features", [])), 21, "Must contain exactly 21 mandals")

        # 2. Basin assessment
        basin_resp = endpoints.get_basin_risk_assessment()
        mandals = getattr(basin_resp, "mandals", None) or basin_resp.get("mandal_assessments")
        self.assertIsNotNone(mandals)
        self.assertEqual(len(mandals), 21, "Must assess all 21 mandals")

        # 3. Point assessment (Rajahmundry)
        pt_resp = endpoints.get_point_assessment_alias(lat=16.985, lon=81.780)
        self.assertTrue(pt_resp.get("is_in_study_area") or pt_resp.get("is_inside_study_area"))

        # 4. Mandal detail
        m_detail = endpoints.get_mandal_risk_alias("Rajahmundry")
        m_name = getattr(m_detail, "mandal_name", None) or m_detail.get("mandal_name")
        self.assertEqual(m_name, "Rajahmundry")

        # 5. Stations
        st_resp = endpoints.get_water_level_stations_alias()
        self.assertIsInstance(st_resp, dict)
        self.assertIn("stations", st_resp)
        self.assertEqual(len(st_resp["stations"]), 10)

        # 6. Facilities
        fac_resp = endpoints.get_facilities_alias(limit=2000)
        self.assertIsInstance(fac_resp, dict)
        self.assertIn("features", fac_resp)
        self.assertEqual(len(fac_resp["features"]), 1542, "Study area mapped facilities must equal 1,542")
        self.assertEqual(fac_resp.get("total_unclipped_facilities"), 1635, "Raw unclipped extraction must equal 1,635")

        # 7. Weather (graceful fallback when API key unconfigured)
        w_curr = endpoints.get_current_weather(lat=16.985, lon=81.780)
        self.assertIsInstance(w_curr, dict)
        self.assertTrue("temperature_c" in w_curr or w_curr.get("status") == "API_KEY_NOT_CONFIGURED")

        w_fore = endpoints.get_weather_forecast_alias(lat=16.985, lon=81.780)
        self.assertIsInstance(w_fore, dict)
        self.assertTrue("daily_forecasts" in w_fore or w_fore.get("status") == "API_KEY_NOT_CONFIGURED")

        # 8. Alerts
        alerts_resp = endpoints.get_alerts_feed_alias()
        self.assertIsInstance(alerts_resp, dict)
        self.assertIn("alerts", alerts_resp)

    def test_05_basemap_configuration(self):
        """Verify app.js uses Esri Dark Canvas as default and does not reference unauthenticated CARTO tiles."""
        with open("frontend/app.js", "r", encoding="utf-8") as f:
            app_js = f.read()

        # Check for Esri Dark Gray Canvas
        self.assertIn("World_Dark_Gray_Base", app_js)
        # Check for Esri Satellite
        self.assertIn("World_Imagery", app_js)
        # Check for OpenStreetMap
        self.assertIn("openstreetmap.org", app_js)
        # Verify cartocdn is not active
        self.assertNotIn("cartocdn.com", app_js)

    def test_06_scientific_reconciliation_figures(self):
        """Verify that authoritative Phase 4 figures and weights are preserved across frontend and backend services."""
        # 1. Verify frontend index.html display strings
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            html = f.read()

        # Baseline: 9,126,355
        self.assertIn("9,126,355", html)
        # Category breakdown
        self.assertIn("6,027,704", html)
        self.assertIn("2,225,020", html)
        self.assertIn("663,126", html)
        self.assertIn("210,505", html)
        # Elevated population: 8,252,724
        self.assertIn("8,252,724", html)
        # Elevated percentage: 90.43%
        self.assertIn("90.43%", html)
        # Mapped facilities: 1,542 study area, 1,146 health, 333 education, 63 shelters
        self.assertIn("1,542", html)
        self.assertIn("1,146", html)
        self.assertIn("333", html)
        self.assertIn("63", html)
        self.assertIn("1,467", html)
        # AHP weights: Elev 25%, Slope 25%, River 20%, Land 15%, Hazard 15%
        self.assertIn("Elev 25%", html)
        self.assertIn("Slope 25%", html)
        self.assertIn("River 20%", html)
        self.assertIn("Land 15%", html)
        self.assertIn("Hazard 15%", html)
        self.assertIn("CR = 0.0001", html)

        # 2. Cross-compare with actual backend production service
        basin_resp = endpoints.get_basin_risk_assessment()
        self.assertEqual(basin_resp.total_population, 9126355, "Backend baseline population must equal 9,126,355")
        self.assertEqual(basin_resp.total_potentially_exposed_population, 8252724, "Backend exposed population must equal 8,252,724")
        self.assertAlmostEqual(basin_resp.exposed_population_pct, 90.43, places=2)
        self.assertEqual(basin_resp.total_mapped_facilities, 1542, "Backend study area mapped facilities must equal 1,542")
        
        elevated_facilities = basin_resp.facilities_by_risk.get("Very High", 0) + basin_resp.facilities_by_risk.get("High", 0)
        self.assertEqual(elevated_facilities, 1467, "Backend elevated facilities must equal 1,467")
        
        # Check raw floating point precision matches authoritative Phase 4 baseline
        self.assertAlmostEqual(basin_resp.raw_total_population, 9126354.98, delta=0.5)
        self.assertAlmostEqual(basin_resp.raw_total_exposed_population, 8252723.55, delta=0.5)


if __name__ == "__main__":
    unittest.main()
