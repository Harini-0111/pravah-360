"""
Google Earth Engine: Sentinel-1 SAR Pre-Flood and Flood-Peak Extraction
Dataset: COPERNICUS/S1_GRD
IW mode, VV + VH polarizations
Event: July 2022 Godavari Flood
"""
import ee
from define_study_area import get_lower_godavari_geometry

def get_sentinel1_collections():
    roi = get_lower_godavari_geometry()
    
    # 1. Base Collection Filter
    s1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
          .filterBounds(roi)
          .filter(ee.Filter.eq('instrumentMode', 'IW'))
          .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
          .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')))
          
    # 2. Pre-flood baseline (1-20 June 2022)
    pre_flood = (s1.filterDate('2022-06-01', '2022-06-20')
                 .select(['VV', 'VH'])
                 .median()
                 .clip(roi))
                 
    # 3. Flood peak window (14-18 July 2022)
    flood_peak = (s1.filterDate('2022-07-14', '2022-07-18')
                  .select(['VV', 'VH'])
                  .mosaic()
                  .clip(roi))
                  
    # 4. Difference detection (Ratio in dB: Pre - Flood)
    diff_vv = pre_flood.select('VV').subtract(flood_peak.select('VV')).rename('VV_diff')
    
    return {
        "pre_flood": pre_flood,
        "flood_peak": flood_peak,
        "diff_vv": diff_vv,
        "roi": roi
    }

def export_rasters(export_to_drive=False):
    collections = get_sentinel1_collections()
    roi = collections["roi"]
    
    print("Sentinel-1 SAR analysis collection configured:")
    print("- Mode: IW (Interferometric Wide Swath)")
    print("- Polarizations: VV, VH")
    print("- Resolution: 10m scale")
    print("- Coordinate Reference System: EPSG:4326")
    
    if export_to_drive:
        task_flood = ee.batch.Export.image.toDrive(
            image=collections["flood_peak"],
            description="Sentinel1_LowerGodavari_FloodPeak_July2022",
            folder="LowerGodavari_Floods",
            fileNamePrefix="s1_godavari_flood_peak_july2022_10m",
            region=roi,
            scale=10,
            crs="EPSG:4326",
            maxPixels=1e9
        )
        task_flood.start()
        print("Export task started for flood peak SAR raster.")

if __name__ == "__main__":
    try:
        ee.Initialize()
        export_rasters(export_to_drive=False)
    except Exception as e:
        print("Earth Engine authentication required.")
        print("Run 'earthengine authenticate' in terminal or authenticate via GEE Code Editor.")
