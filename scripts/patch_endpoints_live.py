import os

endpoints_path = os.path.join("backend", "app", "api", "endpoints.py")
with open(endpoints_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
old_import = "from backend.app.services.emergency_operations_service import EmergencyOperationsService"
new_import = """from backend.app.services.emergency_operations_service import EmergencyOperationsService
from backend.app.services.live_monitoring_service import LiveMonitoringService
from backend.app.services.notification_service import NotificationDeliveryService
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
)"""

assert old_import in content, "old_import not found"
content = content.replace(old_import, new_import, 1)

# 2. Service Instantiation
old_inst = "ops_service = EmergencyOperationsService(geo_service=geo_service, risk_service=risk_service)"
new_inst = """ops_service = EmergencyOperationsService(geo_service=geo_service, risk_service=risk_service)
notification_service = NotificationDeliveryService()
monitoring_service = LiveMonitoringService(weather_service=weather_service)"""

assert old_inst in content, "old_inst not found"
content = content.replace(old_inst, new_inst, 1)

# 3. New Endpoints
new_endpoints = """

# ==============================================================================
# WORKSTREAM C: LIVE DISASTER MONITORING, RIVER GAUGES & NOTIFICATIONS (STAGE 6)
# ==============================================================================

@router.get("/monitoring/health", response_model=MonitoringHealthResponse)
def get_monitoring_daemon_health():
    \"\"\"Returns continuous monitoring daemon health, check frequency, and source status.\"\"\"
    return monitoring_service.get_monitoring_health()

@router.post("/monitoring/refresh", response_model=MonitoringHealthResponse)
def trigger_monitoring_refresh():
    \"\"\"Triggers an immediate on-demand ingestion cycle across all disaster and environmental feeds.\"\"\"
    monitoring_service.execute_all_checks()
    return monitoring_service.get_monitoring_health()

@router.get("/monitoring/ap-disaster-alerts", response_model=List[OfficialDisasterAlert])
def list_ap_official_alerts(severity: Optional[str] = None, lower_godavari_only: bool = False):
    \"\"\"
    Returns official disaster warnings ingested from NDMA SACHET / APSDMA / IMD.
    Optionally filters by severity or Lower Godavari Basin intersection.
    \"\"\"
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
    \"\"\"Returns GeoJSON of all 286 alerted mandals across Andhra Pradesh from live NDMA SACHET feed.\"\"\"
    return monitoring_service.alert_service.get_alerted_mandals_geojson()

@router.get("/monitoring/ap-districts-geojson")
def get_ap_districts_geojson():
    \"\"\"Returns the 28-district administrative GeoJSON for the state-wide Andhra Pradesh map.\"\"\"
    dist_path = os.path.join(geo_service.base_dir, "data", "processed", "boundaries", "andhra_pradesh_districts.geojson")
    if os.path.exists(dist_path):
        with open(dist_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Andhra Pradesh districts GeoJSON not found")

@router.get("/monitoring/river-stages", response_model=List[RiverGaugeObservation])
def get_river_stages():
    \"\"\"Returns Central Water Commission (CWC) and AP WRD river gauge observations along the Godavari.\"\"\"
    stations, _ = monitoring_service.river_service.get_river_observations()
    return stations

@router.post("/monitoring/manual-bulletin", response_model=OfficialDisasterAlert)
def import_manual_bulletin(source: str, event_type: str, severity: str,
                           districts: List[str], mandals: List[str], headline: str,
                           description: str, instruction: str, source_url: Optional[str] = None):
    \"\"\"Allows administrators to import an official bulletin when automated feeds are offline.\"\"\"
    return monitoring_service.alert_service.import_manual_bulletin(
        source=source, event_type=event_type, severity=severity,
        districts=districts, mandals=mandals, headline=headline,
        description=description, instruction=instruction, source_url=source_url
    )

# --- NOTIFICATION DELIVERY ROUTES ---

@router.get("/notifications/recipients", response_model=List[NotificationRecipient])
def list_notification_recipients(test_only: Optional[bool] = None):
    \"\"\"Returns directory of registered notification recipients.\"\"\"
    return notification_service.get_recipients(test_only=test_only)

@router.post("/notifications/recipients", response_model=NotificationRecipient)
def add_notification_recipient(recipient: NotificationRecipient):
    \"\"\"Registers a new recipient for emergency broadcasts.\"\"\"
    return notification_service.add_recipient(recipient)

@router.get("/notifications/history", response_model=List[NotificationDeliveryRecord])
def get_notification_history():
    \"\"\"Returns complete persistent delivery audit log.\"\"\"
    return notification_service.get_delivery_history()

@router.post("/notifications/dispatch", response_model=NotificationDeliveryRecord)
def dispatch_emergency_notification(req: NotificationDispatchCreate):
    \"\"\"
    Dispatches an emergency notification to Email/SMS/In-App.
    Requires approved_by_admin=True before external dispatch occurs.
    \"\"\"
    return notification_service.dispatch_notification(req)

@router.post("/notifications/test-delivery", response_model=NotificationDeliveryRecord)
def send_safe_test_notification(channel: str = "EMAIL", target_mandal: Optional[str] = "Kovvur"):
    \"\"\"Triggers a verified safe test dispatch strictly to registered test recipients.\"\"\"
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
    \"\"\"Allows citizens to submit an assistance or rescue request.\"\"\"
    return monitoring_service.submit_help_request(req)

@router.get("/operations/resident/help-requests", response_model=List[ResidentHelpRequestRecord])
def list_resident_help_requests(mandal: Optional[str] = None, status: Optional[str] = None):
    \"\"\"Lists submitted citizen help requests for administrative review.\"\"\"
    return monitoring_service.get_help_requests(mandal=mandal, status=status)
"""

content = content.rstrip() + new_endpoints + "\n"

with open(endpoints_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully patched backend/app/api/endpoints.py with Live Monitoring and Notification endpoints!")
