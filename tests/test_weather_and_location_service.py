"""
Unit Test Suite for Google Weather API & Location Intelligence Service.
Verifies location resolution across 21 study-area mandals and regional hubs,
safe handling of unconfigured API keys, in-memory TTL caching,
and satellite water extraction endpoints.
"""

import unittest
from backend.app.services.weather_service import WeatherService, PREDEFINED_HUBS
from backend.app.services.geographic_identification_service import GeographicIdentificationService
from backend.app.schemas.weather import UnifiedWeatherResponse, LocationSearchResult
from backend.app.api.endpoints import (
    get_unified_weather,
    get_current_weather,
    get_weather_alerts,
    search_locations,
    get_satellite_water_candidates_summary,
    get_satellite_water_candidates_geojson
)

class TestWeatherAndLocationService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geo_service = GeographicIdentificationService()
        cls.weather_service = WeatherService(geo_service=cls.geo_service)

    def test_unconfigured_api_key_graceful_handling(self):
        """When GOOGLE_WEATHER_API_KEY is not set or empty, service returns safe unconfigured payload."""
        svc = WeatherService(geo_service=self.geo_service)
        svc.api_key = ""  # Explicitly test unconfigured state
        
        res = svc.get_unified_weather(lat=16.9850, lon=81.7800)
        self.assertIsInstance(res, dict)
        self.assertFalse(res["is_available"])
        self.assertEqual(res["api_status"], "API_KEY_NOT_CONFIGURED")
        self.assertEqual(res["alerts_status"], "API_KEY_NOT_CONFIGURED")
        self.assertTrue(res["flood_model_supported"])
        self.assertIn("Exploratory", res["flood_model_note"])
        self.assertIn("Copernicus DSM", res["flood_model_note"])
        self.assertIn("IMD", res["alerts_source_info"])
        self.assertIn("CWC", res["alerts_source_info"])

    def test_in_memory_ttl_caching(self):
        """Verify in-memory caching respects TTL and stores/retrieves valid data."""
        svc = WeatherService(geo_service=self.geo_service)
        cache_key = "test_key_123"
        test_payload = {"temp": 28.5, "condition": "Cloudy"}

        svc._set_in_cache(cache_key, test_payload)
        cached = svc._get_from_cache(cache_key, ttl=10.0)
        self.assertEqual(cached, test_payload)

        # Expired TTL
        expired = svc._get_from_cache(cache_key, ttl=0.0)
        self.assertIsNone(expired)

    def test_location_search_mandal_exact_and_normalized(self):
        """Search should find mandals whether spelled as Kottapeta or Kothapeta."""
        # Exact GADM spelling
        results_exact = self.weather_service.search_locations("Kottapeta")
        self.assertGreater(len(results_exact), 0)
        top_exact = results_exact[0]
        self.assertIn(top_exact["mandal"], ["Kottapeta", "Kothapeta"])
        self.assertTrue(top_exact["within_study_area"])

        # Normalized transliteration
        results_norm = self.weather_service.search_locations("Kothapeta")
        self.assertGreater(len(results_norm), 0)
        top_norm = results_norm[0]
        self.assertIn(top_norm["mandal"], ["Kottapeta", "Kothapeta"])
        self.assertTrue(top_norm["within_study_area"])

        # Amalapuram
        res_amala = self.weather_service.search_locations("Amalapuram")
        self.assertGreater(len(res_amala), 0)
        self.assertEqual(res_amala[0]["mandal"], "Amalapuram")
        self.assertTrue(res_amala[0]["within_study_area"])

    def test_location_search_coordinate_input(self):
        """Search should recognize raw coordinate strings and correctly flag study basin membership."""
        # Inside Lower Godavari basin
        coords_inside = "16.942, 81.776"
        res_in = self.weather_service.search_locations(coords_inside)
        self.assertGreater(len(res_in), 0)
        self.assertIn("Coordinate", res_in[0]["admin_level"])
        self.assertTrue(res_in[0]["within_study_area"])
        self.assertAlmostEqual(res_in[0]["latitude"], 16.942, places=3)
        self.assertAlmostEqual(res_in[0]["longitude"], 81.776, places=3)

        # Outside study area (e.g. Hyderabad coordinates)
        coords_outside = "17.3850, 78.4867"
        res_out = self.weather_service.search_locations(coords_outside)
        self.assertGreater(len(res_out), 0)
        self.assertIn("Coordinate", res_out[0]["admin_level"])
        self.assertFalse(res_out[0]["within_study_area"])

    def test_location_search_regional_hubs(self):
        """Search should return major regional cities and indicate outside study area."""
        results = self.weather_service.search_locations("Hyderabad")
        self.assertGreater(len(results), 0)
        hyd = results[0]
        self.assertEqual(hyd["name"], "Hyderabad")
        self.assertFalse(hyd["within_study_area"])
        self.assertEqual(hyd["country"], "India")

    def test_satellite_water_candidates_endpoints(self):
        """Verify Sentinel-1 water candidates endpoints return validated datasets."""
        # Summary endpoint
        summary = get_satellite_water_candidates_summary()
        self.assertIn("Phase 3.3", summary.get("pipeline", ""))
        self.assertEqual(summary.get("target_date"), "2022-07-16")
        self.assertEqual(summary.get("track"), 129)
        self.assertGreater(summary.get("total_basin_potential_flood_km2", 0), 1000)
        self.assertEqual(len(summary.get("mandal_summaries", [])), 21)

        # GeoJSON endpoint
        geojson = get_satellite_water_candidates_geojson()
        self.assertEqual(geojson.get("type"), "FeatureCollection")
        features = geojson.get("features", [])
        self.assertGreater(len(features), 1000)
        sample = features[0]
        self.assertIn("geometry", sample)
        self.assertIn("properties", sample)
        self.assertIn("est_flood_ha", sample["properties"])

    def test_alert_safety_distinctions_and_sources(self):
        """Verify alert safety states: Active Alert, No Active Alert Reported, and API Error."""
        svc = WeatherService(geo_service=self.geo_service)
        svc.api_key = "dummy_test_key"

        # 1. No active alerts scenario
        svc.get_current_conditions = lambda lat, lon: {"is_available": True, "status": "OK", "data": {"temperature_c": 30.0, "condition": {"description": "Sunny"}}}
        svc.get_hourly_forecast = lambda lat, lon, hours=24: {"is_available": True, "status": "OK", "forecast": []}
        svc.get_daily_forecast = lambda lat, lon, days=10: {"is_available": True, "status": "OK", "forecast": []}
        svc.get_public_alerts = lambda lat, lon: {"is_available": True, "status": "OK", "alerts": []}

        res_no_alerts = svc.get_unified_weather(16.985, 81.78)
        self.assertEqual(res_no_alerts["alerts_status"], "NO_ACTIVE_ALERTS_REPORTED")
        self.assertIn("does not guarantee an absolute absence", res_no_alerts["alerts_source_info"])

        # 2. Active official alert scenario
        mock_alert = [{
            "id": "IMD-001",
            "headline": "Heavy Rainfall Warning",
            "severity": "SEVERE",
            "urgency": "IMMEDIATE",
            "certainty": "OBSERVED",
            "event": "Heavy Monsoon Downpour",
            "description": "Localized heavy rainfall expected across coastal Andhra.",
            "effective_time": "2026-11-02T12:00:00Z",
            "expire_time": "2026-11-02T23:59:59Z",
            "source_agency": "India Meteorological Department (IMD)"
        }]
        svc.get_public_alerts = lambda lat, lon: {"is_available": True, "status": "OK", "alerts": mock_alert}
        res_active = svc.get_unified_weather(16.985, 81.78)
        self.assertEqual(res_active["alerts_status"], "ACTIVE_OFFICIAL_ALERTS")
        self.assertEqual(len(res_active["alerts"]), 1)
        self.assertIn("India Meteorological Department (IMD)", res_active["alerts_source_info"])

        # 3. Alert API Error scenario
        svc.get_public_alerts = lambda lat, lon: {"is_available": False, "status": "UPSTREAM_TIMEOUT", "alerts": []}
        res_err = svc.get_unified_weather(16.985, 81.78)
        self.assertEqual(res_err["alerts_status"], "API_ERROR")
        self.assertIn("failed", res_err["alerts_source_info"])

    def test_product_terminology_scientific_boundaries(self):
        """Verify strict adherence to scientific terminology without misleading claims."""
        svc = WeatherService(geo_service=self.geo_service)
        svc.api_key = ""

        # Point inside Lower Godavari
        res_inside = svc.get_unified_weather(16.985, 81.78)
        self.assertTrue(res_inside["flood_model_supported"])
        self.assertIn("Exploratory flood susceptibility model", res_inside["flood_model_note"])
        self.assertIn("intrinsic terrain susceptibility, not confirmed flood predictions", res_inside["flood_model_note"])

        # Point outside Lower Godavari
        res_outside = svc.get_unified_weather(17.385, 78.486)
        self.assertFalse(res_outside["flood_model_supported"])
        self.assertIn("configured exclusively for the 21 Lower Godavari mandals", res_outside["flood_model_note"])

if __name__ == "__main__":
    unittest.main()
