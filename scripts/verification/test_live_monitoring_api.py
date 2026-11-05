import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json

from backend.app.api.endpoints import (
    get_monitoring_daemon_health,
    trigger_monitoring_refresh,
    list_ap_official_alerts,
    get_ap_alerted_mandals_geojson,
    get_river_stages,
    send_safe_test_notification,
    get_notification_history,
    submit_resident_help_request,
    list_resident_help_requests
)
from backend.app.schemas.monitoring import ResidentHelpRequestCreate

def test_monitoring_and_notifications():
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== 1. Testing Live Monitoring Health & Ingestion ===")
    health = get_monitoring_daemon_health()
    print(f"Daemon Status: {health.daemon_status} | Overall Health: {health.overall_health}")
    print(f"Total Checks: {health.total_checks_executed} | Uptime: {health.uptime_seconds}s")
    print("Monitored Sources:")
    for sid, s in health.sources.items():
        print(f"  * {sid}: Status={s.status}, Records={s.records_count}, Stale={s.stale}")
        assert s.status in ("LIVE", "AVAILABLE", "API_KEY_NOT_CONFIGURED", "STALE")

    print("\n=== 2. Testing AP Official Disaster Alerts ===")
    alerts = list_ap_official_alerts()
    print(f"Official Alerts Ingested: {len(alerts)}")
    assert len(alerts) >= 5, f"Expected >= 5 live alerts from NDMA SACHET, got {len(alerts)}"
    for a in alerts[:3]:
        print(f"  * [{a.severity}] {a.headline} (Source: {a.source})")
        print(f"    - Mandals: {len(a.affected_mandals)}, Lower Godavari: {a.in_lower_godavari}")
        assert a.source != ""
        assert a.status == "ACTIVE"

    # Test Lower Godavari filtering
    lg_alerts = list_ap_official_alerts(lower_godavari_only=True)
    print(f"Alerts intersecting Lower Godavari: {len(lg_alerts)}")

    print("\n=== 3. Testing NDMA SACHET Mandals GeoJSON ===")
    sachet_geojson = get_ap_alerted_mandals_geojson()
    features = sachet_geojson.get("features", [])
    print(f"GeoJSON Alerted Mandals Features Count: {len(features)}")
    assert len(features) >= 100, f"Expected >= 100 features from live feed, got {len(features)}"

    print("\n=== 4. Testing CWC River & Reservoir Monitoring ===")
    river_stations = get_river_stages()
    print(f"Hydrological River Stations Count: {len(river_stations)}")
    assert len(river_stations) >= 4
    for st in river_stations:
        print(f"  * {st.station_name} ({st.river}): Level={st.current_water_level_m}m, Warning={st.warning_level_m}m, Danger={st.danger_level_m}m -> {st.flood_status}")
        assert st.warning_level_m > 0
        assert st.danger_level_m > st.warning_level_m

    print("\n=== 5. Testing Provider-Based Notification Delivery (Safe Test Mode) ===")
    test_delivery = send_safe_test_notification(channel="EMAIL", target_mandal="Kovvur")
    print(f"Dispatch ID: {test_delivery.dispatch_id} | Status: {test_delivery.status} | Provider: {test_delivery.provider_name}")
    assert test_delivery.status in ("DELIVERED", "SENT_TO_PROVIDER")
    assert test_delivery.test_mode is True

    # Check delivery audit log
    history = get_notification_history()
    print(f"Persistent Delivery Log Count: {len(history)}")
    assert len(history) >= 2
    assert any(h.dispatch_id == test_delivery.dispatch_id for h in history)

    print("\n=== 6. Testing Resident Emergency Assistance Help Request ===")
    help_req = submit_resident_help_request(ResidentHelpRequestCreate(
        mandal="Kovvur",
        district="East Godavari",
        contact_name="G. Subba Rao",
        contact_phone="+91 98480 12345",
        location_description="Near Kumaradevam Lanka Ferry Point",
        latitude=17.014,
        longitude=81.730,
        urgency="CRITICAL",
        assistance_type="Evacuation",
        num_persons_affected=6,
        situation_notes="Water entering home from river backflow. Need boat evacuation to high school."
    ))
    print(f"Created Resident Help Request: {help_req.request_id} for {help_req.mandal} (Status: {help_req.status})")
    assert help_req.request_id.startswith("HLP-")

    # List requests
    all_help = list_resident_help_requests(mandal="Kovvur")
    print(f"Help requests for Kovvur: {len(all_help)}")
    assert any(r.request_id == help_req.request_id for r in all_help)

    print("\n>>> ALL LIVE MONITORING & NOTIFICATION TESTS PASSED 100%! <<<")

if __name__ == "__main__":
    test_monitoring_and_notifications()
