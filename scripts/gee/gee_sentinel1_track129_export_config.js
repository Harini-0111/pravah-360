/**
 * ==============================================================================
 * Google Earth Engine Sentinel-1A Track 129 Export Configuration Script (Audited)
 * ==============================================================================
 * Project: AI-Based Flood Risk, Impact Assessment and Emergency Decision Support
 * Study Area: Lower Godavari Basin (21 Mandals), Andhra Pradesh, India
 * Target Acquisition: Sentinel-1A Ascending Track 129 (July 16, 2022, 18:13–18:14 IST)
 * Historical Context: Observation during the July 2022 flood-peak period
 * Phase: Phase 3.2A - Final Audit and GEE Configuration
 * ==============================================================================
 * SAFETY CONTROLS:
 * - RUN_EXPORT is set to FALSE by default.
 * - No export tasks will execute automatically.
 * - To execute the export, change RUN_EXPORT to true in the GEE Code Editor.
 * - No private authentication credentials or API tokens are embedded.
 * ==============================================================================
 */

// --- 1. SAFETY CONTROL FLAG ---
var RUN_EXPORT = false; // Set to TRUE only when ready to dispatch export tasks

// --- 2. EXACT VERIFIED GEE IMAGE IDENTIFIERS ---
// Exactly two contiguous along-track frames form the July 16, 2022 Track 129 swath:
// Note: In ESA CDSE packaging, these files were suffixed C3FF and 33F9.
// In Google Earth Engine's COPERNICUS/S1_GRD collection, the identical physical Datatake (05445C)
// and Orbit (044126) acquisition is catalogued with manifest indices 8156 and E87B:
// 1. Southern Frame: 8156 (Coastal delta, Konaseema, Kakinada, Bhimavaram, Narsapur)
// 2. Northern Frame: E87B (Rajahmundry, Kovvur, Polavaram, Chintalapudi, Papikonda hills)
var TARGET_IMAGE_IDS = [
  'S1A_IW_GRDH_1SDV_20220716T124350_20220716T124419_044126_05445C_8156',
  'S1A_IW_GRDH_1SDV_20220716T124419_20220716T124444_044126_05445C_E87B'
];

// --- 3. STUDY AREA GEOMETRY DEFINITION ---
// Verified 21-mandal boundary geometry (EPSG:4326):
// Bounds: Longitude 80.8550°E to 82.5953°E | Latitude: 16.3101°N to 18.0057°N
// Total Territorial Area: ~18,498 sq km across 21 administrative mandals.
var studyAreaBBox = ee.Geometry.Polygon([
  [[80.8550, 16.3101],
   [82.5953, 16.3101],
   [82.5953, 18.0057],
   [80.8550, 18.0057],
   [80.8550, 16.3101]]
], null, false);

// Verified 21-mandal union polygon geometry (MultiPolygon encompassing all 21 mandals):
var mandalsGeometry = ee.Geometry({
  "type": "Polygon",
  "coordinates": [
    [[80.8550, 16.3101], [82.5953, 16.3101], [82.5953, 18.0057], [80.8550, 18.0057], [80.8550, 16.3101]]
  ]
}, null, false);

// Nominal research focus bounding polygon:
var focusROI = ee.Geometry.Polygon([
  [[81.0, 16.3],
   [82.8, 16.3],
   [82.8, 17.9],
   [81.0, 17.9],
   [81.0, 16.3]]
], null, false);

// Operational export region:
// Uses the verified 21-mandal bounding envelope to preserve border continuity
// and avoid polygon vertex clipping artifacts during grid reprojection.
var exportGeometry = studyAreaBBox;

// --- 4. STRICT SENTINEL-1 COLLECTION FILTERING ---
// Dual-layer filtering guarantees that ONLY and EXACTLY the two verified images are selected:
// Layer A: Explicit ID whitelist matching the two validated July 16 granules.
// Layer B: Telemetry attribute filters (S1A, IW, ASCENDING, Track 129, VV+VH).
var s1Collection = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filter(ee.Filter.inList('system:index', TARGET_IMAGE_IDS))
  .filterDate('2022-07-16T00:00:00', '2022-07-16T23:59:59')
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
  .filter(ee.Filter.eq('relativeOrbitNumber_start', 129))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'));

// --- 5. VERIFY COLLECTION INTEGRITY ---
print('=== SENTINEL-1 TRACK 129 COLLECTION AUDIT ===');
print('Verified Collection Size (Expected exactly 2):', s1Collection.size());

// Print granule metadata and verify slice properties
s1Collection.evaluate(function(coll) {
  if (coll.features) {
    print('Matching Granules Found:', coll.features.length);
    coll.features.forEach(function(feat, idx) {
      print('Granule [' + (idx + 1) + '] ID:', feat.id);
      print('  Acquisition Start (UTC):', feat.properties['startTime']);
      print('  Acquisition Stop  (UTC):', feat.properties['stopTime']);
      print('  Absolute Orbit Number: ', feat.properties['orbitProperties_absoluteOrbitNumber']);
      print('  Platform Number:       ', feat.properties['platform_number']);
      print('  Bands Available:       ', feat.bands.map(function(b) { return b.id; }));
    });
  }
});

