"""
PRAVAH 360 - Continuous Alert & Notification Center Service
Separates alerts into three clear, authoritative tiers:
Tier A: OFFICIAL_WARNING (IMD, APSDMA, CWC, NDMA)
Tier B: MODEL_ADVISORY (PRAVAH 360 multi-criteria AHP & gauge threshold models)
Tier C: COMMUNITY_REPORT (Citizen-submitted, verified or under review)
Deduplicates alerts by fingerprint hash, tracks acknowledgments, and supports location filtering.
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.app.services.live_alert_ingestion_service import LiveAlertIngestionService
from backend.app.services.emergency_operations_service import EmergencyOperationsService
from backend.app.services.community_hazard_service import community_hazard_service

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "operations"))
ACK_FILE = os.path.join(DATA_DIR, "acknowledged_alerts.json")

class ContinuousAlertNotificationService:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(ACK_FILE):
            with open(ACK_FILE, "w", encoding="utf-8") as f:
                json.dump({"acknowledged_ids": []}, f, indent=2)

    def _get_acknowledged_ids(self) -> List[str]:
        if not os.path.exists(ACK_FILE):
            return []
        try:
            with open(ACK_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("acknowledged_ids", [])
        except Exception:
            return []

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "User") -> Dict[str, Any]:
        """Acknowledge an alert to mark it read in the notification center."""
        acks = self._get_acknowledged_ids()
        if alert_id not in acks:
            acks.append(alert_id)
            with open(ACK_FILE, "w", encoding="utf-8") as f:
                json.dump({"acknowledged_ids": acks, "last_updated": datetime.now().isoformat()}, f, indent=2)
        return {"success": True, "alert_id": alert_id, "acknowledged": True}

    def get_unified_notification_feed(self, mandal: Optional[str] = None, district: Optional[str] = None) -> Dict[str, Any]:
        """
        Gathers, deduplicates, and structures alerts into three distinct tiers:
        Tier A: Official Warnings
        Tier B: Model Advisories
        Tier C: Community Reports
        """
        acks = set(self._get_acknowledged_ids())
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Tier A: Official Warnings (IMD / APSDMA / CWC)
        official_warnings = []
        try:
            raw_alerts, health = LiveAlertIngestionService().get_cached_or_live_alerts()
            seen_hashes = set()
            for al in raw_alerts:
                # Deduplicate by (sender, event_type, district)
                fp = hashlib.md5(f"{al.sender}_{al.event_type}_{al.district}_{al.severity}".encode("utf-8")).hexdigest()[:8]
                if fp in seen_hashes:
                    continue
                seen_hashes.add(fp)

                # Filter by mandal if requested
                if mandal and al.affected_mandals:
                    if not any(mandal.lower() in m.lower() for m in al.affected_mandals):
                        continue

                official_warnings.append({
                    "id": f"OFFICIAL-{al.alert_id}",
                    "tier": "TIER_A_OFFICIAL_WARNING",
                    "badge_label": "Official Warning (అధికారిక హెచ్చరిక)",
                    "badge_class": "badge-official",
                    "source": al.sender,
                    "event_type": al.event_type,
                    "severity": al.severity,
                    "headline": al.headline,
                    "description": al.description,
                    "instruction": al.instruction,
                    "affected_district": al.district,
                    "affected_mandals": al.affected_mandals,
                    "issued_at": al.issued_at,
                    "expires_at": al.expires_at,
                    "is_acknowledged": f"OFFICIAL-{al.alert_id}" in acks,
                    "is_authoritative": True
                })
        except Exception as e:
            logger.warning(f"Official alerts retrieval notice: {e}")

        # 2. Tier B: Model Advisories (PRAVAH 360 Scientific Model Outputs)
        model_advisories = []
        try:
            raw_advs = EmergencyOperationsService().list_advisories(mandal=mandal, district=district)
            for adv in raw_advs:
                model_advisories.append({
                    "id": f"MODEL-{adv.advisory_id}",
                    "tier": "TIER_B_MODEL_ADVISORY",
                    "badge_label": "Model Advisory (ఏఐ నమూనా సూచన)",
                    "badge_class": "badge-model",
                    "source": "PRAVAH 360 Geospatial Intelligence",
                    "event_type": adv.hazard_type,
                    "severity": adv.severity.capitalize(),
                    "headline": f"{adv.severity.upper()} {adv.hazard_type} Advisory for {adv.mandal}",
                    "description": adv.summary,
                    "instruction": adv.recommended_action,
                    "affected_district": adv.district,
                    "affected_mandals": [adv.mandal],
                    "issued_at": adv.issued_at,
                    "expires_at": None,
                    "is_acknowledged": f"MODEL-{adv.advisory_id}" in acks,
                    "is_authoritative": False,
                    "scientific_notice": "Generated by multi-criteria AHP & radar susceptibility modeling. Provides decision support; not an official government warning."
                })
        except Exception as e:
            logger.warning(f"Model advisories retrieval notice: {e}")

        # 3. Tier C: Community Reports (Citizen-submitted & admin-verified)
        community_reports = []
        try:
            raw_hzds = community_hazard_service.list_reports(mandal=mandal)
            for hzd in raw_hzds:
                community_reports.append({
                    "id": f"COMMUNITY-{hzd.report_id}",
                    "tier": "TIER_C_COMMUNITY_REPORT",
                    "badge_label": f"Community Hazard: {hzd.status.replace('_', ' ').title()}",
                    "badge_class": "badge-community",
                    "source": f"Citizen Field Report ({hzd.reporter_name_redacted})",
                    "event_type": hzd.category,
                    "severity": "High" if "breach" in hzd.category.lower() or "flood" in hzd.category.lower() else "Medium",
                    "headline": f"{hzd.category} observed in {hzd.mandal}",
                    "description": hzd.description,
                    "instruction": hzd.reviewer_notes or "Field observation under administration review.",
                    "affected_district": hzd.district,
                    "affected_mandals": [hzd.mandal],
                    "status": hzd.status,
                    "issued_at": hzd.created_at,
                    "photo_url": hzd.photo_url,
                    "has_photo": hzd.has_photo,
                    "is_acknowledged": f"COMMUNITY-{hzd.report_id}" in acks,
                    "is_authoritative": False,
                    "community_notice": "Citizen ground observation. Verified reports are escalated to ERT rescue operations."
                })
        except Exception as e:
            logger.warning(f"Community hazards retrieval notice: {e}")

        # Compute unread count
        total_items = official_warnings + model_advisories + community_reports
        unread_count = sum(1 for item in total_items if not item["is_acknowledged"])

        return {
            "last_polled_iso": now_iso,
            "filter_mandal": mandal,
            "filter_district": district,
            "total_active_notifications": len(total_items),
            "unread_count": unread_count,
            "tiers": {
                "official_warnings": {
                    "count": len(official_warnings),
                    "description": "Authoritative alerts issued directly by IMD, APSDMA, CWC, or NDMA.",
                    "items": official_warnings
                },
                "model_advisories": {
                    "count": len(model_advisories),
                    "description": "Scientific decision support advisories computed by PRAVAH 360 models.",
                    "items": model_advisories
                },
                "community_reports": {
                    "count": len(community_reports),
                    "description": "Citizen observations of rising water, breaches, and localized hazards.",
                    "items": community_reports
                }
            },
            "disclaimer": "CRITICAL DISCLOSURE: Official warnings originate from state/national authorities. Model advisories and community reports provide supplemental decision intelligence and are NEVER substituted for official government warnings."
        }

continuous_alert_service = ContinuousAlertNotificationService()
