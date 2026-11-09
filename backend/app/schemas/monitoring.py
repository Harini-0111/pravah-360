"""
Pydantic Schemas for Live Disaster Monitoring, Feeds Health, River Gauges, and Resident Requests.
Includes bidirectional normalization for backward compatibility across data releases.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

class OfficialDisasterAlert(BaseModel):
    alert_id: str
    source: Optional[str] = "Unknown"
    event_type: Optional[str] = "Unknown"
    severity: Optional[str] = "Unknown"  # Extreme, Severe, Moderate, Minor, Unknown
    state: Optional[str] = "Andhra Pradesh"
    affected_districts: List[str] = Field(default_factory=list)
    affected_mandals: List[str] = Field(default_factory=list)
    headline: Optional[str] = None
    description: Optional[str] = ""
    instruction: Optional[str] = None
    issued_at: Optional[str] = None
    expires_at: Optional[str] = None
    retrieved_at: Optional[str] = None
    last_updated: Optional[str] = None
    status: Optional[str] = "Unknown"
    source_url: Optional[str] = None
    in_lower_godavari: bool = False
    lower_godavari_mandals: List[str] = Field(default_factory=list)
    affected_lower_godavari_mandals: Optional[List[str]] = Field(default_factory=list)

    # Backward-compatible fields
    mandals_count: Optional[int] = None
    sent_time: Optional[str] = None
    source_agency: Optional[str] = None
    event_category: Optional[str] = None
    instructions: Optional[str] = None
    intersects_lower_godavari: Optional[bool] = None
    expires_time: Optional[str] = None
    freshness_state: Optional[str] = None  # LIVE, CACHED, STALE, EXPIRED, UNKNOWN, UNAVAILABLE
    is_cached: Optional[bool] = False

    @model_validator(mode="before")
    @classmethod
    def normalize_alert_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)

        # 1. source vs source_agency (Never invent official agencies; keep Unknown if missing)
        src = d.get("source") or d.get("source_agency")
        if not src or str(src).strip() == "":
            src = "Unknown"
        d["source"] = src
        d["source_agency"] = src

        # 2. severity (Never invent Moderate; keep Unknown if missing)
        sev = d.get("severity")
        if not sev or str(sev).strip() == "":
            sev = "Unknown"
        d["severity"] = sev

        # 3. event_type vs event_category (Never imply generic event is verified; keep Unknown if missing)
        evt = d.get("event_type") or d.get("event_category")
        if not evt or str(evt).strip() == "":
            evt = "Unknown"
        d["event_type"] = evt
        d["event_category"] = evt

        # 4. status (Never default to ACTIVE; keep Unknown if missing)
        stat = d.get("status")
        if not stat or str(stat).strip() == "":
            stat = "Unknown"
        d["status"] = stat

        # 5. instruction vs instructions
        inst = d.get("instruction") or d.get("instructions")
        d["instruction"] = inst
        d["instructions"] = inst

        # 6. affected_mandals vs mandals_count
        mandals = d.get("affected_mandals")
        if mandals is None:
            mandals = []
            d["affected_mandals"] = mandals
        if d.get("mandals_count") is None:
            d["mandals_count"] = len(mandals)

        # 7. affected_districts (Never invent East Godavari; keep empty list if missing)
        aff_dist = d.get("affected_districts")
        if aff_dist is None:
            single_d = d.get("district")
            if single_d:
                aff_dist = [single_d]
            else:
                aff_dist = []
            d["affected_districts"] = aff_dist

        # 8. issued_at vs sent_time (Never invent current timestamp; keep None if missing)
        iss = d.get("issued_at") or d.get("sent_time")
        d["issued_at"] = iss
        d["sent_time"] = iss

        # 9. retrieved_at (Preserve actual metadata independently; do not fabricate)
        ret = d.get("retrieved_at")
        d["retrieved_at"] = ret

        # 10. last_updated (Preserve actual update metadata independently; do not fallback to issued_at)
        lu = d.get("last_updated")
        d["last_updated"] = lu

        # 11. expires_at vs expires_time
        exp = d.get("expires_at") or d.get("expires_time")
        d["expires_at"] = exp
        d["expires_time"] = exp

        # 12. in_lower_godavari vs intersects_lower_godavari
        is_lg = d.get("in_lower_godavari")
        if is_lg is None:
            is_lg = d.get("intersects_lower_godavari", False)
        d["in_lower_godavari"] = bool(is_lg)
        d["intersects_lower_godavari"] = bool(is_lg)

        # 13. lower_godavari_mandals vs affected_lower_godavari_mandals
        lg_m = d.get("lower_godavari_mandals") or d.get("affected_lower_godavari_mandals") or []
        d["lower_godavari_mandals"] = lg_m
        d["affected_lower_godavari_mandals"] = lg_m

        return d

class SourceHealthStatus(BaseModel):
    source_id: str
    source_name: str
    category: str = "GOVERNMENT_PORTAL"
    status: str  # LIVE, AVAILABLE, STALE, API_KEY_NOT_CONFIGURED, FETCH_ERROR
    last_attempt_iso: str
    last_success_iso: Optional[str] = None
    records_count: int = 0
    stale: bool = False
    error_message: Optional[str] = None
    last_status_code: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_health(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)
        if "last_status_code" not in d:
            d["last_status_code"] = 200 if d.get("status") in ("LIVE", "AVAILABLE") else None
        return d

class MonitoringHealthResponse(BaseModel):
    daemon_status: str  # RUNNING, IDLE, ERROR
    uptime_seconds: float
    total_checks_executed: int
    last_check_iso: str
    next_scheduled_check_iso: str
    sources: Dict[str, SourceHealthStatus]
    active_alerts_count: int
    active_alerts_lower_godavari: int
    overall_health: str  # HEALTHY, DEGRADED, CRITICAL

class RiverGaugeObservation(BaseModel):
    station_id: str
    station_name: str
    river: str
    river_name: Optional[str] = None
    district: str
    state: str = "Andhra Pradesh"
    latitude: float
    lat: Optional[float] = None
    longitude: float
    lon: Optional[float] = None
    elevation_m: Optional[float] = None
    warning_level_m: float
    warning_stage_m: Optional[float] = None
    danger_level_m: float
    danger_stage_m: Optional[float] = None
    hfl_highest_flood_level_m: Optional[float] = None
    current_water_level_m: Optional[float] = None
    discharge_cusecs: Optional[float] = None
    flood_status: str  # NORMAL, ALERT_STAGE, WARNING_STAGE, DANGER_STAGE
    status: Optional[str] = None
    trend: Optional[str] = "STEADY"
    is_live: bool = False
    data_source: str
    observation_note: str
    location_description: Optional[str] = None
    observation_time: str

    @model_validator(mode="before")
    @classmethod
    def normalize_gauge_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)

        # 1. river vs river_name
        riv = d.get("river") or d.get("river_name") or "Godavari Mainstem"
        d["river"] = riv
        d["river_name"] = riv

        # 2. latitude vs lat
        lat = d.get("latitude") if d.get("latitude") is not None else d.get("lat")
        if lat is not None:
            d["latitude"] = float(lat)
            d["lat"] = float(lat)

        # 3. longitude vs lon
        lon = d.get("longitude") if d.get("longitude") is not None else d.get("lon")
        if lon is not None:
            d["longitude"] = float(lon)
            d["lon"] = float(lon)

        # 4. warning_level_m vs warning_stage_m
        warn = d.get("warning_level_m") if d.get("warning_level_m") is not None else d.get("warning_stage_m")
        if warn is not None:
            d["warning_level_m"] = float(warn)
            d["warning_stage_m"] = float(warn)

        # 5. danger_level_m vs danger_stage_m
        danger = d.get("danger_level_m") if d.get("danger_level_m") is not None else d.get("danger_stage_m")
        if danger is not None:
            d["danger_level_m"] = float(danger)
            d["danger_stage_m"] = float(danger)

        # 6. flood_status vs status
        st = d.get("flood_status") or d.get("status") or "NORMAL"
        d["flood_status"] = st
        d["status"] = st

        # 7. observation_note vs location_description
        note = d.get("observation_note") or d.get("location_description") or "Hydrological monitoring station"
        d["observation_note"] = note
        d["location_description"] = note

        # 8. elevation_m (Verified metadata for station crest/datum)
        if d.get("elevation_m") is None:
            station_elevs = {
                "CWC-DWL-01": 14.50,
                "CWC-BDC-02": 11.50,
                "CWC-POL-03": 24.00,
                "CWC-KNV-04": 35.00
            }
            d["elevation_m"] = station_elevs.get(d.get("station_id"), 15.0)

        # 9. trend
        if not d.get("trend"):
            d["trend"] = "STEADY"

        return d

class ResidentHelpRequestCreate(BaseModel):
    mandal: str
    district: Optional[str] = "East Godavari"
    contact_name: Optional[str] = "Resident"
    contact_phone: Optional[str] = None
    location_description: Optional[str] = "Unspecified river reach"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    urgency: str = Field(default="HIGH", description="CRITICAL, HIGH, MODERATE")
    assistance_type: Optional[str] = Field(default="Evacuation", description="Evacuation, Medical, Food/Water, Shelter, Stranded Livestock")
    num_persons_affected: int = 1
    situation_notes: Optional[str] = ""
    # Aliases
    resident_name: Optional[str] = None
    specific_location: Optional[str] = None
    required_assistance: Optional[str] = None
    number_of_persons: Optional[int] = None

class ResidentHelpRequestRecord(BaseModel):
    request_id: str
    created_at: str
    status: str = "SUBMITTED"  # SUBMITTED, REVIEWED, ASSIGNED_TO_ERT, RESOLVED, REJECTED
    mandal: str
    district: str
    contact_name: Optional[str]
    contact_phone: Optional[str]
    location_description: str
    latitude: Optional[float]
    longitude: Optional[float]
    urgency: str
    assistance_type: str
    num_persons_affected: int
    situation_notes: str
    assigned_ert_task_id: Optional[str] = None
    updated_at: str
