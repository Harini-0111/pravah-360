import subprocess, time, json, urllib.request, sys, os
sys.path.insert(0, os.path.abspath("."))

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PYTHON_PATH = r".venv\Scripts\python.exe"

server = subprocess.Popen([PYTHON_PATH, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# Poll until server is healthy
for i in range(25):
    time.sleep(0.5)
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=1) as resp:
            print("Server ready after", (i+1)*0.5, "s")
            break
    except Exception:
        pass
chrome = subprocess.Popen([CHROME_PATH, "--headless=new", "--remote-debugging-port=9230", "http://127.0.0.1:8000/#overview"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2.0)
try:
    from scripts.deep_browser_gis_audit import CDPClient
    cdp = CDPClient(port=9230)
    cdp.connect()
    cdp.send_cmd("Runtime.enable")
    time.sleep(1.0)
    
    # Check if DOMContentLoaded fired or if there are errors
    ready = cdp.eval_js("document.readyState")
    print("document.readyState:", ready)
    
    app_state = cdp.eval_js("typeof window.appState")
    print("typeof window.appState:", app_state)

    has_switch = cdp.eval_js("typeof window.switchWorkspace")
    print("typeof window.switchWorkspace:", has_switch)

    # Test switching to each workspace
    for wid in ["overview", "explorer", "risk", "impact", "weather", "global", "evidence"]:
        res = cdp.eval_js(f"(() => {{ window.switchWorkspace('{wid}'); const el = document.getElementById('workspace-{wid}'); return {{ id: '{wid}', active: el.classList.contains('active'), display: window.getComputedStyle(el).display, w: Math.round(el.getBoundingClientRect().width), h: Math.round(el.getBoundingClientRect().height) }}; }})()")
        print("switch test:", res)

finally:
    chrome.terminate()
    server.terminate()
