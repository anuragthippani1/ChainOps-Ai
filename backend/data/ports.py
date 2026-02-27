"""
Major global shipping ports database with coordinates and operational data.
"""

MAJOR_PORTS = {
    # Asia-Pacific
    "Shanghai": {
        "country": "China",
        "coordinates": {"lat": 31.2304, "lon": 121.4737},
        "capacity": "High",
        "avg_wait_time": 0.5  # days
    },
    "Singapore": {
        "country": "Singapore",
        "coordinates": {"lat": 1.3521, "lon": 103.8198},
        "capacity": "Very High",
        "avg_wait_time": 0.3
    },
    "Shenzhen": {
        "country": "China",
        "coordinates": {"lat": 22.5431, "lon": 114.0579},
        "capacity": "Very High",
        "avg_wait_time": 0.5
    },
    "Hong Kong": {
        "country": "China",
        "coordinates": {"lat": 22.3193, "lon": 114.1694},
        "capacity": "Very High",
        "avg_wait_time": 0.4
    },
    "Busan": {
        "country": "South Korea",
        "coordinates": {"lat": 35.1796, "lon": 129.0756},
        "capacity": "High",
        "avg_wait_time": 0.4
    },
    "Guangzhou": {
        "country": "China",
        "coordinates": {"lat": 23.1291, "lon": 113.2644},
        "capacity": "High",
        "avg_wait_time": 0.6
    },
    "Qingdao": {
        "country": "China",
        "coordinates": {"lat": 36.0671, "lon": 120.3826},
        "capacity": "High",
        "avg_wait_time": 0.5
    },
    "Tokyo": {
        "country": "Japan",
        "coordinates": {"lat": 35.6532, "lon": 139.8070},
        "capacity": "High",
        "avg_wait_time": 0.4
    },
    "Port Klang": {
        "country": "Malaysia",
        "coordinates": {"lat": 2.9938, "lon": 101.3937},
        "capacity": "High",
        "avg_wait_time": 0.5
    },
    "Kaohsiung": {
        "country": "Taiwan",
        "coordinates": {"lat": 22.6273, "lon": 120.3014},
        "capacity": "High",
        "avg_wait_time": 0.4
    },
    
    # Europe
    "Rotterdam": {
        "country": "Netherlands",
        "coordinates": {"lat": 51.9244, "lon": 4.4777},
        "capacity": "Very High",
        "avg_wait_time": 0.3
    },
    "Antwerp": {
        "country": "Belgium",
        "coordinates": {"lat": 51.2194, "lon": 4.4025},
        "capacity": "High",
        "avg_wait_time": 0.4
    },
    "Hamburg": {
        "country": "Germany",
        "coordinates": {"lat": 53.5511, "lon": 9.9937},
        "capacity": "High",
        "avg_wait_time": 0.5
    },
    "Valencia": {
        "country": "Spain",
        "coordinates": {"lat": 39.4699, "lon": -0.3763},
        "capacity": "Medium",
        "avg_wait_time": 0.6
    },
    "Piraeus": {
        "country": "Greece",
        "coordinates": {"lat": 37.9421, "lon": 23.6463},
        "capacity": "Medium",
        "avg_wait_time": 0.7
    },
    "Le Havre": {
        "country": "France",
        "coordinates": {"lat": 49.4944, "lon": 0.1079},
        "capacity": "Medium",
        "avg_wait_time": 0.6
    },
    "Felixstowe": {
        "country": "United Kingdom",
        "coordinates": {"lat": 51.9606, "lon": 1.3511},
        "capacity": "High",
        "avg_wait_time": 0.5
    },
    
    # Middle East
    "Dubai": {
        "country": "UAE",
        "coordinates": {"lat": 25.2769, "lon": 55.2962},
        "capacity": "Very High",
        "avg_wait_time": 0.4
    },
    "Jeddah": {
        "country": "Saudi Arabia",
        "coordinates": {"lat": 21.5433, "lon": 39.1728},
        "capacity": "High",
        "avg_wait_time": 0.6
    },
    "Port Said": {
        "country": "Egypt",
        "coordinates": {"lat": 31.2653, "lon": 32.3019},
        "capacity": "High",
        "avg_wait_time": 0.5
    },
    
    # Americas
    "Los Angeles": {
        "country": "USA",
        "coordinates": {"lat": 33.7405, "lon": -118.2697},
        "capacity": "Very High",
        "avg_wait_time": 0.8
    },
    "Long Beach": {
        "country": "USA",
        "coordinates": {"lat": 33.7701, "lon": -118.1937},
        "capacity": "Very High",
        "avg_wait_time": 0.8
    },
    "New York": {
        "country": "USA",
        "coordinates": {"lat": 40.6643, "lon": -74.0736},
        "capacity": "Very High",
        "avg_wait_time": 0.7
    },
    "Savannah": {
        "country": "USA",
        "coordinates": {"lat": 32.0809, "lon": -81.0912},
        "capacity": "High",
        "avg_wait_time": 0.6
    },
    "Houston": {
        "country": "USA",
        "coordinates": {"lat": 29.7604, "lon": -95.3698},
        "capacity": "High",
        "avg_wait_time": 0.7
    },
    "Santos": {
        "country": "Brazil",
        "coordinates": {"lat": -23.9608, "lon": -46.3333},
        "capacity": "High",
        "avg_wait_time": 0.8
    },
    "Vancouver": {
        "country": "Canada",
        "coordinates": {"lat": 49.2827, "lon": -123.1207},
        "capacity": "High",
        "avg_wait_time": 0.5
    },
    "Manzanillo": {
        "country": "Mexico",
        "coordinates": {"lat": 19.0544, "lon": -104.3200},
        "capacity": "Medium",
        "avg_wait_time": 0.6
    },
    
    # Africa
    "Durban": {
        "country": "South Africa",
        "coordinates": {"lat": -29.8587, "lon": 31.0218},
        "capacity": "Medium",
        "avg_wait_time": 0.7
    },
    "Lagos": {
        "country": "Nigeria",
        "coordinates": {"lat": 6.4281, "lon": 3.4219},
        "capacity": "Medium",
        "avg_wait_time": 1.0
    },
    "Tangier": {
        "country": "Morocco",
        "coordinates": {"lat": 35.7595, "lon": -5.8340},
        "capacity": "High",
        "avg_wait_time": 0.5
    },
    
    # Australia
    "Sydney": {
        "country": "Australia",
        "coordinates": {"lat": -33.8688, "lon": 151.2093},
        "capacity": "High",
        "avg_wait_time": 0.5
    },
    "Melbourne": {
        "country": "Australia",
        "coordinates": {"lat": -37.8136, "lon": 144.9631},
        "capacity": "High",
        "avg_wait_time": 0.5
    },
    
    # South Asia
    "Mumbai": {
        "country": "India",
        "coordinates": {"lat": 18.9220, "lon": 72.8347},
        "capacity": "High",
        "avg_wait_time": 0.9
    },
    "Chennai": {
        "country": "India",
        "coordinates": {"lat": 13.0827, "lon": 80.2707},
        "capacity": "High",
        "avg_wait_time": 0.8
    },
    "Colombo": {
        "country": "Sri Lanka",
        "coordinates": {"lat": 6.9271, "lon": 79.8612},
        "capacity": "Medium",
        "avg_wait_time": 0.6
    },
    "Karachi": {
        "country": "Pakistan",
        "coordinates": {"lat": 24.8607, "lon": 67.0011},
        "capacity": "Medium",
        "avg_wait_time": 0.9
    },
}

CANALS = {
    "Suez Canal": {
        "coordinates": {"lat": 30.5852, "lon": 32.3439},
        "avg_toll": 450000,  # USD
        "avg_transit_time": 0.5  # days
    },
    "Panama Canal": {
        "coordinates": {"lat": 9.0820, "lon": -79.6805},
        "avg_toll": 400000,  # USD
        "avg_transit_time": 0.4  # days
    }
}

def get_port_by_name(port_name: str):
    """Get port information by name (case-insensitive)"""
    for name, info in MAJOR_PORTS.items():
        if name.lower() == port_name.lower():
            return {**info, "name": name}
    return None

def get_all_port_names():
    """Get list of all port names"""
    return sorted(MAJOR_PORTS.keys())

def search_ports(query: str):
    """Search ports by name or country"""
    query = query.lower()
    results = []
    for name, info in MAJOR_PORTS.items():
        if query in name.lower() or query in info["country"].lower():
            results.append({
                "name": name,
                "country": info["country"],
                "coordinates": info["coordinates"]
            })
    return results

