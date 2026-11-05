"""
Google Earth Engine: Define Study Area for Lower Godavari Basin, AP
"""
import ee

def get_lower_godavari_geometry():
    """
    Returns ee.Geometry.Polygon for the Lower Godavari Basin study area
    encompassing Rajahmundry/Dowleswaram Barrage to the Gautami/Vasishta deltas.
    """
    coords = [
        [81.0, 16.3],
        [82.8, 16.3],
        [82.8, 17.9],
        [81.0, 17.9],
        [81.0, 16.3]
    ]
    return ee.Geometry.Polygon(coords)

if __name__ == "__main__":
    try:
        ee.Initialize()
        geom = get_lower_godavari_geometry()
        print("GEE initialized. Lower Godavari study area geometry created.")
        print("Area (sq km):", geom.area().divide(1e6).getInfo())
    except Exception as e:
        print("Earth Engine not authenticated. Please run 'earthengine authenticate'.")
        print("Details:", e)
