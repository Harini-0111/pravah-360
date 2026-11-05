"""
Quick headless browser diagnostic script using Chrome DevTools.
Inspects DOM, Leaflet maps, console errors, and takes screenshots.
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

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SCREENSHOT_PATH = r"C:\major project\docs\screenshots\diagnostic_overview.png"
EXPLORER_SCREENSHOT_PATH = r"C:\major project\docs\screenshots\diagnostic_explorer.png"

os.makedirs(r"C:\major project\docs\screenshots", exist_ok=True)

# Launch headless Chrome with remote debugging on port 9222
user_data_dir = os.path.join(os.environ.get("TEMP", "C:\\temp"), "chrome_diag_profile")
chrome_cmd = [
    CHROME_PATH,
    "--headless=new",
    "--remote-debugging-port=9222",
    f"--user-data-dir={user_data_dir}",
    "--disable-gpu",
    "--no-sandbox",
    "--window-size=1600,1000",
    "http://127.0.0.1:8000/#overview"
]

proc = subprocess.Popen(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(2.5)

try:
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read().decode())
    page_tab = next(t for t in tabs if t.get("type") == "page")
    ws_url = page_tab["webSocketDebuggerUrl"]
    parsed = urllib.parse.urlparse(ws_url)
    sock = socket.create_connection((parsed.hostname, parsed.port), timeout=15)
    
    # Handshake
    handshake = (
        f"GET {parsed.path} HTTP/1.1\r\n"
        f"Host: {parsed.netloc}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(handshake.encode())
    sock.recv(2048)

    cmd_id = 0
    def send_cmd(method, params=None):
        global cmd_id
        cmd_id += 1
        req = {"id": cmd_id, "method": method}
        if params: req["params"] = params
        data = json.dumps(req).encode('utf-8')
        mask = os.urandom(4)
        l = len(data)
        header = bytes([0x81, 0x80 | (l if l < 126 else 126)])
        if l >= 126:
            header += bytes([(l >> 8) & 0xff, l & 0xff])
        header += mask
        sock.sendall(header + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))
        
        # Read response
        buf = bytearray()
        while True:
            chunk = sock.recv(65536)
            if not chunk: break
            buf.extend(chunk)
            # Find json
            try:
                # Basic frame decoding
                payload_offset = 2
                plen = buf[1] & 0x7f
                if plen == 126: payload_offset = 4
                elif plen == 127: payload_offset = 10
                payload = buf[payload_offset:]
                res = json.loads(payload.decode('utf-8', errors='ignore'))
                if res.get("id") == cmd_id:
                    return res.get("result", {})
            except Exception:
                pass
        return {}

    # Wait for page load
    time.sleep(2.0)

    # 1. Capture diagnostic evaluation
    diag_js = """
    (() => {
        const errors = [];
        const overviewMapElem = document.getElementById('overview-map');
        const explorerMapElem = document.getElementById('explorer-map');
        
        return {
            title: document.title,
            currentWorkspace: window.appState ? window.appState.currentWorkspace : 'N/A',
            mapsObjectPresent: !!window.maps,
            overviewMapInstance: !!(window.maps && window.maps.overview),
            explorerMapInstance: !!(window.maps && window.maps.explorer),
            overviewMapDims: overviewMapElem ? {
                width: overviewMapElem.offsetWidth,
                height: overviewMapElem.offsetHeight,
                clientWidth: overviewMapElem.clientWidth,
                clientHeight: overviewMapElem.clientHeight
            } : null,
            explorerMapDims: explorerMapElem ? {
                width: explorerMapElem.offsetWidth,
                height: explorerMapElem.offsetHeight
            } : null,
            overviewTileLayersCount: (window.maps && window.maps.overview) ? Object.keys(window.maps.overview._layers || {}).length : 0,
            explorerTileLayersCount: (window.maps && window.maps.explorer) ? Object.keys(window.maps.explorer._layers || {}).length : 0,
            hasLeaflet: typeof L !== 'undefined',
            leafletVersion: typeof L !== 'undefined' ? L.version : 'NONE'
        };
    })()
    """
    
    send_cmd("Runtime.enable")
    res = send_cmd("Runtime.evaluate", {"expression": diag_js, "returnByValue": True})
    diag_info = res.get("result", {}).get("value", {})
    print("=== BROWSER DIAGNOSTIC INFO ===")
    print(json.dumps(diag_info, indent=2))

    # Take screenshot of overview
    shot = send_cmd("Page.captureScreenshot", {"format": "png"})
    import base64
    if shot.get("data"):
        with open(SCREENSHOT_PATH, "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print(f"Screenshot saved to {SCREENSHOT_PATH} ({len(shot['data'])} base64 chars)")

    # Now switch to explorer and evaluate
    switch_js = "window.switchWorkspace('explorer');"
    send_cmd("Runtime.evaluate", {"expression": switch_js})
    time.sleep(1.5)
    
    res2 = send_cmd("Runtime.evaluate", {"expression": diag_js, "returnByValue": True})
    diag_info2 = res2.get("result", {}).get("value", {})
    print("\n=== EXPLORER DIAGNOSTIC INFO ===")
    print(json.dumps(diag_info2, indent=2))

    shot2 = send_cmd("Page.captureScreenshot", {"format": "png"})
    if shot2.get("data"):
        with open(EXPLORER_SCREENSHOT_PATH, "wb") as f:
            f.write(base64.b64decode(shot2["data"]))
        print(f"Explorer Screenshot saved to {EXPLORER_SCREENSHOT_PATH}")

finally:
    proc.kill()
    print("Diagnostic finished.")
