"""
Geographic Identification Service.
Performs spatial point-in-polygon queries against verified GADM administrative boundaries
for Andhra Pradesh and the Lower Godavari Basin.

Converts coordinates and detected flood areas into structured, human-readable place names
without fabricating unverified village boundaries.
"""
import os
import json
import logging
from functools import lru_cache
from typing import Dict, Any, List, Optional, Tuple, Union

from shapely.geometry import Point, shape
from shapely.strtree import STRtree

logger = logging.getLogger(__name__)

# Canonical name beautification mapping
NAME_NORMALIZATIONS = {
    "AndhraPradesh": "Andhra Pradesh",
    "EastGodavari": "East Godavari",
    "WestGodavari": "West Godavari",
    "RampaChodavaram": "Rampa Chodavaram",
    "Pithapuram": "Pithapuram",
    "Peddapuram": "Peddapuram",
    "Mummidivaram": "Mummidivaram",
    "Addatigala": "Addatigala",
    "Amalapuram": "Amalapuram",
    "Bhimavaram": "Bhimavaram",
    "Chintalapudi": "Chintalapudi",
    "Eluru": "Eluru",
    "Kakinada": "Kakinada",
    "Kottapeta": "Kothapeta",
    "Kovvur": "Kovvur",
    "Narsapur": "Narsapur",
    "Polavaram": "Polavaram",
    "Prathipadu": "Prathipadu",
    "Rajahmundry": "Rajamahendravaram (Rajahmundry)",
    "Ramachandrapuram": "Ramachandrapuram",
    "Razole": "Razole",
    "Tadepallegudem": "Tadepallegudem",
    "Tanuku": "Tanuku",
    "Tuni": "Tuni"
}

def normalize_name(raw_name: Optional[str]) -> Optional[str]:
    if not raw_name or raw_name == "NA":
        return None
    return NAME_NORMALIZATIONS.get(raw_name, raw_name)

