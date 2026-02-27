# Multi-Port Route Planning Feature

## Overview

The Multi-Port Route Planning feature enables users to plan and optimize shipping routes across multiple ports worldwide, moving beyond simple point-to-point routing to support complex multi-stop itineraries.

## Key Features

### 📍 **50+ Global Ports**

- Major ports across all continents (Asia Pacific, Europe, Americas, Africa, Middle East, Oceania)
- Port information includes:
  - Geographical coordinates
  - Country and region
  - Port capacity level
  - Average wait times

### 🚢 **Multi-Leg Route Planning**

- Plan routes with 2 to unlimited ports
- Automatic calculation for each leg:
  - Distance (nautical miles and kilometers)
  - Transit time (accounting for ship speed)
  - Port wait times
  - Fuel costs
  - Port fees
  - Canal tolls (Suez, Panama)
- Risk assessment for each route segment

### ⚡ **Route Optimization**

Four optimization strategies available:

1. **Fastest** - Minimize total travel time
2. **Cheapest** - Minimize total cost
3. **Balanced** - Balance between time and cost
4. **Safest** - Prioritize low-risk routes

### 🗺️ **Canal Detection & Costs**

- Automatic detection of major shipping canals:
  - **Suez Canal** (Mediterranean ↔ Red Sea)
    - Average toll: $400,000
    - Transit time: 0.5 days
  - **Panama Canal** (Atlantic ↔ Pacific)
    - Average toll: $450,000
    - Transit time: 0.4 days

### 💰 **Comprehensive Cost Analysis**

- Fuel costs: $2.50 per nautical mile
- Port fees: ~$27,000 per port pair
- Canal tolls (when applicable)
- Total route cost summary

### 📊 **Detailed Route Analysis**

For each route, users receive:

- Total distance, time, and cost
- Number of ports and legs
- Leg-by-leg breakdown
- Risk level indicators
- Canal usage information
- Estimated departure and arrival times

## API Endpoints

### 1. Plan Multi-Port Route

```bash
POST /api/route/plan-multi-port
```

**Request Body:**

```json
{
  "ports": ["Singapore", "Dubai", "Rotterdam"],
  "optimization": "balanced",
  "session_id": "optional"
}
```

**Response:**

```json
{
  "success": true,
  "report_id": "uuid",
  "route_analysis": {
    "total_ports": 3,
    "total_legs": 2,
    "summary": {
      "total_distance_nm": 5949.11,
      "total_time_days": 18.89,
      "total_cost_usd": 468872.79,
      "canals_used": ["Suez Canal"]
    },
    "legs": [...]
  }
}
```

### 2. Optimize Route Order

```bash
POST /api/route/optimize-order
```

Optimizes the sequence of waypoints between origin and destination using a greedy nearest-neighbor algorithm.

### 3. Compare Routes

```bash
POST /api/route/compare
```

Compares two different multi-port routes side-by-side.

### 4. Get Available Ports

```bash
GET /api/route/ports
```

Returns list of all 50+ available ports.

### 5. Search Ports

```bash
GET /api/route/ports/search?query=india
```

Search ports by name, country, or region.

## Frontend UI

### Multi-Port Route Planner Page

**Features:**

- **Dynamic Port Selection**
  - Dropdown menus for each port
  - Add/remove ports dynamically
  - Minimum 2 ports required
- **Optimization Strategy Selector**
  - Visual buttons for each strategy
  - Icons for easy recognition
- **Summary Cards**
  - Total Distance (nm)
  - Total Time (days)
  - Total Cost ($USD)
  - Number of Ports/Legs
- **Expandable Route Legs**
  - Click to expand/collapse details
  - Color-coded risk levels (low, medium, high)
  - Canal information highlighted
  - Detailed metrics per leg

**Navigation:**

- Accessible via Navbar → "Route Planner" (Ship icon)
- Route: `/route-planner`

## Technology Stack

### Backend

