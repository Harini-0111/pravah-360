"""
Captures high-resolution screenshots of all 7 workspaces using Chrome headless.
"""
import os
import sys
import time
import subprocess
import tempfile
import urllib.request

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "docs", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PYTHON_PATH = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")

workspaces = [
    ("overview", "Workspace 1: Overview & Executive Summary", "http://127.0.0.1:8000/#overview"),
    ("explorer", "Workspace 2: Geospatial Explorer (Web GIS)", "http://127.0.0.1:8000/#explorer"),
    ("risk", "Workspace 3: Flood Risk Intelligence", "http://127.0.0.1:8000/#risk"),
    ("impact", "Workspace 4: Impact Assessment & Exposure", "http://127.0.0.1:8000/#impact"),
    ("weather", "Workspace 5: Weather & Emergency Intelligence", "http://127.0.0.1:8000/#weather"),
    ("global", "Workspace 6: Global 3D Earth Intelligence", "http://127.0.0.1:8000/#global"),
    ("evidence", "Workspace 7: Evidence & Scientific Methodology", "http://127.0.0.1:8000/#evidence"),
    ("gis_basemap_satellite", "GIS Interactive State: Satellite Basemap", "http://127.0.0.1:8000/?action=satellite#explorer"),
    ("gis_basemap_osm", "GIS Interactive State: OpenStreetMap Basemap", "http://127.0.0.1:8000/?action=osm#explorer"),
    ("gis_inspection_drawer_active", "GIS Interactive State: Active Inspection Drawer", "http://127.0.0.1:8000/?action=inspect#explorer"),
    ("globe_india_selected_card", "Global 3D Earth State: Selected India Card", "http://127.0.0.1:8000/?action=globe_india#global")
]

def main():
    print("Starting FastAPI server on http://127.0.0.1:8000/...")
    log_fp = open("uvicorn_screenshot.log", "w", encoding="utf-8")
    server = subprocess.Popen(
        [PYTHON_PATH, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=log_fp,
        stderr=log_fp
    )

    # Wait for server to become healthy
    started = False
    for i in range(25):
        time.sleep(1.0)
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=2) as resp:
                print("Server Health:", resp.read().decode())
                started = True
                break
        except Exception:
            pass

    if not started:
        print("Server failed to start in time.")
        server.terminate()
        log_fp.close()
        return

    try:
        results = {}
        for ws_id, ws_name, url in workspaces:
            out_file = os.path.join(SCREENSHOTS_DIR, f"{ws_id}.png")
            print(f"Capturing {ws_name} ({url})...")
            
            with tempfile.TemporaryDirectory() as tmpdir:
                cmd = [
                    CHROME_PATH,
                    "--headless=new",
                    f"--user-data-dir={tmpdir}",
                    "--enable-webgl",
                    "--use-gl=angle",
                    "--run-all-compositor-stages-before-draw",
                    "--hide-scrollbars",
                    "--window-size=1680,1050",
                    f"--screenshot={out_file}",
                    url
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
                sz = os.path.getsize(out_file)
                print(f"  -> SUCCESS: {out_file} ({sz:,} bytes)")
                results[ws_id] = {"success": True, "size_bytes": sz, "file": out_file}
                # Also create workspace_<id>.png copy if applicable
                if ws_id in ["overview", "explorer", "risk", "impact", "weather", "global", "evidence"]:
                    ws_alias = os.path.join(SCREENSHOTS_DIR, f"workspace_{ws_id}.png")
                    with open(out_file, 'rb') as f_src, open(ws_alias, 'wb') as f_dst:
                        f_dst.write(f_src.read())
            else:
                print(f"  -> FAILED: returncode {res.returncode}, stderr: {res.stderr}")
                results[ws_id] = {"success": False, "error": res.stderr}
            time.sleep(0.5)

        print("\nAll workspace screenshots captured:")
        for k, v in results.items():
            print(f"  {k}: {v.get('size_bytes', 0):,} bytes")

    finally:
        server.terminate()
        server.wait()
        log_fp.close()
        print("Server stopped.")

if __name__ == "__main__":
    main()
