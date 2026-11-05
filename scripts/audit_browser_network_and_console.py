"""
Audits real browser network payload, tile loading, GeoJSON transfers, and console messages.
"""
import os
import sys
import time
import json
import socket
import subprocess
import urllib.request
import urllib.parse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYTHON_PATH = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def run_network_audit():
    print("Starting FastAPI server on 127.0.0.1:8000...")
    server = subprocess.Popen(
        [PYTHON_PATH, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2.5)

    print("Launching clean headless Chrome (incognito, no extensions)...")
    chrome = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--disable-extensions",
        "--incognito",
        "--remote-debugging-port=9226",
        "--window-size=1680,1050",
        "about:blank"
    ])
    time.sleep(2.0)

    try:
        tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9226/json").read().decode())
        page_tab = next(t for t in tabs if t.get("type") == "page")
        ws_url = page_tab["webSocketDebuggerUrl"]
        print(f"Connecting to Page WebSocket: {ws_url}...")

        parsed = urllib.parse.urlparse(ws_url)
        s = socket.create_connection((parsed.hostname, parsed.port), timeout=15)
        handshake = (
            f"GET {parsed.path} HTTP/1.1\r\n"
            f"Host: {parsed.netloc}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        s.sendall(handshake.encode())
        res = s.recv(2048)

        def call_cdp(cid, method, params=None):
            req = {"id": cid, "method": method}
            if params: req["params"] = params
            data = json.dumps(req).encode('utf-8')
            mask = os.urandom(4)
            l = len(data)
            header = bytes([0x81, 0x80 | (l if l < 126 else 126)])
            if l >= 126:
                header += bytes([(l >> 8) & 0xff, l & 0xff])
            header += mask
            s.sendall(header + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))
            
            # Read until message with id arrives
            start = time.time()
            while time.time() - start < 15.0:
                b1, b2 = s.recv(2)
                length = b2 & 0x7f
                if length == 126:
                    l_bytes = s.recv(2)
                    length = (l_bytes[0] << 8) | l_bytes[1]
                elif length == 127:
                    l_bytes = s.recv(8)
                    length = int.from_bytes(l_bytes, "big")
                
                buf = bytearray()
                while len(buf) < length:
                    chunk = s.recv(min(length - len(buf), 65536))
                    if not chunk: break
                    buf.extend(chunk)
                try:
                    msg = json.loads(buf.decode('utf-8', errors='ignore'))
                    if msg.get("id") == cid:
                        return msg
                except Exception:
                    continue
            return {"error": "Timeout"}

        # Enable Page & Runtime
        call_cdp(1, "Page.enable")
        call_cdp(2, "Runtime.enable")

        print("Navigating to http://127.0.0.1:8000/#explorer...")
        call_cdp(3, "Page.navigate", {"url": "http://127.0.0.1:8000/#explorer"})
        
        # Wait 4 seconds for GIS tiles and vector layers to stream
        print("Waiting 4 seconds for map tiles, vectors, and overlays to load...")
        time.sleep(4.0)

        js_eval = """
        (function() {
            var entries = performance.getEntriesByType('resource');
            return {
                timing: {
                    domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                    load: performance.timing.loadEventEnd - performance.timing.navigationStart
                },
                resources: entries.map(function(r) {
                    return {
                        name: r.name,
                        initiator: r.initiatorType,
                        durationMs: Math.round(r.duration),
                        transferBytes: r.transferSize || 0,
                        decodedBytes: r.decodedBodySize || 0
                    };
                }),
                gisState: {
                    mapExists: !!window.L,
                    hasTiles: document.querySelectorAll('.leaflet-tile-loaded').length,
                    activeWorkspace: window.location.hash
                }
            };
        })()
        """
        reply = call_cdp(4, "Runtime.evaluate", {"expression": js_eval, "returnByValue": True})
        val = reply.get("result", {}).get("result", {}).get("value", {})

        resources = val.get("resources", [])
        timing = val.get("timing", {})
        gis_state = val.get("gisState", {})

        total_transfer = sum(r.get("transferBytes", 0) for r in resources)
        tiles = [r for r in resources if "tile" in r["name"] or "MapServer/tile" in r["name"] or "arcgisonline" in r["name"]]
        geofiles = [r for r in resources if r["name"].endswith(".geojson") or "/data/" in r["name"] or "/boundaries/" in r["name"]]
        png_overlays = [r for r in resources if "overlays" in r["name"]]

        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timing_ms": timing,
            "gis_state": gis_state,
            "total_resources_count": len(resources),
            "total_network_transfer_bytes": total_transfer,
            "total_network_transfer_kb": round(total_transfer / 1024, 1),
            "total_network_transfer_mb": round(total_transfer / (1024 * 1024), 2),
            "tiles_loaded_count": len(tiles),
            "tiles_loaded_in_dom": gis_state.get("hasTiles", 0),
            "tiles_avg_latency_ms": round(sum(t["durationMs"] for t in tiles) / len(tiles), 1) if tiles else 0,
            "geojson_layers_count": len(geofiles),
            "png_overlays_count": len(png_overlays),
            "key_assets": [
                {
                    "name": r["name"].split("/")[-1].split("?")[0],
                    "size_kb": round(r["transferBytes"] / 1024, 1),
                    "duration_ms": r["durationMs"]
                }
                for r in resources if r.get("transferBytes", 0) > 10000 or r["name"].endswith((".geojson", ".png", ".js", ".css"))
            ]
        }

        out_path = os.path.join(BASE_DIR, "data", "metadata", "browser_performance_audit.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print("\n=======================================================")
        print("REAL BROWSER NETWORK & PERFORMANCE AUDIT")
        print("=======================================================")
        print(f"Total Resources Downloaded: {report['total_resources_count']}")
        print(f"Total Network Payload: {report['total_network_transfer_kb']} KB ({report['total_network_transfer_mb']} MB)")
        print(f"DOM Ready: {timing.get('domReady')} ms | Load Event: {timing.get('load')} ms")
        print(f"Esri Canvas Tiles Loaded: {report['tiles_loaded_count']} network tiles (DOM rendered: {report['tiles_loaded_in_dom']})")
        print(f"Average Tile Latency: {report['tiles_avg_latency_ms']} ms")
        print(f"GeoJSON Vector Datasets: {report['geojson_layers_count']}")
        print(f"Sentinel-1 SAR Web Overlays: {report['png_overlays_count']}")
        print(f"\nAudit report saved to: {out_path}")

    finally:
        chrome.terminate()
        chrome.wait()
        server.terminate()
        server.wait()
        print("Server and Chrome shutdown.")

if __name__ == "__main__":
    run_network_audit()
