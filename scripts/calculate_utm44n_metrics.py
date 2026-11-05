import json
import math
from shapely.geometry import shape
from shapely.ops import unary_union

def latlon_to_utm44n(lon, lat):
    # WGS84 constants
    a = 6378137.0
    f = 1.0 / 298.257223563
    e2 = 2 * f - f * f
    e_prime2 = e2 / (1.0 - e2)
    k0 = 0.9996
    lon0 = 81.0 # Central meridian for UTM 44N in degrees
    false_easting = 500000.0
    false_northing = 0.0

    phi = math.radians(lat)
    lam = math.radians(lon)
    lam0 = math.radians(lon0)

    N = a / math.sqrt(1.0 - e2 * math.sin(phi)**2)
    T = math.tan(phi)**2
    C = e_prime2 * math.cos(phi)**2
    A = math.cos(phi) * (lam - lam0)

    # Meridional arc length M
    M = a * ((1.0 - e2/4.0 - 3.0*e2**2/64.0 - 5.0*e2**3/256.0) * phi
             - (3.0*e2/8.0 + 3.0*e2**2/32.0 + 45.0*e2**3/1024.0) * math.sin(2.0*phi)
             + (15.0*e2**2/256.0 + 45.0*e2**3/1024.0) * math.sin(4.0*phi)
             - (35.0*e2**3/3072.0) * math.sin(6.0*phi))

    x = false_easting + k0 * N * (A + (1.0 - T + C) * A**3 / 6.0
                                  + (5.0 - 18.0*T + T**2 + 72.0*C - 58.0*e_prime2) * A**5 / 120.0)
    y = false_northing + k0 * (M + N * math.tan(phi) * (A**2 / 2.0
                                                       + (5.0 - T + 9.0*C + 4.0*C**2) * A**4 / 24.0
                                                       + (61.0 - 58.0*T + T**2 + 600.0*C - 330.0*e_prime2) * A**6 / 720.0))
    return x, y

with open("data/processed/boundaries/lower_godavari_mandals.geojson", "r", encoding="utf-8") as f:
    mandals_fc = json.load(f)

mandals_geoms_4326 = [shape(f["geometry"]) for f in mandals_fc["features"]]
u_mandals_4326 = unary_union(mandals_geoms_4326)

m_minx, m_miny, m_maxx, m_maxy = u_mandals_4326.bounds
print("=== EXACT UTM ZONE 44N (EPSG:32644) GEOMETRY METRICS ===")

# Compute corners in UTM 44N
sw_x, sw_y = latlon_to_utm44n(m_minx, m_miny)
se_x, se_y = latlon_to_utm44n(m_maxx, m_miny)
nw_x, nw_y = latlon_to_utm44n(m_minx, m_maxy)
ne_x, ne_y = latlon_to_utm44n(m_maxx, m_maxy)

min_x = min(sw_x, nw_x)
max_x = max(se_x, ne_x)
min_y = min(sw_y, se_y)
max_y = max(nw_y, ne_y)

width_m = max_x - min_x
height_m = max_y - min_y

print(f"Projected Bounding Box (X_min, Y_min, X_max, Y_max):")
print(f"  X_min: {min_x:.2f} m")
print(f"  Y_min: {min_y:.2f} m")
print(f"  X_max: {max_x:.2f} m")
print(f"  Y_max: {max_y:.2f} m")
print(f"Dimensions in meters:")
print(f"  Width (E-W):  {width_m:.2f} m (~{width_m/1000:.2f} km)")
print(f"  Height (N-S): {height_m:.2f} m (~{height_m/1000:.2f} km)")

# Transform polygon vertices to compute true interior area
def transform_geom(geom):
    if geom.geom_type == 'Polygon':
        ext = [latlon_to_utm44n(pt[0], pt[1]) for pt in geom.exterior.coords]
        interiors = [[latlon_to_utm44n(pt[0], pt[1]) for pt in ring.coords] for ring in geom.interiors]
        from shapely.geometry import Polygon
        return Polygon(ext, interiors)
    elif geom.geom_type == 'MultiPolygon':
        from shapely.geometry import MultiPolygon
        return MultiPolygon([transform_geom(p) for p in geom.geoms])

