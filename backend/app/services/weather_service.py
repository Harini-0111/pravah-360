"""
Weather Service & Location Intelligence.
=========================================
Integrates Google Maps Platform Weather API:
- Current conditions: https://weather.googleapis.com/v1/currentConditions:lookup
- Hourly forecast:    https://weather.googleapis.com/v1/forecast/hours:lookup
- Daily forecast:     https://weather.googleapis.com/v1/forecast/days:lookup
- Public alerts:      https://weather.googleapis.com/v1/publicAlerts:lookup

Features:
1. Secure backend proxy (API key never exposed to browser).
2. TTL caching to conserve quota and minimize billing charges.
3. Graceful handling of unconfigured or quota-exceeded API states.
4. Clean integration with GeographicIdentificationService for supported location resolution.
5. Strict distinction between Lower Godavari exploratory susceptibility model area and general weather locations.
6. Public alerts authority tracking and negative evidence reporting.
"""

import os
import json
import time
import math
import logging
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from backend.app.services.geographic_identification_service import GeographicIdentificationService, normalize_name

logger = logging.getLogger(__name__)

# Cache TTL constants (seconds)
CACHE_TTL_CURRENT = 900    # 15 minutes
CACHE_TTL_HOURLY = 3600    # 1 hour
CACHE_TTL_DAILY = 3600     # 1 hour
CACHE_TTL_ALERTS = 900     # 15 minutes

# Major regional hubs for fallback location search
PREDEFINED_HUBS = [
    {"name": "Dowleswaram", "mandal": "Rajahmundry", "district": "East Godavari", "state": "Andhra Pradesh", "country": "India", "lat": 16.9420, "lon": 81.7760, "admin_level": "Barrage / Station"},
    {"name": "Rajahmundry", "mandal": "Rajahmundry", "district": "East Godavari", "state": "Andhra Pradesh", "country": "India", "lat": 16.9850, "lon": 81.7800, "admin_level": "City / Mandal"},
    {"name": "Kakinada", "mandal": "Kakinada", "district": "Kakinada", "state": "Andhra Pradesh", "country": "India", "lat": 16.9890, "lon": 82.2475, "admin_level": "District Capital"},
    {"name": "Amalapuram", "mandal": "Amalapuram", "district": "Dr. B.R. Ambedkar Konaseema", "state": "Andhra Pradesh", "country": "India", "lat": 16.5780, "lon": 82.0050, "admin_level": "Town / Mandal"},
    {"name": "Bhimavaram", "mandal": "Bhimavaram", "district": "West Godavari", "state": "Andhra Pradesh", "country": "India", "lat": 16.5440, "lon": 81.5230, "admin_level": "Town / Mandal"},
    {"name": "Eluru", "mandal": "Eluru", "district": "Eluru", "state": "Andhra Pradesh", "country": "India", "lat": 16.7107, "lon": 81.0952, "admin_level": "District Capital"},
    {"name": "Narsapur", "mandal": "Narsapur", "district": "West Godavari", "state": "Andhra Pradesh", "country": "India", "lat": 16.4350, "lon": 81.6900, "admin_level": "Town / Mandal"},
    {"name": "Polavaram", "mandal": "Polavaram", "district": "Eluru", "state": "Andhra Pradesh", "country": "India", "lat": 17.2550, "lon": 81.6520, "admin_level": "Project / Mandal"},
    {"name": "Vijayawada", "mandal": "Vijayawada", "district": "NTR", "state": "Andhra Pradesh", "country": "India", "lat": 16.5062, "lon": 80.6480, "admin_level": "Major City"},
    {"name": "Visakhapatnam", "mandal": "Visakhapatnam", "district": "Visakhapatnam", "state": "Andhra Pradesh", "country": "India", "lat": 17.6868, "lon": 83.2185, "admin_level": "Major City"},
    {"name": "Hyderabad", "mandal": "Hyderabad", "district": "Hyderabad", "state": "Telangana", "country": "India", "lat": 17.3850, "lon": 78.4867, "admin_level": "State Capital"},
    {"name": "Bengaluru", "mandal": "Bengaluru", "district": "Bengaluru Urban", "state": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946, "admin_level": "State Capital"},
    {"name": "Chennai", "mandal": "Chennai", "district": "Chennai", "state": "Tamil Nadu", "country": "India", "lat": 13.0827, "lon": 80.2707, "admin_level": "State Capital"},
    {"name": "New Delhi", "mandal": "New Delhi", "district": "New Delhi", "state": "Delhi", "country": "India", "lat": 28.6139, "lon": 77.2090, "admin_level": "National Capital"}
]

