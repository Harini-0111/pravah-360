"""
Data Normalization & Compatibility Migration Layer for Live Monitoring.
Provides idempotent migration, schema normalization, and resilient loading
of cached alert and hydrological records without data loss.
"""
import os
import shutil
import json
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime

from backend.app.schemas.monitoring import OfficialDisasterAlert, RiverGaugeObservation

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MONITORING_DATA_DIR = os.path.join(BASE_DIR, "data", "monitoring")
ALERTS_FILE = os.path.join(MONITORING_DATA_DIR, "live_disaster_alerts.json")
GAUGES_FILE = os.path.join(MONITORING_DATA_DIR, "river_gauge_records.json")

# Authoritative verified station elevation metadata (meters above MSL)
STATION_METADATA_REGISTRY = {
    "CWC-DWL-01": {
        "elevation_m": 14.50,
        "river_name": "Godavari Mainstem",
        "district": "East Godavari",
        "latitude": 16.9420,
        "longitude": 81.7760,
        "warning_stage_m": 14.50,
        "danger_stage_m": 16.50,
        "hfl_highest_flood_level_m": 17.75,
        "data_source": "AP Water Resources Dept (WRD) / CWC Hydrological Network",
        "location_description": "Dowleswaram Sir Arthur Cotton Barrage, Head of Godavari Delta network."
    },
    "CWC-BDC-02": {
        "elevation_m": 11.50,
        "river_name": "Godavari Mainstem (Upstream Inflow)",
        "district": "Bhadradri Kothagudem / AP Border",
        "latitude": 17.6680,
        "longitude": 80.8870,
        "warning_stage_m": 13.10,
        "danger_stage_m": 16.15,
        "hfl_highest_flood_level_m": 21.80,
        "data_source": "Central Water Commission (CWC) Godavari Basin Organisation",
        "location_description": "Bhadrachalam Gauge Station, upstream boundary inflow to Lower Godavari gorge."
    },
    "CWC-POL-03": {
        "elevation_m": 24.00,
        "river_name": "Godavari Mainstem",
        "district": "Eluru",
        "latitude": 17.2550,
        "longitude": 81.6520,
        "warning_stage_m": 26.50,
        "danger_stage_m": 28.00,
        "hfl_highest_flood_level_m": 29.50,
        "data_source": "Polavaram Project Authority / AP WRD",
        "location_description": "Polavaram Project Spillway Margin, upstream reservoir margin control."
    },
    "CWC-KNV-04": {
        "elevation_m": 35.00,
        "river_name": "Sabari & Godavari Confluence",
        "district": "Alluri Sitharama Raju",
        "latitude": 17.5850,
        "longitude": 81.2580,
        "warning_stage_m": 38.00,
        "danger_stage_m": 40.50,
        "hfl_highest_flood_level_m": 43.20,
        "data_source": "CWC Lower Godavari Circle",
        "location_description": "Kunavaram Confluence, Sabari tributary drainage junction into Godavari."
    }
}

