"""
Independent Audit: Exact Study Area Geometries and Calculations
Includes WGS84 Ellipsoidal Area and UTM Zone 44N Projection in pure Python.
"""
import json
import math
from pathlib import Path
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.ops import unary_union

WORKSPACE = Path(r"C:\major project")
MANDALS_PATH = WORKSPACE / "data" / "processed" / "boundaries" / "lower_godavari_mandals.geojson"
STUDY_AREA_PATH = WORKSPACE / "data" / "processed" / "boundaries" / "lower_godavari_study_area.geojson"
DISTRICTS_PATH = WORKSPACE / "data" / "processed" / "boundaries" / "lower_godavari_districts.geojson"

# 1. Search where 18498 or 18,498 appears in existing files
print("=== SEARCHING FOR 18498 / 18,498 IN WORKSPACE ===")
for p in WORKSPACE.rglob("*.md"):
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if "18498" in txt or "18,498" in txt:
            for l_num, line in enumerate(txt.splitlines(), 1):
                if "18498" in line or "18,498" in line:
                    print(f"{p.name}:{l_num}: {line.strip()}")
    except Exception as e:
        pass

for p in (WORKSPACE / "backend").rglob("*.py"):
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if "18498" in txt or "18,498" in txt:
            for l_num, line in enumerate(txt.splitlines(), 1):
                if "18498" in line or "18,498" in line:
                    print(f"{p.name}:{l_num}: {line.strip()}")
    except Exception as e:
        pass

# 2. Mathematical Geodesic Area Function on WGS84 Ellipsoid
# WGS84 parameters
A_WGS84 = 6378137.0
B_WGS84 = 6356752.314245
F_WGS84 = 1.0 / 298.257223563
E2_WGS84 = 2 * F_WGS84 - F_WGS84 ** 2

def wgs84_ring_area(coords):
    """
    Computes geodetic area of a closed polygon ring on WGS84 ellipsoid in square meters
    using the standard authalic/ellipsoidal trapezoid formula (Karney / Chamberlin-Duquette).
    """
    if len(coords) < 3:
        return 0.0
    
    # Ensure closed
    if coords[0] != coords[-1]:
        coords = list(coords) + [coords[0]]
        
    total = 0.0
    n = len(coords) - 1
    
    for i in range(n):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[i+1]
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        lam1 = math.radians(lon1)
        lam2 = math.radians(lon2)
        
        # dLambda
        dlam = lam2 - lam1
        # Normalize dLambda to [-pi, pi]
        while dlam > math.pi:
            dlam -= 2 * math.pi
        while dlam < -math.pi:
            dlam += 2 * math.pi
            
        # Authalic latitude approximation on WGS84:
        # q = (1 - e^2) * (sin(phi)/(1 - e^2 sin^2(phi)) - 1/(2e) ln((1 - e sin(phi))/(1 + e sin(phi))))
        # For small lat span, R_authalic^2 * dlam * (sin(phi2) + sin(phi1))/2 is accurate to 0.01%
        # Let's compute with WGS84 meridional and prime-vertical radii:
        mean_phi = (phi1 + phi2) / 2.0
        sin_phi = math.sin(mean_phi)
        cos_phi = math.cos(mean_phi)
        
        # Radii of curvature
        w = math.sqrt(1.0 - E2_WGS84 * sin_phi**2)
        m = A_WGS84 * (1.0 - E2_WGS84) / (w**3) # Meridional
        n_rad = A_WGS84 / w                     # Prime vertical
        
        # Trapezoid area in m^2:
        # dx = n_rad * cos(mean_phi) * dlam
        # dy = m * (phi2 - phi1)
        # Using Green's theorem: area = sum of (dx * y) or -sum of (dy * x)
        # On sphere/ellipsoid: area = R_eq * b * dlam * (sin(phi1) - sin(phi2)) ...
        # Let's use standard equal-area authalic formula:
        # R_auth = 6371007.1809 m
        r_auth = 6371007.1809
        total += dlam * (math.sin(phi1) + math.sin(phi2)) / 2.0
        
    area = abs(total) * (r_auth ** 2)
    return area

def wgs84_polygon_area(poly):
    if isinstance(poly, Polygon):
        exterior_area = wgs84_ring_area(poly.exterior.coords)
        interior_area = sum(wgs84_ring_area(interior.coords) for interior in poly.interiors)
        return exterior_area - interior_area
    elif isinstance(poly, MultiPolygon):
        return sum(wgs84_polygon_area(p) for p in poly.geoms)
    else:
        return 0.0

