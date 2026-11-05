"""
Google Earth Engine: NASA GPM IMERG Daily & CHIRPS Daily Rainfall Extraction
Datasets: 
- NASA/GPM_L3/IMERG_V06 (or V07)
- UCSB-CHG/CHIRPS/DAILY
"""
import ee
from define_study_area import get_lower_godavari_geometry

def get_rainfall_collections():
    roi = get_lower_godavari_geometry()
    
    # CHIRPS Daily
    chirps = (ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
              .filterBounds(roi)
              .filterDate('2022-07-10', '2022-07-21')
              .select('precipitation'))
              
    chirps_total = chirps.sum().clip(roi).rename('chirps_total_mm')
    
    # NASA GPM IMERG
    gpm = (ee.ImageCollection('NASA/GPM_L3/IMERG_V06')
           .filterBounds(roi)
           .filterDate('2022-07-10', '2022-07-21')
           .select('precipitationCal'))
           
    print("Rainfall comparison pipeline configured (CHIRPS & NASA GPM IMERG for July 2022 flood).")
    return {"chirps_total": chirps_total, "chirps": chirps, "gpm": gpm}

if __name__ == "__main__":
    try:
        ee.Initialize()
        get_rainfall_collections()
    except Exception as e:
        print("Earth Engine authentication required:", e)