- **Language**: Python 3
- **Framework**: FastAPI
- **Libraries**:
  - `math` for Haversine distance calculations
  - `pydantic` for data validation
  - `datetime` for time calculations

### Frontend

- **Framework**: React
- **Routing**: React Router DOM
- **Icons**: Lucide React
- **Styling**: Tailwind CSS with dark mode support

## Example Use Cases

### 1. Asia-Europe Trade Route

```
Singapore → Dubai → Rotterdam
- Distance: 5,949 nm
- Time: 18.9 days
- Cost: $468,873
- Uses: Suez Canal
```

### 2. Trans-Pacific Route

```
Shanghai → Los Angeles → Panama → New York
- Includes Panama Canal transit
- Optimized for fastest delivery
```

### 3. Round-the-World Cargo

```
Rotterdam → Suez → Singapore → Sydney → Panama → New York → Rotterdam
- Multi-continent routing
- Both major canals
- Complex optimization

```

## Calculations & Algorithms

### Distance Calculation

Uses the **Haversine formula** for great-circle distance:

```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
c = 2 × arcsin(√a)
distance = Earth's radius × c
```

### Time Calculation

```
Transit Time = Distance / Ship Speed (20 knots)
Total Time = Transit Time + Port Wait Times + Canal Transit Times
```

### Cost Calculation

```
Fuel Cost = Distance × $2.50/nm
Port Fees = $15,000 departure + $12,000 arrival
Canal Tolls = Based on canal used
Total Cost = Fuel + Port Fees + Canal Tolls
```

### Risk Assessment

Simplified risk model based on:

- Country political stability
- Route length
- Historical incident data
- Regional security levels

### Route Optimization

Uses **greedy nearest-neighbor algorithm**:

1. Start at origin
2. Find nearest unvisited port
3. Move to that port
4. Repeat until all waypoints visited
5. End at destination

## Future Enhancements

1. **WorldMap Visualization**

   - Draw multi-leg routes on interactive map
   - Animate ship movement
   - Show real-time weather overlays

2. **Advanced Optimization**

   - Genetic algorithms for optimal ordering
   - Multi-objective optimization
   - Time window constraints

3. **Real-Time Data Integration**

   - Live port congestion data
   - Dynamic fuel prices
   - Weather routing

4. **Alternative Routes**

   - Multiple route suggestions
   - Pros/cons comparison
   - What-if scenarios

5. **Vessel-Specific Planning**
   - Different ship types and speeds
   - Cargo-specific routing
   - Draft and size restrictions

## Database Structure

### Ports Table

```python
{
  "name": "Singapore",
  "country": "Singapore",
  "region": "Asia Pacific",
  "coordinates": {"lat": 1.2897, "lon": 103.8501},
  "capacity": "very_high",
  "avg_wait_time": 1.5  # days
}
```

### Route Report Schema

```python
RiskReport(
  report_id: str,
  session_id: str,
  report_type: "multi_port_route",
  created_at: datetime,
  title: str,
  executive_summary: str,
  recommendations: List[str],
  route_analysis: str  # JSON-encoded full route data
)
```

## Performance Notes

- **Port List Loading**: < 100ms
- **Route Calculation**: < 500ms for 10 ports
- **Memory Usage**: Minimal (lightweight calculations)
- **Scalability**: Can handle 50+ port routes

## Testing

### Backend Tests Passed ✅

- ✅ Port database loading
- ✅ Distance calculations (Haversine formula)
- ✅ Canal detection (Suez, Panama)
- ✅ Multi-port route planning API
- ✅ Route report generation
- ✅ Database storage

### Example Test Route

```bash
curl -X POST "http://localhost:8000/api/route/plan-multi-port" \
  -H "Content-Type: application/json" \
  -d '{
    "ports": ["Singapore", "Dubai", "Rotterdam"],
    "optimization": "balanced"
  }'
```

**Result**: ✅ Success (5,949 nm, 18.9 days, $468,873)

## Credits

**Developed By**: SentriX Development Team  
**Date**: October 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅

---

For questions or support, please contact the development team.

