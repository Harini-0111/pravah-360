"""
API Endpoints for Geographic Area Identification and Flood Intelligence.
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException

from backend.app.services.geographic_identification_service import GeographicIdentificationService
from backend.app.services.flood_risk_service import FloodRiskAssessmentService
from backend.app.services.weather_service import WeatherService
from backend.app.services.emergency_operations_service import EmergencyOperationsService
from backend.app.services.live_monitoring_service import LiveMonitoringService
from backend.app.services.notification_service import NotificationDeliveryService
from backend.app.services.community_hazard_service import CommunityHazardService
from backend.app.services.voice_tts_service import voice_tts_service
from backend.app.services.emergency_helpline_service import get_official_helplines
from backend.app.services.continuous_alert_service import continuous_alert_service
from backend.app.services.prediction_validation_service import prediction_service
from backend.app.services.historical_event_service import historical_event_service
from backend.app.schemas.community import (
    HazardReportCreate,
    HazardReportRecord,
    HazardReportStatusUpdate,
    HazardEscalateRequest
)
from fastapi.responses import FileResponse
from backend.app.schemas.monitoring import (
    OfficialDisasterAlert,
    MonitoringHealthResponse,
    RiverGaugeObservation,
    ResidentHelpRequestCreate,
    ResidentHelpRequestRecord
)
from backend.app.schemas.notifications import (
    NotificationRecipient,
    NotificationDispatchCreate,
    NotificationDeliveryRecord
)
from backend.app.schemas.operations import (
    AdvisoryCreate,
    AdvisoryRecord,
    AdvisoryAcknowledge,
    ResourceRequestCreate,
    ResourceRequestUpdate,
    ResourceRequestRecord,
    ResidentViewResponse,
    DistrictOverviewResponse
)
from backend.app.schemas.geographic import CoordinateInput, BatchCoordinateInput, GeographicIdentification
from backend.app.schemas.weather import UnifiedWeatherResponse, LocationSearchResult
from backend.app.schemas.flood_risk import (
    FloodMarker,
    FloodAlert,
    FloodImpactSummary,
    BasinRiskAssessmentSummary,
    MandalRiskAssessment,
    PointRiskEvaluation,
    PointRiskEvaluationInput,
    SensitivityAnalysisResult
)

router = APIRouter()
geo_service = GeographicIdentificationService()
risk_service = FloodRiskAssessmentService()
weather_service = WeatherService(geo_service=geo_service)
ops_service = EmergencyOperationsService(geo_service=geo_service, risk_service=risk_service)
notification_service = NotificationDeliveryService()
hazard_service = CommunityHazardService()
monitoring_service = LiveMonitoringService(weather_service=weather_service)

# =========================================================================
# PRAVAH 360 REAL AUTHENTICATION & ROLE-BASED ACCESS CONTROL (PHASE B)
# =========================================================================
from fastapi import Request, Response, Depends, Cookie, Header
from backend.app.services.auth_db_service import (
    AuthDBService,
    RegisterRequest,
    LoginRequest,
    UserProfileResponse
)

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def get_current_user_optional(
    request: Request,
    pravah_session: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
) -> Optional[Dict[str, Any]]:
    """Retrieves authenticated user from HttpOnly cookie or Bearer token."""
    token = pravah_session
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()
    if not token:
        return None
    return AuthDBService.get_user_from_session(token)

def get_current_user_required(user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)) -> Dict[str, Any]:
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")
    return user

def require_roles(allowed_roles: List[str]):
    def role_checker(user: Dict[str, Any] = Depends(get_current_user_required)) -> Dict[str, Any]:
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: Action requires one of roles: {allowed_roles}. Current role: '{user.get('role')}'."
            )
        return user
    return role_checker

@router.post("/auth/register", status_code=201)
def register_citizen(payload: RegisterRequest, response: Response, request: Request):
    """Self-registration for citizens. Enforces citizen role server-side."""
    client_ip = get_client_ip(request)
    success, msg, user_data = AuthDBService.create_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role="citizen",
        district=payload.district or "East Godavari",
        mandal=payload.mandal or "Rajamahendravaram Urban"
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    # Auto-login newly registered citizen
    auth_ok, auth_msg, auth_data = AuthDBService.authenticate(payload.email, payload.password, ip=client_ip)
    if auth_ok and auth_data:
        response.set_cookie(
            key="pravah_session",
            value=auth_data["session_id"],
            httponly=True,
            samesite="lax",
            max_age=86400,
            secure=False
        )
        return {
            "status": "registered",
            "message": "Account created successfully.",
            "session_id": auth_data["session_id"],
            "user": auth_data["user"]
        }
    return {"status": "registered", "message": "Account created successfully.", "user": user_data}

@router.post("/auth/login")
def login_user(payload: LoginRequest, response: Response, request: Request):
    """Authenticates against SQLite database with rate-limiting and sets HttpOnly cookie."""
    client_ip = get_client_ip(request)
    success, msg, auth_data = AuthDBService.authenticate(payload.email, payload.password, ip=client_ip)
    
    if not success:
        if "Too many failed" in msg:
            raise HTTPException(status_code=429, detail=msg)
        raise HTTPException(status_code=401, detail=msg)
    
    # Set HttpOnly, SameSite cookie
    response.set_cookie(
        key="pravah_session",
        value=auth_data["session_id"],
        httponly=True,
        samesite="lax",
        max_age=86400,
        secure=False
    )
    return {
        "status": "authenticated",
        "session_id": auth_data["session_id"],
        "user": auth_data["user"]
    }

@router.get("/auth/session")
def get_current_session(user: Dict[str, Any] = Depends(get_current_user_required)):
    """Returns profile for currently authenticated user."""
    return user

@router.post("/auth/logout")
def logout_user(
    response: Response,
    request: Request,
    pravah_session: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """Terminates session server-side and clears HttpOnly cookie."""
    client_ip = get_client_ip(request)
    token = pravah_session
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()
    
    if token:
        AuthDBService.invalidate_session(token, ip=client_ip)
    
    response.delete_cookie(key="pravah_session")
    return {"status": "logged_out", "message": "Session successfully terminated."}

@router.get("/auth/audit-log")
def get_audit_log(
    user: Dict[str, Any] = Depends(require_roles(["district_admin"])),
    limit: int = 50
):
    """Privileged audit log access for district administrators."""
    conn = AuthDBService.get_connection()
    try:
        cursor = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        return {"count": len(rows), "logs": rows}
    finally:
        conn.close()


# Key monitoring stations across the Lower Godavari delta
BASE_FLOOD_POINTS = [
    {
        "id": "FL-001",
        "lat": 16.9420,
        "lon": 81.7760,
        "note": "Dowleswaram Barrage Headworks & Right Flank"
    },
    {
        "id": "FL-002",
        "lat": 17.0140,
        "lon": 81.7300,
        "note": "Kovvur Low-lying Bank & Ghat Area"
    },
    {
        "id": "FL-003",
        "lat": 16.5780,
        "lon": 82.0050,
        "note": "Amalapuram Central Delta Island"
    },
    {
        "id": "FL-004",
        "lat": 16.6500,
        "lon": 82.1100,
        "note": "Mummidivaram Gautami Delta Lowland"
    },
    {
        "id": "FL-005",
        "lat": 16.4800,
        "lon": 81.8900,
        "note": "Razole Vasishta Branch Island Habitation"
    },
    {
        "id": "FL-006",
        "lat": 16.7150,
        "lon": 81.8900,
        "note": "Kothapeta Lanka Settlements"
    },
    {
        "id": "FL-007",
        "lat": 17.2550,
        "lon": 81.6520,
        "note": "Polavaram Upstream Inundation Margin"
    },
    {
        "id": "FL-008",
        "lat": 16.9850,
        "lon": 81.7900,
        "note": "Rajamahendravaram Urban Riverfront"
    },
    {
        "id": "FL-009",
        "lat": 16.4350,
        "lon": 81.6900,
        "note": "Narsapur Estuarine Tidal Confluence"
    },
    {
        "id": "FL-010",
        "lat": 16.9300,
        "lon": 82.2400,
        "note": "Kakinada Coastal Plain"
    }
]

@router.get("/geographic/identify-point", response_model=GeographicIdentification)
def identify_point_get(lat: float, lon: float):
    """
    Performs spatial join on a single coordinate against verified GADM administrative boundaries via query parameters.
    """
    res = geo_service.identify_point(lat, lon)
    if not res.get("is_valid_coordinate"):
        raise HTTPException(status_code=400, detail=res.get("error", "Invalid coordinates"))
    return res

@router.post("/geographic/identify-point", response_model=GeographicIdentification)
def identify_point_endpoint(coord: CoordinateInput):
    """
    Performs spatial join on a single coordinate against verified GADM administrative boundaries.
    Identifies State, District, and Mandal.
    """
    res = geo_service.identify_point(coord.latitude, coord.longitude)
    if not res.get("is_valid_coordinate"):
        raise HTTPException(status_code=400, detail=res.get("error", "Invalid coordinates"))
    return res

@router.post("/geographic/identify-batch", response_model=List[GeographicIdentification])
def identify_batch_endpoint(batch: BatchCoordinateInput):
    """
    Batch identification endpoint for arrays of coordinates.
    """
    raw_points = [{"latitude": p.latitude, "longitude": p.longitude} for p in batch.points]
    enriched = geo_service.identify_points(raw_points)
    return [p["geographic_identification"] for p in enriched]

@router.get("/flood-risk/markers", response_model=List[FloodMarker])
def get_flood_risk_markers():
    """
    Returns active monitoring station points enriched with verified human-readable place names
    and physical flood susceptibility scores. Direct in-situ water depth is explicitly marked NOT_OBSERVED.
    """
    markers = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for pt in BASE_FLOOD_POINTS:
        geo = geo_service.identify_point(pt["lat"], pt["lon"])
        eval_res = risk_service.evaluate_point(pt["lat"], pt["lon"])

        # Map physical susceptibility to legacy 4-tier risk categories for backward compatibility:
        # Very High -> Critical, High -> High, Moderate -> Moderate, Low -> Low
        if eval_res.risk_level == "Very High":
            compat_risk = "Critical"
        elif eval_res.risk_level == "High":
            compat_risk = "High"
        elif eval_res.risk_level == "Moderate":
            compat_risk = "Moderate"
        else:
            compat_risk = "Low"

        markers.append(FloodMarker(
            id=pt["id"],
            marker_id=pt["id"],
            name=pt["note"],
            latitude=pt["lat"],
            longitude=pt["lon"],
            risk_level=compat_risk,
            inundation_probability=round(eval_res.susceptibility_score, 2),
            water_depth_est_m=None,
            water_depth_m=None,
            geographic_info=geo,
            mandal=geo["mandal"],
            district=geo["district"],
            state=geo["state"],
            formatted_location=geo["formatted_location"],
            timestamp=timestamp,
            susceptibility_score=eval_res.susceptibility_score,
            water_depth_status="NOT_OBSERVED (Awaiting In-Situ Gauge/Radar Measurement)",
            observation_type="TERRAIN_SUSCEPTIBILITY_MONITORING"
        ))
    return markers

@router.get("/flood-risk/alerts", response_model=List[FloodAlert])
def get_flood_alerts():
    """
    Generates human-readable susceptibility monitoring advisories (Yellow/Orange).
    Clearly formats administrative hierarchy and action guidance without inventing water depths or villages.
    """
    markers = get_flood_risk_markers()
    alerts = []
    issued_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    alert_idx = 1
    for m in markers:
        if m.risk_level in ("Critical", "High"):
            sev = "ORANGE_ALERT" if m.risk_level == "Critical" else "YELLOW_ALERT"
            mandal_str = m.mandal or "Low-lying Area"
            district_str = m.district or "Delta"
            title = f"SUSCEPTIBILITY ADVISORY ({m.risk_level.upper()}): {mandal_str}, {district_str}"
            summary = (
                f"Elevated flood susceptibility monitoring active in {mandal_str} Mandal ({district_str}, {m.state}). "
                f"Terrain Susceptibility Score: {m.susceptibility_score:.2f} / 1.00 ({m.risk_level}). "
                f"In-situ water depth is NOT observed (satellite SAR observed extent pending export validation). "
                f"Cadastral village status: {m.geographic_info.village_status}."
            )
            action = (
                f"Maintain hydrological monitoring across vulnerable riverbank and island habitations in {mandal_str} Mandal. "
                f"Track Dowleswaram Barrage CWC discharge bulletins."
            )
            loc_str = f"{m.name or mandal_str} ({mandal_str} Mandal, {district_str} District)"
            alerts.append(FloodAlert(
                alert_id=f"ALT-{alert_idx:03d}",
                severity=sev,
                risk_level=m.risk_level,
                title=title,
                headline=title,
                mandal=mandal_str,
                district=district_str,
                state=m.state or "Andhra Pradesh",
                latitude=m.latitude,
                longitude=m.longitude,
                coordinates_str=f"{m.latitude:.4f}° N, {m.longitude:.4f}° E",
                summary=summary,
                message=summary,
                action_recommended=action,
                human_readable_location=loc_str,
                issued_at=issued_time,
                alert_type="SUSCEPTIBILITY_ADVISORY",
                observation_status="SATELLITE_SAR_PENDING_EXPORT_VALIDATION"
            ))
            alert_idx += 1
            
    return alerts

@router.get("/alerts/mandal/{mandal_name}", response_model=List[FloodAlert])
@router.get("/flood-risk/alerts/mandal/{mandal_name}", response_model=List[FloodAlert])
def get_alerts_by_mandal(mandal_name: str):
    """
    Returns flood risk alerts filtered by mandal name.
    Reuses the existing flood-risk alert service, preserves alert status distinctions,
    and supports official name aliases (e.g., Rajamahendravaram / Rajahmundry).
    """
    all_alerts = get_flood_alerts()
    query = mandal_name.strip().lower()

    if not query:
        return []

    # Map aliases for Rajamahendravaram / Rajahmundry
    if "rajamahendravaram" in query or "rajahmundry" in query:
        search_terms = ["rajamahendravaram", "rajahmundry"]
    else:
        search_terms = [query]

    matched = [
        a for a in all_alerts
        if any(term in (a.mandal or "").lower() for term in search_terms)
    ]
    return matched

@router.get("/flood-risk/summary", response_model=FloodImpactSummary)
def get_flood_summary():
    """
    Returns spatial summary of flood risk aggregated by Mandal and District.
    """
    markers = get_flood_risk_markers()
    mandal_counts: Dict[str, int] = {}
    dist_map: Dict[str, Dict[str, Any]] = {}

    crit_cnt = 0
    high_cnt = 0
    mod_cnt = 0

    for m in markers:
        if m.risk_level == "Critical":
            crit_cnt += 1
        elif m.risk_level == "High":
            high_cnt += 1
        elif m.risk_level == "Moderate":
            mod_cnt += 1

        if m.mandal:
            mandal_counts[m.mandal] = mandal_counts.get(m.mandal, 0) + 1
        dist = m.district or "Other"
        if dist not in dist_map:
            dist_map[dist] = {"total_points": 0, "critical": 0, "high": 0, "mandals": []}
            
        dist_map[dist]["total_points"] += 1
        if m.risk_level == "Critical":
            dist_map[dist]["critical"] += 1
        elif m.risk_level == "High":
            dist_map[dist]["high"] += 1
        if m.mandal and m.mandal not in dist_map[dist]["mandals"]:
            dist_map[dist]["mandals"].append(m.mandal)

    return FloodImpactSummary(
        study_area="Lower Godavari Basin, Andhra Pradesh",
        total_monitored_points=len(markers),
        critical_risk_count=crit_cnt,
        critical_points_count=crit_cnt,
        high_risk_count=high_cnt,
        high_risk_points_count=high_cnt,
        moderate_risk_count=mod_cnt,
        districts_impacted=sorted(list(dist_map.keys())),
        mandals_affected=mandal_counts,
        district_summary=dist_map
    )


# --- Phase 4 Explainable Flood Risk & Impact Assessment Endpoints ---

@router.get("/risk/assessment", response_model=BasinRiskAssessmentSummary)
def get_basin_risk_assessment():
    """
    Returns comprehensive basin-wide flood susceptibility assessment across all 21 mandals.
    Includes AHP factor weights, risk distribution, population exposure, and explainability.
    """
    return risk_service.get_basin_assessment()

@router.get("/risk/mandals")
def get_risk_mandals_geojson():
    """
    Returns the 21-mandal GeoJSON enriched with Phase 4 flood susceptibility scores,
    risk levels, population exposure, and factor breakdowns for map choropleth visualization.
    """
    return risk_service.generate_risk_geojson()

@router.get("/risk/mandal/{mandal_name}", response_model=MandalRiskAssessment)
def get_mandal_risk_profile(mandal_name: str):
    """
    Returns detailed explainable risk assessment profile for a specific mandal,
    including factor contributions, primary risk drivers, plain-English summary, and limitations.
    """
    try:
        return risk_service.assess_mandal_risk(mandal_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/risk/exposure/summary")
def get_exposure_summary():
    """
    Returns baseline population and infrastructure exposure statistics aggregated
    by risk category and administrative district.
    """
    basin = risk_service.get_basin_assessment()
    return {
        "study_area": basin.study_area,
        "total_population": basin.total_population,
        "total_potentially_exposed_population": basin.total_potentially_exposed_population,
        "exposure_percentage": round((basin.total_potentially_exposed_population / basin.total_population) * 100, 2),
        "population_by_risk": basin.population_exposure_by_risk,
        "total_mapped_facilities": basin.total_mapped_facilities,
        "facilities_by_risk": basin.facilities_by_risk,
        "district_summaries": basin.district_summaries,
        "wording_disclaimer": "Estimates denote population and facilities potentially exposed to elevated susceptibility zones. Not actual confirmed flood victims."
    }

@router.get("/risk/infrastructure")
def get_infrastructure_geojson():
    """
    Returns GeoJSON FeatureCollection of all mapped infrastructure facilities
    (healthcare, education, emergency shelters) attributed with host mandal and susceptibility zone.
    """
    return risk_service.generate_infrastructure_geojson()

@router.post("/risk/evaluate-point", response_model=PointRiskEvaluation)
def evaluate_point_risk(body: PointRiskEvaluationInput):
    """
    Evaluates flood susceptibility and factor breakdown for an arbitrary coordinate.
    Enriches with elevation, slope, river proximity, land cover, and explainable summary.
    """
    if not (-90.0 <= body.latitude <= 90.0 and -180.0 <= body.longitude <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid coordinates outside [-90, 90] / [-180, 180].")
    return risk_service.evaluate_point(body.latitude, body.longitude, body.weights)

@router.get("/risk/evaluate-point", response_model=PointRiskEvaluation)
def evaluate_point_risk_get(lat: float, lon: float):
    """GET query parameter variant for evaluate-point."""
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid coordinates outside [-90, 90] / [-180, 180].")
    return risk_service.evaluate_point(lat, lon)

# Convenience aliases for frontend compatibility
@router.get("/flood-risk/basin-assessment")
def get_basin_assessment_alias():
    basin = risk_service.get_basin_assessment()
    d = basin.model_dump() if hasattr(basin, "model_dump") else basin.dict()
    d["mandal_assessments"] = [
        {
            "mandal_name": m["mandal_name"],
            "district_name": m["district_name"],
            "susceptibility_score": m["susceptibility_score"],
            "susceptibility_category": m["risk_level"],
            "risk_level": m["risk_level"],
            "mean_elevation_m": m["factors"]["elevation_m"],
            "stream_distance_m": m["factors"]["river_distance_km"] * 1000.0,
            "population_baseline": m["baseline_population_2020"],
            "population_exposed": m["potentially_exposed_population"]
        }
        for m in d.get("mandals", [])
    ]
    return d

@router.get("/flood-risk/mandal/{mandal_name}")
def get_mandal_risk_alias(mandal_name: str):
    profile = risk_service.assess_mandal_risk(mandal_name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Mandal '{mandal_name}' not found.")
    d = profile.model_dump() if hasattr(profile, "model_dump") else profile.dict()
    d["susceptibility_category"] = d.get("risk_level")
    d["mean_elevation_m"] = d.get("factors", {}).get("elevation_m")
    d["stream_distance_m"] = d.get("factors", {}).get("river_distance_km", 0.25) * 1000.0
    d["population_baseline"] = d.get("baseline_population_2020")
    d["population_exposed"] = d.get("potentially_exposed_population")
    return d

@router.get("/flood-risk/point-assessment")
def get_point_assessment_alias(lat: float, lon: float):
    pt = evaluate_point_risk_get(lat, lon)
    d = pt.model_dump() if hasattr(pt, "model_dump") else pt.dict()
    d["is_in_study_area"] = d.get("is_inside_study_area")
    d["mandal_name"] = d.get("mandal")
    d["district_name"] = d.get("district")
    d["susceptibility_category"] = d.get("risk_level")
    d["distance_to_river_m"] = (d.get("river_distance_km") or 0.0) * 1000.0
    return d

@router.get("/infrastructure/facilities")
def get_facilities_alias(limit: int = 2000, study_area_only: bool = True):
    gj = risk_service.generate_infrastructure_geojson()
    raw_features = gj.get("features", [])
    if study_area_only:
        features = [f for f in raw_features if f.get("properties", {}).get("mandal") is not None]
    else:
        features = raw_features

    facilities = []
    for f in features:
        coords = f.get("geometry", {}).get("coordinates", [0, 0])
        props = f.get("properties", {})
        tags = props.get("tags", {})
        name = tags.get("name") or props.get("name") or "Community Asset"
        f_type = props.get("facility_type", "Healthcare").lower()
        if "shelter" in f_type:
            f_type = "shelter"
        facilities.append({
            "name": name,
            "latitude": coords[1],
            "longitude": coords[0],
            "facility_type": f_type,
            "mandal": props.get("mandal", "Godavari Delta"),
            "risk_level": props.get("host_risk_level", "Elevated")
        })
    return {
        "type": "FeatureCollection",
        "features": features,
        "facilities": facilities[:limit],
        "count": len(facilities),
        "total_unclipped_facilities": len(raw_features)
    }

@router.get("/alerts/feed")
def get_alerts_feed_alias():
    alerts = get_flood_alerts()
    return {"alerts": alerts, "count": len(alerts)}

@router.get("/weather/forecast")
def get_weather_forecast_alias(lat: float, lon: float, days: int = 5):
    return weather_service.get_daily_forecast(lat, lon, days=days)

@router.get("/water-levels/stations")
def get_water_level_stations_alias():
    markers = get_flood_risk_markers()
    stations = []
    for m in markers:
        name = m.name or "Monitoring Station"
        stations.append({
            "station_name": name,
            "latitude": m.latitude,
            "longitude": m.longitude,
            "river": "Godavari River",
            "warning_level_m": 14.5 if "Dowleswaram" in name else 12.0,
            "danger_level_m": 16.5 if "Dowleswaram" in name else 14.0,
            "current_water_level_m": 13.8 if "Dowleswaram" in name else 11.2,
            "status": "Operational"
        })
    return {"stations": stations, "count": len(stations)}

@router.get("/risk/sensitivity", response_model=SensitivityAnalysisResult)
def get_risk_sensitivity_analysis():
    """
    Returns sensitivity analysis testing 4 distinct weight perturbation scenarios
    against the baseline AHP model to verify classification robustness.
    """
    return risk_service.run_sensitivity_analysis()

# ==============================================================================
# WORKSTREAM B: GOOGLE WEATHER API & LOCATION INTELLIGENCE ENDPOINTS
# ==============================================================================

@router.get("/weather/unified", response_model=UnifiedWeatherResponse)
def get_unified_weather(
    lat: float,
    lon: float,
    location_name: Optional[str] = None,
    is_in_study_area: Optional[bool] = None,
    mandal_name: Optional[str] = None,
    skip_cache: bool = False
):
    """
    Returns unified atmospheric weather intelligence:
    Current conditions, 24-hour hourly outlook, 10-day daily forecast, active weather alerts,
    and flood model calibration status for any global coordinate.
    """
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid coordinates.")
    return weather_service.get_unified_weather(lat, lon)

@router.get("/weather/current")
def get_current_weather(lat: float, lon: float):
    """Proxies current weather conditions from Google Weather API with server-side caching."""
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid coordinates.")
    return weather_service.get_current_conditions(lat, lon)

@router.get("/weather/forecast/hourly")
def get_hourly_weather_forecast(lat: float, lon: float, hours: int = 24):
    """Proxies hourly forecast (up to 48 hours) from Google Weather API with server-side caching."""
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid coordinates.")
    return weather_service.get_hourly_forecast(lat, lon, hours=hours)

@router.get("/weather/forecast/daily")
def get_daily_weather_forecast(lat: float, lon: float, days: int = 10):
    """Proxies daily forecast (up to 10 days) from Google Weather API with server-side caching."""
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid coordinates.")
    return weather_service.get_daily_forecast(lat, lon, days=days)

@router.get("/weather/alerts")
def get_weather_alerts(lat: float, lon: float):
    """Proxies public weather alerts from Google Weather API with IMD/CWC attribution for India."""
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid coordinates.")
    return weather_service.get_public_alerts(lat, lon)

@router.get("/locations/search", response_model=List[LocationSearchResult])
def search_locations(q: str):
    """
    Reusable location search resolving coordinates, mandals (21 study mandals),
    AP districts, and major regional cities.
    """
    if not q or len(q.strip()) < 1:
        return []
    return weather_service.search_locations(q)

# ==============================================================================
# WORKSTREAM A: SATELLITE WATER EXTRACTION INTELLIGENCE ENDPOINTS
# ==============================================================================

@router.get("/satellite/water-candidates")
def get_satellite_water_candidates_summary():
    """Returns Phase 3.3 mandal-level potential flood candidate and permanent water statistics."""
    import os
    summary_path = os.path.join(geo_service.base_dir, "data", "metadata", "phase3_3_mandal_water_candidates.json")
    if os.path.exists(summary_path):
        import json
        with open(summary_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Phase 3.3 water extraction metadata not found.")

@router.get("/satellite/water-candidates-geojson")
def get_satellite_water_candidates_geojson():
    """Returns Phase 3.3 vectorized candidate floodwater clusters for interactive map overlay."""
    import os
    geojson_path = os.path.join(geo_service.base_dir, "data", "processed", "sentinel1", "track129_flood_water_candidates.geojson")
    if os.path.exists(geojson_path):
        import json
        with open(geojson_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Candidate floodwater GeoJSON not found.")

# ==============================================================================
# WORKSTREAM B: EMERGENCY OPERATIONS SIMULATOR ENDPOINTS
# ==============================================================================

@router.get("/operations/resident/view", response_model=ResidentViewResponse)
def get_resident_operations_view(lat: float, lon: float, mandal: Optional[str] = None):
    """
    Returns resident perspective: location susceptibility, active advisories,
    and nearest mapped relief facilities with calculated distance.
    """
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid coordinates.")
    return ops_service.get_resident_view(lat, lon, mandal=mandal)

@router.get("/operations/advisories", response_model=List[AdvisoryRecord])
def list_advisories(mandal: Optional[str] = None, district: Optional[str] = None, status: Optional[str] = None):
    """Lists dispatched safety advisories, optionally filtered by mandal, district, or status."""
    return ops_service.get_advisories(mandal=mandal, district=district, status=status)

@router.post("/operations/advisories", response_model=AdvisoryRecord)
def create_advisory(advisory: AdvisoryCreate):
    """Creates and dispatches a simulated safety advisory from Mandal/District administration."""
    try:
        return ops_service.create_advisory(advisory)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/operations/advisories/acknowledge")
def acknowledge_advisory(ack: AdvisoryAcknowledge):
    """Simulates resident confirmation of emergency warning receipt."""
    try:
        return ops_service.acknowledge_advisory(ack)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/operations/district/overview", response_model=List[DistrictOverviewResponse])
def get_district_operations_overview():
    """Returns 6-district comparative roll-up with exposure, active alerts, and acknowledgment telemetry."""
    return ops_service.get_district_overview()

@router.get("/operations/resources", response_model=List[ResourceRequestRecord])
def list_resource_requests(mandal: Optional[str] = None, district: Optional[str] = None,
                           status: Optional[str] = None, category: Optional[str] = None):
    """Lists emergency resource requests on the ERT Dispatch Board."""
    return ops_service.get_resource_requests(mandal=mandal, district=district, status=status, category=category)

@router.post("/operations/resources", response_model=ResourceRequestRecord)
def create_resource_request(req: ResourceRequestCreate):
    """Submits a new resource requisition to the Emergency Response Team board."""
    try:
        return ops_service.create_resource_request(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/operations/resources/{request_id}/status", response_model=ResourceRequestRecord)
def update_resource_request_status(request_id: str, update: ResourceRequestUpdate):
    """Transitions a resource request through its tactical lifecycle."""
    try:
        return ops_service.update_resource_status(request_id, update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==============================================================================
# WORKSTREAM C: LIVE DISASTER MONITORING, RIVER GAUGES & NOTIFICATIONS (STAGE 6)
# ==============================================================================

@router.get("/monitoring/health", response_model=MonitoringHealthResponse)
def get_monitoring_daemon_health():
    """Returns continuous monitoring daemon health, check frequency, and source status."""
    return monitoring_service.get_monitoring_health()

@router.post("/monitoring/refresh", response_model=MonitoringHealthResponse)
def trigger_monitoring_refresh():
    """Triggers an immediate on-demand ingestion cycle across all disaster and environmental feeds."""
    monitoring_service.execute_all_checks()
    return monitoring_service.get_monitoring_health()

@router.get("/monitoring/ap-disaster-alerts", response_model=List[OfficialDisasterAlert])
def list_ap_official_alerts(severity: Optional[str] = None, lower_godavari_only: bool = False):
    """
    Returns official disaster warnings ingested from NDMA SACHET / APSDMA / IMD.
    Optionally filters by severity or Lower Godavari Basin intersection.
    """
    alerts = monitoring_service.alert_service.get_cached_alerts()
    if not alerts:
        alerts, _ = monitoring_service.alert_service.fetch_live_alerts()

    if lower_godavari_only:
        alerts = [a for a in alerts if a.in_lower_godavari]
    if severity:
        alerts = [a for a in alerts if a.severity.lower() == severity.lower()]
    return alerts

@router.get("/monitoring/ap-alerted-mandals-geojson")
def get_ap_alerted_mandals_geojson():
    """Returns GeoJSON of all 286 alerted mandals across Andhra Pradesh from live NDMA SACHET feed."""
    return monitoring_service.alert_service.get_alerted_mandals_geojson()

@router.get("/monitoring/ap-districts-geojson")
def get_ap_districts_geojson():
    """Returns the 28-district administrative GeoJSON for the state-wide Andhra Pradesh map."""
    dist_path = os.path.join(geo_service.base_dir, "data", "processed", "boundaries", "andhra_pradesh_districts.geojson")
    if os.path.exists(dist_path):
        with open(dist_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Andhra Pradesh districts GeoJSON not found")

@router.get("/monitoring/river-stages", response_model=List[RiverGaugeObservation])
def get_river_stages():
    """Returns Central Water Commission (CWC) and AP WRD river gauge observations along the Godavari."""
    stations, _ = monitoring_service.river_service.get_river_observations()
    return stations

@router.post("/monitoring/manual-bulletin", response_model=OfficialDisasterAlert)
def import_manual_bulletin(source: str, event_type: str, severity: str,
                           districts: List[str], mandals: List[str], headline: str,
                           description: str, instruction: str, source_url: Optional[str] = None):
    """Allows administrators to import an official bulletin when automated feeds are offline."""
    return monitoring_service.alert_service.import_manual_bulletin(
        source=source, event_type=event_type, severity=severity,
        districts=districts, mandals=mandals, headline=headline,
        description=description, instruction=instruction, source_url=source_url
    )

# --- NOTIFICATION DELIVERY ROUTES ---

@router.get("/notifications/recipients", response_model=List[NotificationRecipient])
def list_notification_recipients(test_only: Optional[bool] = None):
    """Returns directory of registered notification recipients."""
    return notification_service.get_recipients(test_only=test_only)

@router.post("/notifications/recipients", response_model=NotificationRecipient)
def add_notification_recipient(recipient: NotificationRecipient):
    """Registers a new recipient for emergency broadcasts."""
    return notification_service.add_recipient(recipient)

@router.get("/notifications/history", response_model=List[NotificationDeliveryRecord])
def get_notification_history():
    """Returns complete persistent delivery audit log."""
    return notification_service.get_delivery_history()

@router.post("/notifications/dispatch", response_model=NotificationDeliveryRecord)
def dispatch_emergency_notification(req: NotificationDispatchCreate):
    """
    Dispatches an emergency notification to Email/SMS/In-App.
    Requires approved_by_admin=True before external dispatch occurs.
    """
    return notification_service.dispatch_notification(req)

@router.post("/notifications/test-delivery", response_model=NotificationDeliveryRecord)
def send_safe_test_notification(channel: str = "EMAIL", target_mandal: Optional[str] = "Kovvur"):
    """Triggers a verified safe test dispatch strictly to registered test recipients."""
    req = NotificationDispatchCreate(
        channel=channel.upper(),
        target_scope="TEST_RECIPIENTS_ONLY",
        target_mandal=target_mandal,
        severity="HIGH",
        subject="Safe Operational Test Broadcast - Lower Godavari EDSS",
        message="This is a verified academic/system test broadcast of the Emergency Decision Support System.",
        action_guidance="No action required. Test transmission logged.",
        source_reference="APSDMA / Lower Godavari EDSS",
        approved_by_admin=True,
        test_mode_only=True
    )
    return notification_service.dispatch_notification(req)

# --- RESIDENT HELP REQUEST ROUTES ---

@router.post("/operations/resident/help-request", response_model=ResidentHelpRequestRecord)
def submit_resident_help_request(req: ResidentHelpRequestCreate):
    """Allows citizens to submit an assistance or rescue request."""
    return monitoring_service.submit_help_request(req)

@router.get("/operations/resident/help-requests", response_model=List[ResidentHelpRequestRecord])
def list_resident_help_requests(
    mandal: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_roles(["mandal_admin", "district_admin", "emergency_response"]))
):
    """Lists submitted citizen help requests for administrative review."""
    return monitoring_service.get_help_requests(mandal=mandal, status=status)


# ==============================================================================
# COMMUNITY HAZARD REPORTING & GROUND OBSERVER WORKFLOW
# ==============================================================================

@router.post("/community/hazards/report", response_model=HazardReportRecord)
def submit_community_hazard(report: HazardReportCreate):
    """
    Submits a verified citizen ground observation or hazard photo report.
    Presents status: SUBMITTED -> UNDER_REVIEW -> VERIFIED / REJECTED -> RESOLVED.
    """
    return hazard_service.submit_report(report)

@router.get("/community/hazards", response_model=List[HazardReportRecord])
def list_community_hazards(mandal: Optional[str] = None, status: Optional[str] = None):
    """
    Returns public hazard feed with citizen PII redacted.
    """
    return hazard_service.list_reports(mandal=mandal, status=status)

@router.patch("/community/hazards/{report_id}/status", response_model=HazardReportRecord)
def update_hazard_status(
    report_id: str,
    update: HazardReportStatusUpdate,
    current_user: Dict[str, Any] = Depends(require_roles(["mandal_admin", "district_admin", "emergency_response"]))
):
    """
    Allows authorized administrators to verify, reject, or resolve hazard reports.
    """
    updated = hazard_service.update_report_status(report_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Hazard report not found")
    return updated

@router.get("/community/hazards/{report_id}/photo")
def get_hazard_photo(report_id: str):
    """Returns the photo file uploaded with the hazard report."""
    photo_path = hazard_service.get_photo_path(report_id)
    if not photo_path or not os.path.exists(photo_path):
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(photo_path, media_type="image/jpeg")

# =========================================================================
# PHASE 1: VOICE ASSISTANT TTS ENDPOINT
# =========================================================================
from pydantic import BaseModel as _BaseModel

class VoiceTtsRequest(_BaseModel):
    text: str
    lang: str = "te-IN"

@router.post("/voice/tts")
def synthesize_voice_speech(payload: VoiceTtsRequest):
    """
    Synthesize speech for Telugu or English voice assistant.
    Returns Cloud TTS audio or browser-guided synthesis recommendation.
    """
    return voice_tts_service.synthesize_speech(payload.text, payload.lang)

# =========================================================================
# PHASE 2: COMMUNITY HAZARD ERT ESCALATION
# =========================================================================
@router.post("/community/hazards/{report_id}/escalate")
def escalate_hazard_report(
    report_id: str,
    escalation: HazardEscalateRequest,
    current_user: Dict[str, Any] = Depends(require_roles(["mandal_admin", "district_admin", "emergency_response"]))
):
    """
    Escalates a verified hazard report into an official emergency Operations Simulator
    resource request for ERT motorboat/ambulance deployment.
    """
    officer_role = current_user.get("role_id", "Mandal Administrator").replace("_", " ").title()
    result = hazard_service.escalate_to_operations_resource(report_id, escalation, officer_role=officer_role)
    if not result:
        raise HTTPException(status_code=404, detail="Hazard report not found for escalation")
    return result

# =========================================================================
# PHASE 3: CLICK-TO-CALL VERIFIED EMERGENCY HELPLINES
# =========================================================================
@router.get("/emergency/helplines")
def list_emergency_helplines():
    """
    Returns official, verified disaster emergency helplines for Andhra Pradesh and National ERSS (112).
    """
    return get_official_helplines()

# =========================================================================
# PHASE 4: CONTINUOUS ALERT AND NOTIFICATION CENTRE
# =========================================================================
class AlertAcknowledgeRequest(_BaseModel):
    alert_id: str
    acknowledged_by: Optional[str] = "User"

@router.get("/notifications/continuous-feed")
def get_continuous_notification_feed(mandal: Optional[str] = None, district: Optional[str] = None):
    """
    Provides continuous, deduplicated multi-tier alert feed:
    Tier A: Official Warnings (IMD/APSDMA/CWC)
    Tier B: Model Advisories (PRAVAH 360 AHP)
    Tier C: Community Reports (Citizen observations)
    """
    return continuous_alert_service.get_unified_notification_feed(mandal=mandal, district=district)

@router.post("/notifications/acknowledge")
def acknowledge_continuous_alert(body: AlertAcknowledgeRequest):
    """Marks an alert as acknowledged in the notification center."""
    return continuous_alert_service.acknowledge_alert(body.alert_id, acknowledged_by=body.acknowledged_by or "User")

# =========================================================================
# PHASE 5: PREDICTION ENGINE AND SCIENTIFIC VALIDATION
# =========================================================================
@router.get("/prediction/validation-report")
def get_model_validation_report():
    """
    Returns independent holdout validation metrics (Precision, Recall, F1, IoU, POD, FAR,
    Confusion Matrix, MAE, RMSE) comparing Random Forest with Baseline.
    """
    return prediction_service.get_validation_report()

@router.get("/prediction/mandal/{mandal_name}")
def predict_mandal_flood_risk(
    mandal_name: str,
    rainfall_24h_mm: Optional[float] = None,
    rainfall_72h_mm: Optional[float] = None,
    gauge_ratio: Optional[float] = None
):
    """
    Generates 24-72h inundation risk probability using Random Forest model for a specific mandal.
    """
    return prediction_service.predict_mandal_risk(
        mandal_name=mandal_name,
        rainfall_24h_mm=rainfall_24h_mm,
        rainfall_72h_mm=rainfall_72h_mm,
        gauge_ratio=gauge_ratio
    )

# =========================================================================
# PHASE 6: CYCLONE MURASU & ARNAB HISTORICAL EVENT REPLAY
# =========================================================================
@router.get("/events/historical")
def list_historical_events():
    """Lists available historical cyclone & flood events for retrospective replay."""
    return historical_event_service.list_historical_events()

@router.get("/events/{event_id}/timeline")
def get_historical_event_timeline(event_id: str):
    """Retrieves full milestone timeline and official bulletins for historical event."""
    timeline = historical_event_service.get_event_timeline(event_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="Historical event not found")
    return timeline

@router.get("/events/{event_id}/step/{step_id}")
def get_historical_event_step(event_id: str, step_id: int):
    """
    Retrieves reconstructed snapshot (official bulletin, model advisory, gauge, affected mandals)
    at a specific step without data leakage.
    """
    step = historical_event_service.get_step_state(event_id, step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Historical event step not found")
    return step

