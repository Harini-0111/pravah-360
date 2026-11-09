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
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from backend.app.services.live_alert_ingestion_service import LiveAlertIngestionService, evaluate_alert_freshness, parse_iso_timestamp
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
        Tier A: Official Warnings (IMD / APSDMA / CWC / NDMA)
        Tier B: Model Advisories (PRAVAH 360 Scientific Model Outputs)
        Tier C: Community Reports (Citizen-submitted & verified observations)

        Strict Integrity Rules:
        - Never invent missing alert fields (district remains null, severity/source remain Unknown).
        - Freshness accurately reflects LIVE, CACHED, STALE, EXPIRED, UNKNOWN based on actual metadata.
        - Model advisories are never represented as authoritative official warnings.
        """
        acks = set(self._get_acknowledged_ids())
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Tier A: Official Warnings (IMD / APSDMA / CWC / NDMA)
        official_warnings = []
        try:
            raw_alerts, health = LiveAlertIngestionService().get_cached_or_live_alerts()
            seen_hashes = set()
            for al in raw_alerts:
                # 1. Source: Never default to official agencies; keep Unknown if missing
                src = getattr(al, "source", None) or getattr(al, "source_agency", None) or getattr(al, "sender", None)
                if not src or str(src).strip() == "":
                    src = "Unknown"

                # 2. District: Never default to East Godavari; keep null or Unknown
                aff_dists = getattr(al, "affected_districts", None) or []
                dist = getattr(al, "district", None)
                if not dist and aff_dists and len(aff_dists) > 0:
                    dist = aff_dists[0]
                if dist is None or str(dist).strip() == "":
                    dist = None

                # 3. Severity: Never default to Moderate; keep Unknown if missing
                sev = getattr(al, "severity", None)
                if not sev or str(sev).strip() == "":
                    sev = "Unknown"

                ev_type = getattr(al, "event_type", None) or getattr(al, "event_category", None) or "Unknown"

                # 4. Issue time: Never default to now_iso; keep None if missing
                iss = getattr(al, "issued_at", None) or getattr(al, "sent_time", None)

                # Deduplicate by fingerprint hash
                fp_src = src or "unknown"
                fp_ev = ev_type or "alert"
                fp_dist = dist or "none"
                fp_sev = sev or "unknown"
                fp_iss = iss or ""
                fp = hashlib.md5(f"{fp_src}_{fp_ev}_{fp_dist}_{fp_sev}_{fp_iss}".encode("utf-8")).hexdigest()[:10]
                if fp in seen_hashes:
                    continue
                seen_hashes.add(fp)

                # Filter by mandal if requested
                mandals = getattr(al, "affected_mandals", []) or []
                if mandal and mandals:
                    if not any(mandal.lower() in m.lower() for m in mandals):
                        continue

                # Filter by district if requested
                if district:
                    dist_match = False
                    if dist and district.lower() in dist.lower():
                        dist_match = True
                    if aff_dists and any(district.lower() in d.lower() for d in aff_dists):
                        dist_match = True
                    if not dist_match and (dist or aff_dists):
                        continue

                # Freshness state:
                # Distinguish LIVE, CACHED, STALE, EXPIRED, UNKNOWN.
                # Never mark an alert LIVE simply because no stale flag exists.
                is_cached = getattr(al, "is_cached", False)
                fresh_st = getattr(al, "freshness_state", None)
                if not fresh_st or (fresh_st == "LIVE" and is_cached):
                    fresh_st = evaluate_alert_freshness(
                        al,
                        is_source_stale=getattr(health, "stale", False)
                    )

                is_expired = (fresh_st == "EXPIRED") or (getattr(al, "status", "").upper() == "EXPIRED")
                is_stale = (fresh_st == "STALE") or getattr(health, "stale", False)
                alert_id = getattr(al, "alert_id", None) or fp

                official_warnings.append({
                    "id": f"OFFICIAL-{alert_id}",
                    "tier": "TIER_A_OFFICIAL_WARNING",
                    "badge_label": "Official Warning",
                    "badge_class": "badge-official",
                    "source": src,
                    "event_type": ev_type,
                    "severity": sev,
                    "headline": getattr(al, "headline", None) or "Disaster Alert",
                    "description": getattr(al, "description", ""),
                    "instruction": getattr(al, "instruction", None) or getattr(al, "instructions", "Follow local administration instructions."),
                    "affected_district": dist,
                    "affected_mandals": mandals,
                    "issued_at": iss,
                    "retrieved_at": getattr(al, "retrieved_at", None),
                    "expires_at": getattr(al, "expires_at", getattr(al, "expires_time", None)),
                    "freshness_state": fresh_st,
                    "status": getattr(al, "status", None) or "Unknown",
                    "is_cached": is_cached,
                    "is_stale": is_stale,
                    "is_expired": is_expired,
                    "is_acknowledged": f"OFFICIAL-{alert_id}" in acks,
                    "is_authoritative": True,
                    "is_official": True
                })
        except Exception as e:
            logger.warning(f"Official alerts retrieval notice: {e}")

        # 2. Tier B: Model Advisories (PRAVAH 360 Scientific Model Outputs)
        model_advisories = []
        try:
            raw_advs = EmergencyOperationsService().list_advisories(mandal=mandal, district=district)
            seen_adv_hashes = set()
            for adv in raw_advs:
                adv_id = getattr(adv, "advisory_id", None) or getattr(adv, "id", "ADV")

                # Mandal: Do NOT invent "Basin Reach". Keep None if missing.
                m_name = getattr(adv, "mandal", None)

                # District: Do NOT invent "East Godavari". Keep None if missing.
                d_name = getattr(adv, "district", None)

                # Severity / Priority: Do NOT invent "HIGH" or "Moderate". Keep "Unknown" if missing.
                prio = getattr(adv, "priority", None) or getattr(adv, "severity", None)
                if not prio or str(prio).strip() == "":
                    prio = "Unknown"

                # Status: Do NOT invent "ACTIVE". Keep "Unknown" if missing.
                adv_status = getattr(adv, "status", None)
                if not adv_status or str(adv_status).strip() == "":
                    adv_status = "Unknown"

                # Issue time: Do NOT assign now_iso! Keep None if missing.
                created = getattr(adv, "created_at", None) or getattr(adv, "issued_at", None)

                # Headline
                hl = getattr(adv, "headline", None) or getattr(adv, "title", None)
                if not hl:
                    if m_name and prio != "Unknown":
                        hl = f"{prio} Flood Susceptibility Advisory for {m_name}"
                    elif m_name:
                        hl = f"Flood Susceptibility Advisory for {m_name}"
                    else:
                        hl = "Model Flood Susceptibility Advisory"

                desc = getattr(adv, "message", None) or getattr(adv, "summary", "")
                action = getattr(adv, "action_recommended", None) or getattr(adv, "recommended_action", "Monitor local flood levels.")

                # Freshness for Model Advisories:
                # Must NOT be represented as a live official warning!
                if str(adv_status).upper() == "EXPIRED":
                    adv_freshness = "EXPIRED"
                elif not created:
                    adv_freshness = "UNKNOWN"
                else:
                    cr_dt = parse_iso_timestamp(created)
                    if cr_dt is None:
                        adv_freshness = "UNKNOWN"
                    else:
                        adv_age = (datetime.now(timezone.utc) - cr_dt).total_seconds()
                        if adv_age > 1800:
                            adv_freshness = "STALE"
                        else:
                            adv_freshness = "LIVE"

                # Deduplicate model advisories
                adv_fp = hashlib.md5(f"MODEL_{adv_id}_{m_name}_{d_name}_{prio}_{created}".encode("utf-8")).hexdigest()[:10]
                if adv_fp in seen_adv_hashes:
                    continue
                seen_adv_hashes.add(adv_fp)

                # Mandal and district filtering
                if mandal and m_name:
                    if mandal.lower() not in m_name.lower():
                        continue
                if district and d_name:
                    if district.lower() not in d_name.lower():
                        continue

                model_advisories.append({
                    "id": f"MODEL-{adv_id}",
                    "tier": "TIER_B_MODEL_ADVISORY",
                    "badge_label": "Model Advisory",
                    "badge_class": "badge-model",
                    "source": "PRAVAH 360 Geospatial Intelligence",
                    "event_type": "Flood Susceptibility",
                    "severity": prio.capitalize() if prio != "Unknown" else "Unknown",
                    "headline": hl,
                    "description": desc,
                    "instruction": action,
                    "affected_district": d_name,
                    "affected_mandals": [m_name] if m_name else [],
                    "issued_at": created,
                    "retrieved_at": getattr(adv, "retrieved_at", None),
                    "expires_at": getattr(adv, "expires_at", None),
                    "freshness_state": adv_freshness,
                    "status": adv_status,
                    "is_cached": False,
                    "is_stale": (adv_freshness == "STALE"),
                    "is_expired": (adv_freshness == "EXPIRED"),
                    "is_acknowledged": f"MODEL-{adv_id}" in acks,
                    "is_authoritative": False,
                    "is_official": False,
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
