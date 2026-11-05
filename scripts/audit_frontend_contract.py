"""
Frontend Contract Audit Script (Phase 5.0)
Measures response times, payload sizes, sample responses, invalid-input handling,
out-of-coverage behavior, GeoJSON and raster sizes across all FastAPI endpoints.
"""

import os
import sys
import time
import json
import socket
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

WORKSPACE = Path(r"C:\major project")
sys.path.insert(0, str(WORKSPACE))

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def run_contract_audit():
    port = get_free_port()
    base_url = f"http://127.0.0.1:{port}"
    print(f"[*] Starting local FastAPI server on port {port}...", flush=True)

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(WORKSPACE)
    )

    # Wait for server to become ready
    ready = False
    for _ in range(30):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen(f"{base_url}/api/v1/health", timeout=1.0) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except Exception:
            pass

    if not ready:
        proc.kill()
        raise RuntimeError("Failed to start FastAPI server within 15 seconds.")

    print("[+] FastAPI server is ready. Beginning endpoint contract tests...", flush=True)

    # Endpoints to test
    test_specs = [
        # 1. Location Identification
        {
            "category": "Location Identification",
            "name": "Identify Point GET (Inside Basin)",
            "url": "/api/v1/geographic/identify-point?lat=16.942&lon=81.776",
            "method": "GET",
            "invalid_url": "/api/v1/geographic/identify-point?lat=999&lon=81.776",
            "out_of_coverage_url": "/api/v1/geographic/identify-point?lat=17.385&lon=78.486" # Hyderabad
        },
        {
            "category": "Location Identification",
            "name": "Identify Point POST (Inside Basin)",
            "url": "/api/v1/geographic/identify-point",
            "method": "POST",
            "body": {"latitude": 16.942, "longitude": 81.776},
            "invalid_body": {"latitude": 999, "longitude": 81.776},
            "out_of_coverage_body": {"latitude": 17.385, "longitude": 78.486}
        },
        {
            "category": "Location Identification",
            "name": "Supported Location Search (Mandal Exact/Normalized)",
            "url": "/api/v1/locations/search?q=Kottapeta",
            "method": "GET",
            "invalid_url": "/api/v1/locations/search?q=",
            "out_of_coverage_url": "/api/v1/locations/search?q=New%20Delhi"
        },
        # 2. Administrative Boundaries
        {
            "category": "Administrative Boundaries",
            "name": "Raw Mandal Boundaries GeoJSON",
            "url": "/api/v1/boundaries/mandals-geojson",
            "method": "GET",
            "invalid_url": None,
            "out_of_coverage_url": None
        },
        # 3. Flood Susceptibility & Assessment
        {
            "category": "Flood Susceptibility",
            "name": "Basin Risk Assessment Summary",
            "url": "/api/v1/risk/assessment",
            "method": "GET",
            "invalid_url": None,
            "out_of_coverage_url": None
        },
        {
            "category": "Flood Susceptibility",
            "name": "Enriched Mandal Risk GeoJSON",
            "url": "/api/v1/risk/mandals",
            "method": "GET",
            "invalid_url": None,
            "out_of_coverage_url": None
        },
        {
            "category": "Flood Susceptibility",
            "name": "Mandal Explainable Risk Profile",
            "url": "/api/v1/risk/mandal/Rajahmundry",
            "method": "GET",
            "invalid_url": "/api/v1/risk/mandal/NonExistentMandalXYZ",
            "out_of_coverage_url": None
        },
        {
            "category": "Flood Susceptibility",
            "name": "Coordinate Terrain & Risk Evaluation",
            "url": "/api/v1/risk/evaluate-point",
            "method": "POST",
            "body": {"latitude": 16.942, "longitude": 81.776},
            "invalid_body": {"latitude": "invalid", "longitude": 81.776},
            "out_of_coverage_body": {"latitude": 17.385, "longitude": 78.486}
        },
        # 4. Mandal-level Population Exposure
        {
            "category": "Population Exposure",
            "name": "Baseline & Elevated Population Exposure Summary",
            "url": "/api/v1/risk/exposure/summary",
            "method": "GET",
            "invalid_url": None,
            "out_of_coverage_url": None
        },
        # 5. Infrastructure Exposure
        {
            "category": "Infrastructure Exposure",
            "name": "Mapped Infrastructure Facilities GeoJSON",
            "url": "/api/v1/risk/infrastructure",
            "method": "GET",
            "invalid_url": None,
            "out_of_coverage_url": None
        },
        {
            "category": "Infrastructure Exposure",
            "name": "Active Flood Risk Monitoring Stations",
            "url": "/api/v1/flood-risk/markers",
            "method": "GET",
            "invalid_url": None,
            "out_of_coverage_url": None
        },
        # 6. Sentinel-1 Water Classification & Candidates
        {
            "category": "Sentinel-1 SAR",
            "name": "Track 129 Mandal Water Candidates Summary",
            "url": "/api/v1/satellite/water-candidates",
            "method": "GET",
            "invalid_url": None,
            "out_of_coverage_url": None
        },
        {
            "category": "Sentinel-1 SAR",
            "name": "Track 129 Candidate Water Polygons GeoJSON",
            "url": "/api/v1/satellite/water-candidates-geojson",
            "method": "GET",
            "invalid_url": None,
            "out_of_coverage_url": None
        },
        # 7. Weather Conditions & Forecasts
        {
            "category": "Weather Intelligence",
            "name": "Unified Weather & Location Intelligence",
            "url": "/api/v1/weather/unified?lat=16.985&lon=81.78",
            "method": "GET",
            "invalid_url": "/api/v1/weather/unified?lat=999&lon=81.78",
            "out_of_coverage_url": "/api/v1/weather/unified?lat=17.385&lon=78.486"
        },
        {
            "category": "Weather Intelligence",
            "name": "Current Weather Conditions",
            "url": "/api/v1/weather/current?lat=16.985&lon=81.78",
            "method": "GET",
            "invalid_url": "/api/v1/weather/current?lat=999&lon=81.78",
            "out_of_coverage_url": "/api/v1/weather/current?lat=17.385&lon=78.486"
        },
        {
            "category": "Weather Intelligence",
            "name": "Hourly Weather Forecast (24h)",
            "url": "/api/v1/weather/forecast/hourly?lat=16.985&lon=81.78&hours=24",
            "method": "GET",
            "invalid_url": "/api/v1/weather/forecast/hourly?lat=999&lon=81.78",
            "out_of_coverage_url": "/api/v1/weather/forecast/hourly?lat=17.385&lon=78.486"
        },
        {
            "category": "Weather Intelligence",
            "name": "Daily Weather Forecast (10-day)",
            "url": "/api/v1/weather/forecast/daily?lat=16.985&lon=81.78&days=10",
            "method": "GET",
            "invalid_url": "/api/v1/weather/forecast/daily?lat=999&lon=81.78",
            "out_of_coverage_url": "/api/v1/weather/forecast/daily?lat=17.385&lon=78.486"
        },
        # 8. Public Alerts & Bulletins
        {
            "category": "Public Alerts",
            "name": "Weather Public Alerts Lookup",
            "url": "/api/v1/weather/alerts?lat=16.985&lon=81.78",
            "method": "GET",
            "invalid_url": "/api/v1/weather/alerts?lat=999&lon=81.78",
            "out_of_coverage_url": "/api/v1/weather/alerts?lat=17.385&lon=78.486"
        },
        {
            "category": "Public Alerts",
            "name": "Decision Support Susceptibility Bulletins",
            "url": "/api/v1/flood-risk/alerts",
            "method": "GET",
            "invalid_url": None,
            "out_of_coverage_url": None
        }
    ]

    results = []

    for spec in test_specs:
        item = {
            "category": spec["category"],
            "name": spec["name"],
            "method": spec["method"],
            "endpoint": spec["url"].split("?")[0]
        }

        # 1. Normal Request
        t0 = time.perf_counter()
        status_code = None
        payload_bytes = 0
        resp_data = None
        error_msg = None

        try:
            req_url = f"{base_url}{spec['url']}"
            if spec["method"] == "GET":
                req = urllib.request.Request(req_url)
            else:
                body_bytes = json.dumps(spec.get("body", {})).encode("utf-8")
                req = urllib.request.Request(req_url, data=body_bytes, headers={"Content-Type": "application/json"})
            
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                status_code = resp.status
                raw = resp.read()
                payload_bytes = len(raw)
                try:
                    resp_data = json.loads(raw.decode("utf-8"))
                except Exception:
                    resp_data = {"raw_text": raw.decode("utf-8")[:200]}
        except urllib.error.HTTPError as e:
            status_code = e.code
            raw = e.read()
            payload_bytes = len(raw)
            try:
                resp_data = json.loads(raw.decode("utf-8"))
            except Exception:
                resp_data = {"error": str(e)}
        except Exception as e:
            error_msg = str(e)

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        item["status_code"] = status_code
        item["response_time_ms"] = elapsed_ms
        item["payload_size_bytes"] = payload_bytes
        item["payload_size_kb"] = round(payload_bytes / 1024, 2)
        item["payload_size_mb"] = round(payload_bytes / (1024 * 1024), 2)
        item["sample_response"] = resp_data

        # 2. Invalid Input Test
        if spec.get("invalid_url"):
            try:
                with urllib.request.urlopen(f"{base_url}{spec['invalid_url']}", timeout=5.0) as resp:
                    item["invalid_input_status"] = resp.status
                    item["invalid_input_response"] = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                item["invalid_input_status"] = e.code
                try:
                    item["invalid_input_response"] = json.loads(e.read().decode("utf-8"))
                except Exception:
                    item["invalid_input_response"] = str(e)
            except Exception as e:
                item["invalid_input_status"] = "ERROR"
                item["invalid_input_response"] = str(e)
        elif spec.get("invalid_body"):
            try:
                body_bytes = json.dumps(spec["invalid_body"]).encode("utf-8")
                req = urllib.request.Request(f"{base_url}{spec['url']}", data=body_bytes, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    item["invalid_input_status"] = resp.status
                    item["invalid_input_response"] = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                item["invalid_input_status"] = e.code
                try:
                    item["invalid_input_response"] = json.loads(e.read().decode("utf-8"))
                except Exception:
                    item["invalid_input_response"] = str(e)
        else:
            item["invalid_input_status"] = "N/A"
            item["invalid_input_response"] = "No parameters required"

        # 3. Out of Coverage Test
        if spec.get("out_of_coverage_url"):
            try:
                with urllib.request.urlopen(f"{base_url}{spec['out_of_coverage_url']}", timeout=5.0) as resp:
                    item["out_of_coverage_status"] = resp.status
                    item["out_of_coverage_response"] = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                item["out_of_coverage_status"] = e.code
                try:
                    item["out_of_coverage_response"] = json.loads(e.read().decode("utf-8"))
                except Exception:
                    item["out_of_coverage_response"] = str(e)
            except Exception as e:
                item["out_of_coverage_status"] = "ERROR"
                item["out_of_coverage_response"] = str(e)
        elif spec.get("out_of_coverage_body"):
            try:
                body_bytes = json.dumps(spec["out_of_coverage_body"]).encode("utf-8")
                req = urllib.request.Request(f"{base_url}{spec['url']}", data=body_bytes, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    item["out_of_coverage_status"] = resp.status
                    item["out_of_coverage_response"] = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                item["out_of_coverage_status"] = e.code
                try:
                    item["out_of_coverage_response"] = json.loads(e.read().decode("utf-8"))
                except Exception:
                    item["out_of_coverage_response"] = str(e)
        else:
            item["out_of_coverage_status"] = "N/A"
            item["out_of_coverage_response"] = "Basin-wide endpoint"

        results.append(item)
        print(f"  [{item['status_code']}] {item['name']:40s} | {item['response_time_ms']:6.1f} ms | {item['payload_size_kb']:8.1f} KB", flush=True)

    # Clean shutdown of uvicorn server
    proc.terminate()
    try:
        proc.wait(timeout=3.0)
    except Exception:
        proc.kill()

    # Save benchmark results
    out_file = WORKSPACE / "data" / "metadata" / "frontend_contract_audit_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[+] Contract audit completed successfully. Results saved to: {out_file}", flush=True)

if __name__ == "__main__":
    run_contract_audit()
