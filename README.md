<div align="center">
  <img src="frontend/public/logo.png" alt="ChainOps AI Logo" width="200"/>
</div>

# ChainOps AI

ChainOps AI aggregates political risks, supply chain disruptions, chokepoint status, and route analyses so **ship captains**, **shipping operators**, and **cargo logistics managers** can make fast decisions without manually checking multiple systems. Monitor global shipping risks, get route intelligence, and receive critical alerts in one place.

---

## Core Features

- **Global Maritime Intelligence Snapshot** – Interactive ECDIS-style world map with layers:
  - **Weather** – Marine weather events (OpenWeather or disruption-based fallback)
  - **Risk Zones** – Dynamic zones from political risks, disruptions, and critical alerts
  - **Port Intelligence** – Global ports with congestion levels and ships waiting
  - **Vessel Tracking** – AIS sample data or live feed (when configured)
  - **Disruptions** – Critical alerts mapped by location
  - **Risk Snapshot** – Country-level risk markers
- **Strategic Chokepoints** – Suez Canal, Strait of Hormuz, Bab el-Mandeb, Strait of Malacca, Panama Canal, Taiwan Strait, Gibraltar, English Channel, Bosphorus, Sunda Strait, Lombok Strait
- **AI Assistant** – Natural language queries for route analysis and risk intelligence
- **Multi-Port Route Planner** – Plan routes with risk assessment and optimization
- **Dashboard** – World risk heatmap, political risk analysis, disruption alerts
- **Reports** – Generate and download PDF risk reports
- **Session Manager** – Organize sessions and reports

---

## Tech Stack

| Layer      | Technology                          |
|-----------|--------------------------------------|
| Frontend  | React, Tailwind CSS, react-simple-maps |
| Backend   | FastAPI (Python)                     |
| Database  | MongoDB (Atlas or local)             |
| News APIs | NewsAPI, Mediastack, GNews           |
| Weather   | OpenWeather (marine weather)         |
| Reporting | python-docx, reportlab               |

---

## Quick Start

### Prerequisites

- Node.js 16+ and npm  
- Python 3.8+  
- MongoDB (local or Atlas free tier)

### Installation

```bash
git clone https://github.com/anuragthippani1/ChainOps-Ai.git
cd ChainOps-Ai
npm run install-all
```

### Environment Variables

Copy the example env and add your keys:

```bash
cd backend
cp env.example .env
```

Add to `backend/.env`:

```env
# News (supply chain disruptions, political risks)
NEWSAPI_KEY=
MEDIASTACK_API_KEY=
GNEWS_API_KEY=
NEWSDATA_API_KEY=

# Marine weather (optional; falls back to disruption-based events)
OPENWEATHER_API_KEY=

# MongoDB (optional; uses file fallback)
MONGODB_URI=mongodb://localhost:27017/chainops_ai

# OpenAI (optional; for AI summaries)
OPENAI_API_KEY=
```

For the frontend (production), set `REACT_APP_API_URL` to your backend URL.

### Run Locally

```bash
npm run dev
```

- **Frontend:** http://localhost:3000  
- **Backend:** http://127.0.0.1:8000  

---

## Backend APIs

| Endpoint                   | Description                                |
|---------------------------|--------------------------------------------|
| `/api/shipping-intelligence` | Maritime metrics, chokepoints, alerts   |
| `/api/dashboard`          | World risk data, political risks           |
| `/api/weather`            | Marine weather events                      |
| `/api/risk-zones`         | Dynamic risk zones from intelligence       |
| `/api/ports`              | Port intelligence (congestion, ships)      |
| `/api/vessels`            | Vessel positions (AIS sample or live)      |
| `/api/query`              | AI assistant queries                       |
| `/api/route/plan-multi-port` | Multi-port route planning               |
| `/api/reports`            | Generated reports                          |

---

## Deployment

### Backend (Render – Web Service)

- **Root Directory:** `backend`  
- **Build Command:** `pip install -r requirements.txt`  
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`  
- Add env vars in Render (MongoDB, API keys, etc.)

### Frontend (Render Static Site or Vercel)

- **Root Directory:** `frontend`  
- **Build Command:** `npm install && npm run build`  
- **Publish Directory:** `build`  
- Set `REACT_APP_API_URL` to your backend URL (e.g. `https://your-backend.onrender.com`)

---

## Project Structure

```
chainops-ai/
├── frontend/           # React app
│   └── src/
│       ├── components/ # Home, Dashboard, GlobalShippingMap, etc.
│       ├── context/    # DashboardContext
│       └── config.js   # API URL
├── backend/            # FastAPI app
│   ├── main.py         # API routes
│   ├── agents/         # Assistant, Political Risk, Route Planner, etc.
│   ├── data/           # Ports, AIS sample, logistics regions
│   └── services/       # News fetching, NLP
└── README.md
```

---

## Thinking Logs (Developer)

Thinking Logs are available for debugging and demos:

- Direct URL: `/thinking-logs`  
- Enable in nav: set `chainops-ai-developer-mode=true` in localStorage, or add `?dev=1` to the URL

---

## License

MIT License – see LICENSE for details.
