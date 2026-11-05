import sys
import os
import urllib.request
import urllib.parse
import json

def test_live_server():
    sys.stdout.reconfigure(encoding="utf-8")
    base_url = "http://127.0.0.1:8000"

    print("=== Testing Live Server Endpoints ===")
    
    # 1. Health
    with urllib.request.urlopen(f"{base_url}/api/v1/health") as r:
        print(f"GET /api/v1/health: {r.status}")
        assert r.status == 200

    # 2. Mandal alerts: Rajamahendravaram & Rajahmundry
    for name in ["Rajahmundry", "Rajamahendravaram", "Kovvur"]:
        url = f"{base_url}/api/v1/alerts/mandal/{urllib.parse.quote(name)}"
        with urllib.request.urlopen(url) as r:
            data = json.loads(r.read().decode("utf-8"))
            print(f"GET /api/v1/alerts/mandal/{name}: {r.status}, {len(data)} alerts")
            assert len(data) >= 1

    # 3. Operations: Resident view
    url_res = f"{base_url}/api/v1/operations/resident/view?lat=16.985&lon=81.78&mandal=Rajamahendravaram"
    with urllib.request.urlopen(url_res) as r:
        data = json.loads(r.read().decode("utf-8"))
        print(f"GET /api/v1/operations/resident/view: {r.status}")
        print(f" - Location: {data.get('location_name')}")
        print(f" - Tier: {data.get('susceptibility_tier')}, Score: {data.get('susceptibility_score')}")
        print(f" - Active Advisories: {len(data.get('active_advisories', []))}")
        print(f" - Nearest Facilities: {len(data.get('nearest_facilities', []))}")
        assert len(data.get('nearest_facilities', [])) > 0

    # 4. Operations: District overview
    url_dist = f"{base_url}/api/v1/operations/district/overview"
    with urllib.request.urlopen(url_dist) as r:
        data = json.loads(r.read().decode("utf-8"))
        print(f"GET /api/v1/operations/district/overview: {r.status}, {len(data)} districts")
        assert len(data) == 6
        for d in data:
            print(f"   * {d['district']}: {d['total_mandals']} mandals, {d['exposed_population']:,} exp pop")

    # 5. Operations: Resource list
    url_ert = f"{base_url}/api/v1/operations/resources"
    with urllib.request.urlopen(url_ert) as r:
        data = json.loads(r.read().decode("utf-8"))
        print(f"GET /api/v1/operations/resources: {r.status}, {len(data)} items")
        assert len(data) >= 6

    # 6. Weather transparency check
    w_url = f"{base_url}/api/v1/weather/current?lat=16.985&lon=81.78"
    with urllib.request.urlopen(w_url) as r:
        w_data = json.loads(r.read().decode("utf-8"))
        print(f"GET /api/v1/weather/current: is_available={w_data.get('is_available')}, status={w_data.get('status')}")
        assert w_data.get("is_available") is False
        assert w_data.get("status") == "API_KEY_NOT_CONFIGURED"

    print("\n>>> ALL LIVE HTTP SERVER ENDPOINTS VERIFIED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_live_server()
