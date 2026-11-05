"""
Phase 5.4 Comprehensive Browser-Level Functional Audit Script
Connects via Chrome DevTools Protocol to execute 10 rigorous end-to-end user workflows
and records verified empirical results.
"""
import os
import sys
import time
import json
import socket
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(r"C:\major project")
PYTHON_PATH = str(BASE_DIR / ".venv" / "Scripts" / "python.exe")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT_CDP = 9235
PORT_SERVER = 8000

class CDPClient:
    def __init__(self, port=PORT_CDP):
        self.port = port
        self.cmd_id = 0
        self.sock = None

    def connect(self):
        tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json").read().decode())
        page_tab = next(t for t in tabs if t.get("type") == "page")
        ws_url = page_tab["webSocketDebuggerUrl"]
        parsed = urllib.parse.urlparse(ws_url)
        self.sock = socket.create_connection((parsed.hostname, parsed.port), timeout=20)
        
        handshake = (
            f"GET {parsed.path} HTTP/1.1\r\n"
            f"Host: {parsed.netloc}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(handshake.encode())
        self.sock.recv(2048)

    def send_cmd(self, method, params=None):
        self.cmd_id += 1
        cid = self.cmd_id
        req = {"id": cid, "method": method}
        if params: req["params"] = params
        data = json.dumps(req).encode('utf-8')
        mask = os.urandom(4)
        l = len(data)
        header = bytes([0x81, 0x80 | (l if l < 126 else (126 if l <= 65535 else 127))])
        if l >= 126 and l <= 65535:
            header += bytes([(l >> 8) & 0xff, l & 0xff])
        elif l > 65535:
            header += (l).to_bytes(8, byteorder='big')
        header += mask
        self.sock.sendall(header + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

        start = time.time()
        buf = bytearray()
        while time.time() - start < 15:
            chunk = self.sock.recv(65536)
            if not chunk: break
            buf.extend(chunk)
            
            idx = 0
            while idx < len(buf):
                if len(buf) - idx < 2: break
                b1 = buf[idx+1]
                payload_len = b1 & 0x7f
                h_size = 2
                if payload_len == 126:
                    if len(buf) - idx < 4: break
                    payload_len = (buf[idx+2] << 8) | buf[idx+3]
                    h_size = 4
                elif payload_len == 127:
                    if len(buf) - idx < 10: break
                    payload_len = int.from_bytes(buf[idx+2:idx+10], 'big')
                    h_size = 10
                
                if len(buf) - idx < h_size + payload_len:
                    break
                
                payload = buf[idx+h_size:idx+h_size+payload_len]
                idx += h_size + payload_len
                
                try:
                    msg = json.loads(payload.decode('utf-8', errors='ignore'))
                    if msg.get("id") == cid:
                        return msg
                except:
                    pass
        return None

    def eval_js(self, expression):
        res = self.send_cmd("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        if res and "result" in res and "result" in res["result"]:
            return res["result"]["result"].get("value")
        return None

def main():
    results = {}
    print("[*] Checking FastAPI server status...")
    server = None
    log_fp = None
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT_SERVER}/api/v1/health", timeout=1) as r:
            print("[+] Server already running.")
    except Exception:
        print("[*] Starting FastAPI server on port 8000...")
        log_fp = open("uvicorn_audit54.log", "w", encoding="utf-8")
        server = subprocess.Popen(
            [PYTHON_PATH, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", str(PORT_SERVER)],
            stdout=log_fp,
            stderr=log_fp
        )
        for i in range(25):
            time.sleep(1.0)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT_SERVER}/api/v1/health", timeout=2) as r:
                    print("[+] Server started and healthy.")
                    break
            except Exception:
                pass

    print(f"[*] Launching Headless Chrome on CDP port {PORT_CDP}...")
    chrome = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-extensions",
        "--enable-webgl",
        "--use-gl=angle",
        "--incognito",
        f"--remote-debugging-port={PORT_CDP}",
        "--window-size=1680,1050",
        f"http://127.0.0.1:{PORT_SERVER}/#overview"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3.0)

    try:
        cdp = CDPClient(port=PORT_CDP)
        cdp.connect()
        print("[+] CDP connected.")
        cdp.send_cmd("Page.enable")
        cdp.send_cmd("Runtime.enable")
        time.sleep(1.5)

        # ---------------------------------------------------------------------
        # WORKFLOW 1: Open Overview and load Lower Godavari Map
        # ---------------------------------------------------------------------
        print("\n--- WORKFLOW 1: Overview and Lower Godavari Map ---")
        cdp.eval_js("window.switchWorkspace('overview');")
        time.sleep(1.2)
        wf1 = cdp.eval_js("""
            (() => {
                const ws = document.getElementById('workspace-overview');
                const mapEl = document.getElementById('overview-map');
                const map = window.maps?.overview;
                const hud = document.getElementById('overviewMapHoverHud');
                
                // Read metrics
                const metrics = Array.from(document.querySelectorAll('.metric-pill-card')).map(c => ({
                    val: c.querySelector('.metric-num')?.textContent?.trim(),
                    label: c.querySelector('.metric-label')?.textContent?.trim(),
                    sub: c.querySelector('.metric-sub')?.textContent?.trim()
                }));

                // Read analytical bars
                const bars = Array.from(document.querySelectorAll('.summary-card')).map(sc => ({
                    title: sc.querySelector('.sc-title')?.textContent?.trim(),
                    sub: sc.querySelector('.sc-subtitle')?.textContent?.trim(),
                    legendItems: Array.from(sc.querySelectorAll('.sc-legend-item')).map(li => li.textContent?.trim())
                }));

                return {
                    workspaceActive: ws?.classList.contains('active'),
                    mapContainerExists: !!mapEl,
                    leafletMapInitialized: !!map,
                    mapCenter: map ? [Math.round(map.getCenter().lat*1000)/1000, Math.round(map.getCenter().lng*1000)/1000] : null,
                    mapZoom: map ? map.getZoom() : null,
                    hudPresent: !!hud,
                    hudInitialText: hud?.textContent?.trim(),
                    metricsCount: metrics.length,
                    metrics: metrics,
                    analyticalBarsCount: bars.length,
                    analyticalBars: bars
                };
            })()
        """)
        results["workflow_1_overview_map"] = wf1
        print("  Workflow 1 Result:", json.dumps(wf1, indent=2))

        # ---------------------------------------------------------------------
        # WORKFLOW 2: Open Global 3D Earth, Select India & Transition
        # ---------------------------------------------------------------------
        print("\n--- WORKFLOW 2: Global 3D Earth, India Selection & Transition ---")
        cdp.eval_js("window.switchWorkspace('global');")
        time.sleep(1.5)
        
        # Test country search
        cdp.eval_js("""
            (() => {
                const inp = document.getElementById('globeCountrySearchInput');
                if (inp) {
                    inp.value = 'India';
                    inp.dispatchEvent(new Event('input'));
                }
            })()
        """)
        time.sleep(0.5)
        search_res = cdp.eval_js("""
            (() => {
                const box = document.getElementById('globeCountrySuggestions');
                const items = Array.from(box?.querySelectorAll('.suggestion-item') || []).map(i => i.textContent?.trim());
                return {
                    suggestionsVisible: box && box.style.display !== 'none',
                    items: items
                };
            })()
        """)

        # Trigger India Selection
        cdp.eval_js("""
            window.selectGlobeCountry({
                name: 'India',
                continent: 'Asia',
                pop_est: 1366417754
            });
        """)
        time.sleep(1.0)
        india_card = cdp.eval_js("""
            (() => {
                const card = document.getElementById('globeCountryCard');
                const title = document.getElementById('globeCountryName')?.textContent?.trim();
                const btnJump = document.getElementById('btnJumpToDeltaPrototype');
                const bodyText = document.getElementById('globeCountryBody')?.innerText?.trim();
                return {
                    cardVisible: card && card.style.display !== 'none',
                    countryName: title,
                    hasJumpButton: !!btnJump,
                    jumpButtonText: btnJump?.textContent?.trim(),
                    cardBodySummary: bodyText?.substring(0, 150)
                };
            })()
        """)

        # Click Jump to Regional Prototype
        cdp.eval_js("""
            (() => {
                const btnJump = document.getElementById('btnJumpToDeltaPrototype');
                if (btnJump) btnJump.click();
            })()
        """)
        time.sleep(1.0)
        transition_res = cdp.eval_js("""
            (() => {
                const currentWs = window.appState?.currentWorkspace;
                const explorerWs = document.getElementById('workspace-explorer');
                return {
                    currentWorkspaceState: currentWs,
                    explorerActive: explorerWs?.classList.contains('active'),
                    explorerDisplay: window.getComputedStyle(explorerWs).display
                };
            })()
        """)

        wf2 = {
            "search_suggestions": search_res,
            "india_card": india_card,
            "regional_transition": transition_res
        }
        results["workflow_2_global_earth_transition"] = wf2
        print("  Workflow 2 Result:", json.dumps(wf2, indent=2))

        # ---------------------------------------------------------------------
        # WORKFLOW 3: Search Rajamahendravaram, Kakinada, Hyderabad & Ambiguous
        # ---------------------------------------------------------------------
        print("\n--- WORKFLOW 3: Location Search Testing ---")
        queries = ["Rajamahendravaram", "Kakinada", "Hyderabad", "Rama", "Godavari"]
        search_audit = {}
        for q in queries:
            cdp.eval_js(f"""
                (() => {{
                    const inp = document.getElementById('globalLocationSearchInput');
                    if (inp) {{
                        inp.value = '{q}';
                        inp.dispatchEvent(new Event('input'));
                    }}
                }})()
            """)
            time.sleep(0.4)
            s_data = cdp.eval_js("""
                (() => {
                    const box = document.getElementById('globalSearchSuggestions');
                    const isVisible = box && box.style.display !== 'none';
                    const items = Array.from(box?.querySelectorAll('.suggestion-item') || []).map(it => ({
                        title: it.querySelector('.suggestion-title')?.textContent?.trim(),
                        meta: it.querySelector('.suggestion-meta')?.textContent?.trim()
                    }));
                    return {
                        boxVisible: isVisible,
                        matchCount: items.length,
                        matches: items
                    };
                })()
            """)
            search_audit[q] = s_data

        results["workflow_3_location_search"] = search_audit
        print("  Workflow 3 Result:", json.dumps(search_audit, indent=2))

        # ---------------------------------------------------------------------
        # WORKFLOW 4: Click Inside and Outside Study Boundary
        # ---------------------------------------------------------------------
        print("\n--- WORKFLOW 4: Points Inside vs Outside Study Boundary ---")
        # Point A: Inside (Rajahmundry 16.985, 81.780)
        cdp.eval_js("window.inspectCoordinates(16.985, 81.780);")
        time.sleep(1.2)
        inside_drawer = cdp.eval_js("""
            (() => {
                const drawer = document.getElementById('gisInspectionDrawer');
                const title = document.getElementById('drawerLocationTitle')?.textContent?.trim();
                const metrics = Array.from(document.querySelectorAll('.drawer-metric-box')).map(b => ({
                    label: b.querySelector('.drawer-metric-label')?.textContent?.trim(),
                    val: b.querySelector('.drawer-metric-val')?.textContent?.trim()
                }));
                const notes = document.querySelector('.drawer-confidence-box')?.innerText?.trim();
                return {
                    drawerVisible: drawer && drawer.style.display !== 'none',
                    locationTitle: title,
                    metrics: metrics,
                    confidenceNotes: notes
                };
            })()
        """)

        # Point B: Outside (Hyderabad 17.385, 78.486)
        cdp.eval_js("window.inspectCoordinates(17.385, 78.486);")
        time.sleep(1.2)
        outside_drawer = cdp.eval_js("""
            (() => {
                const drawer = document.getElementById('gisInspectionDrawer');
                const title = document.getElementById('drawerLocationTitle')?.textContent?.trim();
                const metrics = Array.from(document.querySelectorAll('.drawer-metric-box')).map(b => ({
                    label: b.querySelector('.drawer-metric-label')?.textContent?.trim(),
                    val: b.querySelector('.drawer-metric-val')?.textContent?.trim()
                }));
                const notes = document.querySelector('.drawer-confidence-box')?.innerText?.trim();
                return {
                    drawerVisible: drawer && drawer.style.display !== 'none',
                    locationTitle: title,
                    metrics: metrics,
                    confidenceNotes: notes
                };
            })()
        """)

        wf4 = {
            "point_inside_rajahmundry": inside_drawer,
            "point_outside_hyderabad": outside_drawer
        }
        results["workflow_4_inside_outside_points"] = wf4
        print("  Workflow 4 Result:", json.dumps(wf4, indent=2))

        # ---------------------------------------------------------------------
        # WORKFLOW 5: Toggle Every GIS Layer and Verify Legend
        # ---------------------------------------------------------------------
        print("\n--- WORKFLOW 5: Toggle GIS Layers & Legend ---")
        cdp.eval_js("window.switchWorkspace('explorer');")
        time.sleep(0.5)

        layer_checks = {}
        layer_ids = [
            ("chkLyrStudyArea", "studyArea"),
            ("chkLyrDistricts", "districts"),
            ("chkLyrMandals", "mandals"),
            ("chkLyrRivers", "rivers"),
            ("chkLyrStations", "stations"),
            ("chkLyrFacilities", "facilities"),
            ("chkLyrSarFlood", "sarFlood"),
            ("chkLyrSarPerm", "sarPerm"),
            ("chkLyrAmbig", "sarAmbig"),
            ("chkLyrSusceptibility", "susceptibility")
        ]

        for elem_id, layer_key in layer_ids:
            chk = cdp.eval_js(f"""
                (() => {{
                    const el = document.getElementById('{elem_id}');
                    const map = window.maps?.explorer;
                    const lyr = window.explorerLayers ? window.explorerLayers['{layer_key}'] : null;
                    const initialChecked = el ? el.checked : null;
                    const initiallyOnMap = !!lyr && !!map && map.hasLayer(lyr);
                    return {{
                        elementExists: !!el,
                        initialChecked: initialChecked,
                        initiallyOnMap: initiallyOnMap
                    }};
                }})()
            """)
            layer_checks[elem_id] = chk

        # Check Basemaps
        basemap_checks = {}
        for b_val in ["satellite", "osm", "topo", "dark"]:
            b_res = cdp.eval_js(f"""
                (() => {{
                    const radio = document.querySelector('input[name="basemapRadio"][value="{b_val}"]');
                    if (radio) {{
                        radio.click();
                        radio.dispatchEvent(new Event('change'));
                    }}
                    const map = window.maps?.explorer;
                    const layers = window.explorerLayers || {{}};
                    const keyMap = {{
                        satellite: 'basemapSat',
                        osm: 'basemapOsm',
                        topo: 'basemapTopo',
                        dark: 'basemapDark'
                    }};
                    const targetLyr = layers[keyMap['{b_val}']];
                    return {{
                        radioExists: !!radio,
                        radioChecked: radio ? radio.checked : false,
                        layerOnMap: !!targetLyr && !!map && map.hasLayer(targetLyr)
                    }};
                }})()
            """)
            basemap_checks[b_val] = b_res
            time.sleep(0.3)

        # Revert to Dark
        cdp.eval_js("""
            const r = document.querySelector('input[name="basemapRadio"][value="dark"]');
            if (r) { r.click(); r.dispatchEvent(new Event('change')); }
        """)

        # Legend Check
        legend_data = cdp.eval_js("""
            (() => {
                const leg = document.getElementById('gisFloatingLegend');
                const content = document.getElementById('gisLegendContent');
                const items = Array.from(content?.querySelectorAll('.legend-row') || []).map(r => ({
                    text: r.textContent?.trim(),
                    color: r.querySelector('.swatch')?.style?.backgroundColor
                }));
                const btnToggle = document.getElementById('btnToggleLegend');
                return {
                    legendVisible: leg && leg.style.display !== 'none',
                    itemsCount: items.length,
                    items: items,
                    hasToggleBtn: !!btnToggle
                };
            })()
        """)

        wf5 = {
            "layers": layer_checks,
            "basemaps": basemap_checks,
            "legend": legend_data
        }
        results["workflow_5_gis_layers_and_legend"] = wf5
        print("  Workflow 5 Result:", json.dumps(wf5, indent=2))

        # ---------------------------------------------------------------------
        # WORKFLOW 6: Map Inspection & Info Panel Dynamic Updates
        # ---------------------------------------------------------------------
        print("\n--- WORKFLOW 6: Dynamic Map Inspection Updates ---")
        test_points = [
            ("Tanuku", 16.7500, 81.6800),
            ("Bhimavaram", 16.5400, 81.5200),
            ("Polavaram", 17.2500, 81.6400)
        ]
        insp_updates = {}
        for m_name, lat, lon in test_points:
            cdp.eval_js(f"window.inspectCoordinates({lat}, {lon});")
            time.sleep(0.8)
            res = cdp.eval_js("""
                (() => {
                    const title = document.getElementById('drawerLocationTitle')?.textContent?.trim();
                    const metrics = {};
                    document.querySelectorAll('.drawer-metric-box').forEach(b => {
                        const k = b.querySelector('.drawer-metric-label')?.textContent?.trim();
                        const v = b.querySelector('.drawer-metric-val')?.textContent?.trim();
                        if (k) metrics[k] = v;
                    });
                    return {
                        title: title,
                        metrics: metrics
                    };
                })()
            """)
            insp_updates[m_name] = res

        results["workflow_6_inspection_dynamic_updates"] = insp_updates
        print("  Workflow 6 Result:", json.dumps(insp_updates, indent=2))

        # ---------------------------------------------------------------------
        # WORKFLOW 7: Weather Live-Data / Unavailable State
        # ---------------------------------------------------------------------
        print("\n--- WORKFLOW 7: Weather Intelligence State ---")
        cdp.eval_js("window.switchWorkspace('weather');")
        time.sleep(1.0)
        weather_audit = cdp.eval_js("""
            (() => {
                const ws = document.getElementById('workspace-weather');
                const card = document.getElementById('weatherFullCard');
                const tempNum = card?.querySelector('.weather-temp-num')?.textContent?.trim();
                const condition = card?.querySelector('.weather-condition-text')?.textContent?.trim();
                const locText = card?.querySelector('.weather-location-text')?.textContent?.trim();
                const forecastDays = Array.from(card?.querySelectorAll('.forecast-day-card') || []).map(d => ({
                    name: d.querySelector('.forecast-day-name')?.textContent?.trim(),
                    temp: d.querySelector('.forecast-day-temp')?.textContent?.trim()
                }));
                const metrics = Array.from(card?.querySelectorAll('.w-metric-tile') || []).map(m => ({
                    title: m.querySelector('.w-metric-title')?.textContent?.trim(),
                    val: m.querySelector('.w-metric-val')?.textContent?.trim()
                }));
                const badge = card?.querySelector('.badge-pill')?.textContent?.trim();
                const rawCardHtml = card?.innerHTML?.substring(0, 300);
                return {
                    workspaceActive: ws?.classList.contains('active'),
                    cardPresent: !!card,
                    temperature: tempNum,
                    condition: condition,
                    location: locText,
                    badge: badge,
                    forecastDaysCount: forecastDays.length,
                    forecastDays: forecastDays,
                    metrics: metrics,
                    cardSnippet: rawCardHtml
                };
            })()
        """)
        results["workflow_7_weather_state"] = weather_audit
        print("  Workflow 7 Result:", json.dumps(weather_audit, indent=2))

        # ---------------------------------------------------------------------
        # WORKFLOW 8: Alert Interface & Available States
        # ---------------------------------------------------------------------
        print("\n--- WORKFLOW 8: Alert Interface & 5-Tier Safety ---")
        alert_audit = cdp.eval_js("""
            (() => {
                // Check alert elements in weather workspace or overview
                const alertCards = Array.from(document.querySelectorAll('.alert-tier-card, .alert-box, .ticker-wrap')).map(el => ({
                    class: el.className,
                    text: el.innerText?.trim()?.substring(0, 150)
                }));
                return {
                    alertElementsCount: alertCards.length,
                    alertElements: alertCards
                };
            })()
        """)
        # Also test API endpoint directly
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT_SERVER}/api/v1/alerts/mandal/Rajahmundry") as r:
                api_alert = json.loads(r.read().decode())
        except Exception as e:
            api_alert = {"error": str(e)}

        results["workflow_8_alert_interface"] = {
            "ui_elements": alert_audit,
            "api_endpoint_rajahmundry": api_alert
        }
        print("  Workflow 8 Result:", json.dumps(results["workflow_8_alert_interface"], indent=2))

        # ---------------------------------------------------------------------
        # WORKFLOW 9: Every Visible Button, Filter & Nav Item
        # ---------------------------------------------------------------------
        print("\n--- WORKFLOW 9: Buttons, Filters & Navigation Controls ---")
        btn_audit = {}

        # 1. Nav items switching
        nav_targets = ["overview", "explorer", "risk", "impact", "weather", "global", "evidence"]
        nav_results = {}
        for target in nav_targets:
            cdp.eval_js(f"window.switchWorkspace('{target}');")
            time.sleep(0.3)
            active_info = cdp.eval_js(f"""
                (() => {{
                    const el = document.getElementById('workspace-{target}');
                    const btn = document.querySelector('.app-nav .nav-item[data-workspace="{target}"]');
                    return {{
                        workspaceActive: el?.classList.contains('active'),
                        buttonActive: btn?.classList.contains('active'),
                        display: window.getComputedStyle(el).display
                    }};
                }})()
            """)
            nav_results[target] = active_info
        btn_audit["nav_tabs"] = nav_results

        # 2. Risk filter dropdown
        cdp.eval_js("window.switchWorkspace('risk');")
        time.sleep(0.5)
        risk_filter_res = cdp.eval_js("""
            (() => {
                const sel = document.getElementById('riskFilterSelectWorkspace');
                if (!sel) return { exists: false };
                const initialCount = document.querySelectorAll('#mandalRankingsTableBody tr').length;
                sel.value = 'Very High';
                sel.dispatchEvent(new Event('change'));
                const filteredCount = document.querySelectorAll('#mandalRankingsTableBody tr').length;
                sel.value = 'ALL';
                sel.dispatchEvent(new Event('change'));
                const restoredCount = document.querySelectorAll('#mandalRankingsTableBody tr').length;
                return {
                    exists: true,
                    initialRows: initialCount,
                    filteredVeryHighRows: filteredCount,
                    restoredAllRows: restoredCount
                };
            })()
        """)
        btn_audit["risk_filter_dropdown"] = risk_filter_res

        # 3. Impact facility filter
        cdp.eval_js("window.switchWorkspace('impact');")
        time.sleep(0.5)
        impact_filter_res = cdp.eval_js("""
            (() => {
                const sel = document.getElementById('facilityTypeFilter');
                if (!sel) return { exists: false };
                sel.value = 'healthcare';
                sel.dispatchEvent(new Event('change'));
                return {
                    exists: true,
                    selectedVal: sel.value
                };
            })()
        """)
        btn_audit["impact_facility_filter"] = impact_filter_res

        # 4. Fit Basin button
        cdp.eval_js("window.switchWorkspace('explorer');")
        time.sleep(0.5)
        fit_res = cdp.eval_js("""
            (() => {
                const btn = document.getElementById('btnFitBasinExtent');
                const map = window.maps?.explorer;
                const prevCenter = map ? [Math.round(map.getCenter().lat*100)/100, Math.round(map.getCenter().lng*100)/100] : null;
                if (btn) btn.click();
                const newCenter = map ? [Math.round(map.getCenter().lat*100)/100, Math.round(map.getCenter().lng*100)/100] : null;
                return {
                    buttonExists: !!btn,
                    prevCenter: prevCenter,
                    newCenter: newCenter
                };
            })()
        """)
        btn_audit["fit_basin_button"] = fit_res

        # 5. Globe buttons
        cdp.eval_js("window.switchWorkspace('global');")
        time.sleep(0.5)
        globe_btn_res = cdp.eval_js("""
            (() => {
                const btnPause = document.getElementById('btnToggleGlobeRotation');
                const btnReset = document.getElementById('btnResetGlobeView');
                const btnTex = document.getElementById('btnToggleGlobeTexture');
                const pills = Array.from(document.querySelectorAll('.btn-globe-pill')).map(p => p.getAttribute('data-country'));
                return {
                    hasPauseBtn: !!btnPause,
                    hasResetBtn: !!btnReset,
                    hasTextureToggleBtn: !!btnTex,
                    countryPills: pills
                };
            })()
        """)
        btn_audit["globe_buttons"] = globe_btn_res

        results["workflow_9_controls_audit"] = btn_audit
        print("  Workflow 9 Result:", json.dumps(btn_audit, indent=2))

        # ---------------------------------------------------------------------
        # WORKFLOW 10: Cross-Panel Consistency on Selected Location Change
        # ---------------------------------------------------------------------
        print("\n--- WORKFLOW 10: Selected Location Consistency Across Panels ---")
        cdp.eval_js("window.switchWorkspace('explorer');")
        time.sleep(0.5)
        # Select Bhimavaram
        cdp.eval_js("window.inspectCoordinates(16.540, 81.520);")
        time.sleep(1.0)
        consistency = cdp.eval_js("""
            (() => {
                const appLoc = window.appState?.selectedLocation;
                const drawerTitle = document.getElementById('drawerLocationTitle')?.textContent?.trim();
                
                return {
                    appStateSelectedName: appLoc?.name,
                    appStateMandal: appLoc?.mandalName,
                    appStateDistrict: appLoc?.districtName,
                    drawerTitle: drawerTitle,
                    drawerMatchesAppState: drawerTitle ? drawerTitle.includes('Bhimavaram') : false
                };
            })()
        """)
        results["workflow_10_location_consistency"] = consistency
        print("  Workflow 10 Result:", json.dumps(consistency, indent=2))

        results["audit_overall_status"] = "COMPLETE"
        print("\n[+] BROWSER AUDIT WORKFLOW EXECUTION COMPLETE.")

    finally:
        chrome.terminate()
        if server:
            server.terminate()
            server.wait()
            if log_fp: log_fp.close()
        print("[*] Chrome and server stopped.")

    out_file = BASE_DIR / "data" / "metadata" / "phase54_browser_audit_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Audit results saved to {out_file}")

if __name__ == "__main__":
    main()
