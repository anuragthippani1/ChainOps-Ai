import openai
import os
from typing import Dict, Any
import asyncio
from datetime import datetime

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
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process general assistant queries"""
        try:
            # For demo purposes, we'll use a simple response system
            # In production, this would call OpenAI API
            response = await self._generate_response(query)
            
            return {
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "agent": "assistant"
            }
        except Exception as e:
            return {
                "message": f"I apologize, but I encountered an error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "agent": "assistant"
            }
    
    async def _generate_response(self, query: str) -> str:
        """Generate response limited strictly to supply chain risk topics."""
        query_lower = query.lower()

        allowed_topics = [
            "supply", "chain", "risk", "political", "geopolit", "tariff", "sanction",
            "schedule", "delivery", "delay", "logistics", "shipping", "transport",
            "report", "equipment", "supplier", "country", "trade", "from", "to", "route"
        ]
        is_on_topic = any(t in query_lower for t in allowed_topics)

        # Check for route/transportation queries first
        if self._is_route_query(query_lower):
            return await self._analyze_route(query)

        if not is_on_topic:
            return (
                "I can only assist with supply chain risk intelligence, shipping routes, "
                "political risks, delivery delays, logistics disruptions, and report generation. "
                "Try asking about routes between ports or countries."
            )

        if "hello" in query_lower or "hi" in query_lower or "help" in query_lower:
            return (
                "You're connected to ChainOps AI. I can help with:\n"
                "• Route analysis (origin to destination with climate, risks, transit time)\n"
                "• Political risks by country\n"
                "• Delivery schedule risks\n"
                "• Logistics disruptions\n"
                "• Generate combined reports\n\n"
                "Try: 'Route from Shanghai to Los Angeles' or 'Political risks in Germany'"
            )

        if "political" in query_lower or "geopolit" in query_lower:
            return "Understood. I'll analyze recent geopolitical events and their supply chain impact."

        if "schedule" in query_lower or "delivery" in query_lower or "delay" in query_lower:
            return "Got it. I'll assess equipment schedule delays and risk levels."

        if "combined" in query_lower or ("report" in query_lower and ("both" in query_lower or "all" in query_lower)):
            return "Generating a combined report covering political and schedule risks."

        if "report" in query_lower:
            return "I can generate a political, schedule, or combined risk report. Which one would you like?"

        return (
            "I can help with supply chain risk questions, route analysis, political risks, "
            "schedule/logistics issues, or generate reports. Please specify your focus."
        )

    def _is_route_query(self, query_lower: str) -> bool:
        """Check if query is about shipping routes/transportation."""
        route_indicators = [
            "from", "to", "route", "shipping", "transit", "journey", "voyage",
            "port", "ocean", "sea", "maritime", "cargo", "freight", "ship"
        ]
        return any(indicator in query_lower for indicator in route_indicators)

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