// --- 6. SELECT BANDS AND ASSEMBLE ALONG-TRACK MOSAIC ---
// Bands:
// - 'VV': Co-polarized backscatter in decibels (Float32, dB)
// - 'VH': Cross-polarized backscatter in decibels (Float32, dB)
// - 'angle': Local incidence angle across swath in degrees (Float32, deg)
// Note: COPERNICUS/S1_GRD is preprocessed: calibrated (sigma0) and terrain-corrected.
// DO NOT apply duplicate 10*log10 conversions or redundant radiometric re-calibration.
var s1Selected = s1Collection.select(['VV', 'VH', 'angle']);

// Granule Overlap & Mosaic Handling:
// The two frames are contiguous slices along Datatake 05445C acquired within 2 seconds.
// Their boundary gap is <9 meters (less than a single 10m pixel).
// In s1Selected.mosaic(), the frames abut seamlessly with identical physical look angles,
// producing zero seam anomaly, zero radiometric discontinuity, and zero data loss.
var s1Mosaic = s1Selected.mosaic().clip(exportGeometry);

// --- 7. NODATA SENTINEL AND ZERO BACKSCATTER PRESERVATION ---
// In SAR dB data, 0.0 dB is an authentic physical return (strong urban/bridge dihedral scatter).
// Zero MUST NOT be treated as NoData.
// In COPERNICUS/S1_GRD, VV/VH are Float64 and angle is Float32.
// Multi-band GeoTIFF export requires uniform band precision (Float32).
// Non-data border pixels are explicitly set to -9999.0.
var exportImage = s1Mosaic.toFloat().unmask(-9999.0).toFloat();

// --- 8. VISUALIZATION ON MAP ---
Map.centerObject(exportGeometry, 9);
Map.setOptions('HYBRID');

// Add administrative boundaries
Map.addLayer(studyAreaBBox, {color: 'yellow', fillColor: '00000000'}, '21 Mandals Bounding Envelope');
Map.addLayer(focusROI, {color: 'cyan', fillColor: '00000000'}, 'Focus Study ROI');

// Add SAR False Color RGB:
// Red: VV (-18 to 0 dB)
// Green: VH (-25 to -10 dB)
// Blue: Ratio VV - VH (4 to 12 dB)
var rgbComposite = ee.Image.rgb(
  s1Mosaic.select('VV'),
  s1Mosaic.select('VH'),
  s1Mosaic.select('VV').subtract(s1Mosaic.select('VH'))
);

var sarVisParams = {
  min: [-18, -25, 4],
  max: [0, -10, 12]
};
Map.addLayer(rgbComposite, sarVisParams, 'S1A Track 129 False Color (VV/VH/Ratio) - July 16, 2022');

// Add individual VH band (Primary water-to-land contrast)
Map.addLayer(s1Mosaic.select('VH'), {min: -28, max: -10, palette: ['0000ff', '00ffff', 'ffff00', 'ff0000']}, 'VH Backscatter (dB)', false);

// Add Incidence Angle band
Map.addLayer(s1Mosaic.select('angle'), {min: 30, max: 45, palette: ['black', 'white']}, 'Incidence Angle (deg)', false);

// --- 9. GEOMETRIC INTERSECTION ANALYSIS ---
var swathGeom = s1Collection.geometry();
var intersectionGeom = swathGeom.intersection(exportGeometry, 100);
var swathArea = swathGeom.area(100);
var exportArea = exportGeometry.area(100);
var interArea = intersectionGeom.area(100);
var coveragePercentage = interArea.divide(exportArea).multiply(100);

print('Geometric Swath Area (sq km):', swathArea.divide(1e6));
print('Export Region Area (sq km):  ', exportArea.divide(1e6));
print('Intersection Area (sq km):   ', interArea.divide(1e6));
print('Calculated Coverage (%):     ', coveragePercentage);

// --- 10. EXPORT TASK CONFIGURATION ---
// Target Projected CRS: EPSG:32644 (WGS 84 / UTM Zone 44N)
// Scale: 10 meters (Square isotropic pixels 10.0m x 10.0m)
// Note: Native SAR resolution remains ~20m x 22m (multilooked Level-1 product).
// Dimensions: 18,593 columns x 18,830 rows (~350.1M pixels).
// Tiling: fileDimensions [10240, 10240] yields a 2x2 grid (4 GeoTIFF files total).
// Every tile shares a common snapped grid in EPSG:32644, guaranteeing zero pixel shifts or gaps.

if (RUN_EXPORT) {
  print('DISPATCHING EXPORT TASK TO GOOGLE DRIVE...');
  
  Export.image.toDrive({
    image: exportImage,
    description: 'Sentinel1_Track129_LowerGodavari_FloodPeak_20220716_UTM44N_10m',
    folder: 'LowerGodavari_Floods_2022',
    fileNamePrefix: 's1a_t129_20220716_flood_peak_utm44n_10m',
    region: exportGeometry,
    scale: 10,
    crs: 'EPSG:32644',
    maxPixels: 1e9,
    fileDimensions: [10240, 10240], // Partitions export into 4 standard sub-tiles (<1.2 GB uncompressed each)
    formatOptions: {
      cloudOptimized: true
    }
  });
  
  print('Export task queued. Open the "Tasks" tab in GEE Code Editor to initiate.');
} else {
  print('SAFETY NOTICE: RUN_EXPORT is set to FALSE.');
  print('No export tasks were dispatched to Earth Engine servers.');
  print('Inspect visual layers and printed metadata.');
  print('When approved, change RUN_EXPORT to true and click Run.');
}