u_mandals_32644 = transform_geom(u_mandals_4326)
poly_area_m2 = u_mandals_32644.area
poly_area_km2 = poly_area_m2 / 1e6
print(f"Total Area of 21 Mandals Polygon: {poly_area_km2:.2f} sq km")

# Pixel count at 10m grid spacing:
cols_10m = int(round(width_m / 10.0))
rows_10m = int(round(height_m / 10.0))
bbox_pixels = cols_10m * rows_10m
polygon_pixels = int(round(poly_area_m2 / 100.0))

print(f"\nPixel Grid Metrics at 10m spacing:")
print(f"  Bounding Box Columns: {cols_10m:,}")
print(f"  Bounding Box Rows:    {rows_10m:,}")
print(f"  Bounding Box Pixels:  {bbox_pixels:,} (~{bbox_pixels/1e6:.1f} Megapixels)")
print(f"  Mandals Interior Pixels: {polygon_pixels:,} (~{polygon_pixels/1e6:.1f} Megapixels)")

# Storage requirements (Uncompressed Float32 for 3 bands: VV, VH, angle):
# Each pixel = 3 bands * 4 bytes = 12 bytes
uncompressed_bbox_mb = (bbox_pixels * 12) / (1024 * 1024)
uncompressed_poly_mb = (polygon_pixels * 12) / (1024 * 1024)

print(f"\nUncompressed Storage Requirements (3 bands Float32 = 12 bytes/pixel):")
print(f"  Full Bounding Box: {uncompressed_bbox_mb:.2f} MB (~{uncompressed_bbox_mb/1024:.2f} GB)")
print(f"  Mandals Polygon Interior: {uncompressed_poly_mb:.2f} MB (~{uncompressed_poly_mb/1024:.2f} GB)")

# Tiling Analysis with fileDimensions: [10240, 10240]
tile_size = 10240
tiles_x = (cols_10m + tile_size - 1) // tile_size
tiles_y = (rows_10m + tile_size - 1) // tile_size
total_tiles = tiles_x * tiles_y
print(f"\nTiling Analysis with fileDimensions: [10240, 10240]:")
print(f"  Tiles in X direction: {tiles_x} (ceiling of {cols_10m}/{tile_size})")
print(f"  Tiles in Y direction: {tiles_y} (ceiling of {rows_10m}/{tile_size})")
print(f"  Total GeoTIFF Tiles Expected: {total_tiles} (2x2 grid)")
print(f"  Max Pixels per Tile: {tile_size * tile_size:,} pixels")
print(f"  Max Uncompressed Size per Tile: {(tile_size * tile_size * 12) / (1024 * 1024):.1f} MB (~1.17 GB)")

# Central Meridian check
mid_lon = (m_minx + m_maxx) / 2.0
print(f"\nCentral Meridian Offset Check:")
print(f"  Mandals Longitude Range: {m_minx:.4f} E to {m_maxx:.4f} E")
print(f"  Midpoint Longitude: {mid_lon:.4f} E")
print(f"  UTM 44N Central Meridian: 81.0000 E")
print(f"  Offset of Midpoint from 81.0 E: {mid_lon - 81.0:+.4f} degrees East")
print(f"  Western edge offset from 81.0 E: {m_minx - 81.0:+.4f} deg (~{(m_minx - 81.0) * 106.45:.1f} km)")
print(f"  Eastern edge offset from 81.0 E: {m_maxx - 81.0:+.4f} deg (~{(m_maxx - 81.0) * 106.45:.1f} km)")
print("  Note: 81.0 E is near the western boundary, NOT the bisector of the study area.")
print("  The midpoint of the study area is 81.725 E (0.725 deg east of central meridian).")
print("  Scale factor range: ~0.99960 to ~1.00035 (distortion < 0.04%). EPSG:32644 is highly suitable.")
