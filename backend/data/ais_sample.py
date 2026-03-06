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
    {"vessel_name": "Hapag Lloyd Tokyo", "lat": 22.5, "lon": 115.2, "speed": 13.2, "heading": 240.0},
    {"vessel_name": "COSCO Galaxy", "lat": 8.2, "lon": 78.5, "speed": 14.5, "heading": 270.0},
    {"vessel_name": "MSC Olympia", "lat": 38.5, "lon": -9.2, "speed": 11.8, "heading": 45.0},
    {"vessel_name": "ONE Stork", "lat": 5.8, "lon": 52.1, "speed": 12.2, "heading": 340.0},
    {"vessel_name": "PIL Singapore", "lat": 1.3, "lon": 103.9, "speed": 10.5, "heading": 180.0},
    {"vessel_name": "Yang Ming Unity", "lat": 30.8, "lon": 32.2, "speed": 8.2, "heading": 0.0},
    {"vessel_name": "HMM Algeciras", "lat": 35.1, "lon": 129.0, "speed": 15.0, "heading": 310.0},
    {"vessel_name": "ZIM Rotterdam", "lat": 51.9, "lon": 4.4, "speed": 6.0, "heading": 90.0},
    {"vessel_name": "APL Charleston", "lat": -33.9, "lon": 18.4, "speed": 14.0, "heading": 60.0},
    {"vessel_name": "MOL Triumph", "lat": -6.1, "lon": 106.8, "speed": 13.8, "heading": 125.0},
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
