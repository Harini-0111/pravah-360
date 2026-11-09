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
from datetime import datetime, timezone, timedelta
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


# Documented Regional Timezone Assumption:
# Upstream regional government feeds in Andhra Pradesh (APSDMA, CWC regional gauges, local emergency operations)
# frequently emit naive local timestamps without UTC offset notation (e.g., '2026-11-09 16:30:00').
# In accordance with project spatial scope (Lower Godavari Basin, India), any naive timestamp is assumed
# to be in Indian Standard Time (IST = UTC+05:30) and converted to a timezone-aware UTC datetime.
IST_TIMEZONE = timezone(timedelta(hours=5, minutes=30))

def parse_iso_timestamp(ts: Any, default_tz: timezone = IST_TIMEZONE) -> Optional[datetime]:
    """
    Parses ISO-8601 and operational timestamp formats into a timezone-aware UTC datetime.

    Supports:
    - ISO-8601 strings ending with 'Z' (e.g. '2026-11-09T16:30:00Z') -> UTC.
    - Offsets with positive and negative notation (e.g. '+05:30', '-04:00', '+00:00').
    - Naive timestamps (e.g. '2026-11-09 16:30:00' or '2026-11-09T16:30:00') -> interpreted as default_tz (IST), then converted to UTC.
    - datetime objects (aware or naive).

    Safety:
    - Never uses string-splitting to strip offsets or 'Z'.
    - Returns None on missing (None/empty) or unparseable input without raising exceptions.
    """
    if ts is None:
        return None
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=default_tz).astimezone(timezone.utc)
        return ts.astimezone(timezone.utc)

    ts_str = str(ts).strip()
    if not ts_str:
        return None

    if ts_str.endswith("Z") or ts_str.endswith("z"):
        ts_str = ts_str[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=default_tz)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d-%m-%Y %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            dt = datetime.strptime(ts_str, fmt)
            dt = dt.replace(tzinfo=default_tz)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue

    return None

def evaluate_alert_freshness(
    alert: Any,
    is_feed_down: bool = False,
    is_source_stale: bool = False,
    feed_timestamp: Optional[str] = None
) -> str:
    """
    Evaluates the temporal state of an alert into one of 6 distinct states:
    - EXPIRED: When alert.expires_at (or expires_time) is in the past, or status == 'EXPIRED'.
    - STALE: When alert is explicitly flagged stale, or retrieval/issue timestamp age > 1800s (30m).
    - CACHED: When alert is from confirmed cache storage (is_cached=True), within freshness threshold (age <= 1800s), and not expired.
    - LIVE: When alert was confirmed actively retrieved from live stream (is_cached=False), within freshness threshold (age <= 1800s), and not expired.
    - UNKNOWN: When temporal metadata is missing, unavailable, or invalid.
    - UNAVAILABLE: When no alert object is present or feed is completely down with no usable data.
    """
    if alert is None:
        return "UNAVAILABLE"

    now_utc = datetime.now(timezone.utc)

    # 1. Check expiration (authoritative status or explicit expiration timestamp)
    if str(getattr(alert, "status", "")).upper() == "EXPIRED":
        return "EXPIRED"

    exp_raw = getattr(alert, "expires_at", None) or getattr(alert, "expires_time", None)
    if exp_raw:
        exp_dt = parse_iso_timestamp(exp_raw)
        if exp_dt is not None and exp_dt < now_utc:
            return "EXPIRED"

    # 2. Check explicit staleness flag on the alert itself
    if getattr(alert, "is_stale", False) is True:
        return "STALE"

    # 3. Check temporal metadata
    ret_raw = getattr(alert, "retrieved_at", None)
    feed_raw = feed_timestamp
    iss_raw = getattr(alert, "issued_at", None) or getattr(alert, "sent_time", None)

    target_dt = parse_iso_timestamp(ret_raw) or parse_iso_timestamp(feed_raw) or parse_iso_timestamp(iss_raw)

    if target_dt is None:
        return "UNKNOWN"

    age_seconds = (now_utc - target_dt).total_seconds()

    if age_seconds > 1800:
        return "STALE"

    if is_source_stale and (ret_raw is None or age_seconds > 1800):
        return "STALE"

    # 4. Check CACHED vs LIVE
    is_cached = getattr(alert, "is_cached", False)
    if is_cached:
        return "CACHED"

    if is_feed_down:
        return "CACHED"

    return "LIVE"

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
                    exp_dt = parse_iso_timestamp(g["expires_at"])
                    if exp_dt is not None and exp_dt < datetime.now(timezone.utc):
                        is_expired = True
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


    def get_cached_or_live_alerts(self) -> Tuple[List[OfficialDisasterAlert], SourceHealthStatus]:
        """
        Returns cached alerts if available, otherwise attempts a live fetch.
        Computes accurate temporal freshness states (LIVE, CACHED, STALE, EXPIRED, UNKNOWN, UNAVAILABLE).
        """
        cached = self.get_cached_alerts()
        if cached:
            now_utc = datetime.now(timezone.utc)
            is_stale = False
            last_success = None
            last_up = None
            try:
                if os.path.exists(ALERTS_FILE):
                    with open(ALERTS_FILE, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    last_up = meta.get("last_updated") or meta.get("feed_generated_at")
                    if last_up:
                        last_dt = parse_iso_timestamp(last_up)
                        if last_dt:
                            last_success = last_dt.strftime("%Y-%m-%d %H:%M:%S")
                            if (now_utc - last_dt).total_seconds() > 1800:
                                is_stale = True
            except Exception:
                is_stale = True

            health = SourceHealthStatus(
                source_id="NDMA_SACHET_APSDMA",
                source_name="NDMA SACHET / APSDMA State Disaster Monitoring",
                status="AVAILABLE" if not is_stale else "STALE",
                last_attempt_iso=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                last_success_iso=last_success or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                records_count=len(cached),
                stale=is_stale
            )
            # Update freshness state on individual alerts from cache
            for a in cached:
                a.is_cached = True
                a.freshness_state = evaluate_alert_freshness(
                    a,
                    is_feed_down=False,
                    is_source_stale=is_stale,
                    feed_timestamp=last_up
                )
            return cached, health

        # No cache exists - attempt live fetch
        alerts, status = self.fetch_live_alerts()
        if not alerts:
            # When upstream feed fails and no cached data exists -> status is UNAVAILABLE
            status.status = "UNAVAILABLE"
            status.stale = False
            return [], status

        for a in alerts:
            a.is_cached = False
            a.freshness_state = evaluate_alert_freshness(a, is_feed_down=False, is_source_stale=False)
        return alerts, status

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
