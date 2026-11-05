import re

with open('scripts/deep_browser_gis_audit.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Fix WebSocket 64-bit frame payload length unpacking
old_ws = """                elif payload_len == 127:
                    if len(buf) - idx < 10: break
                    h_size = 10"""

new_ws = """                elif payload_len == 127:
                    if len(buf) - idx < 10: break
                    payload_len = int.from_bytes(buf[idx+2:idx+10], 'big')
                    h_size = 10"""
code = code.replace(old_ws, new_ws)

# 2. Add capture_screenshot method to CDPClient
old_eval_js = """    def eval_js(self, expression):
        res = self.send_cmd("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        if res and "result" in res and "result" in res["result"]:
            return res["result"]["result"].get("value")
        return None"""

new_eval_js = """    def eval_js(self, expression):
        res = self.send_cmd("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        if res and "result" in res and "result" in res["result"]:
            return res["result"]["result"].get("value")
        return None

    def capture_screenshot(self, out_path):
        import base64
        res = self.send_cmd("Page.captureScreenshot", {"format": "png"})
        if res and "result" in res and "data" in res["result"]:
            raw = base64.b64decode(res["result"]["data"])
            with open(out_path, "wb") as f:
                f.write(raw)
            print(f"    [+] Saved screenshot {out_path.name} ({len(raw):,} bytes)")
            return len(raw)
        return 0"""
code = code.replace(old_eval_js, new_eval_js)

# 3. Add server start logic in main()
old_main_start = """def main():
    print("[*] Launching headless Chrome with remote debugging on port 9227...")
    chrome = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-extensions",
        "--incognito",
        "--remote-debugging-port=9227",
        "--window-size=1680,1050",
        "http://127.0.0.1:8000/#overview"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3.0)"""

new_main_start = """def main():
    # Check if server is running, if not start it
    server = None
    log_fp = None
    server_running = False
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=1) as r:
            server_running = True
            print("[+] FastAPI server is already running.")
    except Exception:
        pass

    if not server_running:
        print("[*] Starting local FastAPI server on http://127.0.0.1:8000/...")
        log_fp = open("uvicorn_deep_audit.log", "w", encoding="utf-8")
        server = subprocess.Popen(
            [PYTHON_PATH, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=log_fp,
            stderr=log_fp
        )
        for i in range(25):
            time.sleep(1.0)
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=2) as resp:
                    print("[+] Server started & healthy.")
                    break
            except Exception:
                pass

    print("[*] Launching headless Chrome with remote debugging on port 9227...")
    chrome = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-extensions",
        "--enable-webgl",
        "--use-gl=angle",
        "--incognito",
        "--remote-debugging-port=9227",
        "--window-size=1680,1050",
        "http://127.0.0.1:8000/#overview"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3.0)"""
code = code.replace(old_main_start, new_main_start)

# 4. In workspace loop, take screenshots
old_ws_loop = """        ws_ids = ["overview", "explorer", "risk", "impact", "weather", "global", "evidence"]
        for wid in ws_ids:
            cdp.eval_js(f"window.switchWorkspace('{wid}');")
            time.sleep(0.6)"""

new_ws_loop = """        ws_ids = ["overview", "explorer", "risk", "impact", "weather", "global", "evidence"]
        for wid in ws_ids:
            cdp.eval_js(f"window.switchWorkspace('{wid}');")
            time.sleep(1.2 if wid in ['overview', 'explorer', 'risk', 'impact', 'global'] else 0.8)
            cdp.capture_screenshot(SCREENSHOTS_DIR / f"{wid}.png")
            cdp.capture_screenshot(SCREENSHOTS_DIR / f"workspace_{wid}.png")"""
code = code.replace(old_ws_loop, new_ws_loop)

# 5. Capture interactive state screenshots:
# Satellite basemap
old_sat = """        sat_check = cdp.eval_js(\"\"\"
            (() => {
                const map = window.maps?.explorer;
                const layers = window.explorerLayers || {};
                return {
                    switchedToSatellite: document.querySelector('input[name="basemapRadio"]:checked')?.value === 'satellite',
                    satelliteLayerOnMap: !!layers.basemapSat && map.hasLayer(layers.basemapSat)
                };
            })()
        \"\"\")"""

new_sat = """        sat_check = cdp.eval_js(\"\"\"
            (() => {
                const map = window.maps?.explorer;
                const layers = window.explorerLayers || {};
                return {
                    switchedToSatellite: document.querySelector('input[name="basemapRadio"]:checked')?.value === 'satellite',
                    satelliteLayerOnMap: !!layers.basemapSat && map.hasLayer(layers.basemapSat)
                };
            })()
        \"\"\")
        time.sleep(1.0)
        cdp.capture_screenshot(SCREENSHOTS_DIR / "gis_basemap_satellite.png")"""
code = code.replace(old_sat, new_sat)

# OSM basemap
old_osm = """        osm_check = cdp.eval_js(\"\"\"
            (() => {
                const map = window.maps?.explorer;
                const layers = window.explorerLayers || {};
                return {
                    switchedToOsm: document.querySelector('input[name="basemapRadio"]:checked')?.value === 'osm',
                    osmLayerOnMap: !!layers.basemapOsm && map.hasLayer(layers.basemapOsm)
                };
            })()
        \"\"\")"""

new_osm = """        osm_check = cdp.eval_js(\"\"\"
            (() => {
                const map = window.maps?.explorer;
                const layers = window.explorerLayers || {};
                return {
                    switchedToOsm: document.querySelector('input[name="basemapRadio"]:checked')?.value === 'osm',
                    osmLayerOnMap: !!layers.basemapOsm && map.hasLayer(layers.basemapOsm)
                };
            })()
        \"\"\")
        time.sleep(1.0)
        cdp.capture_screenshot(SCREENSHOTS_DIR / "gis_basemap_osm.png")"""
code = code.replace(old_osm, new_osm)

# Inspection drawer
old_drawer = """        drawer_res = cdp.eval_js(\"\"\"
            (() => {
                const drawer = document.getElementById('gisInspectionDrawer');
                const title = document.getElementById('drawerLocationTitle')?.textContent;
                const metrics = Array.from(document.querySelectorAll('.drawer-metric-box')).map(b => ({
                    label: b.querySelector('.drawer-metric-label')?.textContent,
                    val: b.querySelector('.drawer-metric-val')?.textContent
                }));
                return {
                    drawerVisible: drawer && drawer.style.display !== 'none',
                    title: title,
                    metrics: metrics
                };
            })()
        \"\"\")"""

new_drawer = """        drawer_res = cdp.eval_js(\"\"\"
            (() => {
                const drawer = document.getElementById('gisInspectionDrawer');
                const title = document.getElementById('drawerLocationTitle')?.textContent;
                const metrics = Array.from(document.querySelectorAll('.drawer-metric-box')).map(b => ({
                    label: b.querySelector('.drawer-metric-label')?.textContent,
                    val: b.querySelector('.drawer-metric-val')?.textContent
                }));
                return {
                    drawerVisible: drawer && drawer.style.display !== 'none',
                    title: title,
                    metrics: metrics
                };
            })()
        \"\"\")
        time.sleep(0.8)
        cdp.capture_screenshot(SCREENSHOTS_DIR / "gis_inspection_drawer_active.png")"""
code = code.replace(old_drawer, new_drawer)

# India selected card
old_india = """        india_card_check = cdp.eval_js(\"\"\"
            (() => {
                const card = document.getElementById('globeCountryCard');
                const name = document.getElementById('globeCountryName')?.textContent;
                const hasBtn = !!document.getElementById('btnJumpToDeltaPrototype');
                const globe = window.getGlobeInstance ? window.getGlobeInstance() : window.globeInstance;
                const pov = globe ? globe.pointOfView() : null;
                return {
                    cardVisible: card && card.style.display !== 'none',
                    countryName: name,
                    hasRegionalJumpButton: hasBtn,
                    cameraPov: pov ? { lat: Math.round(pov.lat*10)/10, lng: Math.round(pov.lng*10)/10, alt: Math.round(pov.altitude*10)/10 } : null
                };
            })()
        \"\"\")"""

new_india = """        india_card_check = cdp.eval_js(\"\"\"
            (() => {
                const card = document.getElementById('globeCountryCard');
                const name = document.getElementById('globeCountryName')?.textContent;
                const hasBtn = !!document.getElementById('btnJumpToDeltaPrototype');
                const globe = window.getGlobeInstance ? window.getGlobeInstance() : window.globeInstance;
                const pov = globe ? globe.pointOfView() : null;
                return {
                    cardVisible: card && card.style.display !== 'none',
                    countryName: name,
                    hasRegionalJumpButton: hasBtn,
                    cameraPov: pov ? { lat: Math.round(pov.lat*10)/10, lng: Math.round(pov.lng*10)/10, alt: Math.round(pov.altitude*10)/10 } : null
                };
            })()
        \"\"\")
        time.sleep(1.0)
        cdp.capture_screenshot(SCREENSHOTS_DIR / "globe_india_selected_card.png")"""
code = code.replace(old_india, new_india)

# 6. Finally: cleanup server
old_finally = """    finally:
        chrome.terminate()
        print("[*] Chrome terminated.")"""

new_finally = """    finally:
        chrome.terminate()
        print("[*] Chrome terminated.")
        if server:
            server.terminate()
            server.wait()
            if log_fp: log_fp.close()
            print("[*] Server terminated.")"""
code = code.replace(old_finally, new_finally)

with open('scripts/deep_browser_gis_audit.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully updated scripts/deep_browser_gis_audit.py")