class GeographicIdentificationService:
    def __init__(self, base_dir: Optional[str] = None):
        if not base_dir:
            # Default to C:\major project
            self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        else:
            self.base_dir = os.path.abspath(base_dir)

        self.mandal_geojson_path = os.path.join(self.base_dir, "data", "processed", "boundaries", "lower_godavari_mandals.geojson")
        self.district_geojson_path = os.path.join(self.base_dir, "data", "processed", "boundaries", "andhra_pradesh_districts.geojson")

        self.mandals: List[Dict[str, Any]] = []
        self.mandal_geoms: List[Any] = []
        self.mandal_tree: Optional[STRtree] = None

        self.districts: List[Dict[str, Any]] = []
        self.district_geoms: List[Any] = []
        self.district_tree: Optional[STRtree] = None

        self._load_boundary_data()

    def _load_boundary_data(self):
        """Loads and indexes GADM mandals and districts with Shapely STRtrees."""
        if os.path.exists(self.mandal_geojson_path):
            with open(self.mandal_geojson_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for feat in data.get("features", []):
                geom = shape(feat["geometry"])
                self.mandal_geoms.append(geom)
                self.mandals.append({
                    "properties": feat.get("properties", {}),
                    "geometry": geom
                })
            if self.mandal_geoms:
                self.mandal_tree = STRtree(self.mandal_geoms)
                logger.info(f"Loaded and indexed {len(self.mandal_geoms)} mandals.")

        if os.path.exists(self.district_geojson_path):
            with open(self.district_geojson_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for feat in data.get("features", []):
                geom = shape(feat["geometry"])
                self.district_geoms.append(geom)
                self.districts.append({
                    "properties": feat.get("properties", {}),
                    "geometry": geom
                })
            if self.district_geoms:
                self.district_tree = STRtree(self.district_geoms)
                logger.info(f"Loaded and indexed {len(self.district_geoms)} districts.")

    @staticmethod
    def validate_coordinates(lat: Any, lon: Any) -> Tuple[bool, Optional[str], Optional[float], Optional[float]]:
        """Validates that latitude and longitude are valid non-null floats within global ranges."""
        if lat is None or lon is None:
            return False, "Missing coordinates", None, None
        try:
            f_lat = float(lat)
            f_lon = float(lon)
        except (ValueError, TypeError):
            return False, "Non-numeric coordinates", None, None

        import math
        if math.isnan(f_lat) or math.isnan(f_lon) or math.isinf(f_lat) or math.isinf(f_lon):
            return False, "NaN or Infinite coordinates", None, None

        if not (-90.0 <= f_lat <= 90.0):
            return False, f"Latitude {f_lat} out of range [-90, 90]", None, None
        if not (-180.0 <= f_lon <= 180.0):
            return False, f"Longitude {f_lon} out of range [-180, 180]", None, None

        return True, None, f_lat, f_lon

    def identify_point(self, lat: Any, lon: Any) -> Dict[str, Any]:
        """
        Performs spatial join against administrative boundaries.
        Returns administrative place names with village boundary limitation notice.
        """
        is_valid, err_msg, f_lat, f_lon = self.validate_coordinates(lat, lon)
        if not is_valid:
            return {
                "latitude": lat,
                "longitude": lon,
                "is_valid_coordinate": False,
                "error": err_msg,
                "country": None,
                "state": None,
                "district": None,
                "mandal": None,
                "village": None,
                "village_status": "Unavailable (Invalid coordinates)",
                "formatted_location": "Invalid Coordinates",
                "within_study_area": False,
                "precision_level": "None"
            }

        # Check in memory cache for exact round coordinates
        return self._cached_identify(round(f_lat, 6), round(f_lon, 6))

    @lru_cache(maxsize=10000)
    def _cached_identify(self, lat: float, lon: float) -> Dict[str, Any]:
        point = Point(lon, lat)

        country = "India"
        state = None
        district = None
        mandal = None
        subdistrict_code = None
        district_code = None
        within_study_area = False

        # 1. Query Mandals via R-tree index
        if self.mandal_tree and self.mandal_geoms:
            candidate_indices = self.mandal_tree.query(point)
            # Handle boundary edge cases: point within polygon or touching boundary (within 1e-5 deg ~1m)
            matched_mandal_idx = None
            for idx in candidate_indices:
                geom = self.mandal_geoms[idx]
                if geom.intersects(point) or geom.distance(point) < 1e-5:
                    matched_mandal_idx = idx
                    break

            if matched_mandal_idx is not None:
                props = self.mandals[matched_mandal_idx]["properties"]
                mandal = normalize_name(props.get("NAME_3"))
                district = normalize_name(props.get("NAME_2"))
                state = normalize_name(props.get("NAME_1"))
                subdistrict_code = props.get("GID_3")
                district_code = props.get("GID_2")
                within_study_area = True

        # 2. Fallback to District search if outside Lower Godavari mandals but inside Andhra Pradesh
        if not district and self.district_tree and self.district_geoms:
            candidate_indices = self.district_tree.query(point)
            for idx in candidate_indices:
                geom = self.district_geoms[idx]
                if geom.intersects(point) or geom.distance(point) < 1e-5:
                    props = self.districts[idx]["properties"]
                    district = normalize_name(props.get("NAME_2"))
                    state = normalize_name(props.get("NAME_1"))
                    district_code = props.get("GID_2")
                    break

        # 3. Format result
        if mandal and district:
            formatted_location = f"{mandal} Mandal, {district}, {state or 'Andhra Pradesh'}"
            precision = "Mandal"
        elif district:
            formatted_location = f"{district} District, {state or 'Andhra Pradesh'}"
            precision = "District"
        elif state:
            formatted_location = f"{state}, India"
            precision = "State"
        else:
            formatted_location = f"Outside Monitored AP Boundaries ({lat:.4f}° N, {lon:.4f}° E)"
            country = None
            precision = "None"

        return {
            "latitude": lat,
            "longitude": lon,
            "is_valid_coordinate": True,
            "country": country,
            "state": state or ("Andhra Pradesh" if within_study_area else None),
            "district": district,
            "district_code": district_code,
            "mandal": mandal,
            "subdistrict_code": subdistrict_code,
            "village": None,  # NEVER fabricate village names
            "village_status": "Cadastral village boundaries unavailable in official project datasets",
            "formatted_location": formatted_location,
            "within_study_area": within_study_area,
            "precision_level": precision
        }

    def identify_points(self, points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a batch of points.
        Accepts list of dicts with keys ('latitude', 'longitude') or ('lat', 'lon').
        Preserves all original fields and attaches geographic identification.
        """
        results = []
        for p in points:
            lat = p.get("latitude") if "latitude" in p else p.get("lat")
            lon = p.get("longitude") if "longitude" in p else p.get("lon")
            geo_info = self.identify_point(lat, lon)
            
            # Combine original item properties with enriched geographic identification
            combined = {**p, "geographic_identification": geo_info}
            # Also attach convenient top-level place names
            combined["mandal"] = geo_info["mandal"]
            combined["district"] = geo_info["district"]
            combined["state"] = geo_info["state"]
            combined["formatted_location"] = geo_info["formatted_location"]
            combined["village"] = None
            results.append(combined)
        return results

if __name__ == "__main__":
    service = GeographicIdentificationService()
    # Test sample points
    test_pts = [
        {"name": "Dowleswaram Barrage Head", "lat": 16.942, "lon": 81.776},
        {"name": "Kovvur Riverside", "lat": 17.014, "lon": 81.730},
        {"name": "Amalapuram Island Center", "lat": 16.578, "lon": 82.005},
        {"name": "Polavaram Dam Project", "lat": 17.255, "lon": 81.652},
        {"name": "Bay of Bengal Offshore", "lat": 16.100, "lon": 82.500},
        {"name": "Boundary Line Test", "lat": 17.0, "lon": 81.75},
        {"name": "Invalid Coordinate", "lat": "invalid", "lon": None}
    ]
    
    print("Testing GeographicIdentificationService:")
    for pt in test_pts:
        res = service.identify_point(pt["lat"], pt["lon"])
        print(f"\nTarget: {pt['name']} ({pt['lat']}, {pt['lon']})")
        print(f"  Location: {res['formatted_location']}")
        print(f"  District: {res['district']} | Mandal: {res['mandal']}")
        print(f"  Village Status: {res['village_status']}")
        print(f"  Precision: {res['precision_level']} | Valid: {res['is_valid_coordinate']}")
