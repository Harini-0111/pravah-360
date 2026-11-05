import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://apsdmagis.ap.gov.in/weather-watch/cyclone.html", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
    html = r.read().decode("utf-8", errors="ignore")

lines = [l.strip() for l in html.splitlines() if "DATA" in l and ("=" in l or ":" in l)]
for l in lines[:15]:
    print("DATA line:", l[:100])

lines_opt = [l.strip() for l in html.splitlines() if "function optional" in l or "function get" in l]
for l in lines_opt[:5]:
    print("Func line:", l[:100])
