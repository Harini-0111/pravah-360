"""
Live Alert Ingestion Service.
Fetches, normalizes, and matches official disaster warnings across Andhra Pradesh
from NDMA SACHET National Disaster Alert Portal, APSDMA State Emergency Operations Centre,
and IMD (India Meteorological Department).
"""
import os
import ssl
import json
import uuid
import logging
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from backend.app.schemas.monitoring import OfficialDisasterAlert, SourceHealthStatus

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "monitoring"))
ALERTS_FILE = os.path.join(DATA_DIR, "live_disaster_alerts.json")
GEOJSON_CACHE_FILE = os.path.join(DATA_DIR, "sachet_mandals_cache.geojson")

SACHET_GEOJSON_URL = "https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/layers/sachet_alerted_mandals.geojson"
CYCLONE_JSON_URL = "https://apsdmagis.ap.gov.in/weather-watch/data/cyclone/cyclone.json"

# The 21 Lower Godavari study mandals for spatial intersection
LOWER_GODAVARI_MANDALS_SET = {
    "rajahmundry", "rajamahendravaram", "rajamahendravaram urban", "rajahmundry urban",
    "rajamahendravaram rural", "rajahmundry rural", "kovvur", "amalapuram", "mummidivaram",
    "razole", "kothapeta", "kottapeta", "ravulapalem", "ramachandrapuram", "pithapuram",
    "kakinada", "kakinada rural", "peddapuram", "prathipadu", "tuni", "narsapur",
    "palakollu", "achanta", "tanuku", "bhimavaram", "tadepallegudem", "polavaram",
    "eluru", "chintalapudi", "devipatnam", "rampachodavaram", "addatigala", "dowleswaram",
    "seethanagaram", "korukonda"
}

