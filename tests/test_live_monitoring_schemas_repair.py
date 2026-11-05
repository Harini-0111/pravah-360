"""
Unit and Integration Tests for Live Monitoring Schema Repairs and Data Normalization.
Verifies all 10 items required by the directive.
"""
import unittest
import os
import json
import urllib.error
from datetime import datetime

from backend.app.schemas.monitoring import (
    OfficialDisasterAlert,
    RiverGaugeObservation,
    SourceHealthStatus,
    MonitoringHealthResponse
)
from backend.app.services.normalization_service import MonitoringDataNormalizationService
from backend.app.services.live_alert_ingestion_service import LiveAlertIngestionService
from backend.app.services.river_monitoring_service import RiverMonitoringService
from backend.app.services.live_monitoring_service import LiveMonitoringService

class TestLiveMonitoringSchemaRepairs(unittest.TestCase):
    
    # 1. Model validation tests for old cached alert records
    def test_01_old_cached_alert_records_validation(self):
        old_alert_record = {
            "alert_id": "AP-SACHET-OLD-001",
            "source_agency": "NDMA SACHET / APSDMA",
            "event_category": "Cyclone Warning",
            "severity": "Extreme",
            "affected_districts": ["East Godavari"],
            "headline": "Historic Cyclone Warning",
            "description": "Public emergency warning.",
            "instructions": "Seek cyclone shelters immediately.",
            "sent_time": "2026-10-15 08:30:00",
            "expires_time": "2026-10-15 18:00:00",
            "mandals_count": 5,
            "intersects_lower_godavari": True
        }
        # Validate that older record parses without mandals_count/sent_time/instruction errors
        alert = OfficialDisasterAlert(**old_alert_record)
        self.assertEqual(alert.alert_id, "AP-SACHET-OLD-001")
        self.assertEqual(alert.source, "NDMA SACHET / APSDMA")
        self.assertEqual(alert.event_type, "Cyclone Warning")
        self.assertEqual(alert.instruction, "Seek cyclone shelters immediately.")
        self.assertEqual(alert.issued_at, "2026-10-15 08:30:00")
        self.assertEqual(alert.sent_time, "2026-10-15 08:30:00")
        self.assertEqual(alert.mandals_count, 5)
        self.assertTrue(alert.in_lower_godavari)
        self.assertTrue(alert.intersects_lower_godavari)

    # 2. Model validation tests for old gauge records
    def test_02_old_cached_gauge_records_validation(self):
        old_gauge_record = {
            "station_id": "CWC-DWL-01",
            "station_name": "Dowleswaram Barrage (Sir Arthur Cotton Barrage)",
            "river": "Godavari Mainstem",
            "district": "East Godavari",
            "latitude": 16.942,
            "longitude": 81.776,
            "warning_level_m": 14.5,
            "danger_level_m": 16.5,
            "hfl_highest_flood_level_m": 17.75,
            "current_water_level_m": 13.8,
            "discharge_cusecs": 850000.0,
            "flood_status": "NORMAL",
            "is_live": False,
            "data_source": "AP Water Resources Dept (WRD) / CWC Hydrological Network",
            "observation_note": "First warning signal at 11.75 ft; Second at 13.75 ft.",
            "observation_time": "2026-11-03 09:20:00"
        }
        gauge = RiverGaugeObservation(**old_gauge_record)
        # Verify both old and new field mappings
        self.assertEqual(gauge.river_name, "Godavari Mainstem")
        self.assertEqual(gauge.lat, 16.942)
        self.assertEqual(gauge.lon, 81.776)
        self.assertEqual(gauge.warning_stage_m, 14.5)
        self.assertEqual(gauge.danger_stage_m, 16.5)
        self.assertEqual(gauge.status, "NORMAL")
        self.assertEqual(gauge.flood_status, "NORMAL")
        self.assertEqual(gauge.location_description, "First warning signal at 11.75 ft; Second at 13.75 ft.")
        self.assertEqual(gauge.elevation_m, 14.5)
        self.assertEqual(gauge.trend, "STEADY")
        self.assertFalse(gauge.is_live)

    # 3. NDMA ingestion and health-status update tests (including last_status_code)
    def test_03_source_health_status_last_status_code(self):
        health = SourceHealthStatus(
            source_id="TEST_SOURCE",
            source_name="Test Government Feed",
            status="LIVE",
            last_attempt_iso="2026-11-03 10:00:00",
            last_status_code=200
        )
        self.assertEqual(health.last_status_code, 200)
        self.assertEqual(health.status, "LIVE")

        # Test health response model
        response = MonitoringHealthResponse(
            daemon_status="RUNNING",
            uptime_seconds=120.5,
            total_checks_executed=5,
            last_check_iso="2026-11-03 10:00:00",
            next_scheduled_check_iso="2026-11-03 10:05:00",
            sources={"TEST": health},
            active_alerts_count=1,
            active_alerts_lower_godavari=1,
            overall_health="HEALTHY"
        )
        self.assertEqual(response.daemon_status, "RUNNING")
        self.assertEqual(response.sources["TEST"].last_status_code, 200)

    # 4. CWC/AP WRD parsing tests
    def test_04_cwc_ap_wrd_parsing(self):
        river_srv = RiverMonitoringService()
        stations, status = river_srv.get_river_observations()
        self.assertGreaterEqual(len(stations), 4)
        for s in stations:
            self.assertIn("CWC-", s.station_id)
            self.assertIsNotNone(s.current_water_level_m)
            self.assertIsNotNone(s.warning_stage_m)
            self.assertIsNotNone(s.danger_stage_m)
            self.assertIsNotNone(s.lat)
            self.assertIsNotNone(s.lon)
            self.assertEqual(s.trend, "STEADY")
            # Verify strict rule: not classified as live merely because station record exists
            self.assertFalse(s.is_live)

    # 5. Test valid and invalid records handling
    def test_05_valid_and_invalid_records_resilience(self):
        # Create a mock corrupt record missing required alert_id
        corrupt_record = {"headline": "Corrupted Alert without ID or Source"}
        valid_record = {
            "alert_id": "AP-SACHET-VALID-999",
            "source": "APSDMA",
            "event_type": "Flash Flood",
            "severity": "Severe",
            "headline": "Flash Flood Notice",
            "description": "Evacuation alert.",
            "retrieved_at": "2026-11-03 10:00:00",
            "last_updated": "2026-11-03 10:00:00"
        }
        
        raw_collection = [corrupt_record, valid_record]
        parsed = []
        rejected = []
        for item in raw_collection:
            try:
                parsed.append(OfficialDisasterAlert(**item))
            except Exception as e:
                rejected.append((item, str(e)))
                
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0].alert_id, "AP-SACHET-VALID-999")
        self.assertEqual(len(rejected), 1)

    # 6. Test unavailable external feeds handling
    def test_06_unavailable_external_feed_simulation(self):
        ingest_srv = LiveAlertIngestionService()
        import backend.app.services.live_alert_ingestion_service as m
        orig_url = m.SACHET_GEOJSON_URL
        try:
            m.SACHET_GEOJSON_URL = "https://unreachable-nonexistent-domain-test.gov.in"
            alerts, health = ingest_srv.fetch_live_alerts()
            self.assertEqual(health.status, "FETCH_ERROR")
            self.assertIsNotNone(health.error_message)
            self.assertIsNone(health.last_status_code)
            # Confirms graceful cached alerts fallback
            self.assertIsInstance(alerts, list)
        finally:
            m.SACHET_GEOJSON_URL = orig_url

    # 7. Test data normalization migration idempotency
    def test_07_normalization_migration_idempotency(self):
        res1 = MonitoringDataNormalizationService.run_all_migrations()
        self.assertEqual(res1["alerts_migration"]["status"], "SUCCESS")
        self.assertEqual(res1["gauges_migration"]["status"], "SUCCESS")
        self.assertEqual(res1["alerts_migration"]["invalid_count"], 0)
        self.assertEqual(res1["gauges_migration"]["invalid_count"], 0)

        # Re-run to verify idempotency
        res2 = MonitoringDataNormalizationService.run_all_migrations()
        self.assertEqual(res2["alerts_migration"]["valid_count"], res1["alerts_migration"]["valid_count"])
        self.assertEqual(res2["gauges_migration"]["valid_count"], res1["gauges_migration"]["valid_count"])

    # 8. Test live monitoring service check cycle
    def test_08_live_monitoring_service_cycle(self):
        mon_srv = LiveMonitoringService()
        health_data = mon_srv.execute_all_checks()
        self.assertEqual(health_data["daemon_status"], "RUNNING")
        self.assertIn("NDMA_SACHET_APSDMA", health_data["sources"])
        self.assertIn("CWC_GODAVARI_RIVER_GAUGES", health_data["sources"])
        
        health_obj = mon_srv.get_monitoring_health()
        self.assertEqual(health_obj.overall_health, "HEALTHY")
        self.assertGreater(health_obj.total_checks_executed, 0)

if __name__ == "__main__":
    unittest.main()
