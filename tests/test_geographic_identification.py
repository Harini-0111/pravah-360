"""
Comprehensive Test Suite for Geographic Area Identification & Human-Readable Flood Alerts
Phase 2 Verification Suite
"""

import unittest
from typing import List
from fastapi import HTTPException

from backend.app.services.geographic_identification_service import (
    GeographicIdentificationService
)
from backend.app.schemas.geographic import (
    CoordinateInput,
    BatchCoordinateInput,
    GeographicIdentification
)
from backend.app.schemas.flood_risk import FloodMarker, FloodAlert, FloodImpactSummary
from backend.app.api import endpoints


class TestGeographicIdentificationService(unittest.TestCase):
    """Unit tests for GeographicIdentificationService spatial queries and boundaries."""

    @classmethod
    def setUpClass(cls):
        cls.service = GeographicIdentificationService()

    def test_service_initialization(self):
        """Verify mandal and district polygons loaded properly."""
        self.assertGreater(len(self.service.mandals), 0, "Mandal polygons should be loaded.")
        self.assertGreater(len(self.service.districts), 0, "District polygons should be loaded.")
        self.assertIsNotNone(self.service.mandal_tree, "Mandal spatial index must be built.")
        self.assertIsNotNone(self.service.district_tree, "District spatial index must be built.")

    def test_known_mandals_and_districts(self):
        """Test known coordinates inside target study mandals."""
        # 1. Rajahmundry / Dowleswaram (East Godavari)
        res_rjy = self.service.identify_point(17.0005, 81.8040)
        self.assertIn("Rajahmundry", res_rjy["mandal"])
        self.assertEqual(res_rjy["district"], "East Godavari")
        self.assertEqual(res_rjy["state"], "Andhra Pradesh")
        self.assertTrue(res_rjy["within_study_area"])

        # 2. Kovvur (West Godavari) - 17.0140, 81.7300 (West bank)
        res_kov = self.service.identify_point(17.0140, 81.7300)
        self.assertEqual(res_kov["mandal"], "Kovvur")
        self.assertEqual(res_kov["district"], "West Godavari")
        self.assertEqual(res_kov["state"], "Andhra Pradesh")
        self.assertTrue(res_kov["within_study_area"])

        # 3. Amalapuram (East Godavari / Konaseema)
        res_ama = self.service.identify_point(16.5787, 82.0061)
        self.assertEqual(res_ama["mandal"], "Amalapuram")
        self.assertEqual(res_ama["district"], "East Godavari")
        self.assertEqual(res_ama["state"], "Andhra Pradesh")
        self.assertTrue(res_ama["within_study_area"])

        # 4. Polavaram (West Godavari / Eluru / Alluri Sitharama Raju)
        res_pol = self.service.identify_point(17.2500, 81.6333)
        self.assertEqual(res_pol["mandal"], "Polavaram")
        self.assertEqual(res_pol["district"], "West Godavari")
        self.assertEqual(res_pol["state"], "Andhra Pradesh")
        self.assertTrue(res_pol["within_study_area"])

        # 5. Razole (East Godavari / Konaseema delta)
        res_raz = self.service.identify_point(16.4833, 81.8333)
        self.assertEqual(res_raz["mandal"], "Razole")
        self.assertEqual(res_raz["district"], "East Godavari")
        self.assertEqual(res_raz["state"], "Andhra Pradesh")
        self.assertTrue(res_raz["within_study_area"])

    def test_strict_village_unavailability_policy(self):
        """Confirm village is strictly None and policy note is provided without fabricating names."""
        test_points = [
            (17.0005, 81.8040),
            (17.0140, 81.7300),
            (16.5787, 82.0061),
            (17.2500, 81.6333),
            (16.4833, 81.8333)
        ]
        for lat, lon in test_points:
            res = self.service.identify_point(lat, lon)
            self.assertIsNone(res["village"], "Village must strictly be None as cadastral data is unavailable.")
            self.assertIn("unavailable", res["village_status"].lower())
            self.assertIn("mandal", res["precision_level"].lower())

    def test_raw_coordinates_preservation(self):
        """Confirm original latitude and longitude are preserved exactly."""
        lat, lon = 16.942123, 81.776456
        res = self.service.identify_point(lat, lon)
        self.assertEqual(res["latitude"], lat)
        self.assertEqual(res["longitude"], lon)

    def test_outside_study_area(self):
        """Test points clearly outside the Godavari study area."""
        # Deep in Bay of Bengal (Ocean)
        res_ocean = self.service.identify_point(15.0, 84.0)
        self.assertFalse(res_ocean["within_study_area"])
        self.assertIsNone(res_ocean["mandal"])
        self.assertIsNone(res_ocean["district"])

        # Hyderabad (Telangana - outside AP GADM boundaries)
        res_hyd = self.service.identify_point(17.3850, 78.4867)
        self.assertFalse(res_hyd["within_study_area"])
        self.assertIsNone(res_hyd["mandal"])

    def test_invalid_coordinates(self):
        """Test out of range coordinates are captured safely with is_valid_coordinate=False."""
        # Latitude > 90
        res_high_lat = self.service.identify_point(91.0, 81.0)
        self.assertFalse(res_high_lat["is_valid_coordinate"])
        self.assertIsNotNone(res_high_lat["error"])

        # Latitude < -90
        res_low_lat = self.service.identify_point(-95.0, 81.0)
        self.assertFalse(res_low_lat["is_valid_coordinate"])

        # Longitude > 180
        res_high_lon = self.service.identify_point(17.0, 185.0)
        self.assertFalse(res_high_lon["is_valid_coordinate"])

        # None / string input
        res_none = self.service.identify_point(None, 81.0)
        self.assertFalse(res_none["is_valid_coordinate"])

    def test_batch_identification(self):
        """Verify batch point queries produce consistent results."""
        points = [
            {"lat": 17.0005, "lon": 81.8040},
            {"lat": 17.0140, "lon": 81.7300},
            {"lat": 16.5787, "lon": 82.0061},
            {"lat": 15.0, "lon": 84.0}
        ]
        batch_results = self.service.identify_points(points)
        self.assertEqual(len(batch_results), 4)

        for i, pt in enumerate(points):
            single_res = self.service.identify_point(pt["lat"], pt["lon"])
            self.assertEqual(batch_results[i]["mandal"], single_res["mandal"])
            self.assertEqual(batch_results[i]["district"], single_res["district"])
            self.assertEqual(batch_results[i]["geographic_identification"]["within_study_area"], single_res["within_study_area"])

    def test_caching(self):
        """Verify internal LRU cache retains and delivers exact results."""
        res1 = self.service.identify_point(16.942, 81.776)
        res2 = self.service.identify_point(16.942, 81.776)
        self.assertEqual(res1, res2)