class LiveAlertIngestionService:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "active_alerts": [],
                    "archived_alerts": [],
                    "raw_feed_metadata": {}
                }, f, indent=2)

    def fetch_live_alerts(self) -> Tuple[List[OfficialDisasterAlert], SourceHealthStatus]:
        """
        Polls authoritative feeds (NDMA SACHET and APSDMA) and normalizes active warnings.
        Deduplicates, identifies affected districts and Lower Godavari mandals, and updates state.
        """
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = SourceHealthStatus(
            source_id="NDMA_SACHET_APSDMA",
            source_name="NDMA SACHET / APSDMA Official Disaster Feed",
            category="DISASTER_ALERTS",
            status="FETCH_ERROR",
            last_attempt_iso=now_iso,
            records_count=0
        )

        try:
            req = urllib.request.Request(
                SACHET_GEOJSON_URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FloodIntelligence/2.0"}
            )
            with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=12) as response:
                status_code = response.status
                status.last_status_code = status_code
                raw_bytes = response.read()

            # Cache the raw GeoJSON for map display
            with open(GEOJSON_CACHE_FILE, "wb") as f:
                f.write(raw_bytes)

            geojson_data = json.loads(raw_bytes.decode("utf-8"))
            features = geojson_data.get("features", [])
            feed_generated = geojson_data.get("generated", now_iso)

            # Group alerted features by event / sender / district
            grouped_alerts: Dict[str, Dict[str, Any]] = {}

            for feat in features:
                props = feat.get("properties", {})
                district = props.get("district", "Andhra Pradesh")
                mandal = props.get("mandal", "")
                event = props.get("events", "Heavy Weather Advisory")
                severity = props.get("severity", "Severe")
                sender = props.get("senders", "NDMA SACHET / IMD")
                last_sent = props.get("last_sent", now_iso)
                expires = props.get("expires")

                # Composite key to aggregate mandals under the same official event
                group_key = f"{district}_{event}_{severity}_{sender}"
                if group_key not in grouped_alerts:
                    grouped_alerts[group_key] = {
                        "district": district,
                        "event": event,
                        "severity": severity,
                        "sender": sender,
                        "issued_at": last_sent,
                        "expires_at": expires,
                        "mandals": []
                    }
                if mandal and mandal not in grouped_alerts[group_key]["mandals"]:
                    grouped_alerts[group_key]["mandals"].append(mandal)

            alerts_list: List[OfficialDisasterAlert] = []

            for idx, (key, g) in enumerate(grouped_alerts.items(), 1):
                mandals = g["mandals"]
                dist = g["district"]
                event = g["event"]
                sev = g["severity"]

                # Check intersection with Lower Godavari Basin
                lg_mandals = [m for m in mandals if any(lg in m.lower() for lg in LOWER_GODAVARI_MANDALS_SET)]
                is_lg = len(lg_mandals) > 0 or dist.lower() in ("east godavari", "west godavari", "dr. b.r. ambedkar konaseema", "kakinada", "eluru")

                headline = f"Official {event} ({sev}): {dist} District"
                if len(mandals) == 1:
                    headline = f"Official {event} ({sev}): {mandals[0]}, {dist}"

                desc = (
                    f"Official public warning issued by {g['sender']} for {len(mandals)} mandals in {dist} District. "
                    f"Warning category: {event} ({sev} Severity). In force until {g['expires_at'] or 'further notice'}."
                )

                instruction = (
                    "Stay informed via local authority broadcasts. Keep livestock and essential items elevated. "
                    "Avoid entering inundated drains, canals or low causeways. Follow State Emergency Operations Centre directives."
                )

                is_expired = False
                if g.get("expires_at"):
                    try:
                        exp_clean = g["expires_at"].replace("Z", "").split("+")[0]
                        if datetime.fromisoformat(exp_clean) < datetime.now():
                            is_expired = True
                    except Exception:
                        pass
                alert_status = "EXPIRED" if is_expired else "ACTIVE"

                alert_obj = OfficialDisasterAlert(
                    alert_id=f"AP-SACHET-{datetime.now().strftime('%Y%m%d')}-{idx:03d}",
                    source=g["sender"],
                    event_type=event,
                    severity=sev,
                    state="Andhra Pradesh",
                    affected_districts=[dist],
                    affected_mandals=mandals[:25],  # Cap listed mandals for neat display
                    headline=headline,
                    description=desc,
                    instruction=instruction,
                    issued_at=g["issued_at"],
                    expires_at=g["expires_at"],
                    retrieved_at=now_iso,
                    last_updated=now_iso,
                    status=alert_status,
                    source_url="https://sachet.ndma.gov.in/",
                    in_lower_godavari=is_lg,
                    lower_godavari_mandals=lg_mandals,
                    affected_lower_godavari_mandals=lg_mandals
                )
                alerts_list.append(alert_obj)

            # Persist updated alerts
            self._save_alerts(alerts_list, feed_generated)

            status.status = "LIVE"
            status.last_status_code = 200
            status.last_success_iso = now_iso
            status.records_count = len(alerts_list)
            status.stale = False
            status.error_message = None

            logger.info(f"Ingested {len(alerts_list)} live disaster alerts covering {len(features)} mandals from NDMA SACHET.")
            return alerts_list, status

        except urllib.error.HTTPError as e:
            logger.warning(f"HTTP error fetching NDMA SACHET live alerts: {e}")
            status.status = "FETCH_ERROR"
            status.last_status_code = e.code
            status.error_message = f"HTTP {e.code}: {e.reason}"
            cached_alerts = self.get_cached_alerts()
            if cached_alerts:
                status.records_count = len(cached_alerts)
                status.stale = True
            return cached_alerts, status
        except Exception as e:
            logger.warning(f"Error fetching NDMA SACHET live alerts: {e}")
            status.status = "FETCH_ERROR"
            status.last_status_code = None
            status.error_message = str(e)
            # Load cached alerts if available
            cached_alerts = self.get_cached_alerts()
            if cached_alerts:
                status.records_count = len(cached_alerts)
                status.stale = True
            return cached_alerts, status

    def _save_alerts(self, alerts: List[OfficialDisasterAlert], feed_gen_time: str):
        with open(ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "feed_generated_at": feed_gen_time,
                "active_alerts": [a.dict() for a in alerts],
                "total_alerts": len(alerts)
            }, f, indent=2)

    def get_cached_alerts(self) -> List[OfficialDisasterAlert]:
        if not os.path.exists(ALERTS_FILE):
            return []
        try:
            with open(ALERTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            raw_alerts = data.get("active_alerts", [])
            valid_alerts: List[OfficialDisasterAlert] = []
            for raw in raw_alerts:
                try:
                    alert_obj = OfficialDisasterAlert(**raw)
                    valid_alerts.append(alert_obj)
                except Exception as val_err:
                    a_id = raw.get("alert_id", "UNKNOWN_ALERT")
                    logger.warning(f"Skipping malformed alert record [{a_id}]: {val_err}")
            return valid_alerts
        except Exception as e:
            logger.error(f"Error reading cached alerts: {e}")
            return []

    def get_alerted_mandals_geojson(self) -> Dict[str, Any]:
        """Returns the GeoJSON of all currently alerted mandals across Andhra Pradesh."""
        if os.path.exists(GEOJSON_CACHE_FILE):
            try:
                with open(GEOJSON_CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading cached sachet GeoJSON: {e}")
        return {"type": "FeatureCollection", "features": []}

    def import_manual_bulletin(self, source: str, event_type: str, severity: str,
                               districts: List[str], mandals: List[str], headline: str,
                               description: str, instruction: str, source_url: Optional[str] = None) -> OfficialDisasterAlert:
        """
        Supports official manual bulletin import with full provenance attribution
        when automated feeds are offline or for special meteorological releases.
        """
        now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lg_mandals = [m for m in mandals if any(lg in m.lower() for lg in LOWER_GODAVARI_MANDALS_SET)]

        new_alert = OfficialDisasterAlert(
            alert_id=f"AP-BULLETIN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            source=source,
            event_type=event_type,
            severity=severity,
            state="Andhra Pradesh",
            affected_districts=districts,
            affected_mandals=mandals,
            headline=headline,
            description=description,
            instruction=instruction,
            issued_at=now_iso,
            expires_at=None,
            retrieved_at=now_iso,
            last_updated=now_iso,
            status="ACTIVE",
            source_url=source_url or "https://mausam.imd.gov.in/",
            in_lower_godavari=len(lg_mandals) > 0,
            affected_lower_godavari_mandals=lg_mandals
        )

        cached = self.get_cached_alerts()
        cached.insert(0, new_alert)
        self._save_alerts(cached, now_iso)
        logger.info(f"Imported official manual bulletin: {new_alert.alert_id} ({source})")
        return new_alert
