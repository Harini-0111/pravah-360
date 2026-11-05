import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = "https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/"

def inspect_file(fname):
    print(f"\n=== Inspecting {fname} ===")
    url = base + fname
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
        js = json.loads(r.read().decode("utf-8"))
        if isinstance(js, dict):
            print("Top keys:", list(js.keys()))
            for k in list(js.keys())[:4]:
                v = js[k]
                if isinstance(v, (str, int, float, bool)):
                    print(f"  {k}: {v}")
                elif isinstance(v, list):
                    print(f"  {k}: list of {len(v)} items; sample item: {v[0] if v else 'empty'}")
                elif isinstance(v, dict):
                    print(f"  {k}: dict keys: {list(v.keys())[:5]}")
        elif isinstance(js, list):
            print(f"List of {len(js)} items; sample item: {js[0] if js else 'empty'}")

inspect_file("cyclone.json")
inspect_file("layers/sachet_alerted_mandals.geojson")
inspect_file("obs_rain/index.json")
