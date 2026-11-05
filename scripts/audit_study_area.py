"""
Audit Study Area Geometries and Calculations
"""
import json
import math
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import unary_union, transform
import pyproj

WORKSPACE = Path(r"C:\major project")
MANDALS_PATH = WORKSPACE / "data" / "processed" / "boundaries" / "lower_godavari_mandals.geojson"
STUDY_AREA_PATH = WORKSPACE / "data" / "processed" / "boundaries" / "lower_godavari_study_area.geojson"
DISTRICTS_PATH = WORKSPACE / "data" / "processed" / "boundaries" / "lower_godavari_districts.geojson"

# Geodetic calculator
geod = pyproj.Geod(ellps="WGS84")

# Projections
# UTM Zone 44N (EPSG:32644) covers 78E to 84E, perfect for Andhra Pradesh (81-83E)
proj_utm44n = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32644", always_xy=True).transform
# India National Projected CRS: EPSG:7755 (India Central Zone) or EPSG:24378 (Kalianpur 1975)
proj_india_cea = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:7755", always_xy=True).transform

def get_geodesic_area(geom):
    # returns area in m^2
    area, _ = geod.geometry_area_perimeter(geom)
    return abs(area) / 1e6 # km^2

def get_projected_area(geom, proj_func):
    proj_geom = transform(proj_func, geom)
    return proj_geom.area / 1e6 # km^2

def audit_file(path, name):
    print("=" * 80)
    print(f"AUDITING: {name} ({path})")
    print("=" * 80)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    features = data.get("features", [])
    print(f"Feature count: {len(features)}")
    
    geoms = []
    total_flat_approx = 0.0
    total_geodesic = 0.0
    total_utm = 0.0
    total_cea = 0.0
    
    print(f"{'#':2s} | {'Name':22s} | {'Deg^2 Area':10s} | {'Flat Approx':12s} | {'Geodesic km2':12s} | {'UTM44N km2':12s}")
    print("-" * 80)
    
    for i, feat in enumerate(features):
        props = feat.get("properties", {})
        feat_name = props.get("NAME_3") or props.get("NAME_2") or props.get("MANDAL_NAME") or props.get("name") or f"Feature_{i+1}"
        g = shape(feat["geometry"])
        geoms.append(g)
        
        deg2 = g.area
        # Flat approx used in service: g.area * (111.0 ** 2) * cos(rad(16.9))
        flat = deg2 * (111.0 ** 2) * math.cos(math.radians(16.9))
        geo = get_geodesic_area(g)
        utm = get_projected_area(g, proj_utm44n)
        
        total_flat_approx += flat
        total_geodesic += geo
        total_utm += utm
        
        print(f"{i+1:2d} | {feat_name:22s} | {deg2:10.6f} | {flat:10.2f} km2 | {geo:10.2f} km2 | {utm:10.2f} km2")
    
    union_geom = unary_union(geoms)
    union_deg2 = union_geom.area
    union_flat = union_deg2 * (111.0 ** 2) * math.cos(math.radians(16.9))
    union_geo = get_geodesic_area(union_geom)
    union_utm = get_projected_area(union_geom, proj_utm44n)
    
    print("-" * 80)
    print(f"SUM OF INDIVIDUAL MANDALS:")
    print(f"  Flat Approx:  {total_flat_approx:10.2f} km2")
    print(f"  Geodesic:     {total_geodesic:10.2f} km2")
    print(f"  UTM 44N:      {total_utm:10.2f} km2")
    print(f"UNION GEOMETRY:")
    print(f"  Deg^2:        {union_deg2:10.6f} deg^2")
    print(f"  Flat Approx:  {union_flat:10.2f} km2")
    print(f"  Geodesic:     {union_geo:10.2f} km2")
    print(f"  UTM 44N:      {union_utm:10.2f} km2")
    print(f"Overlap difference (Sum - Union): {total_geodesic - union_geo:.4f} km2")
    print()

if __name__ == "__main__":
    audit_file(MANDALS_PATH, "21 Mandals Boundary")
    if STUDY_AREA_PATH.exists():
        audit_file(STUDY_AREA_PATH, "Study Area Boundary")
    if DISTRICTS_PATH.exists():
        audit_file(DISTRICTS_PATH, "Districts Boundary")
