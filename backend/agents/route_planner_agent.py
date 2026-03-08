import math
import copy
from typing import List, Dict, Tuple, Optional, Any
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
        self.base_crew_cost_per_day = 4200  # USD/day
        self.base_co2_tons_per_nm = 0.065  # tCO2 per nautical mile (indicative)
        self.base_port_fee_usd = 13500  # USD per port call
        
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

        # Major maritime chokepoints used in risk and timeline modeling.
        self.maritime_chokepoints = {
            "Strait of Hormuz": {
                "coordinates": {"lat": 26.57, "lon": 56.25},
                "risk_boost": 0.45,
                "transit_time_days": 0.12,
                "security_surcharge_usd": 12000,
            },
            "Strait of Malacca": {
                "coordinates": {"lat": 2.55, "lon": 101.3},
                "risk_boost": 0.35,
                "transit_time_days": 0.18,
                "security_surcharge_usd": 9000,
            },
            "Bab el-Mandeb": {
                "coordinates": {"lat": 12.58, "lon": 43.33},
                "risk_boost": 0.4,
                "transit_time_days": 0.14,
                "security_surcharge_usd": 10000,
            },
            "Suez Canal": {
                "coordinates": self.canals["Suez Canal"]["coordinates"],
                "risk_boost": 0.3,
                "transit_time_days": self.canals["Suez Canal"]["avg_transit_time"],
                "security_surcharge_usd": 6000,
            },
            "Panama Canal": {
                "coordinates": self.canals["Panama Canal"]["coordinates"],
                "risk_boost": 0.28,
                "transit_time_days": self.canals["Panama Canal"]["avg_transit_time"],
                "security_surcharge_usd": 5500,
            },
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

    def _haversine_km(self, coord1: Dict, coord2: Dict) -> float:
        """Great-circle distance in kilometers."""
        return self.calculate_distance(coord1, coord2) * 1.852

    def _normalize_lon(self, lon: float) -> float:
        """Normalize longitude to [-180, 180]."""
        while lon > 180:
            lon -= 360
        while lon < -180:
            lon += 360
        return lon

    def _interpolate_route_points(self, coord1: Dict, coord2: Dict, steps: int = 80) -> List[Dict[str, float]]:
        """
        Build sampled points along the route segment.
        Uses wrapped longitude interpolation to avoid date-line artifacts.
        """
        lat1, lon1 = coord1["lat"], coord1["lon"]
        lat2, lon2 = coord2["lat"], coord2["lon"]
        lon_delta = lon2 - lon1
        if lon_delta > 180:
            lon_delta -= 360
        elif lon_delta < -180:
            lon_delta += 360

        points: List[Dict[str, float]] = []
        for i in range(steps + 1):
            t = i / steps
            lat = lat1 + ((lat2 - lat1) * t)
            lon = self._normalize_lon(lon1 + (lon_delta * t))
            points.append({"lat": lat, "lon": lon})
        return points

    def _detect_nearby_chokepoints(self, coord1: Dict, coord2: Dict, threshold_km: float = 300.0) -> List[Dict[str, Any]]:
        """
        Detect chokepoints within a proximity threshold to a route leg.
        """
        sampled_points = self._interpolate_route_points(coord1, coord2)
        nearby: List[Dict[str, Any]] = []
        for name, meta in self.maritime_chokepoints.items():
            cp_coord = meta["coordinates"]
            min_km = min(self._haversine_km(pt, cp_coord) for pt in sampled_points)
            if min_km <= threshold_km:
                nearby.append({
                    "name": name,
                    "distance_km": round(min_km, 1),
                    "risk_boost": float(meta.get("risk_boost", 0.0)),
                    "transit_time_days": float(meta.get("transit_time_days", 0.0)),
                    "security_surcharge_usd": float(meta.get("security_surcharge_usd", 0.0)),
                })
        nearby.sort(key=lambda x: x["distance_km"])
        return nearby

    def _estimate_port_congestion(self, port: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate congestion conditions from wait-time and capacity."""
        wait_days = float(port.get("avg_wait_time", 0.8) or 0.8)
        capacity = (port.get("capacity") or "").lower()

        score = 1.5
        if wait_days >= 1.4:
            score = 3.8
        elif wait_days >= 1.0:
            score = 2.8
        elif wait_days >= 0.7:
            score = 2.1

        if "high" in capacity and wait_days < 1.0:
            score = max(1.0, score - 0.2)
        if "medium" in capacity and wait_days >= 1.0:
            score = min(5.0, score + 0.2)

        return {
            "estimated_wait_days": round(wait_days, 2),
            "risk_score": round(score, 2),
            "risk_level": self._risk_label_from_score(score),
        }

    def _estimate_weather_conditions(self, coord1: Dict, coord2: Dict) -> Dict[str, Any]:
        """Lightweight weather heuristic by route midpoint and season."""
        mid_lat = (coord1["lat"] + coord2["lat"]) / 2
        mid_lon = self._normalize_lon((coord1["lon"] + coord2["lon"]) / 2)
        month = datetime.utcnow().month

        condition = "Stable marine weather"
        weather_score = 1.8
        wave_height_m = 1.8
        wind_knots = 16

        # North Indian Ocean monsoon tendency
        if 5 <= mid_lat <= 25 and 40 <= mid_lon <= 110 and month in [5, 6, 7, 8, 9, 10]:
            condition = "Monsoon-influenced seas with squalls"
            weather_score = 3.2
            wave_height_m = 3.6
            wind_knots = 28
        elif abs(mid_lat) >= 45:
            condition = "Rough seas and strong frontal winds"
            weather_score = 3.0
            wave_height_m = 3.2
            wind_knots = 30
        elif abs(mid_lat) <= 15:
            condition = "Tropical convection with localized storms"
            weather_score = 2.4
            wave_height_m = 2.6
            wind_knots = 22

        return {
            "condition": condition,
            "risk_score": round(weather_score, 2),
            "risk_level": self._risk_label_from_score(weather_score),
            "avg_wave_height_m": round(wave_height_m, 1),
            "avg_wind_speed_knots": wind_knots,
        }

    def _risk_label_from_score(self, score: float) -> str:
        if score >= 4:
            return "critical"
        if score >= 3:
            return "high"
        if score >= 2:
            return "medium"
        return "low"

    def _build_leg_timeline(
        self,
        departure_time: float,
        open_ocean_time: float,
        arrival_time: float,
        chokepoints: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Build timeline phases for one leg using day offsets."""
        timeline: List[Dict[str, Any]] = []
        elapsed = 0.0

        def add_phase(phase: str, duration: float):
            nonlocal elapsed
            timeline.append({
                "phase": phase,
                "start_day_offset": round(elapsed, 2),
                "end_day_offset": round(elapsed + duration, 2),
                "duration_days": round(duration, 2),
            })
            elapsed += duration

        add_phase("departure_port_operations", departure_time)
        add_phase("open_ocean_transit", open_ocean_time)
        for cp in chokepoints:
            add_phase(f"chokepoint_crossing:{cp['name']}", float(cp.get("transit_time_days", 0.0)))
        add_phase("arrival_port_operations", arrival_time)
        return timeline

    def _assess_operational_risk_score(
        self,
        distance_nm: float,
        from_country: str,
        to_country: str,
        weather_score: float,
        max_congestion_score: float,
        chokepoint_risk_boost: float,
    ) -> float:
        """Operational (non-political) risk score for the leg on a 1-5 scale."""
        score = 1.2
        if distance_nm > 6000:
            score += 0.8
        elif distance_nm > 3500:
            score += 0.5
        elif distance_nm > 1500:
            score += 0.25

        high_risk_countries = {"Nigeria", "Somalia", "Yemen"}
        medium_risk_countries = {"Egypt", "Pakistan", "Venezuela", "Iran"}
        if from_country in high_risk_countries or to_country in high_risk_countries:
            score += 1.0
        elif from_country in medium_risk_countries or to_country in medium_risk_countries:
            score += 0.45

        score += max(0.0, (weather_score - 1.5) * 0.35)
        score += max(0.0, (max_congestion_score - 1.5) * 0.25)
        score += chokepoint_risk_boost

        return round(min(5.0, max(1.0, score)), 2)
    
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
        departure_time_days = (port1["avg_wait_time"] * profile["port_wait_multiplier"])
        arrival_time_days = (port2["avg_wait_time"] * profile["port_wait_multiplier"])
        total_time_days = transit_time_days + port_wait_time
        
        # Core direct costs
        fuel_cost = distance * fuel_cost_per_nm
        congestion_origin = self._estimate_port_congestion(port1)
        congestion_destination = self._estimate_port_congestion(port2)
        origin_fee = self.base_port_fee_usd * (1.0 + (congestion_origin["risk_score"] - 1.0) * 0.08)
        destination_fee = self.base_port_fee_usd * (1.0 + (congestion_destination["risk_score"] - 1.0) * 0.08)
        port_fees = origin_fee + destination_fee
        
        # Check if route crosses major canals + chokepoints.
        canal_info = self._check_canal_crossing(port1["coordinates"], port2["coordinates"])
        chokepoints_nearby = self._detect_nearby_chokepoints(port1["coordinates"], port2["coordinates"])
        if canal_info and all(cp["name"] != canal_info["name"] for cp in chokepoints_nearby):
            cp_meta = self.maritime_chokepoints.get(canal_info["name"], {})
            chokepoints_nearby.append({
                "name": canal_info["name"],
                "distance_km": 0.0,
                "risk_boost": float(cp_meta.get("risk_boost", 0.0)),
                "transit_time_days": float(canal_info.get("avg_transit_time", 0.0)),
                "security_surcharge_usd": float(cp_meta.get("security_surcharge_usd", 0.0)),
            })

        chokepoint_transit_time = sum(cp.get("transit_time_days", 0.0) for cp in chokepoints_nearby)
        total_time_days += chokepoint_transit_time

        canal_cost = float(canal_info["avg_toll"]) if canal_info else 0.0
        security_surcharge = sum(float(cp.get("security_surcharge_usd", 0.0)) for cp in chokepoints_nearby)

        weather = self._estimate_weather_conditions(port1["coordinates"], port2["coordinates"])
        max_congestion_score = max(congestion_origin["risk_score"], congestion_destination["risk_score"])
        chokepoint_risk_boost = min(1.0, sum(float(cp.get("risk_boost", 0.0)) for cp in chokepoints_nearby))
        operational_risk_score = self._assess_operational_risk_score(
            distance_nm=distance,
            from_country=port1["country"],
            to_country=port2["country"],
            weather_score=float(weather["risk_score"]),
            max_congestion_score=float(max_congestion_score),
            chokepoint_risk_boost=chokepoint_risk_boost,
        )

        crew_cost = total_time_days * self.base_crew_cost_per_day
        insurance_rate = 0.012 + (operational_risk_score - 1.0) * 0.003
        insurance_base = fuel_cost + port_fees + canal_cost + crew_cost + security_surcharge
        insurance_cost = insurance_base * insurance_rate

        total_cost = fuel_cost + port_fees + canal_cost + crew_cost + insurance_cost + security_surcharge
        estimated_co2_tons = distance * self.base_co2_tons_per_nm * profile["speed_multiplier"]
        if weather["risk_level"] in ["high", "critical"]:
            estimated_co2_tons *= 1.05  # More maneuvering/fuel use in rough weather.

        voyage_timeline = self._build_leg_timeline(
            departure_time=departure_time_days,
            open_ocean_time=transit_time_days,
            arrival_time=arrival_time_days,
            chokepoints=chokepoints_nearby,
        )
        
        return {
            "from": port1["name"],
            "to": port2["name"],
            "from_country": port1["country"],
            "to_country": port2["country"],
            "distance_nm": round(distance, 2),
            "distance_km": round(distance * 1.852, 2),
            "transit_time_days": round(transit_time_days, 2),
            "port_wait_time_days": round(port_wait_time, 2),
            "total_time_days": round(total_time_days, 2),
            "fuel_cost_usd": round(fuel_cost, 2),
            "crew_cost_usd": round(crew_cost, 2),
            "insurance_cost_usd": round(insurance_cost, 2),
            "security_surcharge_usd": round(security_surcharge, 2),
            "port_fees_usd": round(port_fees, 2),
            "canal_cost_usd": round(canal_cost, 2),
            "canal_name": canal_info["name"] if canal_info else None,
            "total_cost_usd": round(total_cost, 2),
            "cost_breakdown_usd": {
                "fuel": round(fuel_cost, 2),
                "crew": round(crew_cost, 2),
                "insurance": round(insurance_cost, 2),
                "port_fees": round(port_fees, 2),
                "canal_tolls": round(canal_cost, 2),
                "security_surcharge": round(security_surcharge, 2),
            },
            "estimated_co2_tons": round(estimated_co2_tons, 2),
            "weather_conditions": weather["condition"],
            "weather_risk_level": weather["risk_level"],
            "weather_risk_score": weather["risk_score"],
            "weather": weather,
            "congestion_risk_origin": congestion_origin,
            "congestion_risk_destination": congestion_destination,
            "congestion_risk_level": self._risk_label_from_score(max_congestion_score),
            "chokepoints_nearby": chokepoints_nearby,
            "chokepoint_risk_boost": round(chokepoint_risk_boost, 2),
            "voyage_timeline": voyage_timeline,
            "operational_risk_score": operational_risk_score,
            "operational_risk_level": self._risk_label_from_score(operational_risk_score),
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
    
    def plan_multi_port_route(
        self,
        ports: List[str],
        optimization: str = "balanced",
        include_alternatives: bool = True,
    ) -> Dict:
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

        # Normalize user-entered names to canonical known ports.
        canonical_ports = []
        for p in ports:
            port_obj = get_port_by_name(p)
            if not port_obj:
                return {"error": f"Invalid port: {p}"}
            canonical_ports.append(port_obj["name"])
        
        legs = []
        total_distance = 0.0
        total_time = 0.0
        total_cost = 0.0
        total_co2 = 0.0
        canals_used = []
        chokepoints_encountered: List[str] = []
        weather_scores: List[float] = []
        cost_breakdown = {
            "fuel": 0.0,
            "crew": 0.0,
            "insurance": 0.0,
            "port_fees": 0.0,
            "canal_tolls": 0.0,
            "security_surcharge": 0.0,
        }
        
        # Calculate each leg with optimization applied
        for i in range(len(canonical_ports) - 1):
            leg = self.calculate_route_leg(canonical_ports[i], canonical_ports[i+1], optimization)
            if not leg:
                return {"error": f"Invalid port: {canonical_ports[i]} or {canonical_ports[i+1]}"}
            
            legs.append(leg)
            total_distance += leg["distance_nm"]
            total_time += leg["total_time_days"]
            total_cost += leg["total_cost_usd"]
            total_co2 += float(leg.get("estimated_co2_tons", 0.0))
            weather_scores.append(float(leg.get("weather_risk_score", 1.0)))

            for key in cost_breakdown.keys():
                cost_breakdown[key] += float((leg.get("cost_breakdown_usd") or {}).get(key, 0.0))
            
            if leg["canal_name"]:
                canals_used.append(leg["canal_name"])
            for cp in leg.get("chokepoints_nearby", []):
                cp_name = cp.get("name")
                if cp_name and cp_name not in chokepoints_encountered:
                    chokepoints_encountered.append(cp_name)
        
        # Operational risk assessment per leg.
        for leg in legs:
            leg["risk_level"] = self._assess_leg_risk(leg)
        route_operational_risk = max([float(leg.get("operational_risk_score", 1.0)) for leg in legs] or [1.0])
        route_weather_score = max(weather_scores or [1.0])
        
        # Generate alternative routes if optimization requested
        alternatives = []
        if include_alternatives and len(canonical_ports) > 3 and optimization in ["cheapest", "fastest"]:
            alternatives = self._generate_alternatives(canonical_ports, optimization)
        
        # Get optimization profile info
        profile = self.optimization_profiles.get(optimization, self.optimization_profiles["balanced"])
        departure_dt = datetime.utcnow()

        timeline_summary: List[Dict[str, Any]] = []
        elapsed_days = 0.0
        for idx, leg in enumerate(legs):
            for phase in leg.get("voyage_timeline", []):
                start_offset = elapsed_days + float(phase.get("start_day_offset", 0.0))
                end_offset = elapsed_days + float(phase.get("end_day_offset", 0.0))
                timeline_summary.append({
                    "leg": idx + 1,
                    "from": leg.get("from"),
                    "to": leg.get("to"),
                    "phase": phase.get("phase"),
                    "start_day_offset": round(start_offset, 2),
                    "end_day_offset": round(end_offset, 2),
                    "duration_days": phase.get("duration_days"),
                    "start_time_utc": (departure_dt + timedelta(days=start_offset)).strftime("%Y-%m-%d %H:%M UTC"),
                    "end_time_utc": (departure_dt + timedelta(days=end_offset)).strftime("%Y-%m-%d %H:%M UTC"),
                })
            elapsed_days += float(leg.get("total_time_days", 0.0))

        origin_congestion = legs[0].get("congestion_risk_origin", {}) if legs else {}
        destination_congestion = legs[-1].get("congestion_risk_destination", {}) if legs else {}
        overall_congestion_score = max(
            float(origin_congestion.get("risk_score", 1.0) or 1.0),
            float(destination_congestion.get("risk_score", 1.0) or 1.0),
        )

        primary_weather_condition = "Stable marine weather"
        if legs:
            weather_priority = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            sorted_weather = sorted(
                [leg.get("weather") for leg in legs if isinstance(leg.get("weather"), dict)],
                key=lambda w: weather_priority.get((w or {}).get("risk_level", "low"), 0),
                reverse=True,
            )
            if sorted_weather:
                primary_weather_condition = sorted_weather[0].get("condition", primary_weather_condition)
        
        return {
            "route_type": "multi_port",
            "route": " → ".join(canonical_ports),
            "optimization": optimization,
            "optimization_description": profile["description"],
            "total_ports": len(canonical_ports),
            "ports": canonical_ports,
            "total_legs": len(legs),
            "legs": legs,
            "total_distance": round(total_distance, 2),
            "estimated_time": round(total_time, 2),
            "chokepoints": chokepoints_encountered,
            "operational_risk_score": round(route_operational_risk, 2),
            "overall_risk_score": round(route_operational_risk, 2),
            "final_risk_score": round(route_operational_risk, 2),
            "cost_estimation": {
                "currency": "USD",
                "total_cost_usd": round(total_cost, 2),
                "breakdown_usd": {k: round(v, 2) for k, v in cost_breakdown.items()},
            },
            "emissions_estimation": {
                "estimated_co2_tons": round(total_co2, 2),
                "co2_intensity_tons_per_nm": round((total_co2 / total_distance), 4) if total_distance else 0,
            },
            "weather_conditions": {
                "condition": primary_weather_condition,
                "weather_risk_level": self._risk_label_from_score(route_weather_score),
                "weather_risk_score": round(route_weather_score, 2),
            },
            "congestion_risk": {
                "origin": origin_congestion,
                "destination": destination_congestion,
                "overall_risk_level": self._risk_label_from_score(overall_congestion_score),
                "overall_risk_score": round(overall_congestion_score, 2),
            },
            "timeline_summary": timeline_summary,
            "summary": {
                "total_distance_nm": round(total_distance, 2),
                "total_distance_km": round(total_distance * 1.852, 2),
                "total_time_days": round(total_time, 2),
                "total_cost_usd": round(total_cost, 2),
                "canals_used": list(set(canals_used)),
                "estimated_co2_tons": round(total_co2, 2),
                "cost_breakdown_usd": {k: round(v, 2) for k, v in cost_breakdown.items()},
                "weather_overview": {
                    "condition": primary_weather_condition,
                    "risk_level": self._risk_label_from_score(route_weather_score),
                    "risk_score": round(route_weather_score, 2),
                },
                "congestion_risk": {
                    "origin": origin_congestion,
                    "destination": destination_congestion,
                    "overall_risk_level": self._risk_label_from_score(overall_congestion_score),
                    "overall_risk_score": round(overall_congestion_score, 2),
                },
                "timeline_summary": timeline_summary,
                "chokepoints_encountered": chokepoints_encountered,
                "operational_risk_score": round(route_operational_risk, 2),
                "estimated_departure": departure_dt.strftime("%Y-%m-%d %H:%M UTC"),
                "estimated_arrival": (departure_dt + timedelta(days=total_time)).strftime("%Y-%m-%d %H:%M UTC"),
                "avg_speed_knots": round(self.base_ship_speed * profile["speed_multiplier"], 1),
            },
            "alternatives": alternatives,
            "generated_at": datetime.now().isoformat()
        }
    
    def _assess_leg_risk(self, leg: Dict) -> str:
        """Assess risk level for a route leg"""
        operational_score = float(leg.get("operational_risk_score", 1.0))
        return self._risk_label_from_score(operational_score)
    
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
            alt_route = self.plan_multi_port_route(reversed_ports, optimization, include_alternatives=False)
            if "error" not in alt_route:
                alt_route["alternative_id"] = 1
                alt_route["description"] = "Reversed intermediate stops"
                alternatives.append(alt_route)
        
        return alternatives[:3]  # Return max 3 alternatives

    def _safe_risk_score(self, route_analysis: Dict[str, Any]) -> float:
        """Extract a route-level risk score with fallback order."""
        for key in ["final_risk_score", "overall_risk_score", "operational_risk_score"]:
            value = route_analysis.get(key)
            if isinstance(value, (int, float)):
                return float(value)
        return 1.0

    def _apply_what_if_scenario(
        self,
        simulated: Dict[str, Any],
        scenario: str,
        target_port: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Apply scenario stress adjustments to a planned route.
        Returns scenario impact metadata.
        """
        scenario_id = (scenario or "suez_closure").strip().lower()
        legs = simulated.get("legs") or []
        summary = simulated.get("summary") or {}

        total_eta_delta = 0.0
        total_cost_delta = 0.0
        risk_delta = 0.0
        notes: List[str] = []
        impacted_legs: List[int] = []
        resolved_target = None

        def mark_leg(idx: int, eta_add: float, cost_add: float, forced_risk: Optional[str] = None):
            nonlocal total_eta_delta, total_cost_delta
            leg = legs[idx]
            leg["total_time_days"] = round(float(leg.get("total_time_days", 0.0)) + eta_add, 2)
            leg["total_cost_usd"] = round(float(leg.get("total_cost_usd", 0.0)) + cost_add, 2)
            if isinstance(leg.get("port_wait_time_days"), (int, float)):
                leg["port_wait_time_days"] = round(float(leg["port_wait_time_days"]) + max(0.0, eta_add * 0.45), 2)
            if forced_risk:
                leg["risk_level"] = forced_risk
            impacted_legs.append(idx)
            total_eta_delta += eta_add
            total_cost_delta += cost_add

        if scenario_id == "suez_closure":
            suz_legs = [
                idx for idx, leg in enumerate(legs)
                if leg.get("canal_name") == "Suez Canal"
                or any((cp or {}).get("name") == "Suez Canal" for cp in (leg.get("chokepoints_nearby") or []))
            ]
            if suz_legs:
                for idx in suz_legs:
                    mark_leg(idx, eta_add=4.5, cost_add=85000.0, forced_risk="critical")
                risk_delta = 1.1
                notes.append("Suez Canal unavailable. Route segments crossing Suez are rerouted around Cape lanes.")
            else:
                total_eta_delta = 1.2
                total_cost_delta = 25000.0
                risk_delta = 0.3
                notes.append("No direct Suez crossing, but regional congestion and insurance premiums increase.")

        elif scenario_id == "red_sea_escalation":
            red_sea_cp = {"Bab el-Mandeb", "Suez Canal", "Strait of Hormuz"}
            hit_legs = []
            for idx, leg in enumerate(legs):
                nearby = {cp.get("name") for cp in (leg.get("chokepoints_nearby") or []) if isinstance(cp, dict)}
                if red_sea_cp.intersection(nearby):
                    hit_legs.append(idx)
            if hit_legs:
                for idx in hit_legs:
                    mark_leg(idx, eta_add=2.0, cost_add=42000.0, forced_risk="critical")
                risk_delta = 0.9
                notes.append("Escalation near Red Sea chokepoints adds convoy delays and security surcharges.")
            else:
                total_eta_delta = 0.8
                total_cost_delta = 18000.0
                risk_delta = 0.25
                notes.append("Indirect impact from market-wide security and fuel premiums.")

        elif scenario_id == "port_strike":
            resolved_target = target_port
            if resolved_target:
                target_match = get_port_by_name(resolved_target)
                resolved_target = target_match["name"] if target_match else resolved_target
            if not resolved_target and legs:
                resolved_target = legs[-1].get("to")

            strike_legs = [
                idx for idx, leg in enumerate(legs)
                if leg.get("from") == resolved_target or leg.get("to") == resolved_target
            ]
            if strike_legs:
                for idx in strike_legs:
                    mark_leg(idx, eta_add=2.8, cost_add=38000.0, forced_risk="high")
                risk_delta = 0.7
                notes.append(f"Labor disruption at {resolved_target} increases berth wait and handling costs.")
            else:
                total_eta_delta = 0.6
                total_cost_delta = 12000.0
                risk_delta = 0.2
                notes.append("No direct port strike on route legs, minor network ripple delays applied.")

        else:
            notes.append("Unknown scenario selected. Baseline route returned without stress adjustments.")

        base_eta = float(simulated.get("estimated_time", summary.get("total_time_days", 0.0)) or 0.0)
        base_cost = float(
            ((simulated.get("cost_estimation") or {}).get("total_cost_usd"))
            or summary.get("total_cost_usd", 0.0)
            or 0.0
        )
        base_risk = self._safe_risk_score(simulated)

        new_eta = round(base_eta + total_eta_delta, 2)
        new_cost = round(base_cost + total_cost_delta, 2)
        new_risk = round(min(5.0, max(1.0, base_risk + risk_delta)), 2)

        simulated["estimated_time"] = new_eta
        simulated["final_risk_score"] = new_risk
        simulated["overall_risk_score"] = new_risk
        simulated["operational_risk_score"] = max(
            float(simulated.get("operational_risk_score", 1.0) or 1.0),
            round(min(5.0, max(1.0, float(simulated.get("operational_risk_score", 1.0) or 1.0) + (risk_delta * 0.7))), 2),
        )
        simulated["risk_level"] = self._risk_label_from_score(new_risk)

        if isinstance(simulated.get("cost_estimation"), dict):
            simulated["cost_estimation"]["total_cost_usd"] = new_cost

        summary["total_time_days"] = new_eta
        summary["total_cost_usd"] = new_cost
        summary["scenario_notes"] = notes
        simulated["summary"] = summary
        simulated["scenario_notes"] = notes

        return {
            "scenario_id": scenario_id,
            "eta_delta_days": round(total_eta_delta, 2),
            "cost_delta_usd": round(total_cost_delta, 2),
            "risk_delta": round(new_risk - base_risk, 2),
            "impacted_legs": impacted_legs,
            "target_port": resolved_target,
            "notes": notes,
        }

    def _get_scenario_meta(self, scenario: str) -> Dict[str, str]:
        scenario_id = (scenario or "suez_closure").strip().lower()
        catalog = {
            "suez_closure": {
                "name": "Suez Canal Closure",
                "description": "Simulates Suez blockage and reroute/insurance impacts.",
            },
            "red_sea_escalation": {
                "name": "Red Sea Security Escalation",
                "description": "Simulates risk and delay spikes across Red Sea-linked chokepoints.",
            },
            "port_strike": {
                "name": "Major Port Strike",
                "description": "Simulates operational disruptions from labor actions at a target port.",
            },
        }
        meta = catalog.get(scenario_id, {"name": "Custom Scenario", "description": "Custom simulation scenario"})
        return {"id": scenario_id, **meta}

    def _recommended_mitigations(
        self,
        scenario: str,
        impact: Dict[str, Any],
        route: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        scenario_id = (scenario or "").strip().lower()
        mitigations: List[Dict[str, Any]] = []

        def add_mitigation(
            mitigation_id: str,
            title: str,
            description: str,
            priority: str,
            risk_reduction: float,
            eta_days_change: float,
            cost_usd_change: float,
            tradeoffs: str,
            action_plan: List[str],
        ):
            impact_score = round((risk_reduction * 2.0) - (max(0.0, eta_days_change) * 0.2) - (max(0.0, cost_usd_change) / 100000.0), 2)
            mitigations.append({
                "id": mitigation_id,
                "title": title,
                "description": description,
                "priority": priority,
                "expected_impact": {
                    "risk_reduction": round(risk_reduction, 2),
                    "eta_days_change": round(eta_days_change, 2),
                    "cost_usd_change": round(cost_usd_change, 2),
                },
                "impact_score": impact_score,
                "tradeoffs": tradeoffs,
                "action_plan": action_plan,
            })

        if scenario_id == "suez_closure":
            add_mitigation(
                "reroute_cape",
                "Reroute via Cape of Good Hope",
                "Shift affected legs away from Suez and rebalance transit windows.",
                "high",
                risk_reduction=0.9,
                eta_days_change=2.8,
                cost_usd_change=62000,
                tradeoffs="Longer sailing distance and higher fuel burn.",
                action_plan=["Re-issue voyage plan with Cape lane", "Pre-book bunkering at Cape Town", "Notify downstream terminal operators"],
            )
            add_mitigation(
                "split_cargo",
                "Split Cargo Across Parallel Services",
                "Allocate critical loads to alternate vessels/routes to reduce concentration risk.",
                "high",
                risk_reduction=0.75,
                eta_days_change=1.1,
                cost_usd_change=38000,
                tradeoffs="Requires vessel coordination and cargo fragmentation.",
                action_plan=["Tag priority SKUs", "Assign expedited lot to alternate loop", "Consolidate non-urgent shipments"],
            )

        elif scenario_id == "red_sea_escalation":
            add_mitigation(
                "security_convoy",
                "Adopt Security Corridor + Convoy Scheduling",
                "Use escorted windows and tighten transit timing through exposed segments.",
                "high",
                risk_reduction=0.7,
                eta_days_change=0.9,
                cost_usd_change=24000,
                tradeoffs="Higher security/insurance fees.",
                action_plan=["Book convoy slot", "Increase onboard security protocol", "Update insurer with mitigation controls"],
            )
            add_mitigation(
                "safest_profile",
                "Switch Optimization to Safest Profile",
                "Reduce exposure by favoring safer legs and reliable ports.",
                "medium",
                risk_reduction=0.55,
                eta_days_change=1.3,
                cost_usd_change=18000,
                tradeoffs="Slightly slower ETA.",
                action_plan=["Re-plan route with safest profile", "Reconfirm ETA commitments", "Trigger customer advisories"],
            )

        elif scenario_id == "port_strike":
            target_port = impact.get("target_port") or (route.get("ports") or [None])[-1]
            add_mitigation(
                "alternate_port",
                "Shift to Alternate Gateway Port",
                f"Temporarily reroute calls from {target_port} to a nearby alternate hub.",
                "high",
                risk_reduction=0.8,
                eta_days_change=-0.6,
                cost_usd_change=22000,
                tradeoffs="Possible inland drayage uplift from alternate terminal.",
                action_plan=["Select nearest backup port", "Re-book berth and customs slots", "Issue revised inland transfer plan"],
            )
            add_mitigation(
                "buffer_inventory",
                "Build Buffer Inventory for Critical Orders",
                "Protect service continuity by buffering demand near destination markets.",
                "medium",
                risk_reduction=0.45,
                eta_days_change=0.0,
                cost_usd_change=15000,
                tradeoffs="Working-capital and storage overhead.",
                action_plan=["Identify top-priority SKUs", "Pre-position inventory at DC", "Activate exception replenishment cadence"],
            )

        # Common mitigations for every scenario.
        add_mitigation(
            "dynamic_alerting",
            "Enable 6-hour Dynamic Alerting",
            "Increase monitoring frequency to trigger faster operational responses.",
            "medium",
            risk_reduction=0.35,
            eta_days_change=0.0,
            cost_usd_change=4000,
            tradeoffs="More operational noise for teams.",
            action_plan=["Set alert threshold to risk >= 4", "Assign on-call owner", "Run daily mitigation stand-up"],
        )
        add_mitigation(
            "insurance_review",
            "Review War/Delay Insurance Coverage",
            "Reduce downside by adjusting policy clauses for current corridor conditions.",
            "medium",
            risk_reduction=0.25,
            eta_days_change=0.0,
            cost_usd_change=8000,
            tradeoffs="Short-term premium increase.",
            action_plan=["Audit current policy terms", "Request temporary endorsement", "Map claims workflow to operations"],
        )

        mitigations.sort(key=lambda m: ({"high": 3, "medium": 2, "low": 1}.get(m["priority"], 0), m["impact_score"]), reverse=True)
        return mitigations[:6]

    def _build_snapshot(self, route_analysis: Dict[str, Any]) -> Dict[str, Any]:
        summary = route_analysis.get("summary", {}) if isinstance(route_analysis.get("summary"), dict) else {}
        risk_score = self._safe_risk_score(route_analysis)
        return {
            "route": route_analysis.get("route"),
            "risk_score": round(risk_score, 2),
            "risk_level": self._risk_label_from_score(risk_score),
            "eta_days": round(float(route_analysis.get("estimated_time", summary.get("total_time_days", 0.0)) or 0.0), 2),
            "total_cost_usd": round(
                float(
                    ((route_analysis.get("cost_estimation") or {}).get("total_cost_usd"))
                    or summary.get("total_cost_usd", 0.0)
                    or 0.0
                ),
                2,
            ),
            "chokepoints": route_analysis.get("chokepoints", []) or [],
        }

    def simulate_what_if(
        self,
        ports: List[str],
        optimization: str = "balanced",
        scenario: str = "suez_closure",
        target_port: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a what-if simulation over a baseline route and return mitigation recommendations.
        """
        baseline = self.plan_multi_port_route(ports, optimization, include_alternatives=False)
        if "error" in baseline:
            return baseline

        simulated = copy.deepcopy(baseline)
        scenario_meta = self._get_scenario_meta(scenario)
        impact = self._apply_what_if_scenario(simulated, scenario_meta["id"], target_port)
        mitigations = self._recommended_mitigations(scenario_meta["id"], impact, simulated)

        baseline_snapshot = self._build_snapshot(baseline)
        simulated_snapshot = self._build_snapshot(simulated)

        deltas = {
            "risk_delta": round(simulated_snapshot["risk_score"] - baseline_snapshot["risk_score"], 2),
            "eta_delta_days": round(simulated_snapshot["eta_days"] - baseline_snapshot["eta_days"], 2),
            "cost_delta_usd": round(simulated_snapshot["total_cost_usd"] - baseline_snapshot["total_cost_usd"], 2),
        }

        return {
            "scenario": scenario_meta,
            "baseline": baseline_snapshot,
            "simulated": simulated_snapshot,
            "deltas": deltas,
            "recommended_mitigations": mitigations,
            "route_analysis": simulated,
            "impact_details": impact,
            "generated_at": datetime.utcnow().isoformat(),
        }
    
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

