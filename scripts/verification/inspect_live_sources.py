import urllib.request
import ssl
import json
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def inspect_sachet():
    print("=== Checking NDMA SACHET ===")
    url = "https://sachet.ndma.gov.in/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
            title = re.findall(r"<title>(.*?)</title>", html, re.I)
            print("SACHET title:", title)
            # Find URLs or JS files
            scripts = re.findall(r'<script[^>]*src=["\'](.*?)["\']', html)
            print("Scripts:", scripts[:5])
            # Common SACHET public API endpoints:
            test_apis = [
                "https://sachet.ndma.gov.in/cap_public_website/FetchAlertsDetails",
                "https://sachet.ndma.gov.in/cap_public_website/Common/getAlerts",
                "https://sachet.ndma.gov.in/cap_public_website/assets/js/",
                "https://sachet.ndma.gov.in/api/v1/alerts",
                "https://sachet.ndma.gov.in/cap_public_website/GetStateDetails"
            ]
            for api in test_apis:
                try:
                    req_a = urllib.request.Request(api, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    with urllib.request.urlopen(req_a, context=ctx, timeout=5) as ra:
                        print(f"API {api} -> Status {ra.status}, length: {len(ra.read())}")
                except Exception as ea:
                    print(f"API {api} -> {ea}")
    except Exception as e:
        print("SACHET Error:", e)

def inspect_apsdma():
    print("\n=== Checking APSDMA Cyclone / Disaster Watch ===")
    url = "https://apsdmagis.ap.gov.in/weather-watch/cyclone.html"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
            title = re.findall(r"<title>(.*?)</title>", html, re.I)
            print("APSDMA title:", title)
            # Look for alert tables or geojson links
            geojson_links = re.findall(r'[\'"]([^\'"]*?(?:geojson|json|alert|cyclone)[^\'"]*?)[\'"]', html, re.I)
            print("APSDMA data/json links:", list(set(geojson_links))[:10])
    except Exception as e:
        print("APSDMA Error:", e)

def inspect_imd():
    print("\n=== Checking IMD National & Regional Warning Services ===")
    # Official IMD RSS and Bulletin endpoints:
    imd_urls = [
        "https://mausam.imd.gov.in/backend/assets/press_release/press_release.php",
        "https://mausam.imd.gov.in/",
        "https://rsmcnewdelhi.imd.gov.in/",
        "https://www.imd.gov.in/pages/allindiawxfc.php"
    ]
    for url in imd_urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
                print(f"IMD {url} -> Status {r.status}, length: {len(r.read())}")
        except Exception as e:
            print(f"IMD {url} -> {e}")

if __name__ == "__main__":
    inspect_sachet()
    inspect_apsdma()
    inspect_imd()
