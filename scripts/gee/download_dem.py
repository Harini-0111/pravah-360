"""
Google Earth Engine: Copernicus DEM GLO-30 Extraction
Dataset: COPERNICUS/DEM/GLO30
"""
import ee
from define_study_area import get_lower_godavari_geometry

def export_copernicus_dem():
    roi = get_lower_godavari_geometry()
    dem = ee.ImageCollection('COPERNICUS/DEM/GLO30').select('DEM').mosaic().clip(roi)
    slope = ee.Terrain.slope(dem).rename('slope_deg')
    aspect = ee.Terrain.aspect(dem).rename('aspect_deg')
    
    terrain = dem.addBands(slope).addBands(aspect)
    print("Copernicus DEM GLO-30 pipeline configured (Elevation, Slope, Aspect at 30m).")
    return terrain

if __name__ == "__main__":
    try:
        ee.Initialize()
        export_copernicus_dem()
    except Exception as e:
        print("Earth Engine authentication required:", e)
