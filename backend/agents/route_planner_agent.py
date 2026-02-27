import math
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import ports data
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.ports import MAJOR_PORTS, CANALS, get_port_by_name

class RoutePlannerAgent:
    """
    Advanced route planning agent for multi-port shipping routes.
    Optimizes routes based on distance, time, cost, and risk factors.
    """
    
    def __init__(self):
        self.ports = MAJOR_PORTS
        self.canals = CANALS
        self.base_ship_speed = 20  # knots
        self.base_fuel_cost_per_nm = 2.5  # USD per nautical mile
        
        # Optimization multipliers
        self.optimization_profiles = {
            "fastest": {
                "speed_multiplier": 1.25,  # 25% faster (25 knots)
                "fuel_cost_multiplier": 1.5,  # 50% more fuel cost
                "port_wait_multiplier": 0.5,  # Priority port access (50% wait time)
                "description": "Maximum speed with priority port access"
            },
            "cheapest": {
                "speed_multiplier": 0.8,  # 20% slower (16 knots) - eco-speed
                "fuel_cost_multiplier": 0.7,  # 30% less fuel cost
                "port_wait_multiplier": 1.3,  # 30% longer wait (cheaper ports)
                "description": "Eco-speed navigation with budget ports"
            },
            "balanced": {
                "speed_multiplier": 1.0,  # Standard speed (20 knots)
                "fuel_cost_multiplier": 1.0,  # Standard fuel cost
                "port_wait_multiplier": 1.0,  # Standard wait time
                "description": "Optimal balance of speed, cost, and efficiency"
            },
            "safest": {
                "speed_multiplier": 0.9,  # 10% slower for safety (18 knots)
                "fuel_cost_multiplier": 1.1,  # 10% more fuel (safer routes may be longer)
                "port_wait_multiplier": 0.8,  # Better scheduled, safer ports
                "description": "Prioritizes low-risk routes and reliable ports"
            }
        }
        
    def calculate_distance(self, coord1: Dict, coord2: Dict) -> float:
        """
        Calculate great circle distance between two coordinates in nautical miles.
        Using Haversine formula.
        """
        lat1, lon1 = math.radians(coord1["lat"]), math.radians(coord1["lon"])
        lat2, lon2 = math.radians(coord2["lat"]), math.radians(coord2["lon"])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in nautical miles
        r = 3440.065
        
        return c * r
    
    def calculate_route_leg(self, port1_name: str, port2_name: str, optimization: str = "balanced") -> Optional[Dict]:
        """Calculate details for a single leg of the route"""
        port1 = get_port_by_name(port1_name)
        port2 = get_port_by_name(port2_name)
        
        if not port1 or not port2:
            return None
        
        # Get optimization profile
        profile = self.optimization_profiles.get(optimization, self.optimization_profiles["balanced"])
        
        # Apply optimization to speed and costs
        ship_speed = self.base_ship_speed * profile["speed_multiplier"]
        fuel_cost_per_nm = self.base_fuel_cost_per_nm * profile["fuel_cost_multiplier"]
        
        distance = self.calculate_distance(port1["coordinates"], port2["coordinates"])
        transit_time_hours = distance / ship_speed
        transit_time_days = transit_time_hours / 24
        
        # Apply optimization to port wait times
        port_wait_time = (port1["avg_wait_time"] + port2["avg_wait_time"]) * profile["port_wait_multiplier"]
        total_time_days = transit_time_days + port_wait_time
        
        # Calculate costs
        fuel_cost = distance * fuel_cost_per_nm
        port_fees = 15000 + 12000  # Simplified port fees for departure and arrival
        
        # Check if route crosses major canals
        canal_info = self._check_canal_crossing(port1["coordinates"], port2["coordinates"])
        canal_cost = 0
        canal_time = 0
        if canal_info:
            canal_cost = canal_info["avg_toll"]
            canal_time = canal_info["avg_transit_time"]
            total_time_days += canal_time
        
        total_cost = fuel_cost + port_fees + canal_cost
        
        return {
            "from": port1_name,
            "to": port2_name,
            "from_country": port1["country"],
            "to_country": port2["country"],
            "distance_nm": round(distance, 2),
            "distance_km": round(distance * 1.852, 2),
            "transit_time_days": round(transit_time_days, 2),
            "port_wait_time_days": round(port_wait_time, 2),
            "total_time_days": round(total_time_days, 2),
            "fuel_cost_usd": round(fuel_cost, 2),
            "port_fees_usd": port_fees,
            "canal_cost_usd": canal_cost,
            "canal_name": canal_info["name"] if canal_info else None,
            "total_cost_usd": round(total_cost, 2),
            "ship_speed_knots": round(ship_speed, 1),
            "optimization_applied": optimization,
            "coordinates": {
                "from": port1["coordinates"],
                "to": port2["coordinates"]
            }
        }
    
    def _check_canal_crossing(self, coord1: Dict, coord2: Dict) -> Optional[Dict]:
        """
        Check if route crosses a major canal.
        Simplified logic - checks if route crosses specific regions.
        """
        lat1, lon1 = coord1["lat"], coord1["lon"]
        lat2, lon2 = coord2["lat"], coord2["lon"]
        
        # Check for Suez Canal (Mediterranean <-> Red Sea/Indian Ocean)
        if ((lon1 < 30 and lon2 > 40) or (lon1 > 40 and lon2 < 30)):
            if (20 < lat1 < 40 or 20 < lat2 < 40):
                return {**self.canals["Suez Canal"], "name": "Suez Canal"}
        
        # Check for Panama Canal (Atlantic <-> Pacific)
        if ((lon1 < -80 and lon2 > -80) or (lon1 > -80 and lon2 < -80)):
            if (-10 < lat1 < 30 or -10 < lat2 < 30):
                return {**self.canals["Panama Canal"], "name": "Panama Canal"}
        
        return None
    
    def plan_multi_port_route(self, ports: List[str], optimization: str = "balanced") -> Dict:
        """
        Plan a complete multi-port route.
        
        Args:
            ports: List of port names in order
            optimization: 'fastest', 'cheapest', 'balanced', 'safest'
        
        Returns:
            Complete route analysis with all legs and totals
        """
        if len(ports) < 2:
            return {"error": "At least 2 ports are required"}
        
        legs = []
        total_distance = 0
        total_time = 0
        total_cost = 0
        canals_used = []
        
        # Calculate each leg with optimization applied
        for i in range(len(ports) - 1):
            leg = self.calculate_route_leg(ports[i], ports[i+1], optimization)
            if not leg:
                return {"error": f"Invalid port: {ports[i]} or {ports[i+1]}"}
            
            legs.append(leg)
            total_distance += leg["distance_nm"]
            total_time += leg["total_time_days"]
            total_cost += leg["total_cost_usd"]
            
            if leg["canal_name"]:
                canals_used.append(leg["canal_name"])
        
        # Risk assessment for each leg (simplified)
        for leg in legs:
            leg["risk_level"] = self._assess_leg_risk(leg)
        
        # Generate alternative routes if optimization requested
        alternatives = []
        if len(ports) > 3 and optimization in ["cheapest", "fastest"]:
            alternatives = self._generate_alternatives(ports, optimization)
        
        # Get optimization profile info
        profile = self.optimization_profiles.get(optimization, self.optimization_profiles["balanced"])
        
        return {
            "route_type": "multi_port",
            "optimization": optimization,
            "optimization_description": profile["description"],
            "total_ports": len(ports),
            "ports": ports,
            "total_legs": len(legs),
            "legs": legs,
            "summary": {
                "total_distance_nm": round(total_distance, 2),
                "total_distance_km": round(total_distance * 1.852, 2),
                "total_time_days": round(total_time, 2),
                "total_cost_usd": round(total_cost, 2),
                "canals_used": list(set(canals_used)),
                "estimated_departure": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
                "estimated_arrival": (datetime.now() + timedelta(days=total_time)).strftime("%Y-%m-%d %H:%M UTC"),
                "avg_speed_knots": round(self.base_ship_speed * profile["speed_multiplier"], 1)
            },
            "alternatives": alternatives,
            "generated_at": datetime.now().isoformat()
        }
    
    def _assess_leg_risk(self, leg: Dict) -> str:
        """Assess risk level for a route leg"""
        # Simplified risk assessment based on region and distance
        from_country = leg["from_country"]
        to_country = leg["to_country"]
        
        high_risk_countries = ["Nigeria", "Somalia", "Yemen"]
        medium_risk_countries = ["Egypt", "Pakistan", "Venezuela"]
        
        if from_country in high_risk_countries or to_country in high_risk_countries:
            return "high"
        elif from_country in medium_risk_countries or to_country in medium_risk_countries:
            return "medium"
        elif leg["distance_nm"] > 5000:
            return "medium"  # Long distance = higher risk
        else:
            return "low"
    
    def _generate_alternatives(self, ports: List[str], optimization: str) -> List[Dict]:
        """
        Generate alternative route orderings for optimization.
        For now, returns a simplified alternative route.
        """
        # This is a simplified version - in production, you'd use
        # more sophisticated algorithms like Traveling Salesman Problem solvers
        alternatives = []
        
        # Try reverse order
        if len(ports) > 2:
            reversed_ports = [ports[0]] + list(reversed(ports[1:-1])) + [ports[-1]]
            alt_route = self.plan_multi_port_route(reversed_ports, optimization)
            if "error" not in alt_route:
                alt_route["alternative_id"] = 1
                alt_route["description"] = "Reversed intermediate stops"
                alternatives.append(alt_route)
        
        return alternatives[:3]  # Return max 3 alternatives
    
    def optimize_route_order(self, origin: str, destination: str, waypoints: List[str], 
                            optimization: str = "balanced") -> List[str]:
        """
        Optimize the order of waypoints between origin and destination.
        Uses a greedy nearest-neighbor approach.
        """
        if not waypoints:
            return [origin, destination]
        
        remaining = set(waypoints)
        route = [origin]
        current = origin
        
        while remaining:
            # Find nearest port from current location
            nearest = None
            min_distance = float('inf')
            
            current_port = get_port_by_name(current)
            if not current_port:
                break
            
            for waypoint in remaining:
                waypoint_port = get_port_by_name(waypoint)
                if waypoint_port:
                    dist = self.calculate_distance(
                        current_port["coordinates"],
                        waypoint_port["coordinates"]
                    )
                    if dist < min_distance:
                        min_distance = dist
                        nearest = waypoint
            
            if nearest:
                route.append(nearest)
                remaining.remove(nearest)
                current = nearest
            else:
                break
        
        route.append(destination)
        return route
    
    def compare_routes(self, route1: List[str], route2: List[str]) -> Dict:
        """Compare two different routes"""
        analysis1 = self.plan_multi_port_route(route1)
        analysis2 = self.plan_multi_port_route(route2)
        
        if "error" in analysis1 or "error" in analysis2:
            return {"error": "Invalid route comparison"}
        
        return {
            "route1": analysis1,
            "route2": analysis2,
            "comparison": {
                "time_difference_days": round(
                    analysis1["summary"]["total_time_days"] - 
                    analysis2["summary"]["total_time_days"], 2
                ),
                "cost_difference_usd": round(
                    analysis1["summary"]["total_cost_usd"] - 
                    analysis2["summary"]["total_cost_usd"], 2
                ),
                "distance_difference_nm": round(
                    analysis1["summary"]["total_distance_nm"] - 
                    analysis2["summary"]["total_distance_nm"], 2
                ),
                "faster_route": "route1" if analysis1["summary"]["total_time_days"] < analysis2["summary"]["total_time_days"] else "route2",
                "cheaper_route": "route1" if analysis1["summary"]["total_cost_usd"] < analysis2["summary"]["total_cost_usd"] else "route2"
            }
        }

