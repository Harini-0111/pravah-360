import sys
import os
sys.path.insert(0, os.path.abspath("."))
import json
from backend.app.api.endpoints import (
    get_resident_operations_view,
    list_advisories,
    create_advisory,
    acknowledge_advisory,
    get_district_operations_overview,
    list_resource_requests,
    create_resource_request,
    update_resource_request_status
)
from backend.app.schemas.operations import (
    AdvisoryCreate,
    AdvisoryAcknowledge,
    ResourceRequestCreate,
    ResourceRequestUpdate
)

def test_operations():
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== 1. Testing Resident Operations View ===")
    rv = get_resident_operations_view(16.985, 81.78, "Rajamahendravaram")
    print(f"Location: {rv.location_name}")
    print(f"Tier: {rv.susceptibility_tier}, Score: {rv.susceptibility_score}")
    print(f"Active Advisories: {len(rv.active_advisories)}")
    print(f"Nearest Facilities: {len(rv.nearest_facilities)}")
    assert len(rv.nearest_facilities) > 0
    assert rv.susceptibility_tier in ("Very High", "High", "Moderate", "Low")
    for f in rv.nearest_facilities[:2]:
        print(f" - {f.name} ({f.facility_type}, {f.distance_km} km away)")

    print("\n=== 2. Testing District Operations Overview ===")
    d_ov = get_district_operations_overview()
    print(f"Total Districts: {len(d_ov)}")
    assert len(d_ov) == 6, f"Expected 6 districts, got {len(d_ov)}"
    for d in d_ov:
        print(f" - {d.district}: {d.total_mandals} mandals, {d.exposed_population:,} exposed pop ({d.exposure_percentage}%), {d.active_advisories_count} active advisories, {d.acknowledgment_rate_pct}% ack rate")
        assert d.total_mandals > 0
        assert d.total_population > 0

    print("\n=== 3. Testing ERT Resource Board Lifecycle ===")
    res_list = list_resource_requests()
    assert len(res_list) >= 6
    print(f"Total initial requests: {len(res_list)}")
    sample_req = res_list[0]
    print(f"Request: {sample_req.request_id} ({sample_req.category}) in {sample_req.mandal} - Status: {sample_req.current_status}")
    
    # Transition status
    up = update_resource_request_status(
        sample_req.request_id,
        ResourceRequestUpdate(status="On Scene", note="Field teams confirmed on scene", updated_by="Dispatcher-Test")
    )
    print(f"Updated status: {up.current_status}")
    assert up.current_status == "On Scene"

    # Create new resource request
    new_req = create_resource_request(ResourceRequestCreate(
        mandal="Polavaram",
        district="Eluru",
        category="Rescue boats",
        quantity=6,
        unit="motorized boats",
        priority="CRITICAL",
        reason="Assisting submerged tribal hamlet evacuation near gorge",
        requester_role="ITDA Project Officer"
    ))
    print(f"Created new resource request: {new_req.request_id} for {new_req.mandal}")
    assert new_req.request_id.startswith("RES-")

    print("\n=== 4. Testing Mandal Advisory Dispatch & Resident Acknowledgment ===")
    new_adv = create_advisory(AdvisoryCreate(
        mandal="Kovvur",
        district="East Godavari",
        target_tiers=["Very High", "High"],
        priority="CRITICAL",
        headline="Kumaradevam Low-Lying Embankment Reinforcement",
        message="Emergency sandbagging along vulnerable 1.2km stretch. Residents within 200m move to high school.",
        action_recommended="Report to Kovvur Cyclone Shelter immediately.",
        dispatched_by="Tahsildar Kovvur"
    ))
    print(f"Created advisory: {new_adv.advisory_id} for {new_adv.mandal}")
    assert new_adv.advisory_id.startswith("ADV-")
    assert new_adv.stats["queued"] > 0

    # Acknowledge
    ack_res = acknowledge_advisory(AdvisoryAcknowledge(
        advisory_id=new_adv.advisory_id,
        resident_identifier="Resident-Test-01",
        mandal="Kovvur",
        district="East Godavari",
        latitude=17.014,
        longitude=81.730
    ))
    print("Acknowledgment result:", ack_res["status"], "| stats:", ack_res["updated_stats"])
    assert ack_res["status"] == "SUCCESS"
    assert ack_res["updated_stats"]["acknowledged_simulated"] == 1

    print("\n>>> ALL EMERGENCY OPERATIONS TESTS PASSED! <<<")

if __name__ == "__main__":
    test_operations()
