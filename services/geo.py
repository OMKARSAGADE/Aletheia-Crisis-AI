import sqlite_utils
from geopy.geocoders import Nominatim
from .config import DB_PATH

geolocator = Nominatim(user_agent="crisislens_authority_app_v1")

def get_geo_cache_db():
    return sqlite_utils.Database(DB_PATH)

def init_geo_cache():
    db = get_geo_cache_db()
    if "geo_cache" not in db.table_names():
        db["geo_cache"].create({
            "location_name": str,
            "lat": float,
            "lon": float
        }, pk="location_name")

def get_coordinates(location_name):
    if not location_name or location_name.lower() in ["unknown", "none", ""]:
        return None, None
        
    db = get_geo_cache_db()
    init_geo_cache()
    
    # Check cache first
    try:
        cached = db["geo_cache"].get(location_name)
        return cached["lat"], cached["lon"]
    except sqlite_utils.db.NotFoundError:
        pass
        
    # Not in cache, geocode it
    try:
        # Append India to make it more reliable for the demo, since we are using Indian cities mostly
        query = f"{location_name}, India"
        location = geolocator.geocode(query, timeout=5)
        
        if location:
            lat, lon = location.latitude, location.longitude
            # Save to cache
            db["geo_cache"].insert({
                "location_name": location_name,
                "lat": lat,
                "lon": lon
            })
            return lat, lon
        else:
            # If not found, store None to prevent retrying
            db["geo_cache"].insert({
                "location_name": location_name,
                "lat": None,
                "lon": None
            })
            return None, None
    except Exception as e:
        print(f"Geocoding error for {location_name}: {e}")
        return None, None