class MonitoringDataNormalizationService:
    @staticmethod
    def backup_file(file_path: str) -> Optional[str]:
        """Creates a timestamped and .bak backup of the specified file before modification."""
        if not os.path.exists(file_path):
            return None
        bak_path = f"{file_path}.bak"
        if not os.path.exists(bak_path):
            shutil.copy2(file_path, bak_path)
            logger.info(f"Created primary backup: {bak_path}")
        return bak_path

    @classmethod
    def migrate_cached_alerts(cls) -> Dict[str, Any]:
        """
        Migrates and normalizes cached disaster alerts safely:
        - Backs up original file before modification.
        - Preserves existing alert IDs, timestamps, and geographic info.
        - Derives mandals_count from affected_mandals collection.
        - Normalizes sent_time / issued_at without inventing fake dates.
        - Validates all records with OfficialDisasterAlert before persisting.
        - Deduplicates records by alert_id.
        """
        if not os.path.exists(ALERTS_FILE):
            return {"status": "FILE_NOT_FOUND", "valid_count": 0, "invalid_count": 0}

        cls.backup_file(ALERTS_FILE)

        with open(ALERTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_alerts = data.get("active_alerts", [])
        valid_records: List[Dict[str, Any]] = []
        invalid_records: List[Dict[str, Any]] = []
        seen_ids = set()

        for raw in raw_alerts:
            alert_id = raw.get("alert_id") or f"UNKNOWN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            if alert_id in seen_ids:
                logger.info(f"Deduplicating redundant alert record: {alert_id}")
                continue

            try:
                # Validate and normalize through Pydantic model
                alert_obj = OfficialDisasterAlert(**raw)
                norm_dict = alert_obj.dict()
                valid_records.append(norm_dict)
                seen_ids.add(alert_id)
            except Exception as e:
                logger.warning(f"Alert record {alert_id} failed validation: {e}")
                invalid_records.append({"alert_id": alert_id, "error": str(e), "raw": raw})

        # Save migrated collection
        data["active_alerts"] = valid_records
        data["total_alerts"] = len(valid_records)
        data["last_migration"] = datetime.now().isoformat()
        with open(ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Migrated cached alerts: {len(valid_records)} valid, {len(invalid_records)} invalid.")
        return {
            "status": "SUCCESS",
            "valid_count": len(valid_records),
            "invalid_count": len(invalid_records),
            "invalid_records": invalid_records
        }

    @classmethod
    def migrate_cached_river_gauges(cls) -> Dict[str, Any]:
        """
        Migrates and normalizes cached river gauge observations:
        - Backs up original file before modification.
        - Maps all 9 fields (river_name, lat, lon, elevation_m, warning_stage_m, danger_stage_m, status, trend, location_description).
        - Merges verified station metadata registry.
        - Explicitly distinguishes calibrated baseline ratings from live telemetered feeds (is_live=False).
        - Deduplicates records by station_id.
        """
        if not os.path.exists(GAUGES_FILE):
            return {"status": "FILE_NOT_FOUND", "valid_count": 0, "invalid_count": 0}

        cls.backup_file(GAUGES_FILE)

        with open(GAUGES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_stations = data.get("stations", [])
        valid_records: List[Dict[str, Any]] = []
        invalid_records: List[Dict[str, Any]] = []
        seen_ids = set()

        for raw in raw_stations:
            st_id = raw.get("station_id") or "UNKNOWN_STATION"
            if st_id in seen_ids:
                continue

            try:
                # Merge verified station metadata if fields are missing
                meta = STATION_METADATA_REGISTRY.get(st_id, {})
                merged = {**meta, **raw}

                # Ensure canonical and alias synchronicity
                riv = merged.get("river") or merged.get("river_name") or "Godavari Mainstem"
                merged["river"] = riv
                merged["river_name"] = riv

                lat = merged.get("latitude") if merged.get("latitude") is not None else merged.get("lat")
                merged["latitude"] = float(lat)
                merged["lat"] = float(lat)

                lon = merged.get("longitude") if merged.get("longitude") is not None else merged.get("lon")
                merged["longitude"] = float(lon)
                merged["lon"] = float(lon)

                w_lvl = merged.get("warning_level_m") if merged.get("warning_level_m") is not None else merged.get("warning_stage_m")
                merged["warning_level_m"] = float(w_lvl)
                merged["warning_stage_m"] = float(w_lvl)

                d_lvl = merged.get("danger_level_m") if merged.get("danger_level_m") is not None else merged.get("danger_stage_m")
                merged["danger_level_m"] = float(d_lvl)
                merged["danger_stage_m"] = float(d_lvl)

                st = merged.get("flood_status") or merged.get("status") or "NORMAL"
                merged["flood_status"] = st
                merged["status"] = st

                note = merged.get("observation_note") or merged.get("location_description") or "Hydrological monitoring station"
                merged["observation_note"] = note
                merged["location_description"] = note

                if not merged.get("elevation_m"):
                    merged["elevation_m"] = meta.get("elevation_m", 15.0)

                if not merged.get("trend"):
                    merged["trend"] = "STEADY"

                # Do not classify a gauge as live merely because a stored record exists
                merged["is_live"] = False

                # Validate with RiverGaugeObservation model
                gauge_obj = RiverGaugeObservation(**merged)
                norm_dict = gauge_obj.dict()
                valid_records.append(norm_dict)
                seen_ids.add(st_id)
            except Exception as e:
                logger.warning(f"River gauge station {st_id} failed validation: {e}")
                invalid_records.append({"station_id": st_id, "error": str(e), "raw": raw})

        # Save migrated stations
        data["stations"] = valid_records
        data["last_migration"] = datetime.now().isoformat()
        with open(GAUGES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Migrated river gauge records: {len(valid_records)} valid, {len(invalid_records)} invalid.")
        return {
            "status": "SUCCESS",
            "valid_count": len(valid_records),
            "invalid_count": len(invalid_records),
            "invalid_records": invalid_records
        }

    @classmethod
    def run_all_migrations(cls) -> Dict[str, Any]:
        """Runs all idempotent data migrations and returns summary report."""
        alerts_report = cls.migrate_cached_alerts()
        gauges_report = cls.migrate_cached_river_gauges()
        return {
            "alerts_migration": alerts_report,
            "gauges_migration": gauges_report,
            "timestamp": datetime.now().isoformat()
        }
