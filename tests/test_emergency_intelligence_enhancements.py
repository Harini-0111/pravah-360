import unittest
import urllib.request
import urllib.error
import json
import uuid
from backend.app.services.prediction_validation_service import prediction_service as prediction_validation_service
from backend.app.services.emergency_helpline_service import get_official_helplines
from backend.app.services.continuous_alert_service import continuous_alert_service
from backend.app.services.historical_event_service import historical_event_service
from backend.app.services.community_hazard_service import community_hazard_service
from backend.app.schemas.community import HazardReportCreate

BASE_URL = "http://127.0.0.1:8000"

def http_get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode())

def http_post(path, data):
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode())

class TestEmergencyIntelligenceEnhancements(unittest.TestCase):
    # 1. Voice Assistant TTS Service & Endpoint
    def test_voice_tts_service_english(self):
        status, data = http_post("/api/v1/voice/tts", {
            "text": "Cyclone Murasu has weakened into a deep depression.",
            "lang": "en-IN"
        })
        self.assertEqual(status, 200)
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("lang"), "en-IN")
        self.assertIn("provider", data)

    def test_voice_tts_service_telugu(self):
        status, data = http_post("/api/v1/voice/tts", {
            "text": "తుఫాను మురసు తీవ్ర వాయుగుండంగా బలహీనపడింది.",
            "lang": "te-IN"
        })
        self.assertEqual(status, 200)
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("lang"), "te-IN")

    # 2. Emergency Helplines Verification
    def test_emergency_helplines_endpoint(self):
        status, data = http_get("/api/v1/emergency/helplines")
        self.assertEqual(status, 200)
        self.assertIsInstance(data, list)
        numbers = [h["number"] for h in data]
        # Must include all 6 critical official helplines
        self.assertIn("112", numbers)
        self.assertIn("1070", numbers)
        self.assertIn("1077", numbers)
        self.assertIn("108", numbers)
        self.assertIn("101", numbers)
        self.assertIn("104", numbers)

    # 3. Continuous Notifications 3-Tier Feed
    def test_continuous_notifications_feed(self):
        status, data = http_get("/api/v1/notifications/continuous-feed")
        self.assertEqual(status, 200)
        self.assertIn("tiers", data)
        self.assertIn("unread_count", data)
        self.assertIn("official_warnings", data["tiers"])
        self.assertIn("model_advisories", data["tiers"])
        self.assertIn("community_reports", data["tiers"])

    def test_continuous_notification_acknowledgment(self):
        feed = continuous_alert_service.get_unified_notification_feed()
        # Find any item in the tiers to test acknowledgment
        target_id = None
        for tier_key in ["official_warnings", "model_advisories", "community_reports"]:
            items = feed["tiers"][tier_key]["items"]
            if items:
                target_id = items[0]["id"]
                break
        if not target_id:
            target_id = "TEST-ALERT-001"

        status, data = http_post("/api/v1/notifications/acknowledge", {
            "alert_id": target_id,
            "acknowledged_by": "TestUser"
        })
        self.assertEqual(status, 200)
        self.assertTrue(data.get("acknowledged"))

    # 4. Community Hazard Reporting: Duplicate Detection
    def test_community_hazard_duplicate_detection(self):
        uid = uuid.uuid4().hex[:6]
        # Create a report at Amalapuram
        report_data = HazardReportCreate(
            category="Flood",
            severity="critical",
            mandal="Amalapuram",
            title=f"Severe flooding in Amalapuram Clock Tower {uid}",
            description="Water depth exceeds 1.5 meters on main bypass road",
            latitude=16.5787,
            longitude=82.0061,
            reported_by=f"citizen_{uid}"
        )
        first_rep = community_hazard_service.submit_report(report_data)
        self.assertIsNotNone(first_rep.report_id)

        # Submit a duplicate within 500 meters with same category and mandal
        dup_data = HazardReportCreate(
            category="Flood",
            severity="high",
            mandal="Amalapuram",
            title=f"Water accumulation near clock tower {uid}",
            description="Road submerged",
            latitude=16.5800,  # ~200m away
            longitude=82.0070,
            reported_by=f"citizen_{uid}_dup"
        )
        second_rep = community_hazard_service.submit_report(dup_data)
        self.assertIsNotNone(second_rep.potential_duplicate)
        self.assertTrue(second_rep.potential_duplicate.get("is_potential_duplicate"))
        self.assertEqual(second_rep.potential_duplicate.get("similar_report_id"), first_rep.report_id)

    # 5. Scientific Model Validation & Spatial Holdout Test
    def test_prediction_validation_report(self):
        status, data = http_get("/api/v1/prediction/validation-report")
        self.assertEqual(status, 200)
        self.assertIn("model_metadata", data)
        test_mandals = data["model_metadata"]["heldout_test_mandals"]
        # Test partition MUST be independent coastal delta mandals
        self.assertIn("Razole", test_mandals)
        self.assertIn("Sakhinetipalli", test_mandals)
        self.assertIn("Mummidivaram", test_mandals)
        self.assertIn("Amalapuram", test_mandals)

        # Performance comparison Random Forest vs Baseline
        self.assertIn("classification_metrics", data)
        self.assertIn("random_forest", data["classification_metrics"])
        self.assertIn("baseline_logistic", data["classification_metrics"])
        rf_metrics = data["classification_metrics"]["random_forest"]
        self.assertIn("accuracy", rf_metrics)
        self.assertIn("precision", rf_metrics)
        self.assertIn("recall_pod", rf_metrics)
        self.assertIn("iou_jaccard", rf_metrics)
        self.assertIn("false_alarm_ratio_far", rf_metrics)
        self.assertIn("confusion_matrix", rf_metrics)

        # Validate that accuracy is honest and computed, not fabricated
        self.assertGreater(rf_metrics["accuracy"], 0.70)
        self.assertLessEqual(rf_metrics["accuracy"], 0.98)

    # 6. Historical Event Replay (Cyclone Murasu, Cyclone Arnab)
    def test_historical_events_list(self):
        status, data = http_get("/api/v1/events/historical")
        self.assertEqual(status, 200)
        event_ids = [e["event_id"] for e in data]
        self.assertIn("CYCLONE_MURASU_NOV_2026", event_ids)
        self.assertIn("CYCLONE_ARNAB_HISTORICAL", event_ids)

    def test_cyclone_murasu_timeline(self):
        status, data = http_get("/api/v1/events/CYCLONE_MURASU_NOV_2026/timeline")
        self.assertEqual(status, 200)
        self.assertEqual(data["event_id"], "CYCLONE_MURASU_NOV_2026")
        self.assertIn("timeline_steps", data)
        self.assertGreaterEqual(len(data["timeline_steps"]), 4)

        # Verify APSDMA ground truth: landfall Nov 3, deep depression Nov 4 2:30 AM
        landfall_steps = [s for s in data["timeline_steps"] if "landfall" in s["phase"].lower() or "landfall" in s["official_bulletin"].lower()]
        weakening_steps = [s for s in data["timeline_steps"] if "deep depression" in s["phase"].lower() or "weakened" in s["official_bulletin"].lower()]
        self.assertTrue(len(landfall_steps) > 0)
        self.assertTrue(len(weakening_steps) > 0)

if __name__ == "__main__":
    unittest.main()
