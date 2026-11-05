"""
Independent Acceptance Test and Live Feed Verification Script.
Conducts strict, unvarnished testing of all feeds, river gauges, background daemon,
notifications, emergency operations, and scientific metrics.
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error
from datetime import datetime

REPORT = {}

def log_section(title):
    print(f"\n{'='*70}\n{title}\n{'='*70}")

# =============================================================================
# 1. LIVE FEEDS AUDIT
# =============================================================================
log_section("1. VERIFYING THE FIVE CLAIMED FEEDS")

# 1.1 NDMA SACHET / APSDMA
sachet_url = "https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/layers/sachet_alerted_mandals.geojson"
print(f"Testing Feed 1: NDMA SACHET / APSDMA Alerted Mandals from {sachet_url}...")
try:
    req = urllib.request.Request(sachet_url, headers={"User-Agent": "Mozilla/5.0"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=15) as res:
        status_code = res.status
        content_bytes = res.read()
        latency = round(time.time() - t0, 3)
        sachet_data = json.loads(content_bytes.decode('utf-8'))
        features = sachet_data.get('features', [])
        
        # Analyze timestamps in features
        timestamps = []
        expired_count = 0
        active_count = 0
        now_dt = datetime.now()
        
        sample_feature = features[0] if features else {}
        for f in features:
            props = f.get('properties', {})
            exp = props.get('expires')
            sent = props.get('last_sent')
            if exp:
                timestamps.append(exp)
                # Check expiration format (e.g. ISO or date string)
                try:
                    # typical formats in SACHET: 'YYYY-MM-DDTHH:MM:SS' or similar
                    exp_clean = exp.replace('Z', '').split('+')[0]
                    exp_dt = datetime.fromisoformat(exp_clean)
                    if exp_dt < now_dt:
                        expired_count += 1
                    else:
                        active_count += 1
                except Exception:
                    pass

        REPORT['FEED_1_SACHET'] = {
            "source_provider": "NDMA SACHET / APSDMA Weather-Watch GIS",
            "endpoint": sachet_url,
            "http_status": status_code,
            "retrieval_timestamp": datetime.now().isoformat(),
            "latency_seconds": latency,
            "records_retrieved": len(features),
            "sample_record": sample_feature.get('properties'),
            "sample_geometry_type": sample_feature.get('geometry', {}).get('type'),
            "timestamps_found": len(timestamps),
            "expired_features_in_feed": expired_count,
            "active_features_in_feed": active_count,
            "size_kb": round(len(content_bytes) / 1024, 1)
        }
        print(f"  -> SUCCESS: HTTP {status_code}, {len(features)} mandals retrieved ({round(len(content_bytes)/1024, 1)} KB, {latency}s)")
        print(f"  -> Sample feature props: {sample_feature.get('properties')}")
except Exception as e:
    print(f"  -> ERROR: {e}")
    REPORT['FEED_1_SACHET'] = {"error": str(e), "endpoint": sachet_url}

# Also test APSDMA Cyclone Model
cyclone_url = "https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/cyclone.json"
try:
    with urllib.request.urlopen(urllib.request.Request(cyclone_url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15) as res:
        c_bytes = res.read()
        c_data = json.loads(c_bytes.decode('utf-8'))
        REPORT['FEED_1_CYCLONE'] = {
            "endpoint": cyclone_url,
            "http_status": res.status,
            "size_kb": round(len(c_bytes) / 1024, 1),
            "keys": list(c_data.keys()) if isinstance(c_data, dict) else len(c_data)
        }
        print(f"  -> Cyclone JSON Feed: HTTP {res.status}, {round(len(c_bytes)/1024, 1)} KB")
except Exception as e:
    REPORT['FEED_1_CYCLONE'] = {"error": str(e)}

# 1.2 & 1.3 CWC & AP WRD River Gauges
# Check our river monitoring service implementation
from backend.app.services.river_monitoring_service import RiverMonitoringService
river_srv = RiverMonitoringService()
gauges, source_status = river_srv.get_river_observations()
REPORT['FEED_2_AND_3_RIVER_GAUGES'] = {
    "source_status": source_status.dict(),
    "gauge_count": len(gauges),
    "gauges_detail": [g.dict() for g in gauges]
}
print(f"Feed 2 & 3: CWC / AP WRD Hydrological Stations:")
for g in gauges:
    print(f"  * {g.station_name}: Level={g.current_water_level_m}m, Warning={g.warning_stage_m}m, Danger={g.danger_stage_m}m, Status={g.status}, LiveFlag={getattr(g, 'is_live', False)}, Source={g.data_source}")

# 1.4 & 1.5 Open-Meteo Rainfall & Runoff
open_meteo_url = "https://api.open-meteo.com/v1/forecast?latitude=16.985&longitude=81.780&hourly=precipitation,rain,surface_runoff,river_discharge&forecast_days=1"
print(f"Testing Feed 4 & 5: Open-Meteo Precipitation & Runoff for Rajahmundry ({open_meteo_url})...")
try:
    req = urllib.request.Request(open_meteo_url, headers={"User-Agent": "Mozilla/5.0"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=10) as res:
        status_code = res.status
        content_bytes = res.read()
        latency = round(time.time() - t0, 3)
        om_data = json.loads(content_bytes.decode('utf-8'))
        hourly = om_data.get('hourly', {})
        
        REPORT['FEED_4_AND_5_OPEN_METEO'] = {
            "source_provider": "Open-Meteo Global Hydrometeorological API",
            "endpoint": open_meteo_url,
            "http_status": status_code,
            "retrieval_timestamp": datetime.now().isoformat(),
            "latency_seconds": latency,
            "hourly_variables": list(hourly.keys()),
            "has_precipitation": "precipitation" in hourly,
            "has_surface_runoff": "surface_runoff" in hourly,
            "has_river_discharge": "river_discharge" in hourly,
            "sample_precipitation_series": hourly.get('precipitation', [])[:5],
            "sample_surface_runoff_series": hourly.get('surface_runoff', [])[:5],
            "sample_river_discharge_series": hourly.get('river_discharge', [])[:5] if hourly.get('river_discharge') else "NOT_IN_FORECAST_API"
        }
        print(f"  -> SUCCESS: HTTP {status_code}, latency {latency}s")
        print(f"  -> Hourly variables available: {list(hourly.keys())}")
        print(f"  -> Sample precipitation: {hourly.get('precipitation', [])[:4]}")
        print(f"  -> Sample surface_runoff: {hourly.get('surface_runoff', [])[:4]}")
except Exception as e:
    print(f"  -> ERROR: {e}")
    REPORT['FEED_4_AND_5_OPEN_METEO'] = {"error": str(e), "endpoint": open_meteo_url}

# Write intermediate report
with open(r"C:\major project\scripts\verification\acceptance_report_raw.json", "w", encoding="utf-8") as f:
    json.dump(REPORT, f, indent=2)

print("\nRaw Feed Data Captured.")
