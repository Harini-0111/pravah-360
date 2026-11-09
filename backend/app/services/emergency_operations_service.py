"""
Emergency Operations Service.
Manages persistent state for the Decision Support Simulation:
- Resident Location Awareness & Acknowledgment
- Mandal Administrator Advisory Composition & Broadcast
- District Administrator Multi-Mandal Oversight
- Emergency Response Team (ERT) Resource Allocation Board
"""
import os
import json
import math
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.app.schemas.operations import (
    AdvisoryCreate,
    AdvisoryRecord,
    AdvisoryAcknowledge,
    ResourceRequestCreate,
    ResourceRequestUpdate,
    ResourceRequestRecord,
    NearestFacility,
    ResidentViewResponse,
    DistrictOverviewResponse
)
from backend.app.services.geographic_identification_service import GeographicIdentificationService
from backend.app.services.flood_risk_service import FloodRiskAssessmentService

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "operations"))
STORE_FILE = os.path.join(DATA_DIR, "operations_store.json")

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

class EmergencyOperationsService:
    def __init__(self, geo_service: Optional[GeographicIdentificationService] = None,
                 risk_service: Optional[FloodRiskAssessmentService] = None):
        self.geo_service = geo_service or GeographicIdentificationService()
        self.risk_service = risk_service or FloodRiskAssessmentService()
        os.makedirs(DATA_DIR, exist_ok=True)
        self._ensure_store()

    def _ensure_store(self):
        """Initializes persistent store file with verified Lower Godavari initial records if not present."""
        if not os.path.exists(STORE_FILE):
            now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            initial_data = {
                "advisories": [
                    {
                        "advisory_id": "ADV-2026-001",
                        "mandal": "Rajamahendravaram (Rajahmundry)",
                        "district": "East Godavari",
                        "target_tiers": ["Very High", "High"],
                        "priority": "HIGH",
                        "headline": "Riverbank Inundation Preparedness Advisory - Dowleswaram Barrage 1st Warning Stage",
                        "message": "Water levels at Dowleswaram Barrage are approaching warning threshold. Habitations within 500m of the riverfront must prepare for potential backflow inundation.",
                        "action_recommended": "Move livestock and farm equipment to elevated bunds. Follow ward volunteer evacuation directions. Nearest shelter: Kotipalli Bus Stand Community Relief Center.",
                        "dispatched_by": "Tahsildar & Executive Magistrate, Rajamahendravaram Urban",
                        "created_at": now_iso,
                        "status": "ACTIVE",
                        "stats": {
                            "queued": 12400,
                            "delivered_simulated": 11950,
                            "acknowledged_simulated": 8420
                        }
                    },
                    {
                        "advisory_id": "ADV-2026-002",
                        "mandal": "Kovvur",
                        "district": "East Godavari",
                        "target_tiers": ["Very High"],
                        "priority": "CRITICAL",
                        "headline": "Low-Lying Habitational Alert - Godavari Right Bank Trough",
                        "message": "Elevated terrain susceptibility combined with rising river stages requires active preparedness across Kumaradevam and riverside settlements in Kovvur.",
                        "action_recommended": "Immediate evacuation advisory for identified kutcha houses in flood-fringe depressions. Report to designated Cyclone Shelter, Kovvur High School.",
                        "dispatched_by": "Mandal Emergency Operations Cell, Kovvur",
                        "created_at": now_iso,
                        "status": "ACTIVE",
                        "stats": {
                            "queued": 8200,
                            "delivered_simulated": 7910,
                            "acknowledged_simulated": 6120
                        }
                    },
                    {
                        "advisory_id": "ADV-2026-003",
                        "mandal": "Amalapuram",
                        "district": "Dr. B.R. Ambedkar Konaseema",
                        "target_tiers": ["Very High", "High", "Moderate"],
                        "priority": "MODERATE",
                        "headline": "Delta Estuarine Drainage & High Tide Advisory",
                        "message": "High tidal confluence in Gautami Godavari distributaries may impede gravity canal drainage over the next 48 hours.",
                        "action_recommended": "Monitor sluice gate outflows and avoid entering swollen agricultural channels. Keep emergency torches and clean drinking water ready.",
                        "dispatched_by": "Sub-Collector Office, Amalapuram",
                        "created_at": now_iso,
                        "status": "ACTIVE",
                        "stats": {
                            "queued": 9500,
                            "delivered_simulated": 9100,
                            "acknowledged_simulated": 5480
                        }
                    }
                ],
                "resource_requests": [
                    {
                        "request_id": "RES-2026-001",
                        "mandal": "Kovvur",
                        "district": "East Godavari",
                        "category": "Rescue boats",
                        "quantity": 12,
                        "unit": "motorized inflatable boats",
                        "priority": "CRITICAL",
                        "reason": "Evacuation standby for vulnerable low-lying riverbank habitations near Kumaradevam.",
                        "requester_role": "Mandal Incident Commander, Kovvur",
                        "current_status": "Dispatched",
                        "created_at": now_iso,
                        "updated_at": now_iso,
                        "status_history": [
                            {"status": "Requested", "timestamp": now_iso, "note": "Initial request submitted from Kovvur field post"},
                            {"status": "Approved", "timestamp": now_iso, "note": "District Emergency Operations Centre approved allocation"},
                            {"status": "Dispatched", "timestamp": now_iso, "note": "SDRF Unit 3 en route from Kakinada staging depot"}
                        ]
                    },
                    {
                        "request_id": "RES-2026-002",
                        "mandal": "Rajamahendravaram (Rajahmundry)",
                        "district": "East Godavari",
                        "category": "Food and drinking water",
                        "quantity": 5000,
                        "unit": "ration packets & potable water pouches",
                        "priority": "HIGH",
                        "reason": "Pre-positioning supplies at Kotipalli Bus Stand and Municipal High School relief camps.",
                        "requester_role": "Municipal Commissioner, Rajamahendravaram",
                        "current_status": "Approved",
                        "created_at": now_iso,
                        "updated_at": now_iso,
                        "status_history": [
                            {"status": "Requested", "timestamp": now_iso, "note": "Request logged by Civil Supplies Officer"},
                            {"status": "Approved", "timestamp": now_iso, "note": "Joint Collector authorized dispatch from Central Warehouse"}
                        ]
                    },
                    {
                        "request_id": "RES-2026-003",
                        "mandal": "Amalapuram",
                        "district": "Dr. B.R. Ambedkar Konaseema",
                        "category": "Medical kits and first aid",
                        "quantity": 250,
                        "unit": "emergency trauma & sanitation kits",
                        "priority": "HIGH",
                        "reason": "Mobile medical team deployment across tail-end distributary habitations.",
                        "requester_role": "District Medical & Health Officer",
                        "current_status": "Requested",
                        "created_at": now_iso,
                        "updated_at": now_iso,
                        "status_history": [
                            {"status": "Requested", "timestamp": now_iso, "note": "Requested from Amalapuram Area Hospital"}
                        ]
                    },
                    {
                        "request_id": "RES-2026-004",
                        "mandal": "Polavaram",
                        "district": "Eluru",
                        "category": "Temporary shelters and essential supplies",
                        "quantity": 150,
                        "unit": "all-weather modular tents",
                        "priority": "HIGH",
                        "reason": "Upstream Godavari margin temporary staging for riverside hamlets.",
                        "requester_role": "Integrated Tribal Development Agency (ITDA)",
                        "current_status": "On Scene",
                        "created_at": now_iso,
                        "updated_at": now_iso,
                        "status_history": [
                            {"status": "Requested", "timestamp": now_iso, "note": "Submitted by ITDA Project Officer"},
                            {"status": "Approved", "timestamp": now_iso, "note": "District Collector approved emergency reserve release"},
                            {"status": "Dispatched", "timestamp": now_iso, "note": "Loaded onto transport trucks from Eluru"},
                            {"status": "On Scene", "timestamp": now_iso, "note": "Arrived at Polavaram Community Hall staging point"}
                        ]
                    },
                    {
                        "request_id": "RES-2026-005",
                        "mandal": "Devipatnam",
                        "district": "Alluri Sitharama Raju",
                        "category": "Rescue personnel and transport support",
                        "quantity": 4,
                        "unit": "SDRF rescue teams & 4x4 light vehicles",
                        "priority": "CRITICAL",
                        "reason": "Gorge-section monitoring and assistance for isolated hilltop tribal settlements.",
                        "requester_role": "Sub-Divisional Police Officer",
                        "current_status": "Requested",
                        "created_at": now_iso,
                        "updated_at": now_iso,
                        "status_history": [
                            {"status": "Requested", "timestamp": now_iso, "note": "Urgent request due to road access inundation"}
                        ]
                    },
                    {
                        "request_id": "RES-2026-006",
                        "mandal": "Achanta",
                        "district": "West Godavari",
                        "category": "Emergency medicines",
                        "quantity": 800,
                        "unit": "anti-diarrheal & waterborne treatment kits",
                        "priority": "MODERATE",
                        "reason": "Preventative medical distribution in waterlogged habitations.",
                        "requester_role": "Primary Health Centre Incharge",
                        "current_status": "Completed",
                        "created_at": now_iso,
                        "updated_at": now_iso,
                        "status_history": [
                            {"status": "Requested", "timestamp": now_iso, "note": "Initial requisition"},
                            {"status": "Approved", "timestamp": now_iso, "note": "Approved by DMHO West Godavari"},
                            {"status": "Dispatched", "timestamp": now_iso, "note": "Dispatched from Bhimavaram"},
                            {"status": "On Scene", "timestamp": now_iso, "note": "Received at Achanta PHC"},
                            {"status": "Completed", "timestamp": now_iso, "note": "Fully distributed across 8 flood-prone villages"}
                        ]
                    }
                ],
                "acknowledgements": []
            }
            with open(STORE_FILE, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _read_store(self) -> Dict[str, Any]:
        self._ensure_store()
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading operations store: {e}")
            return {"advisories": [], "resource_requests": [], "acknowledgements": []}

    def _write_store(self, data: Dict[str, Any]):
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # -------------------------------------------------------------------------
    # 1. RESIDENT VIEW
    # -------------------------------------------------------------------------
    def get_resident_view(self, lat: float, lon: float, mandal: Optional[str] = None) -> ResidentViewResponse:
        geo = self.geo_service.identify_point(lat, lon)
        eval_pt = self.risk_service.evaluate_point(lat, lon)

        # Match mandal name
        resolved_mandal = mandal or geo.get("mandal") or "Lower Godavari Basin"
        resolved_district = geo.get("district") or "East Godavari"

        # Find active advisories matching this mandal or district
        store = self._read_store()
        active_advs: List[AdvisoryRecord] = []
        norm_mandal = resolved_mandal.lower()

        for adv_dict in store.get("advisories", []):
            if adv_dict.get("status") != "ACTIVE":
                continue
            adv_m = (adv_dict.get("mandal") or "").lower()
            adv_d = (adv_dict.get("district") or "").lower()

            # Check match: direct mandal match, alias match, or district-wide match
            mandal_matched = False
            if norm_mandal in adv_m or adv_m in norm_mandal:
                mandal_matched = True
            elif ("rajamahendravaram" in norm_mandal or "rajahmundry" in norm_mandal) and \
                 ("rajamahendravaram" in adv_m or "rajahmundry" in adv_m):
                mandal_matched = True

            if mandal_matched or (resolved_district.lower() in adv_d):
                active_advs.append(AdvisoryRecord(**adv_dict))

        # Calculate nearest mapped facilities
        nearest_facs: List[NearestFacility] = []
        infra_geojson = self.risk_service.generate_infrastructure_geojson()
        features = infra_geojson.get("features", [])

        scored_facs = []
        for feat in features:
            coords = feat.get("geometry", {}).get("coordinates", [])
            if len(coords) >= 2:
                f_lon, f_lat = coords[0], coords[1]
                dist = haversine_km(lat, lon, f_lat, f_lon)
                props = feat.get("properties", {})
                scored_facs.append((dist, props, f_lat, f_lon))

        scored_facs.sort(key=lambda x: x[0])
        for dist, props, f_lat, f_lon in scored_facs[:5]:
            nearest_facs.append(NearestFacility(
                name=props.get("name") or f"{props.get('facility_type', 'Community')} Facility",
                facility_type=props.get("facility_type") or "Community Shelter",
                distance_km=dist,
                host_risk_level=props.get("host_risk_level"),
                latitude=f_lat,
                longitude=f_lon,
                emergency_ready=bool(props.get("emergency") == "yes" or "hospital" in props.get("facility_type", "").lower())
            ))

        return ResidentViewResponse(
            location_name=geo.get("formatted_location") or f"{resolved_mandal}, {resolved_district}",
            mandal=resolved_mandal,
            district=resolved_district,
            state=geo.get("state") or "Andhra Pradesh",
            latitude=lat,
            longitude=lon,
            within_study_area=geo.get("within_study_area", False),
            susceptibility_score=round(eval_pt.susceptibility_score, 2),
            susceptibility_tier=eval_pt.risk_level,
            active_advisories=active_advs,
            nearest_facilities=nearest_facs,
            advisory_count=len(active_advs)
        )

    # -------------------------------------------------------------------------
    # 2. MANDAL ADMINISTRATOR WORKFLOW
    # -------------------------------------------------------------------------
    def get_advisories(self, mandal: Optional[str] = None, district: Optional[str] = None,
                       status: Optional[str] = None) -> List[AdvisoryRecord]:
        store = self._read_store()
        results = []
        for adv in store.get("advisories", []):
            if status and adv.get("status") != status:
                continue
            if mandal:
                adv_m = (adv.get("mandal") or "").lower()
                query_m = mandal.lower()
                if "rajamahendravaram" in query_m or "rajahmundry" in query_m:
                    if not ("rajamahendravaram" in adv_m or "rajahmundry" in adv_m):
                        continue
                elif query_m not in adv_m and adv_m not in query_m:
                    continue
            if district and district.lower() not in (adv.get("district") or "").lower():
                continue
            results.append(AdvisoryRecord(**adv))
        return results

    # Backward compatibility alias
    list_advisories = get_advisories

    def create_advisory(self, adv_in: AdvisoryCreate) -> AdvisoryRecord:
        store = self._read_store()
        adv_id = f"ADV-2026-{len(store.get('advisories', [])) + 1:03d}"
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Estimate target population in target tiers for simulation counts
        # Pull mandal profile if available
        base_pop = 25000
        try:
            m_profile = self.risk_service.assess_mandal_risk(adv_in.mandal)
            base_pop = max(1000, int(getattr(m_profile, 'potentially_exposed_population', getattr(m_profile, 'exposed_population', 25000))))
        except Exception:
            pass

        queued_cnt = base_pop
        delivered_cnt = int(base_pop * 0.95)
        ack_cnt = 0

        new_rec = AdvisoryRecord(
            advisory_id=adv_id,
            mandal=adv_in.mandal,
            district=adv_in.district,
            target_tiers=adv_in.target_tiers,
            priority=adv_in.priority.upper(),
            headline=adv_in.headline,
            message=adv_in.message,
            action_recommended=adv_in.action_recommended,
            dispatched_by=adv_in.dispatched_by,
            created_at=now_iso,
            status="ACTIVE",
            stats={
                "queued": queued_cnt,
                "delivered_simulated": delivered_cnt,
                "acknowledged_simulated": ack_cnt
            }
        )

        store.setdefault("advisories", []).insert(0, new_rec.dict())
        self._write_store(store)
        logger.info(f"Created emergency advisory {adv_id} for {adv_in.mandal}")
        return new_rec

    def acknowledge_advisory(self, ack_in: AdvisoryAcknowledge) -> Dict[str, Any]:
        store = self._read_store()
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Find target advisory
        found = False
        target_adv = None
        for adv in store.get("advisories", []):
            if adv.get("advisory_id") == ack_in.advisory_id:
                adv["stats"]["acknowledged_simulated"] = adv["stats"].get("acknowledged_simulated", 0) + 1
                found = True
                target_adv = adv
                break

        if not found:
            raise ValueError(f"Advisory {ack_in.advisory_id} not found")

        # Record individual acknowledgment event
        ack_event = {
            "ack_id": f"ACK-{uuid.uuid4().hex[:8].upper()}",
            "advisory_id": ack_in.advisory_id,
            "mandal": ack_in.mandal or target_adv.get("mandal"),
            "district": ack_in.district or target_adv.get("district"),
            "resident_identifier": ack_in.resident_identifier,
            "timestamp": now_iso,
            "latitude": ack_in.latitude,
            "longitude": ack_in.longitude
        }
        store.setdefault("acknowledgements", []).append(ack_event)
        self._write_store(store)

        return {
            "status": "SUCCESS",
            "message": "Simulated resident warning acknowledged successfully.",
            "advisory_id": ack_in.advisory_id,
            "acknowledged_at": now_iso,
            "updated_stats": target_adv["stats"]
        }

    # -------------------------------------------------------------------------
    # 3. DISTRICT ADMINISTRATOR WORKFLOW
    # -------------------------------------------------------------------------
    def get_district_overview(self) -> List[DistrictOverviewResponse]:
        from backend.app.services.flood_risk_service import MANDAL_2022_DISTRICT_MAP
        store = self._read_store()
        advisories = store.get("advisories", [])
        resources = store.get("resource_requests", [])
        basin = self.risk_service.get_basin_assessment()

        results = []
        for dist_name, d_sum in basin.district_summaries.items():
            # Find mandals in this district
            mandals = [m for m, d in MANDAL_2022_DISTRICT_MAP.items() if d == dist_name]

            # Count active advisories in this district
            d_advs = [a for a in advisories if dist_name.lower() in (a.get("district") or "").lower() and a.get("status") == "ACTIVE"]
            
            # Compute acknowledgment rate across district advisories
            total_deliv = sum(a.get("stats", {}).get("delivered_simulated", 0) for a in d_advs)
            total_ack = sum(a.get("stats", {}).get("acknowledged_simulated", 0) for a in d_advs)
            ack_pct = round((total_ack / total_deliv * 100), 1) if total_deliv > 0 else 0.0

            # Count resource requests
            d_res = [r for r in resources if dist_name.lower() in (r.get("district") or "").lower()]
            pending_res = [r for r in d_res if r.get("current_status") in ("Requested", "Approved", "Dispatched", "On Scene")]

            vh_cnt = d_sum.mandals_by_risk.get("Very High", 0)
            h_cnt = d_sum.mandals_by_risk.get("High", 0)
            highest_tier = "Very High" if vh_cnt > 0 else ("High" if h_cnt > 0 else "Moderate")

            base_pop = d_sum.total_baseline_population
            exp_pop = d_sum.total_exposed_population
            exp_pct = round((exp_pop / base_pop * 100), 2) if base_pop > 0 else 0.0

            results.append(DistrictOverviewResponse(
                district=dist_name,
                total_mandals=len(mandals),
                mandals=mandals,
                total_population=base_pop,
                exposed_population=exp_pop,
                exposure_percentage=exp_pct,
                highest_risk_tier=highest_tier,
                active_advisories_count=len(d_advs),
                acknowledgment_rate_pct=ack_pct,
                resource_requests_count=len(d_res),
                pending_resources_count=len(pending_res)
            ))

        return results

    # -------------------------------------------------------------------------
    # 4. EMERGENCY RESPONSE TEAM (ERT) BOARD WORKFLOW
    # -------------------------------------------------------------------------
    def get_resource_requests(self, mandal: Optional[str] = None, district: Optional[str] = None,
                              status: Optional[str] = None, category: Optional[str] = None) -> List[ResourceRequestRecord]:
        store = self._read_store()
        results = []
        for req in store.get("resource_requests", []):
            if status and req.get("current_status") != status:
                continue
            if category and category.lower() not in (req.get("category") or "").lower():
                continue
            if mandal and mandal.lower() not in (req.get("mandal") or "").lower():
                continue
            if district and district.lower() not in (req.get("district") or "").lower():
                continue
            results.append(ResourceRequestRecord(**req))
        return results

    def create_resource_request(self, req_in: ResourceRequestCreate) -> ResourceRequestRecord:
        store = self._read_store()
        req_id = f"RES-2026-{len(store.get('resource_requests', [])) + 1:03d}"
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        initial_history = [{
            "status": "Requested",
            "timestamp": now_iso,
            "note": f"Initial request submitted by {req_in.requester_role}"
        }]

        new_rec = ResourceRequestRecord(
            request_id=req_id,
            mandal=req_in.mandal,
            district=req_in.district,
            category=req_in.category,
            quantity=req_in.quantity,
            unit=req_in.unit,
            priority=req_in.priority.upper(),
            reason=req_in.reason,
            requester_role=req_in.requester_role,
            current_status="Requested",
            created_at=now_iso,
            updated_at=now_iso,
            status_history=initial_history
        )

        store.setdefault("resource_requests", []).insert(0, new_rec.dict())
        self._write_store(store)
        logger.info(f"Created resource request {req_id} ({req_in.category}) for {req_in.mandal}")
        return new_rec

    def update_resource_status(self, request_id: str, update_in: ResourceRequestUpdate) -> ResourceRequestRecord:
        store = self._read_store()
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        valid_statuses = ["Requested", "Approved", "Dispatched", "On Scene", "Completed", "Rejected", "Cancelled"]
        if update_in.status not in valid_statuses:
            raise ValueError(f"Invalid status '{update_in.status}'. Must be one of {valid_statuses}")

        target_req = None
        for req in store.get("resource_requests", []):
            if req.get("request_id") == request_id:
                target_req = req
                break

        if not target_req:
            raise ValueError(f"Resource request {request_id} not found")

        target_req["current_status"] = update_in.status
        target_req["updated_at"] = now_iso
        note_str = update_in.note or f"Status transitioned to {update_in.status} by {update_in.updated_by}"
        target_req.setdefault("status_history", []).append({
            "status": update_in.status,
            "timestamp": now_iso,
            "note": note_str
        })

        self._write_store(store)
        logger.info(f"Updated resource request {request_id} to {update_in.status}")
        return ResourceRequestRecord(**target_req)
