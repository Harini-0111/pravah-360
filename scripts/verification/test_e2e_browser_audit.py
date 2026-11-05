import os
import sys
import time
import json
import socket
import tempfile
import shutil
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT_CDP = 9244
PORT_SERVER = 8000

class CDPClient:
    def __init__(self, port=PORT_CDP):
        self.port = port
        self.cmd_id = 0
        self.sock = None

    def connect(self):
        # Poll for Chrome CDP endpoint
        for attempt in range(10):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json", timeout=2) as r:
                    tabs = json.loads(r.read().decode())
                    page_tab = next((t for t in tabs if t.get("type") == "page"), None)
                    if page_tab and "webSocketDebuggerUrl" in page_tab:
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
                        return True
            except Exception:
                time.sleep(1.0)
        raise RuntimeError("Failed to connect to Chrome CDP WebSocket after 10 attempts.")

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
                    payload_len = int.from_bytes(buf[idx+2:idx+4], 'big')
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

def run_e2e_tests():
    sys.stdout.reconfigure(encoding="utf-8")
    temp_dir = tempfile.mkdtemp(prefix="chrome_cdp_")
    print(f"[*] Launching Headless Chrome on CDP port {PORT_CDP} (temp profile: {temp_dir})...")

    chrome = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-extensions",
        f"--user-data-dir={temp_dir}",
        f"--remote-debugging-port={PORT_CDP}",
        "--window-size=1680,1050",
        f"http://127.0.0.1:{PORT_SERVER}/#overview"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        cdp = CDPClient(port=PORT_CDP)
        cdp.connect()
        print("[+] CDP connected successfully.")
        cdp.send_cmd("Page.enable")
        cdp.send_cmd("Runtime.enable")
        time.sleep(2.0)

        # ---------------------------------------------------------------------
        # TEST 1: Universal Search for "Rajamahendravaram" and "Rajahmundry"
        # ---------------------------------------------------------------------
        print("\n--- TEST 1: Universal Geographic Search ---")
        search_res1 = cdp.eval_js("""
            (() => {
                const input = document.getElementById('globalLocationSearchInput');
                input.value = 'Rajamahendravaram';
                input.dispatchEvent(new Event('input'));
                const items = Array.from(document.querySelectorAll('#globalSearchSuggestions .suggestion-item')).map(el => ({
                    title: el.querySelector('.suggestion-title')?.textContent?.trim(),
                    meta: el.querySelector('.suggestion-meta')?.textContent?.trim(),
                    lat: el.getAttribute('data-lat'),
                    lon: el.getAttribute('data-lon')
                }));
                return items;
            })()
        """)
        print(f"Suggestions for 'Rajamahendravaram': {len(search_res1)} found")
        assert len(search_res1) >= 2
        urban_r = next(x for x in search_res1 if "Rajamahendravaram (Rajahmundry)" in x["title"])
        print(f"  * Matched: {urban_r['title']} ({urban_r['lat']}, {urban_r['lon']})")
        assert urban_r["lat"] == "16.985"
        assert urban_r["lon"] == "81.78"

        # Click the suggestion
        cdp.eval_js("""
            (() => {
                const first = document.querySelector('#globalSearchSuggestions .suggestion-item');
                if (first) first.click();
            })()
        """)
        time.sleep(1.0)
        sel_loc = cdp.eval_js("window.appState.selectedLocation.name")
        print(f"  * Location after selection: {sel_loc}")

        # Search for accepted alternative "Rajahmundry"
        search_res2 = cdp.eval_js("""
            (() => {
                const input = document.getElementById('globalLocationSearchInput');
                input.value = 'Rajahmundry';
                input.dispatchEvent(new Event('input'));
                const items = Array.from(document.querySelectorAll('#globalSearchSuggestions .suggestion-item')).map(el => ({
                    title: el.querySelector('.suggestion-title')?.textContent?.trim(),
                    lat: el.getAttribute('data-lat'),
                    lon: el.getAttribute('data-lon')
                }));
                return items;
            })()
        """)
        print(f"Suggestions for 'Rajahmundry': {len(search_res2)} found")
        assert len(search_res2) >= 2
        print("[+] Test 1 (Search Aliases) PASSED!")

        # ---------------------------------------------------------------------
        # TEST 2: Weather Transparency
        # ---------------------------------------------------------------------
        print("\n--- TEST 2: Weather Transparency ---")
        cdp.eval_js("window.switchWorkspace('weather');")
        time.sleep(2.0)
        weather_text = cdp.eval_js("document.getElementById('weatherFullCard')?.innerText") or ""
        print("Weather Card Content Preview:\n", weather_text[:280])
        assert "Weather information unavailable. Google Weather API is not configured." in weather_text
        assert "29°C" not in weather_text
        assert "Partly Cloudy" not in weather_text
        print("[+] Test 2 (Weather Transparency) PASSED!")

        # ---------------------------------------------------------------------
        # TEST 3: Emergency Operations Simulator: Resident Role
        # ---------------------------------------------------------------------
        print("\n--- TEST 3: Emergency Operations Simulator (Resident View) ---")
        cdp.eval_js("window.switchWorkspace('operations');")
        time.sleep(1.5)
        cdp.eval_js("window.switchOpsRole('resident');")
        time.sleep(1.5)

        res_view = cdp.eval_js("""
            (() => {
                return {
                    location: document.getElementById('residentLocationTitle')?.textContent?.trim(),
                    tier: document.getElementById('residentTierBadge')?.textContent?.trim(),
                    score: document.getElementById('residentScoreVal')?.textContent?.trim(),
                    headline: document.getElementById('residentAdvHeadline')?.textContent?.trim(),
                    facilitiesCount: document.querySelectorAll('#residentFacilitiesList .facility-item-row').length
                };
            })()
        """)
        print("Resident View Details:", res_view)
        assert "Rajamahendravaram" in res_view["location"] or "Rajahmundry" in res_view["location"]
        assert "VERY HIGH" in res_view["tier"]
        assert float(res_view["score"]) > 0.6
        assert res_view["facilitiesCount"] >= 3

        # Click Acknowledge Warning button
        print("Testing Resident Acknowledgment button...")
        ack_click_res = cdp.eval_js("""
            (() => {
                const btn = document.getElementById('btnResidentAcknowledge');
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            })()
        """)
        time.sleep(1.5)
        btn_text = cdp.eval_js("document.getElementById('btnResidentAcknowledge')?.innerText") or ""
        print(f"Acknowledgment button text after click: '{btn_text}'")
        assert "Acknowledged" in btn_text
        print("[+] Test 3 (Resident View & Acknowledgment) PASSED!")

        # ---------------------------------------------------------------------
        # TEST 4: Emergency Operations Simulator: Mandal Admin Role
        # ---------------------------------------------------------------------
        print("\n--- TEST 4: Emergency Operations Simulator (Mandal Admin) ---")
        cdp.eval_js("window.switchOpsRole('mandal');")
        time.sleep(1.5)

        mandal_stats = cdp.eval_js("""
            (() => {
                return {
                    risk: document.getElementById('mandalPillRisk')?.textContent?.trim(),
                    base: document.getElementById('mandalPillBase')?.textContent?.trim(),
                    exp: document.getElementById('mandalPillExp')?.textContent?.trim(),
                    queued: document.getElementById('telemetryQueued')?.textContent?.trim()
                };
            })()
        """)
        print("Mandal Admin View Stats:", mandal_stats)
        assert mandal_stats["risk"] in ("Very High", "High")
        assert int(mandal_stats["queued"].replace(",", "")) > 0

        # Broadcast simulated advisory
        print("Submitting new advisory via form...")
        broadcast_res = cdp.eval_js("""
            (() => {
                const headline = document.getElementById('advHeadlineInput');
                const msg = document.getElementById('advMessageInput');
                const action = document.getElementById('advActionInput');
                const submitBtn = document.getElementById('btnDispatchAdvisory');

                headline.value = 'Automated Verification Flood Advisory';
                msg.value = 'Water flow rate increasing rapidly along Godavari main channel.';
                action.value = 'Move to secondary high school cyclone shelter immediately.';
                submitBtn.click();
                return true;
            })()
        """)
        time.sleep(2.0)
        table_rows = cdp.eval_js("document.querySelectorAll('#mandalAdvisoriesTbody tr').length")
        print(f"Mandal advisory history table row count: {table_rows}")
        assert table_rows >= 1
        print("[+] Test 4 (Mandal Broadcast Telemetry) PASSED!")

        # ---------------------------------------------------------------------
        # TEST 5: Emergency Operations Simulator: District Admin Role
        # ---------------------------------------------------------------------
        print("\n--- TEST 5: Emergency Operations Simulator (District Admin) ---")
        cdp.eval_js("window.switchOpsRole('district');")
        time.sleep(1.5)

        dist_rows = cdp.eval_js("""
            (() => {
                const rows = Array.from(document.querySelectorAll('#districtComparisonTbody tr')).map(tr => {
                    const cells = tr.querySelectorAll('td');
                    return {
                        district: cells[0]?.textContent?.trim(),
                        mandals: cells[1]?.textContent?.trim(),
                        tier: cells[2]?.textContent?.trim(),
                        pop: cells[3]?.textContent?.trim(),
                        expPop: cells[4]?.textContent?.trim(),
                        expPct: cells[5]?.textContent?.trim()
                    };
                });
                return rows;
            })()
        """)
        print(f"District Comparison Table: {len(dist_rows)} districts loaded")
        assert len(dist_rows) == 6
        for d in dist_rows:
            print(f"  * {d['district']}: {d['mandals']} | {d['expPop']} exposed ({d['expPct']})")
        print("[+] Test 5 (District Oversight) PASSED!")

        # ---------------------------------------------------------------------
        # TEST 6: Emergency Operations Simulator: ERT Dispatch Board
        # ---------------------------------------------------------------------
        print("\n--- TEST 6: Emergency Operations Simulator (ERT Dispatch Board) ---")
        cdp.eval_js("window.switchOpsRole('ert');")
        time.sleep(1.5)

        ert_rows_count = cdp.eval_js("document.querySelectorAll('#ertResourcesTbody tr').length")
        print(f"ERT Tactical Board items count: {ert_rows_count}")
        assert ert_rows_count >= 6

        # Test lifecycle transition button click
        print("Testing lifecycle action button click on first row...")
        action_btn_clicked = cdp.eval_js("""
            (() => {
                const firstBtn = document.querySelector('#ertResourcesTbody .btn-lc');
                if (firstBtn) {
                    const reqId = firstBtn.getAttribute('data-id');
                    const action = firstBtn.getAttribute('data-action');
                    firstBtn.click();
                    return { reqId, action };
                }
                return null;
            })()
        """)
        time.sleep(2.0)
        print("Lifecycle Action Clicked:", action_btn_clicked)
        assert action_btn_clicked is not None
        print("[+] Test 6 (ERT Tactical Allocation Board) PASSED!")

        # ---------------------------------------------------------------------
        # TEST 7: Global 3D Earth
        # ---------------------------------------------------------------------
        print("\n--- TEST 7: Global 3D Earth Workspace ---")
        cdp.eval_js("window.switchWorkspace('global');")
        time.sleep(2.5)
        globe_canvas = cdp.eval_js("document.querySelector('#globe-container canvas') !== null")
        print(f"WebGL Globe Canvas initialized: {globe_canvas}")
        assert globe_canvas is True
        print("[+] Test 7 (Global 3D Earth) PASSED!")

        print("\n=======================================================")
        print(">>> ALL 7 BROWSER END-TO-END WORKFLOWS PASSED 100%! <<<")
        print("=======================================================")

    finally:
        try:
            chrome.kill()
        except:
            pass
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

if __name__ == "__main__":
    run_e2e_tests()