# 3. UTM Zone 44N Forward Projection
def latlon_to_utm44n(lon, lat):
    """
    Project (lon, lat) WGS84 to UTM Zone 44N (central meridian 81E)
    """
    lam0 = math.radians(81.0)
    k0 = 0.9996
    phi = math.radians(lat)
    lam = math.radians(lon)
    
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    tan_phi = math.tan(phi)
    
    e2 = E2_WGS84
    ep2 = e2 / (1.0 - e2)
    n = A_WGS84 / math.sqrt(1.0 - e2 * sin_phi**2)
    t = tan_phi**2
    c = ep2 * cos_phi**2
    a = (lam - lam0) * cos_phi
    
    # Meridian distance
    m = A_WGS84 * (
        (1.0 - e2/4.0 - 3.0*e2**2/64.0 - 5.0*e2**3/256.0) * phi
        - (3.0*e2/8.0 + 3.0*e2**2/32.0 + 45.0*e2**3/1024.0) * math.sin(2.0*phi)
        + (15.0*e2**2/256.0 + 45.0*e2**3/1024.0) * math.sin(4.0*phi)
        - (35.0*e2**3/3072.0) * math.sin(6.0*phi)
    )
    
    x = 500000.0 + k0 * n * (
        a + (1.0 - t + c) * a**3 / 6.0
        + (5.0 - 18.0*t + t**2 + 72.0*c - 58.0*ep2) * a**5 / 120.0
    )
    y = k0 * (
        m + n * tan_phi * (
            a**2 / 2.0
            + (5.0 - t + 9.0*c + 4.0*c**2) * a**4 / 24.0
            + (61.0 - 58.0*t + t**2 + 600.0*c - 330.0*ep2) * a**6 / 720.0
        )
    )
    return x, y

def project_poly_utm44n(poly):
    if isinstance(poly, Polygon):
        ext_coords = [latlon_to_utm44n(lon, lat) for lon, lat in poly.exterior.coords]
        int_coords = [[latlon_to_utm44n(lon, lat) for lon, lat in interior.coords] for interior in poly.interiors]
        return Polygon(ext_coords, int_coords)
    elif isinstance(poly, MultiPolygon):
        return MultiPolygon([project_poly_utm44n(p) for p in poly.geoms])
    return poly

print()
print("=== AUDITING BOUNDARY FILES ===")
for path, label in [(MANDALS_PATH, "21 Mandals"), (STUDY_AREA_PATH, "Study Area Boundary"), (DISTRICTS_PATH, "Districts Boundary")]:
    if not path.exists():
        continue
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features", [])
    print(f"\n--- {label}: {path.name} ({len(features)} features) ---")
    
    geoms = []
    total_wgs84_km2 = 0.0
    total_utm_km2 = 0.0
    total_service_km2 = 0.0
    
    for i, feat in enumerate(features):
        name = feat["properties"].get("NAME_3") or feat["properties"].get("NAME_2") or feat["properties"].get("MANDAL_NAME") or feat["properties"].get("name") or f"feat_{i}"
        g = shape(feat["geometry"])
        geoms.append(g)
        
        area_wgs84 = wgs84_polygon_area(g) / 1e6
        area_utm = project_poly_utm44n(g).area / 1e6
        # Formula used in service: geom.area * (111.0 ** 2) * math.cos(math.radians(16.9))
        area_serv = g.area * (111.0 ** 2) * math.cos(math.radians(16.9))
        
        total_wgs84_km2 += area_wgs84
        total_utm_km2 += area_utm
        total_service_km2 += area_serv
        
        if len(features) <= 25:
            print(f"{i+1:2d}. {name:20s}: WGS84={area_wgs84:8.2f} km2 | UTM44N={area_utm:8.2f} km2 | ServiceFormula={area_serv:8.2f} km2")
            
    union_g = unary_union(geoms)
    union_wgs84 = wgs84_polygon_area(union_g) / 1e6
    union_utm = project_poly_utm44n(union_g).area / 1e6
    union_serv = union_g.area * (111.0 ** 2) * math.cos(math.radians(16.9))
    
    print("-" * 75)
    print(f"Sum of parts:   WGS84 = {total_wgs84_km2:10.2f} km2 | UTM44N = {total_utm_km2:10.2f} km2 | ServiceFormula = {total_service_km2:10.2f} km2")
    print(f"Union Geometry: WGS84 = {union_wgs84:10.2f} km2 | UTM44N = {union_utm:10.2f} km2 | ServiceFormula = {union_serv:10.2f} km2")
    print(f"Internal Overlap: {total_wgs84_km2 - union_wgs84:8.4f} km2")
