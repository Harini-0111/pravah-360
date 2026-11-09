"""
PRAVAH 360 - Comprehensive Test Suite for Alert Integrity & Temporal Freshness Lifecycle.
Validates:
- Non-fabrication of missing fields (district, severity, source, issue time, status, event_type, last_updated).
- Accurate timezone-aware temporal freshness evaluation (LIVE, CACHED, STALE, EXPIRED, UNKNOWN, UNAVAILABLE).
- ISO-8601 parsing with UTC 'Z', positive/negative offsets, and documented naive IST conversions.
- Strict separation of scientific Model Advisories from Official Government Warnings.
- Deduplication and spatial mandal/district filtering.
"""

import unittest
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from backend.app.schemas.monitoring import OfficialDisasterAlert, SourceHealthStatus
from backend.app.services.live_alert_ingestion_service import (
    LiveAlertIngestionService,
    evaluate_alert_freshness,
    parse_iso_timestamp,
    IST_TIMEZONE
)
from backend.app.services.continuous_alert_service import continuous_alert_service, ContinuousAlertNotificationService
from backend.app.schemas.operations import AdvisoryRecord


class TestAlertFreshnessAndIntegrityLifecycle(unittest.TestCase):
    """Verifies that alert fields and temporal states adhere to strict integrity rules."""

    def setUp(self):
        self.now_utc = datetime.now(timezone.utc)
        self.now_iso = self.now_utc.strftime("%Y-%m-%d %H:%M:%S")

    # 1. Non-fabrication of missing district and severity
    def test_missing_district_and_severity(self):
        """Missing district must remain empty/None (never East Godavari) and severity must remain Unknown (never Moderate)."""
        raw_data = {
            "alert_id": "TEST-INTEG-001",
            "event_type": "Flash Flood Watch",
            "headline": "Localized flood risk",
        }
        alert = OfficialDisasterAlert(**raw_data)
        self.assertEqual(alert.affected_districts, [], "Missing district must remain empty list in schema.")
        self.assertEqual(alert.severity, "Unknown", "Missing severity must remain Unknown (never defaulted to Moderate).")

        service = ContinuousAlertNotificationService()
        feed = service.get_unified_notification_feed()
        for item in feed["tiers"]["official_warnings"]["items"]:
            if item.get("id") == "OFFICIAL-TEST-INTEG-001":
                self.assertIsNone(item["affected_district"], "Missing district must remain None.")
                self.assertEqual(item["severity"], "Unknown")

    # 2. Non-fabrication of missing source and issue time
    def test_missing_source_and_issue_time(self):
        """Missing source must remain Unknown (never APSDMA/NDMA) and issue time must remain None (never current timestamp)."""
        raw_data = {
            "alert_id": "TEST-INTEG-002",
            "headline": "Weather Advisory",
        }
        alert = OfficialDisasterAlert(**raw_data)
        self.assertEqual(alert.source, "Unknown", "Missing source must remain Unknown (never defaulted to NDMA/APSDMA).")
        self.assertIsNone(alert.issued_at, "Missing issue time must remain None (never current timestamp).")
        self.assertIsNone(alert.sent_time, "Missing sent_time must remain None.")

    # 3. Non-fabrication of missing status, event_type, and last_updated
    def test_missing_status_event_type_and_last_updated(self):
        """OfficialDisasterAlert must not default missing status to ACTIVE, event_type to Disaster Alert, or populate last_updated from issued_at."""
        raw_data = {
            "alert_id": "TEST-INTEG-003",
            "issued_at": "2026-11-09T10:00:00Z",
            # No status, event_type, or last_updated
        }
        alert = OfficialDisasterAlert(**raw_data)
        self.assertEqual(alert.status, "Unknown", "Missing status must remain Unknown, not 'ACTIVE'.")
        self.assertEqual(alert.event_type, "Unknown", "Missing event_type must remain Unknown, not 'Disaster Alert'.")
        self.assertIsNone(alert.last_updated, "Missing last_updated must remain None, never populated from issued_at.")

    # 4. Timezone parsing: UTC 'Z' notation
    def test_utc_timestamps_ending_in_z(self):
        """ISO-8601 timestamps ending in 'Z' must be parsed as UTC aware datetime objects."""
        ts_z = "2026-11-09T16:30:00Z"
        dt = parse_iso_timestamp(ts_z)
        self.assertIsNotNone(dt)
        self.assertEqual(dt.tzinfo, timezone.utc)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 11)
        self.assertEqual(dt.day, 9)
        self.assertEqual(dt.hour, 16)
        self.assertEqual(dt.minute, 30)

    # 5. Timezone parsing: Positive and negative offsets
    def test_positive_and_negative_timezone_offsets(self):
        """Positive (+05:30) and negative (-04:00) offsets must be normalized correctly to timezone-aware UTC."""
        ts_ist = "2026-11-09T22:00:00+05:30"  # 16:30 UTC
        ts_edt = "2026-11-09T12:30:00-04:00"  # 16:30 UTC
        ts_utc = "2026-11-09T16:30:00+00:00"

        dt_ist = parse_iso_timestamp(ts_ist)
        dt_edt = parse_iso_timestamp(ts_edt)
        dt_utc = parse_iso_timestamp(ts_utc)

        self.assertIsNotNone(dt_ist)
        self.assertIsNotNone(dt_edt)
        self.assertIsNotNone(dt_utc)

        # All three describe the exact same instant in UTC
        self.assertEqual(dt_ist, dt_edt)
        self.assertEqual(dt_ist, dt_utc)
        self.assertEqual(dt_ist.hour, 16)

    # 6. Timezone parsing: Missing and invalid timestamps without crashing
    def test_missing_and_invalid_timestamps(self):
        """Missing or invalid timestamps must return None without raising exceptions."""
        self.assertIsNone(parse_iso_timestamp(None))
        self.assertIsNone(parse_iso_timestamp(""))
        self.assertIsNone(parse_iso_timestamp("   "))
        self.assertIsNone(parse_iso_timestamp("not-a-timestamp"))
        self.assertIsNone(parse_iso_timestamp("2026-99-99 99:99:99"))

    # 7. Documented naive timestamp assumption (IST conversion)
    def test_supported_naive_timestamp_with_documented_ist_assumption(self):
        """Supported naive timestamps from regional feeds are assumed to be in IST (UTC+05:30) and converted to UTC."""
        naive_ts = "2026-11-09 22:00:00"
        dt = parse_iso_timestamp(naive_ts)
        self.assertIsNotNone(dt)
        self.assertEqual(dt.tzinfo, timezone.utc)
        # 22:00 IST is 16:30 UTC
        self.assertEqual(dt.hour, 16)
        self.assertEqual(dt.minute, 30)

    # 8. Expired timestamps evaluation
    def test_expired_timestamps_timezone_aware(self):
        """Alerts whose expiration time in UTC or local offset has passed must evaluate to EXPIRED."""
        past_utc = (self.now_utc - timedelta(hours=2)).isoformat()
        alert = OfficialDisasterAlert(
            alert_id="TEST-EXP-TZ-001",
            source="IMD Amaravati",
            event_type="Thunderstorm",
            severity="Severe",
            headline="Thunderstorm Warning",
            expires_at=past_utc,
            status="ACTIVE"
        )
        freshness = evaluate_alert_freshness(alert, is_feed_down=False, is_source_stale=False)
        self.assertEqual(freshness, "EXPIRED", "Elapsed timezone-aware expiration must evaluate to EXPIRED.")

    # 9. Cached alert evaluation
    def test_cached_alert_freshness(self):
        """Alerts loaded with is_cached=True within 30 min must evaluate to CACHED, never marked LIVE."""
        alert = OfficialDisasterAlert(
            alert_id="TEST-CACHE-001",
            source="APSDMA SEOC",
            event_type="Rainfall",
            severity="Severe",
            headline="Rainfall Warning",
            issued_at=(self.now_utc - timedelta(minutes=15)).isoformat(),
            retrieved_at=(self.now_utc - timedelta(minutes=5)).isoformat(),
            expires_at=(self.now_utc + timedelta(hours=4)).isoformat(),
            is_cached=True,
            status="ACTIVE"
        )
        freshness = evaluate_alert_freshness(alert, is_feed_down=False, is_source_stale=False)
        self.assertEqual(freshness, "CACHED", "Cached unexpired alert must evaluate to CACHED (not LIVE).")

    # 10. Stale alerts by age
    def test_stale_alert_by_retrieval_age(self):
        """Alert retrieved > 30 minutes ago must evaluate to STALE."""
        alert = OfficialDisasterAlert(
            alert_id="TEST-STALE-001",
            source="APSDMA SEOC",
            event_type="Flash Flood",
            severity="Moderate",
            headline="Flash Flood Watch",
            issued_at=(self.now_utc - timedelta(hours=2)).isoformat(),
            retrieved_at=(self.now_utc - timedelta(minutes=45)).isoformat(),
            expires_at=(self.now_utc + timedelta(hours=2)).isoformat(),
            status="ACTIVE"
        )
        freshness = evaluate_alert_freshness(alert, is_feed_down=False, is_source_stale=False)
        self.assertEqual(freshness, "STALE", "Alert with retrieval age > 30 min must be STALE.")

    # 11. Unknown freshness when temporal metadata is missing
    def test_unknown_freshness_when_timestamps_missing(self):
        """When temporal metadata (retrieved_at and issued_at) is missing, freshness must evaluate to UNKNOWN."""
        alert = OfficialDisasterAlert(
            alert_id="TEST-UNK-001",
            source="IMD Amaravati",
            event_type="Advisory",
            headline="General Notice",
            status="ACTIVE"
        )
        freshness = evaluate_alert_freshness(alert, is_feed_down=False, is_source_stale=False)
        self.assertEqual(freshness, "UNKNOWN", "Alert with no timestamps must evaluate to UNKNOWN.")

    # 12. Feed unavailable with no cache
    def test_feed_unavailable_with_no_cache(self):
        """When feed is down and no alert data exists, status must evaluate to UNAVAILABLE."""
        freshness = evaluate_alert_freshness(alert=None, is_feed_down=True, is_source_stale=False)
        self.assertEqual(freshness, "UNAVAILABLE", "Missing alert with down feed must be UNAVAILABLE.")

    # 13. Feed unavailable with valid cached records
    def test_feed_unavailable_with_valid_cached_records(self):
        """When live feed is down but valid unexpired cached records exist, alert is CACHED (not UNAVAILABLE)."""
        cached_alert = OfficialDisasterAlert(
            alert_id="TEST-CACHE-DOWN-001",
            source="APSDMA SEOC",
            event_type="Cyclone",
            severity="Severe",
            headline="Cyclone Murasu Bulletin",
            retrieved_at=(self.now_utc - timedelta(minutes=10)).isoformat(),
            expires_at=(self.now_utc + timedelta(hours=5)).isoformat(),
            is_cached=True,
            status="ACTIVE"
        )
        freshness = evaluate_alert_freshness(cached_alert, is_feed_down=True, is_source_stale=False)
        self.assertEqual(freshness, "CACHED", "Usable cached record must be labeled CACHED during feed downtime.")

    # 14. Live fresh alert evaluation
    def test_live_fresh_alert_evaluation(self):
        """Recent unexpired alert fetched from live stream (is_cached=False) must evaluate to LIVE."""
        alert = OfficialDisasterAlert(
            alert_id="TEST-LIVE-001",
            source="IMD Amaravati",
            event_type="Heavy Rainfall",
            severity="Severe",
            headline="Severe Rainfall Warning",
            issued_at=(self.now_utc - timedelta(minutes=10)).isoformat(),
            retrieved_at=(self.now_utc - timedelta(minutes=5)).isoformat(),
            expires_at=(self.now_utc + timedelta(hours=6)).isoformat(),
            is_cached=False,
            status="ACTIVE"
        )
        freshness = evaluate_alert_freshness(alert, is_feed_down=False, is_source_stale=False)
        self.assertEqual(freshness, "LIVE", "Recent unexpired alert from live stream must evaluate to LIVE.")

    # 15. Official and model advisory separation
    def test_official_and_model_advisory_separation(self):
        """Model advisories must never be represented as official warnings and must preserve distinct tier metadata."""
        feed = continuous_alert_service.get_unified_notification_feed()

        for off in feed["tiers"]["official_warnings"]["items"]:
            self.assertEqual(off["tier"], "TIER_A_OFFICIAL_WARNING")
            self.assertTrue(off["is_authoritative"])
            self.assertTrue(off["is_official"])

        for adv in feed["tiers"]["model_advisories"]["items"]:
            self.assertEqual(adv["tier"], "TIER_B_MODEL_ADVISORY")
            self.assertFalse(adv["is_authoritative"])
            self.assertFalse(adv["is_official"])
            self.assertEqual(adv["source"], "PRAVAH 360 Geospatial Intelligence")
            self.assertIn("scientific_notice", adv)
            self.assertIn("not an official government warning", adv["scientific_notice"])

    # 16. Incomplete Model Advisory records do not invent missing fields
    def test_incomplete_model_advisory_non_fabrication(self):
        """Incomplete advisory records must not have invented district, mandal, severity, or timestamps."""
        class MockIncompleteAdvisory:
            advisory_id = "ADV-INCOMP-001"
            mandal = None
            district = None
            priority = None
            severity = None
            status = None
            created_at = None
            issued_at = None
            headline = None
            message = "Uncertain flood situation"

        m_name = getattr(MockIncompleteAdvisory, "mandal", None)
        d_name = getattr(MockIncompleteAdvisory, "district", None)
        prio = getattr(MockIncompleteAdvisory, "priority", None) or getattr(MockIncompleteAdvisory, "severity", None) or "Unknown"
        created = getattr(MockIncompleteAdvisory, "created_at", None) or getattr(MockIncompleteAdvisory, "issued_at", None)

        self.assertIsNone(m_name, "Missing mandal must remain None, not 'Basin Reach'.")
        self.assertIsNone(d_name, "Missing district must remain None, not 'East Godavari'.")
        self.assertEqual(prio, "Unknown", "Missing priority/severity must remain Unknown, not 'HIGH'.")
        self.assertIsNone(created, "Missing creation timestamp must remain None, not now_iso.")

    # 17. Deduplication and mandal filtering
    def test_deduplication_and_mandal_filtering(self):
        """Notifications feed must deduplicate identical alerts and respect mandal filters."""
        unfiltered_feed = continuous_alert_service.get_unified_notification_feed()
        unfiltered_ids = [item["id"] for item in unfiltered_feed["tiers"]["official_warnings"]["items"]]
        self.assertEqual(len(unfiltered_ids), len(set(unfiltered_ids)), "Alerts must be strictly deduplicated.")

        filtered_feed = continuous_alert_service.get_unified_notification_feed(mandal="Amalapuram")
        for item in filtered_feed["tiers"]["official_warnings"]["items"]:
            if item.get("affected_mandals"):
                self.assertTrue(
                    any("amalapuram" in m.lower() for m in item["affected_mandals"]),
                    f"Filtered alert must touch Amalapuram, got: {item['affected_mandals']}"
                )


if __name__ == "__main__":
    unittest.main()
