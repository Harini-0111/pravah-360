"""
Inspect GeoTIFF tags and bounding coordinates of all processed rasters
"""
from pathlib import Path
import tifffile

WORKSPACE = Path(r"C:\major project")

def inspect_geotiff(path):
    print("=" * 80)
    print(f"FILE: {path.name}")
    print("=" * 80)
    with tifffile.TiffFile(str(path)) as tif:
        page = tif.pages[0]
        print("Shape:", page.shape)
        scale = page.tags.get("ModelPixelScaleTag")
        tiepoint = page.tags.get("ModelTiepointTag")
        if scale:
            print("Pixel Scale (dx, dy, dz):", scale.value)
        if tiepoint:
            print("Tiepoint (I, J, K, X, Y, Z):", tiepoint.value)
            
        if scale and tiepoint:
            sx, sy = scale.value[0], scale.value[1]
            # Tiepoint: (I, J, K, X, Y, Z) where (I,J) is pixel coordinate (usually 0,0) and (X,Y) is geographic coordinate
            tp_x, tp_y = tiepoint.value[3], tiepoint.value[4]
            rows, cols = page.shape[0], page.shape[1]
            min_lon = tp_x
            max_lat = tp_y
            max_lon = tp_x + cols * sx
            min_lat = tp_y - rows * sy
            print(f"Calculated Georeferenced Extent:")
            print(f"  Longitude: [{min_lon:.6f}, {max_lon:.6f}] (width: {max_lon - min_lon:.6f} deg)")
            print(f"  Latitude:  [{min_lat:.6f}, {max_lat:.6f}] (height: {max_lat - min_lat:.6f} deg)")
        else:
            print("No ModelPixelScaleTag / ModelTiepointTag found directly.")
            # Check ImageDescription
            desc = page.tags.get("ImageDescription")
            if desc:
                print("ImageDescription:", desc.value)

for p in (WORKSPACE / "data" / "processed").rglob("*.tif"):
    inspect_geotiff(p)

for p in (WORKSPACE / "data" / "raw" / "dem").glob("*.tif"):
    inspect_geotiff(p)
