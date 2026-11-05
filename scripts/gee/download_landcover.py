"""
Google Earth Engine: ESA WorldCover 10m Extraction
Dataset: ESA/WorldCover/v200 (2021)
"""
import ee
from define_study_area import get_lower_godavari_geometry

def get_esa_worldcover():
    roi = get_lower_godavari_geometry()
    wc = ee.ImageCollection('ESA/WorldCover/v200').first().select('Map').clip(roi)
    print("ESA WorldCover 10m pipeline configured for Lower Godavari Basin.")
    return wc

if __name__ == "__main__":
    try:
        ee.Initialize()
        get_esa_worldcover()
    except Exception as e:
        print("Earth Engine authentication required:", e)
