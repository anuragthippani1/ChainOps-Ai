"""
Sample AIS vessel feed for backend fallback when live AIS is unavailable.
"""

import math
from typing import Dict, List, Tuple


AIS_SAMPLE_VESSELS: List[Dict[str, float | str]] = [
    {"vessel_name": "MV Horizon Star", "lat": 17.2, "lon": 60.4, "speed": 14.2, "heading": 318.0},
    {"vessel_name": "MSC Meridian", "lat": 25.5, "lon": 54.7, "speed": 12.8, "heading": 132.0},
    {"vessel_name": "CMA Nova", "lat": 11.9, "lon": 43.6, "speed": 13.5, "heading": 325.0},
    {"vessel_name": "Maersk Atlas", "lat": 2.1, "lon": 101.1, "speed": 15.1, "heading": 305.0},
    {"vessel_name": "Ever Zenith", "lat": 32.3, "lon": 121.7, "speed": 14.8, "heading": 205.0},
    {"vessel_name": "OOCL Pacific", "lat": 35.2, "lon": 140.1, "speed": 16.0, "heading": 118.0},
]


def project_position(lat: float, lon: float, speed_knots: float, heading_deg: float, hours_elapsed: float) -> Tuple[float, float]:
    """
    Approximate vessel projection from heading/speed over elapsed hours.
    """
    distance_nm = max(0.0, float(speed_knots)) * max(0.0, float(hours_elapsed))
    heading_rad = math.radians(float(heading_deg) % 360.0)

    delta_lat = (distance_nm * math.cos(heading_rad)) / 60.0
    mid_lat = float(lat) + (delta_lat / 2.0)
    lon_scale = max(0.1, math.cos(math.radians(mid_lat)))
    delta_lon = (distance_nm * math.sin(heading_rad)) / (60.0 * lon_scale)

    new_lat = max(-85.0, min(85.0, float(lat) + delta_lat))
    new_lon = float(lon) + delta_lon

    if new_lon > 180.0:
        new_lon -= 360.0
    elif new_lon < -180.0:
        new_lon += 360.0

    return new_lat, new_lon