class TestAPIEndpoints(unittest.TestCase):
    """Unit tests for API endpoints in backend.app.api.endpoints."""

    def test_endpoint_identify_point_get(self):
        """Test GET /api/v1/geographic/identify-point."""
        res = endpoints.identify_point_get(lat=17.0005, lon=81.8040)
        self.assertIsInstance(res, dict)
        self.assertIn("Rajahmundry", res["mandal"])
        self.assertEqual(res["district"], "East Godavari")
        self.assertEqual(res["state"], "Andhra Pradesh")
        self.assertIsNone(res["village"])
        self.assertEqual(res["latitude"], 17.0005)
        self.assertEqual(res["longitude"], 81.8040)
        self.assertIn("Rajamahendravaram", res["formatted_location"])

    def test_endpoint_identify_point_post(self):
        """Test POST /api/v1/geographic/identify-point."""
        coord = CoordinateInput(latitude=17.0140, longitude=81.7300)
        res = endpoints.identify_point_endpoint(coord)
        self.assertIsInstance(res, dict)
        self.assertEqual(res["mandal"], "Kovvur")
        self.assertEqual(res["district"], "West Godavari")

    def test_endpoint_identify_point_invalid_coords(self):
        """Test GET /api/v1/geographic/identify-point with out-of-range latitude raises HTTP 400."""
        with self.assertRaises(HTTPException) as ctx:
            endpoints.identify_point_get(lat=95.0, lon=81.8040)
        self.assertEqual(ctx.exception.status_code, 400)

    def test_endpoint_identify_batch(self):
        """Test POST /api/v1/geographic/identify-batch."""
        req = BatchCoordinateInput(
            points=[
                CoordinateInput(latitude=17.0005, longitude=81.8040),
                CoordinateInput(latitude=17.0140, longitude=81.7300),
                CoordinateInput(latitude=16.5787, longitude=82.0061)
            ]
        )
        res = endpoints.identify_batch_endpoint(req)
        self.assertEqual(len(res), 3)
        self.assertIn("Rajahmundry", res[0]["mandal"])
        self.assertEqual(res[1]["mandal"], "Kovvur")
        self.assertEqual(res[2]["mandal"], "Amalapuram")

    def test_endpoint_flood_risk_markers(self):
        """Test GET /api/v1/flood-risk/markers."""
        markers = endpoints.get_flood_risk_markers()
        self.assertGreater(len(markers), 0)
        for m in markers:
            self.assertIsInstance(m, FloodMarker)
            self.assertIsNotNone(m.geographic_info)
            self.assertIsNotNone(m.mandal)
            self.assertIsNotNone(m.district)
            self.assertIsNone(m.geographic_info.village)
            # Coordinates preserved
            self.assertIsInstance(m.latitude, float)
            self.assertIsInstance(m.longitude, float)
            self.assertIn(m.risk_level, ["Critical", "High", "Moderate", "Low"])

    def test_endpoint_flood_risk_alerts(self):
        """Test GET /api/v1/flood-risk/alerts."""
        alerts = endpoints.get_flood_alerts()
        self.assertGreater(len(alerts), 0)
        for a in alerts:
            self.assertIsInstance(a, FloodAlert)
            self.assertIsNotNone(a.human_readable_location)
            # Ensure human-readable location contains Mandal & District
            self.assertIn("Mandal", a.human_readable_location)
            self.assertIn("District", a.human_readable_location)
            self.assertIsNotNone(a.action_recommended)

    def test_endpoint_flood_risk_summary(self):
        """Test GET /api/v1/flood-risk/summary."""
        summary = endpoints.get_flood_summary()
        self.assertIsInstance(summary, FloodImpactSummary)
        self.assertGreater(summary.total_monitored_points, 0)
        self.assertGreater(summary.critical_risk_count, 0)
        self.assertIn("East Godavari", summary.districts_impacted)
        self.assertIn("West Godavari", summary.districts_impacted)
        self.assertIn("Kovvur", summary.mandals_affected)


if __name__ == "__main__":
    unittest.main()
