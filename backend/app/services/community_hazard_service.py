"""
Community Hazard Reporting Service.
Persists citizen-submitted hazard reports and photos, protects resident privacy
by redacting reporter PII in public/admin views, supports duplicate detection,
and coordinates full lifecycle workflow connected to Emergency Operations:
SUBMITTED -> UNDER_REVIEW -> VERIFIED -> RESPONSE_ASSIGNED -> IN_PROGRESS -> RESOLVED
(Plus: NEEDS_MORE_INFORMATION, DUPLICATE, REJECTED)
"""
import os
import json
import uuid
import math
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from backend.app.schemas.community import (
    HazardReportCreate,
    HazardReportRecord,
    HazardReportStatusUpdate,
    HazardEscalateRequest
)
from backend.app.schemas.operations import ResourceRequestCreate
from backend.app.services.emergency_operations_service import EmergencyOperationsService

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "community"))
REPORTS_FILE = os.path.join(DATA_DIR, "hazard_reports.json")
PHOTOS_DIR = os.path.join(DATA_DIR, "photos")

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class CommunityHazardService:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(PHOTOS_DIR, exist_ok=True)
        if not os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, "w", encoding="utf-8") as f:
                json.dump({"reports": []}, f, indent=2)

    def _redact_name(self, name: Optional[str]) -> str:
        if not name or name.strip().lower() in ("anonymous", "resident", "anonymous resident"):
            return "Resident (Verified)"
        parts = name.strip().split()
        if len(parts) == 1:
            return f"{parts[0][0]}***"
        return f"{parts[0][0]}*** {parts[-1][0]}***"

    def _find_potential_duplicate(self, mandal: str, category: str, lat: Optional[float], lon: Optional[float]) -> Optional[Dict[str, Any]]:
        """Identify potential duplicate reports in same mandal/category within 2.0 km."""
        if not os.path.exists(REPORTS_FILE) or lat is None or lon is None:
            return None
        try:
            with open(REPORTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for r in data.get("reports", []):
                r_lat = r.get("latitude")
                r_lon = r.get("longitude")
                if r_lat is not None and r_lon is not None:
                    dist = haversine_distance_km(lat, lon, r_lat, r_lon)
                    if dist <= 2.0 and r.get("category", "").lower() == category.lower():
                        return {
                            "is_potential_duplicate": True,
                            "similar_report_id": r.get("report_id"),
                            "distance_km": round(dist, 2),
                            "existing_status": r.get("status"),
                            "suggestion": f"Proximity warning: A similar '{category}' report was submitted {round(dist, 2)} km away ({r.get('report_id')})."
                        }
        except Exception as e:
            logger.warning(f"Duplicate scan error: {e}")
        return None

    def submit_report(self, report_in: HazardReportCreate) -> HazardReportRecord:
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_id = f"HZD-2026-{uuid.uuid4().hex[:6].upper()}"

        photo_url = None
        has_photo = False
        if report_in.photo_data and len(report_in.photo_data) > 30:
            has_photo = True
            photo_filename = f"{report_id}.jpg"
            photo_path = os.path.join(PHOTOS_DIR, photo_filename)
            try:
                import base64
                data_part = report_in.photo_data
                if "," in data_part:
                    data_part = data_part.split(",", 1)[1]
                img_bytes = base64.b64decode(data_part)
                with open(photo_path, "wb") as pf:
                    pf.write(img_bytes)
                photo_url = f"/api/v1/community/hazards/{report_id}/photo"
            except Exception as e:
                logger.error(f"Failed to decode photo for {report_id}: {e}")
                has_photo = False

        dup_info = self._find_potential_duplicate(
            mandal=report_in.mandal,
            category=report_in.category,
            lat=report_in.latitude,
            lon=report_in.longitude
        )

        record = HazardReportRecord(
            report_id=report_id,
            created_at=now_iso,
            updated_at=now_iso,
            status="SUBMITTED",
            mandal=report_in.mandal,
            district=report_in.district or "East Godavari",
            category=report_in.category,
            description=report_in.description,
            location_description=report_in.location_description,
            latitude=report_in.latitude,
            longitude=report_in.longitude,
            reporter_name_redacted=self._redact_name(report_in.reporter_name),
            has_photo=has_photo,
            photo_url=photo_url,
            voice_note_transcript=report_in.voice_note_transcript,
            reviewer_notes=None,
            reviewed_by=None,
            linked_resource_request_id=None,
            potential_duplicate=dup_info
        )

        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("reports", []).insert(0, record.model_dump())
        with open(REPORTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Recorded community hazard report: {report_id} in {report_in.mandal}")
        return record

    def list_reports(self, mandal: Optional[str] = None, status: Optional[str] = None) -> List[HazardReportRecord]:
        if not os.path.exists(REPORTS_FILE):
            return []
        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        results = []
        for r in data.get("reports", []):
            if mandal and mandal.lower() not in (r.get("mandal") or "").lower():
                continue
            if status and r.get("status") != status:
                continue
            results.append(HazardReportRecord(**r))
        return results

    def get_report_by_id(self, report_id: str) -> Optional[HazardReportRecord]:
        if not os.path.exists(REPORTS_FILE):
            return None
        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for r in data.get("reports", []):
            if r.get("report_id") == report_id:
                return HazardReportRecord(**r)
        return None

    def update_report_status(self, report_id: str, update: HazardReportStatusUpdate) -> Optional[HazardReportRecord]:
        if not os.path.exists(REPORTS_FILE):
            return None
        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for r in data.get("reports", []):
            if r.get("report_id") == report_id:
                r["status"] = update.status
                if update.reviewer_notes is not None:
                    r["reviewer_notes"] = update.reviewer_notes
                if update.reviewed_by is not None:
                    r["reviewed_by"] = update.reviewed_by
                r["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(REPORTS_FILE, "w", encoding="utf-8") as out_f:
                    json.dump(data, out_f, indent=2)
                return HazardReportRecord(**r)
        return None

    def escalate_to_operations_resource(self, report_id: str, escalate: HazardEscalateRequest, officer_role: str = "Mandal Administrator") -> Optional[Dict[str, Any]]:
        """
        Escalates a verified hazard report into an official emergency Operations Simulator
        resource dispatch request for ERT motorboat/ambulance deployment.
        """
        report = self.get_report_by_id(report_id)
        if not report:
            return None

        # Build Resource Request for Operations Simulator
        res_create = ResourceRequestCreate(
            mandal=report.mandal,
            district=report.district,
            category="Rescue Boats" if "boat" in escalate.resource_type.lower() else "Medical Assistance" if "amb" in escalate.resource_type.lower() else "Dewatering Pumps",
            quantity=1,
            unit="Team Unit",
            priority=escalate.priority,
            reason=f"Escalated from verified hazard {report_id} ({report.category}): {report.description[:120]}",
            requester_role=officer_role
        )

        res_record = EmergencyOperationsService().create_resource_request(res_create)

        # Update hazard report status to RESPONSE_ASSIGNED and link the resource ID
        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        updated_report = None
        for r in data.get("reports", []):
            if r.get("report_id") == report_id:
                r["status"] = "RESPONSE_ASSIGNED"
                r["linked_resource_request_id"] = res_record.request_id
                r["reviewer_notes"] = f"Verified & escalated to ERT ({res_record.request_id}). Team: {escalate.assigned_team}. Notes: {escalate.dispatch_notes or 'Immediate response initiated.'}"
                r["reviewed_by"] = officer_role
                r["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated_report = r
                break

        with open(REPORTS_FILE, "w", encoding="utf-8") as out_f:
            json.dump(data, out_f, indent=2)

        return {
            "success": True,
            "report_id": report_id,
            "hazard_status": "RESPONSE_ASSIGNED",
            "linked_resource_request": res_record.model_dump(),
            "updated_report": updated_report
        }

    def get_photo_path(self, report_id: str) -> Optional[str]:
        p = os.path.join(PHOTOS_DIR, f"{report_id}.jpg")
        return p if os.path.exists(p) else None

community_hazard_service = CommunityHazardService()