class WeatherService:
    def __init__(self, geo_service: Optional[GeographicIdentificationService] = None):
        self.api_key = os.getenv("GOOGLE_WEATHER_API_KEY", "").strip()
        self.geo_service = geo_service or GeographicIdentificationService()
        self._cache: Dict[str, Tuple[Any, float]] = {}

    def _get_from_cache(self, key: str, ttl: float) -> Optional[Any]:
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < ttl:
                return data
            else:
                del self._cache[key]
        return None

    def _set_in_cache(self, key: str, data: Any):
        self._cache[key] = (data, time.time())

    def _make_request(self, url: str, params: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Makes an HTTP GET request to Google Maps Platform Weather API without leaking API key in logs."""
        if not self.api_key:
            return False, None, "API_KEY_NOT_CONFIGURED"

        query_params = {**params, "key": self.api_key}
        full_url = f"{url}?{urllib.parse.urlencode(query_params)}"

        try:
            req = urllib.request.Request(full_url, headers={"User-Agent": "FloodIntelligence/2.0"})
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return True, data, None
        except urllib.error.HTTPError as e:
            # Mask API key in error message
            msg = f"HTTP Error {e.code}: {e.reason}"
            logger.warning(f"Google Weather API request failed: {msg}")
            return False, None, msg
        except urllib.error.URLError as e:
            msg = f"Network Error: {e.reason}"
            logger.warning(f"Google Weather API network error: {msg}")
            return False, None, msg
        except Exception as e:
            logger.warning(f"Unexpected error in weather request: {type(e).__name__}")
            return False, None, str(e)

    def get_current_conditions(self, lat: float, lon: float) -> Dict[str, Any]:
        cache_key = f"current_{round(lat, 4)}_{round(lon, 4)}"
        cached = self._get_from_cache(cache_key, CACHE_TTL_CURRENT)
        if cached is not None:
            return {**cached, "cached": True}

        url = "https://weather.googleapis.com/v1/currentConditions:lookup"
        params = {
            "location.latitude": round(lat, 4),
            "location.longitude": round(lon, 4),
            "unitsSystem": "METRIC"
        }
        success, data, err = self._make_request(url, params)
        if not success:
            return {"is_available": False, "status": err, "data": None}

        # Normalize Google API format
        current = self._normalize_current_conditions(data)
        res = {"is_available": True, "status": "OK", "data": current, "cached": False}
        self._set_in_cache(cache_key, res)
        return res

    def get_hourly_forecast(self, lat: float, lon: float, hours: int = 24) -> Dict[str, Any]:
        cache_key = f"hourly_{round(lat, 4)}_{round(lon, 4)}_{hours}"
        cached = self._get_from_cache(cache_key, CACHE_TTL_HOURLY)
        if cached is not None:
            return {**cached, "cached": True}

        url = "https://weather.googleapis.com/v1/forecast/hours:lookup"
        params = {
            "location.latitude": round(lat, 4),
            "location.longitude": round(lon, 4),
            "hours": min(hours, 48),
            "unitsSystem": "METRIC"
        }
        success, data, err = self._make_request(url, params)
        if not success:
            return {"is_available": False, "status": err, "forecast": []}

        hourly = self._normalize_hourly_forecast(data)
        res = {"is_available": True, "status": "OK", "forecast": hourly, "cached": False}
        self._set_in_cache(cache_key, res)
        return res

    def get_daily_forecast(self, lat: float, lon: float, days: int = 10) -> Dict[str, Any]:
        cache_key = f"daily_{round(lat, 4)}_{round(lon, 4)}_{days}"
        cached = self._get_from_cache(cache_key, CACHE_TTL_DAILY)
        if cached is not None:
            return {**cached, "cached": True}

        url = "https://weather.googleapis.com/v1/forecast/days:lookup"
        params = {
            "location.latitude": round(lat, 4),
            "location.longitude": round(lon, 4),
            "days": min(days, 10),
            "unitsSystem": "METRIC"
        }
        success, data, err = self._make_request(url, params)
        if not success:
            return {"is_available": False, "status": err, "forecast": []}

        daily = self._normalize_daily_forecast(data)
        res = {"is_available": True, "status": "OK", "forecast": daily, "cached": False}
        self._set_in_cache(cache_key, res)
        return res

    def get_public_alerts(self, lat: float, lon: float) -> Dict[str, Any]:
        cache_key = f"alerts_{round(lat, 4)}_{round(lon, 4)}"
        cached = self._get_from_cache(cache_key, CACHE_TTL_ALERTS)
        if cached is not None:
            return {**cached, "cached": True}

        url = "https://weather.googleapis.com/v1/publicAlerts:lookup"
        params = {
            "location.latitude": round(lat, 4),
            "location.longitude": round(lon, 4)
        }
        success, data, err = self._make_request(url, params)
        if not success:
            return {"is_available": False, "status": err, "alerts": []}

        alerts = self._normalize_public_alerts(data)
        res = {"is_available": True, "status": "OK", "alerts": alerts, "cached": False}
        self._set_in_cache(cache_key, res)
        return res

    def get_unified_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Combines current conditions, hourly outlook, daily forecast, alerts, and geographic identity in one call."""
        geo_info = self.geo_service.identify_point(lat, lon)
        within_study = geo_info.get("within_study_area", False)

        flood_model_note = (
            "Exploratory flood susceptibility model configured for Lower Godavari Basin (Copernicus DSM, HydroSHEDS, ESA WorldCover, WorldPop). Demonstrates intrinsic terrain susceptibility, not confirmed flood predictions."
            if within_study else
            "Geospatial flood susceptibility model is configured exclusively for the 21 Lower Godavari mandals. Showing atmospheric weather observations only."
        )

        curr_res = self.get_current_conditions(lat, lon)
        hourly_res = self.get_hourly_forecast(lat, lon, hours=24)
        daily_res = self.get_daily_forecast(lat, lon, days=10)
        alerts_res = self.get_public_alerts(lat, lon)

        # Check API status
        if not self.api_key:
            api_status = "API_KEY_NOT_CONFIGURED"
            msg = "Google Maps Platform Weather API key is not configured. Add GOOGLE_WEATHER_API_KEY to .env to enable live weather streaming."
            is_avail = False
            # Return structured unavailable state with clear notes
            return {
                "is_available": is_avail,
                "api_status": api_status,
                "message": msg,
                "location": geo_info,
                "flood_model_supported": within_study,
                "flood_model_note": flood_model_note,
                "current": None,
                "hourly_forecast": [],
                "daily_forecast": [],
                "alerts": [],
                "alerts_status": "API_KEY_NOT_CONFIGURED",
                "alerts_source_info": "Live alert integration is inactive until GOOGLE_WEATHER_API_KEY is configured in .env. When enabled, official weather and flood bulletins in India are published by IMD and CWC via Google Public Alerts.",
                "cached": False,
                "cache_expiry_utc": None
            }

        is_avail = curr_res.get("is_available", False)
        api_status = curr_res.get("status", "OK" if is_avail else "API_ERROR")

        raw_alerts = alerts_res.get("alerts", [])
        if not alerts_res.get("is_available", False):
            alerts_status = "API_ERROR"
            alerts_info = f"Public alerts query failed: {alerts_res.get('status', 'API_ERROR')}."
        elif len(raw_alerts) > 0:
            alerts_status = "ACTIVE_OFFICIAL_ALERTS"
            sources = sorted(list(set(a.get("source_agency", "Official Service") for a in raw_alerts)))
            alerts_info = f"Active official emergency bulletins reported by: {', '.join(sources)}."
        else:
            alerts_status = "NO_ACTIVE_ALERTS_REPORTED"
            alerts_info = "No active severe weather or flood warnings returned by Google Public Alerts for this coordinate. This indicates no active alerts are currently published in the provider feed, but does not guarantee an absolute absence of localized weather hazards."

        return {
            "is_available": is_avail,
            "api_status": api_status,
            "message": None if is_avail else f"Weather API error: {api_status}",
            "location": geo_info,
            "flood_model_supported": within_study,
            "flood_model_note": flood_model_note,
            "current": curr_res.get("data"),
            "hourly_forecast": hourly_res.get("forecast", []),
            "daily_forecast": daily_res.get("forecast", []),
            "alerts": raw_alerts,
            "alerts_status": alerts_status,
            "alerts_source_info": alerts_info,
            "cached": curr_res.get("cached", False),
            "cache_expiry_utc": (datetime.now(timezone.utc) + timedelta(seconds=CACHE_TTL_CURRENT)).isoformat()
        }

    def search_locations(self, query: str) -> List[Dict[str, Any]]:
        """
        Reusable location search supporting:
        1. Coordinate strings (e.g. "16.942, 81.776" or "16.942 81.776")
        2. Mandal names from Lower Godavari Basin (GADM 21 mandals)
        3. District names from Andhra Pradesh
        4. Predefined regional hubs and major Indian cities
        """
        q = query.strip().lower()
        if not q:
            return []

        results = []

        # 1. Coordinate string parsing
        coord_match = self._parse_coordinate_query(q)
        if coord_match:
            c_lat, c_lon = coord_match
            geo_info = self.geo_service.identify_point(c_lat, c_lon)
            results.append({
                "name": f"Coordinates ({c_lat:.4f}, {c_lon:.4f})",
                "formatted_name": geo_info.get("formatted_location"),
                "latitude": c_lat,
                "longitude": c_lon,
                "admin_level": "Coordinate Point",
                "district": geo_info.get("district"),
                "mandal": geo_info.get("mandal"),
                "state": geo_info.get("state") or "Andhra Pradesh",
                "country": geo_info.get("country") or "India",
                "within_study_area": geo_info.get("within_study_area", False)
            })
            return results

        # 2. Check 21 mandals in Lower Godavari
        for m_dict in self.geo_service.mandals:
            props = m_dict["properties"]
            m_name = props.get("NAME_3", "")
            d_name = props.get("NAME_2", "")
            norm_m = normalize_name(m_name) or ""
            norm_d = normalize_name(d_name) or ""
            if (q in m_name.lower() or q in d_name.lower() or
                q in norm_m.lower() or q in norm_d.lower()):
                # Compute centroid
                centroid = m_dict["geometry"].centroid
                disp_m = norm_m or m_name
                disp_d = norm_d or d_name
                results.append({
                    "name": f"{disp_m} Mandal",
                    "formatted_name": f"{disp_m} Mandal, {disp_d}, Andhra Pradesh",
                    "latitude": round(centroid.y, 4),
                    "longitude": round(centroid.x, 4),
                    "admin_level": "Mandal (Study Area)",
                    "district": disp_d,
                    "mandal": disp_m,
                    "state": "Andhra Pradesh",
                    "country": "India",
                    "within_study_area": True
                })

        # 3. Check Predefined Hubs
        for hub in PREDEFINED_HUBS:
            if (q in hub["name"].lower() or 
                q in hub["mandal"].lower() or 
                q in hub["district"].lower() or 
                q in hub["state"].lower()):
                # Avoid duplicates
                if not any(r["name"] == hub["name"] or r["name"] == f"{hub['name']} Mandal" for r in results):
                    within_study = (81.0 <= hub["lon"] <= 82.8 and 16.3 <= hub["lat"] <= 17.9)
                    results.append({
                        "name": hub["name"],
                        "formatted_name": f"{hub['name']}, {hub['district']}, {hub['state']}",
                        "latitude": hub["lat"],
                        "longitude": hub["lon"],
                        "admin_level": hub["admin_level"],
                        "district": hub["district"],
                        "mandal": hub["mandal"],
                        "state": hub["state"],
                        "country": hub["country"],
                        "within_study_area": within_study
                    })

        return results[:10]

    def _parse_coordinate_query(self, query: str) -> Optional[Tuple[float, float]]:
        cleaned = query.replace(",", " ").replace(";", " ")
        parts = cleaned.split()
        if len(parts) == 2:
            try:
                lat = float(parts[0])
                lon = float(parts[1])
                if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                    return lat, lon
            except ValueError:
                pass
        return None

    # Normalization helpers for Google Maps Weather API
    def _normalize_current_conditions(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        cond = raw.get("currentConditions", raw)
        temp = cond.get("temperature", {})
        temp_c = temp.get("degrees") if isinstance(temp, dict) else temp

        feels = cond.get("feelsLikeTemperature", {})
        feels_c = feels.get("degrees") if isinstance(feels, dict) else feels

        wind = cond.get("wind", {})
        w_speed = wind.get("speed", {}).get("value") if isinstance(wind.get("speed"), dict) else None
        w_dir_deg = wind.get("direction", {}).get("degrees") if isinstance(wind.get("direction"), dict) else None
        w_cardinal = wind.get("direction", {}).get("cardinal") if isinstance(wind.get("direction"), dict) else None

        precip = cond.get("precipitation", {})
        p_qpf = precip.get("qpf", {}).get("quantity") if isinstance(precip.get("qpf"), dict) else None
        p_prob = precip.get("probability", {}).get("percent") if isinstance(precip.get("probability"), dict) else None

        desc = cond.get("weatherCondition", {}).get("description", {}).get("text", "Clear")
        icon_uri = cond.get("weatherCondition", {}).get("icon", {}).get("uri")

        # Local time in IST (UTC+5:30)
        now_utc = datetime.now(timezone.utc)
        ist_time = now_utc + timedelta(hours=5, minutes=30)
        local_str = ist_time.strftime("%d %b %Y, %I:%M %p IST")

        return {
            "temperature_c": round(float(temp_c), 1) if temp_c is not None else None,
            "feels_like_c": round(float(feels_c), 1) if feels_c is not None else None,
            "relative_humidity_pct": cond.get("relativeHumidity"),
            "wind_speed_kmh": round(float(w_speed), 1) if w_speed is not None else None,
            "wind_direction_deg": w_dir_deg,
            "wind_direction_cardinal": w_cardinal,
            "precipitation_mm": float(p_qpf) if p_qpf is not None else 0.0,
            "precipitation_probability_pct": p_prob or 0,
            "condition": {
                "description": desc,
                "icon_uri": icon_uri,
                "icon_code": cond.get("weatherCondition", {}).get("type")
            },
            "update_time_utc": now_utc.isoformat(),
            "update_time_local": local_str
        }

    def _normalize_hourly_forecast(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        hours_list = raw.get("forecastHours", [])
        normalized = []
        for h in hours_list[:24]:
            t_obj = h.get("temperature", {})
            temp_c = t_obj.get("degrees") if isinstance(t_obj, dict) else t_obj
            feels_obj = h.get("feelsLikeTemperature", {})
            feels_c = feels_obj.get("degrees") if isinstance(feels_obj, dict) else feels_obj

            p_obj = h.get("precipitation", {})
            p_qpf = p_obj.get("qpf", {}).get("quantity") if isinstance(p_obj.get("qpf"), dict) else 0.0
            p_prob = p_obj.get("probability", {}).get("percent") if isinstance(p_obj.get("probability"), dict) else 0

            desc = h.get("weatherCondition", {}).get("description", {}).get("text", "Fair")
            icon_uri = h.get("weatherCondition", {}).get("icon", {}).get("uri")

            start_t = h.get("interval", {}).get("startTime", "")
            # Convert to local IST hour display
            try:
                dt = datetime.fromisoformat(start_t.replace("Z", "+00:00"))
                ist_dt = dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
                hour_label = ist_dt.strftime("%I %p")
            except Exception:
                hour_label = start_t[:16]

            normalized.append({
                "time_utc": start_t,
                "time_local": hour_label,
                "temperature_c": round(float(temp_c), 1) if temp_c is not None else 0.0,
                "feels_like_c": round(float(feels_c), 1) if feels_c is not None else None,
                "precipitation_probability_pct": int(p_prob) if p_prob is not None else 0,
                "precipitation_mm": round(float(p_qpf), 1) if p_qpf is not None else 0.0,
                "condition": {
                    "description": desc,
                    "icon_uri": icon_uri,
                    "icon_code": h.get("weatherCondition", {}).get("type")
                }
            })
        return normalized

    def _normalize_daily_forecast(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        days_list = raw.get("forecastDays", [])
        normalized = []
        for d in days_list[:10]:
            max_t = d.get("maxTemperature", {}).get("degrees") if isinstance(d.get("maxTemperature"), dict) else 0.0
            min_t = d.get("minTemperature", {}).get("degrees") if isinstance(d.get("minTemperature"), dict) else 0.0

            daytime = d.get("daytimeForecast", {})
            p_obj = daytime.get("precipitation", {})
            p_qpf = p_obj.get("qpf", {}).get("quantity") if isinstance(p_obj.get("qpf"), dict) else 0.0
            p_prob = p_obj.get("probability", {}).get("percent") if isinstance(p_obj.get("probability"), dict) else 0

            desc = daytime.get("weatherCondition", {}).get("description", {}).get("text", "Fair")
            icon_uri = daytime.get("weatherCondition", {}).get("icon", {}).get("uri")

            start_t = d.get("interval", {}).get("startTime", "")
            try:
                dt = datetime.fromisoformat(start_t.replace("Z", "+00:00"))
                date_label = dt.strftime("%a, %d %b")
            except Exception:
                date_label = start_t[:10]

            normalized.append({
                "date": date_label,
                "max_temperature_c": round(float(max_t), 1) if max_t is not None else 0.0,
                "min_temperature_c": round(float(min_t), 1) if min_t is not None else 0.0,
                "precipitation_probability_pct": int(p_prob) if p_prob is not None else 0,
                "precipitation_mm": round(float(p_qpf), 1) if p_qpf is not None else 0.0,
                "condition": {
                    "description": desc,
                    "icon_uri": icon_uri,
                    "icon_code": daytime.get("weatherCondition", {}).get("type")
                }
            })
        return normalized

    def _normalize_public_alerts(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts_list = raw.get("publicAlerts", [])
        normalized = []
        for a in alerts_list:
            normalized.append({
                "id": a.get("id", f"ALT-{len(normalized)+1}"),
                "headline": a.get("headline", "Weather Advisory"),
                "severity": a.get("severity", "MODERATE"),
                "urgency": a.get("urgency", "FUTURE"),
                "certainty": a.get("certainty"),
                "event": a.get("event", "Precipitation Event"),
                "description": a.get("description", ""),
                "effective_time": a.get("effectiveTime", ""),
                "expire_time": a.get("expireTime", ""),
                "source_agency": a.get("source", "Official Meteorological Service")
            })
        return normalized
