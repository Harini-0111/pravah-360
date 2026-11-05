import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://apsdmagis.ap.gov.in/weather-watch/cyclone.html", headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
    html = r.read().decode("utf-8", errors="ignore")

# Find all fetch and XMLHttpRequest occurrences
calls = re.findall(r'(?:fetch|\$\.ajax|\$\.get|open\()\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', html)
print("Fetch/AJAX URLs in APSDMA page:", set(calls))

# Find lines containing sachet_alerted_mandals
lines = [l.strip() for l in html.splitlines() if "sachet_alerted_mandals" in l or "obs_rain" in l]
for l in lines[:10]:
    print("Match line:", l[:120])
