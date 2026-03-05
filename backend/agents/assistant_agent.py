import openai
import os
import re
from typing import Dict, Any, Optional, List, Tuple
import asyncio
from datetime import datetime
from data.ports import get_port_by_name

COUNTRY_MAJOR_PORTS = {
    "germany": "Hamburg",
    "netherlands": "Rotterdam",
    "china": "Shanghai",
    "india": "Mumbai",
    "singapore": "Singapore",
    "uae": "Dubai",
    "united arab emirates": "Dubai",
    "japan": "Yokohama",
    "south korea": "Busan",
    "usa": "Los Angeles",
    "united states": "Los Angeles",
    "uk": "Felixstowe",
    "united kingdom": "Felixstowe",
}

COUNTRY_QUERY_ALIASES = {
    "united states of america": "united states",
    "u.s.": "usa",
    "u.s.a": "usa",
    "us": "usa",
    "u.k.": "uk",
    "great britain": "united kingdom",
    "korea": "south korea",
}

class AssistantAgent:
    def __init__(self):
        # Initialize OpenAI client (using free tier)
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-key-here")
        )
        self.system_prompt = """
        You are ChainOps AI, an AI assistant specialized in supply chain risk intelligence. 
        You help users understand and analyze supply chain risks including:
        - Political and geopolitical risks
        - Schedule delays and delivery risks
        - Tariff changes and trade policies
        - Logistics disruptions
        
        Always provide helpful, accurate information and guide users to use the appropriate 
        features for their queries. Be concise but informative.
        """

    def _contains_any(self, text: str, keywords: List[str]) -> bool:
        return any(keyword in text for keyword in keywords)

    def _normalize_location_key(self, location: str) -> str:
        cleaned = re.sub(r"[^\w\s\-']", " ", (location or "").lower())
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if cleaned.startswith("the "):
            cleaned = cleaned[4:]
        return COUNTRY_QUERY_ALIASES.get(cleaned, cleaned)

    def _display_location_name(self, normalized_location: str) -> str:
        if normalized_location == "usa":
            return "United States"
        if normalized_location == "uk":
            return "United Kingdom"
        if normalized_location == "uae":
            return "UAE"
        return " ".join(part.capitalize() for part in normalized_location.split())

    def _extract_route_points_from_query(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        q = (query or "").strip()
        patterns = [
            r"\bfrom\s+(.+?)\s+(?:to|->|→)\s+(.+?)(?:\s+with\b|\s+priority\b|\s*\(|$)",
            r"\broute\s+(.+?)\s+(?:to|->|→)\s+(.+?)(?:\s+with\b|\s+priority\b|\s*\(|$)",
            r"^\s*([a-zA-Z][a-zA-Z\s\.\-']+?)\s*(?:to|->|→)\s+([a-zA-Z][a-zA-Z\s\.\-']+?)\s*$",
        ]
        for pattern in patterns:
            m = re.search(pattern, q, flags=re.I)
            if not m:
                continue
            origin = (m.group(1) or "").strip(" ,.;:!?")
            destination = (m.group(2) or "").strip(" ,.;:!?")
            if origin and destination:
                return origin, destination
        return None, None

    def resolve_ports_from_query(self, query: str) -> Dict[str, Any]:
        """Resolve route endpoints from query text to known major ports when countries are provided."""
        origin_raw, destination_raw = self._extract_route_points_from_query(query)
        result: Dict[str, Any] = {
            "origin_input": origin_raw,
            "destination_input": destination_raw,
            "origin_port": None,
            "destination_port": None,
            "origin_country": None,
            "destination_country": None,
            "origin_resolved_from_country": False,
            "destination_resolved_from_country": False,
            "success": False,
        }
        if not origin_raw or not destination_raw:
            return result

        def resolve_one(raw_value: str):
            port_obj = get_port_by_name(raw_value)
            if port_obj and port_obj.get("name"):
                return port_obj["name"], None, False

            normalized = self._normalize_location_key(raw_value)
            mapped_port = COUNTRY_MAJOR_PORTS.get(normalized)
            if mapped_port:
                return mapped_port, self._display_location_name(normalized), True

            return None, None, False

        origin_port, origin_country, origin_from_country = resolve_one(origin_raw)
        destination_port, destination_country, destination_from_country = resolve_one(destination_raw)

        result.update(
            {
                "origin_port": origin_port,
                "destination_port": destination_port,
                "origin_country": origin_country,
                "destination_country": destination_country,
                "origin_resolved_from_country": origin_from_country,
                "destination_resolved_from_country": destination_from_country,
                "success": bool(origin_port and destination_port),
            }
        )
        return result

    def _build_contextual_intelligence(self, context: Optional[Dict[str, Any]]) -> str:
        if not context:
            return ""

        notes: List[str] = []
        disruption = context.get("disruption_summary") if isinstance(context, dict) else None
        if isinstance(disruption, dict):
            count = disruption.get("disruption_count", 0)
            impact = disruption.get("estimated_impact")
            if count:
                notes.append(f"Live disruption monitor: {count} active alert(s), estimated impact {impact}.")

        political = context.get("political_summary") if isinstance(context, dict) else None
        if isinstance(political, dict):
            high = political.get("high_risk_count")
            countries = political.get("countries_analyzed")
            if high is not None and countries is not None:
                notes.append(f"Political monitor: {high} high-risk country signals out of {countries} analyzed.")

        schedule = context.get("schedule_summary") if isinstance(context, dict) else None
        if isinstance(schedule, dict):
            delays = schedule.get("high_delay_routes")
            avg_delay = schedule.get("average_delay_days")
            if delays:
                notes.append(f"Schedule monitor: {delays} high-delay route(s), avg delay {avg_delay} day(s).")

        route_error = context.get("route_error") if isinstance(context, dict) else None
        if route_error:
            notes.append(
                "I could not compute an exact lane with current place names; try major origin and destination ports "
                "for route-grade ETA/cost output."
            )

        if not notes:
            return ""
        return "\n\nCurrent intelligence snapshot: " + " ".join(notes)

    def generate_logistics_explanation(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        q = (query or "").lower().strip()
        if not q:
            return None

        context_note = self._build_contextual_intelligence(context)

        if self._contains_any(q, ["causes of delays", "cause of delays", "shipment delay", "cargo delay", "why is my shipment delayed"]):
            return (
                "Common causes of global shipment delays include port congestion, customs inspections, extreme weather events, "
                "labor strikes, geopolitical tensions, vessel capacity shortages, and inland trucking bottlenecks."
                + context_note
            )

        if self._contains_any(
            q,
            [
                "documents required",
                "documents are required",
                "required for international shipping",
                "shipping documents",
                "international shipping documents",
                "bill of lading",
                "customs declaration",
            ],
        ):
            return (
                "Typical international shipping documents include the Bill of Lading, Commercial Invoice, Packing List, "
                "Certificate of Origin, and Customs Declaration. Depending on cargo type, you may also need "
                "inspection certificates, MSDS, insurance documents, and import permits."
            )

        if self._contains_any(q, ["customs clearance", "customs delay", "customs processing", "how long customs"]):
            return (
                "Customs clearance depends on documentation quality, HS code accuracy, duties/tax payment, and inspection rates. "
                "Delays usually happen when paperwork is incomplete, commodity classification is incorrect, or random inspections increase."
                + context_note
            )

        if self._contains_any(q, ["air vs sea", "air freight vs sea freight", "air freight or sea freight", "difference between air and sea"]):
            return (
                "Air freight is faster but significantly more expensive and capacity-constrained. "
                "Sea freight is slower but cost-efficient for heavy or high-volume cargo. "
                "Use air for urgent/high-value SKUs and sea for stable-demand bulk replenishment."
            )

        if self._contains_any(q, ["suez canal", "hormuz", "malacca", "bab el-mandeb", "panama canal", "chokepoint"]):
            return (
                "Major maritime chokepoints carry concentrated risk. The Suez corridor can face Red Sea security incidents, "
                "canal blockages, queue congestion, and rerouting pressure around the Cape of Good Hope. "
                "Risk controls include dynamic rerouting triggers, buffer inventory, and security-adjusted transit planning."
                + context_note
            )

        if self._contains_any(q, ["port strike", "labor strike", "port congestion", "terminal congestion", "blockade"]):
            return (
                "Port strikes and congestion reduce berth productivity, increase dwell time, and cause cascading delays downstream. "
                "Mitigation includes pre-booking alternative ports, splitting bookings across carriers, and activating intermodal fallbacks."
                + context_note
            )

        if self._contains_any(q, ["weather impact", "storm", "typhoon", "hurricane", "cyclone", "weather disruption"]):
            if "taiwan" in q and ("semiconductor" in q or "chip" in q):
                return (
                    "A typhoon near Taiwan can delay semiconductor exports because many chip supply chains depend on Taiwanese ports and airports. "
                    "Likely impacts include terminal shutdowns, canceled sailings/flights, delayed feeder services, and longer lead times "
                    "for electronics manufacturers globally."
                    + context_note
                )
            return (
                "Severe weather disrupts schedules through port closures, reduced vessel speed, route deviations, and missed transshipment windows. "
                "Best practice is to combine weather forecasts with dynamic ETA risk scoring and contingency port options."
                + context_note
            )

        if self._contains_any(q, ["geopolitical risk", "geopolitical disruptions", "middle east risk", "risks affect shipments to the middle east"]):
            return (
                "Shipment risk in geopolitically sensitive corridors is driven by sanctions exposure, conflict spillover, "
                "insurance surcharges, and chokepoint volatility (especially Suez/Red Sea and Hormuz-linked lanes). "
                "Use country risk scoring plus route security monitoring before dispatch."
                + context_note
            )

        if self._contains_any(q, ["fastest route", "quickest route", "shortest transit", "best route"]):
            return (
                "The fastest route usually prioritizes transit time over cost, favoring direct services, minimal transshipment, "
                "and low-congestion gateways. For precise planning, provide origin and destination ports to compute lane-specific ETAs and risk."
                + context_note
            )

        if self._contains_any(q, ["cheapest route", "lowest cost route", "reduce shipping cost", "route alternatives", "alternative routes"]):
            return (
                "The cheapest route typically balances ocean freight rates, fuel consumption, canal toll exposure, and port fees. "
                "Alternative routing through lower-congestion hubs can reduce total landed cost when delay penalties are high."
                + context_note
            )

        if self._contains_any(q, ["fuel prices rise", "fuel prices increase", "bunker price rise"]):
            return (
                "If fuel prices rise globally, ocean and air freight rates usually increase via bunker adjustment factors and fuel surcharges. "
                "Long-haul lanes, low-margin products, and expedited modes face the largest cost impact."
            )

        if self._contains_any(q, ["should shipments be rerouted", "should we reroute", "rerouted if port congestion"]):
            return (
                "Yes. When congestion risk is high, AI-driven rerouting to alternative ports or multimodal corridors can reduce total delay exposure. "
                "Reroute decisions should compare additional transit cost against probable delay penalties and service-level commitments."
                + context_note
            )

        if self._contains_any(q, ["how can ai predict supply chain disruptions", "ai predict disruptions", "ai prediction", "disruption detection"]):
            return (
                "AI predicts disruptions by combining news signals, weather feeds, port congestion metrics, vessel movement patterns, "
                "and geopolitical indicators. Models score lane-level risk and trigger early alerts for procurement, routing, and inventory actions."
                + context_note
            )

        if self._contains_any(q, ["reduce supply chain risk", "mitigate supply chain risk", "risk reduction strategy"]):
            return (
                "To reduce supply chain risk, diversify suppliers geographically, maintain safety stock for critical items, "
                "define alternate route playbooks, monitor political/disruption signals continuously, and run weekly risk reviews for key lanes."
                + context_note
            )

        return None
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process general assistant queries"""
        try:
            # For demo purposes, we'll use a simple response system
            # In production, this would call OpenAI API
            response = await self._generate_response(query, context=context)
            
            return {
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "agent": "assistant"
            }
        except Exception as e:
            return {
                "message": "I'm here to help with shipping routes, supply chain risks, cargo delays, and logistics optimization. Could you clarify your question?",
                "timestamp": datetime.now().isoformat(),
                "agent": "assistant"
            }
    
    async def _generate_response(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response limited strictly to supply chain risk topics."""
        query_lower = query.lower()
        context = context or {}

        allowed_topics = [
            "supply", "chain", "risk", "political", "geopolit", "tariff", "sanction",
            "schedule", "delivery", "delay", "logistics", "shipping", "transport",
            "report", "equipment", "supplier", "country", "trade", "from", "to", "route",
            "customs", "document", "freight", "air", "sea", "port", "congestion",
            "weather", "typhoon", "hurricane", "chokepoint", "canal", "fuel", "cost", "optimiz", "ai",
        ]
        is_on_topic = any(t in query_lower for t in allowed_topics)

        # Route analysis from assistant is optional and only used when explicitly enabled.
        if context.get("allow_mock_route_analysis") and self._is_route_query(query_lower):
            return await self._analyze_route(query)

        knowledge_response = self.generate_logistics_explanation(query, context=context)
        if knowledge_response:
            return knowledge_response

        if not is_on_topic:
            return "I'm here to help with shipping routes, supply chain risks, cargo delays, and logistics optimization. Could you clarify your question?"

        if re.search(r"\b(hello|hi|help)\b", query_lower):
            return (
                "You're connected to ChainOps AI. I can help with:\n"
                "• Route analysis (origin to destination with climate, risks, transit time)\n"
                "• Political risks by country\n"
                "• Delivery schedule risks\n"
                "• Logistics disruptions\n"
                "• Generate combined reports\n\n"
                "Try: 'Route from Shanghai to Los Angeles' or 'Political risks in Germany'"
            )

        if "shipping cost" in query_lower or "shipping costs" in query_lower or "what affects shipping costs" in query_lower:
            return (
                "Shipping costs are influenced by fuel prices, canal tolls, port congestion, "
                "cargo weight/volume, vessel speed, insurance premiums, and geopolitical risk exposure. "
                "Operationally, route length, weather deviations, and security surcharges also impact final cost."
            )

        if "disruption" in query_lower or "congestion" in query_lower or "strike" in query_lower or "blockade" in query_lower:
            return (
                "Major disruption drivers include port congestion, labor strikes, canal or chokepoint incidents, "
                "customs bottlenecks, weather shocks, and geopolitical tensions. "
                "You can ask for a live disruption summary by region, port, or route."
            )

        if "delay" in query_lower or "cargo delay" in query_lower or "delivery delay" in query_lower:
            return (
                "Cargo delays typically come from port queuing, customs clearance lag, equipment shortages, "
                "weather rerouting, and supplier-side production slippage. "
                "To reduce delays, prioritize high-risk lanes, pre-book port slots, and monitor route risk daily."
            )

        if "political" in query_lower or "geopolit" in query_lower:
            return "Understood. I'll analyze recent geopolitical events and their supply chain impact."

        if "schedule" in query_lower or "delivery" in query_lower or "delay" in query_lower:
            return "Got it. I'll assess equipment schedule delays and risk levels."

        if "risk" in query_lower and ("reduce" in query_lower or "mitigate" in query_lower):
            return (
                "To reduce supply chain risk: diversify suppliers across regions, maintain safety stock on critical SKUs, "
                "set alternate routing playbooks, monitor political/disruption signals continuously, "
                "and run weekly risk reviews on high-value lanes."
            )

        if "logistics recommendation" in query_lower or "recommendation" in query_lower or "optimiz" in query_lower:
            return (
                "For logistics optimization: use balanced route planning by default, switch to safest mode for unstable corridors, "
                "combine disruption alerts with political risk scores, and review cost-vs-risk tradeoffs before dispatch."
            )

        if "combined" in query_lower or ("report" in query_lower and ("both" in query_lower or "all" in query_lower)):
            return "Generating a combined report covering political and schedule risks."

        if "report" in query_lower:
            return "I can generate a political, schedule, or combined risk report. Which one would you like?"

        return "I'm here to help with shipping routes, supply chain risks, cargo delays, and logistics optimization. Could you clarify your question?"

    def _is_route_query(self, query_lower: str) -> bool:
        """Check if query is about shipping routes/transportation."""
        route_patterns = [
            r"\broute\b",
            r"\bfrom\b.+\bto\b",
            r"\bshipping route\b",
            r"\btransit\b",
            r"\bjourney\b",
            r"\bvoyage\b",
            r"\bport\b",
            r"\bocean\b",
            r"\bsea\b",
            r"\bmaritime\b",
            r"\bcargo route\b",
            r"\bfreight route\b",
            r"^\s*[a-z][a-z\s\.\-']+\s+(?:to|->|→)\s+[a-z][a-z\s\.\-']+\s*$",
        ]
        return any(re.search(pattern, query_lower) for pattern in route_patterns)

    async def _analyze_route(self, query: str) -> str:
        """Analyze shipping route with detailed real-time projections and comprehensive information."""
        # Extract origin and destination (simplified)
        words = query.lower().split()
        origin = None
        destination = None
        
        # Look for "from X to Y" pattern
        if "from" in words and "to" in words:
            from_idx = words.index("from")
            to_idx = words.index("to")
            if from_idx < to_idx and to_idx < len(words):
                origin = " ".join(words[from_idx+1:to_idx])
                destination = " ".join(words[to_idx+1:])
        
        if not origin or not destination:
            return "Please specify origin and destination. Example: 'Route from Shanghai to Los Angeles'"

        # Mock detailed analysis (in production, integrate with real shipping APIs)
        current_time = datetime.now()
        
        analysis = f"""
🚢 **COMPREHENSIVE ROUTE ANALYSIS**
**{origin.title()} → {destination.title()}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📍 ROUTE OVERVIEW
• **Total Distance**: 5,794 nautical miles (10,730 km)
• **Total Duration**: 12-15 days (288-360 hours)
• **Average Speed**: 20 knots (37 km/h)
• **Route Type**: Trans-Pacific Great Circle
• **Departure Time**: {current_time.strftime('%B %d, %Y %H:%M UTC')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ⏰ REAL-TIME PROJECTIONS

### **Next 12 Hours**:
• **Distance Covered**: 240 nautical miles (444 km)
• **Current Position**: Approx. 200 km east of {origin.title()}
• **Speed**: 20 knots steady
• **Weather**: Clear skies, moderate winds (15-20 knots)
• **Next Waypoint**: Point Alpha (480 nm from origin)
• **ETA to Next Waypoint**: {(current_time.hour + 24) % 24}:00 UTC tomorrow

### **Next 24 Hours**:
• **Distance Covered**: 480 nautical miles (888 km)
• **Position**: Mid North Pacific (30% of journey)
• **Fuel Consumption**: ~18 tons (65% remaining)
• **Crew Status**: All systems normal

### **Next 48 Hours**:
• **Distance Covered**: 960 nautical miles (1,778 km)
• **Position**: Crossing International Date Line
• **Expected Conditions**: Moderate seas, 2-3m waves

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🗺️ DETAILED WAYPOINTS & TIMELINE

**Waypoint 1: Departure Port** ({origin.title()})
├─ Time: Day 0, 00:00
├─ Distance: 0 nm
├─ Action: Cargo loading, customs clearance
└─ Status: ✅ Completed

**Waypoint 2: Open Waters** (East China Sea)
├─ Time: Day 1, 12:00
├─ Distance: 300 nm from origin
├─ ETA: 15 hours from now
├─ Weather: Clear, winds 10-15 knots
└─ Action: Full speed ahead

**Waypoint 3: North Pacific** (Mid-Ocean)
├─ Time: Day 5, 18:00
├─ Distance: 2,400 nm from origin (41% complete)
├─ ETA: 5 days from now
├─ Weather: Moderate seas, possible squalls
├─ Risk: Medium weather risk
└─ Action: Monitor storm systems

**Waypoint 4: International Date Line**
├─ Time: Day 7, 06:00
├─ Distance: 3,500 nm from origin (60% complete)
├─ ETA: 7 days from now
├─ Weather: Improving conditions
└─ Action: Time zone adjustment

**Waypoint 5: Eastern Pacific**
├─ Time: Day 10, 12:00
├─ Distance: 5,000 nm from origin (86% complete)
├─ ETA: 10 days from now
├─ Weather: Calm seas expected
├─ Action: Prepare for port arrival
└─ Status: Coast guard notification required

**Waypoint 6: Arrival Port** ({destination.title()})
├─ Time: Day 12-15, Variable
├─ Distance: 5,794 nm (100% complete)
├─ ETA: 12-15 days from now
├─ Action: Port clearance, cargo unloading
└─ Status: ⏳ Pending arrival

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🌊 OCEAN & CLIMATE CONDITIONS

**Current Conditions**:
• Sea State: 2-3 (Smooth to slight)
• Wave Height: 0.5-1.25 meters
• Wind Speed: 10-15 knots from NW
• Visibility: Excellent (>10 nm)
• Water Temperature: 18°C (64°F)
• Air Temperature: 20°C (68°F)

**Forecast (Next 7 Days)**:
• **Days 1-3**: Calm seas, favorable conditions
• **Days 4-6**: Moderate winds, possible rain squalls
• **Days 7-9**: Improving, clear skies expected
• **Days 10-12**: Excellent conditions for arrival

**Seasonal Considerations**:
• Current Season: Moderate (Best for navigation)
• Typhoon/Hurricane Season: Low risk (outside peak season)
• El Niño/La Niña: Neutral conditions
• Recommended Departure Window: ✅ Optimal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ⚠️ COMPREHENSIVE RISK ASSESSMENT

**Political & Geopolitical Risks**: 🟢 Low (1/5)
• No active conflicts in transit zones
• Stable diplomatic relations
• No trade embargoes affecting route
• Coast guard cooperation: Excellent
• Customs clearance: Standard procedures

**Weather & Climate Risks**: 🟡 Medium (3/5)
• Winter storm potential: Moderate
• Seasonal patterns: Favorable
• Historical data: 95% on-time arrival
• Recommended action: Monitor forecasts daily
• Contingency: Alternative routing available

**Maritime Security Risks**: 🟢 Low (1/5)
• Piracy Risk: Negligible (well-patrolled)
• Terrorism Risk: Very low
• Illegal fishing: Minimal interference
• Security level: ISPS Code Level 1
• Naval presence: Regular patrols

**Port & Infrastructure Risks**: 🟡 Medium (3/5)
• Origin Port Congestion: Low (2-3 day wait)
• Destination Port Congestion: Medium (4-7 day wait)
• Equipment Availability: Good
• Labor Disputes: None reported
• Customs Delays: Possible (1-2 days)

**Operational Risks**: 🟢 Low (2/5)
• Vessel Reliability: 98% uptime
• Crew Experience: Highly qualified
• Fuel Availability: Adequate reserves
• Mechanical Issues: Routine maintenance current
• Communication: Satellite systems operational

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ⏱️ DETAILED TIMING BREAKDOWN

**Pre-Departure** (Days -1 to 0):
├─ Cargo Loading: 12-18 hours
├─ Customs Clearance: 4-6 hours
├─ Vessel Preparation: 6-8 hours
├─ Crew Briefing: 2 hours
└─ Final Checks: 2 hours

**Transit Phase** (Days 1-12):
├─ Open Ocean Navigation: 10-13 days
├─ Weather Delays (potential): 0-2 days
├─ Route Deviations (if needed): 0-1 days
└─ Emergency Stops: 0 days (none anticipated)

**Arrival Phase** (Days 12-15):
├─ Port Approach: 4-6 hours
├─ Pilot Boarding: 2 hours
├─ Docking: 2-3 hours
├─ Customs Inspection: 6-12 hours
├─ Cargo Unloading: 18-24 hours
└─ Final Clearance: 4-6 hours

**Total Timeline**: 12-15 days door-to-door

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🛡️ SAFETY & MITIGATION STRATEGIES

**Mandatory Protocols**:
✅ 24/7 weather monitoring via satellite
✅ Regular position reporting every 6 hours
✅ Coast guard communication protocols active
✅ Emergency response team on standby
✅ Life-saving equipment inspected
✅ Fire suppression systems tested
✅ Navigation systems redundancy verified

**Risk Mitigation**:
• **Weather Delays**: Alternative routes pre-planned
• **Port Congestion**: Booking flexibility arrangements
• **Mechanical Issues**: Spare parts inventory onboard
• **Medical Emergencies**: Ship doctor + telemedicine
• **Security Threats**: Armed security if needed
• **Communication Loss**: Backup satellite systems

**Recommended Actions**:
1. **Daily**: Check weather updates, monitor vessel position
2. **Every 6 hours**: Report position to fleet management
3. **Every 12 hours**: Review route optimization
4. **Weekly**: Comprehensive systems check
5. **Before arrival**: Pre-clear customs documentation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 💰 COST & LOGISTICS ESTIMATES

**Fuel Costs**: ~$85,000 (280 tons @ $300/ton)
**Port Fees**: ~$15,000 (origin + destination)
**Canal Fees**: N/A (direct route)
**Insurance**: ~$12,000 (cargo + hull)
**Crew Wages**: ~$18,000 (12-day voyage)
**Miscellaneous**: ~$5,000
**Total Estimated Cost**: ~$135,000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📊 FINAL RECOMMENDATION

**Route Status**: ✅ **APPROVED - OPTIMAL CONDITIONS**

**Confidence Level**: 92% (High)

**Key Strengths**:
✓ Favorable weather forecast
✓ Low security risks
✓ Experienced crew and vessel
✓ Optimal seasonal timing
✓ Well-established route

**Key Concerns**:
⚠ Potential port congestion at destination
⚠ Moderate weather risk in mid-Pacific
⚠ Standard customs delay possible

**Overall Assessment**: This route is highly recommended for immediate departure. All conditions are favorable, and risks are within acceptable parameters. Estimated arrival window: 12-15 days with 95% confidence.

**Next Steps**:
1. Confirm final cargo manifest
2. File departure notice with authorities
3. Activate real-time tracking systems
4. Brief crew on route specifics
5. Monitor weather daily

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 *Report generated by ChainOps AI Intelligence Platform*
🕒 *Analysis timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""

        return analysis
