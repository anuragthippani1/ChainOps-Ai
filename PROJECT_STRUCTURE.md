# ChainOps AI – Project Structure & Architecture

**For project review – file responsibilities and how they connect**
 
---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                                 │
│  App.js → Routes → Pages (Home, Dashboard, Assistant, Reports, etc.)     │
│                    ↓                                                     │
│  DashboardContext (shared state, API calls via config.API_URL)           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP (axios)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                                │
│  main.py → API endpoints                                                │
│     ↓                                                                   │
│  Agents (Assistant, Political Risk, Scheduler, Reporting, Route Planner) │
│  Services (News fetch, NLP)   Data (ports, AIS, logistics)              │
│     ↓                                                                   │
│  MongoDBClient (DB or file fallback)                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Frontend Structure

### Entry Point
| File | Responsibility |
|------|----------------|
| `frontend/src/index.js` | App entry point, renders `<App />` into DOM |
| `frontend/src/App.js` | Root component: Router, Navbar, Routes. Wraps with ThemeProvider & DashboardProvider |

### Routing (App.js)
| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | Home | Landing page, hero, shipping metrics, GlobalShippingMap |
| `/dashboard` | Dashboard | Risk heatmap (WorldMap), charts, disruption alerts |
| `/assistant` | ChainOpsAIAssistantPage | AI chat for route/risk queries |
| `/reports` | Reports | List and download generated reports |
| `/thinking-logs` | ThinkingLogs | Dev view of AI reasoning (muted in nav) |
| `/session-manager` | SessionManagerPage | Manage sessions |
| `/route-planner` | MultiPortRoutePlanner | Multi-port route planning |

### Shared State (Context)
| File | Responsibility |
|------|----------------|
| `context/DashboardContext.js` | Central state: dashboardData, shippingIntelligence, chatMessages, reports, sessions. Fetches from `/api/dashboard`, `/api/shipping-intelligence`, `/api/reports`, etc. |
| `context/ThemeContext.js` | Light/dark theme state |
| `config.js` | `API_URL` – backend base URL (from `REACT_APP_API_URL` or default) |

### Pages & Components
| File | Responsibility |
|------|----------------|
| `Home.js` | Hero, metrics cards, Global Maritime Intelligence Snapshot (map), critical alerts, recent routes |
| `Dashboard.js` | WorldMap heatmap, RiskCharts, RiskTables, DisruptionAlerts |
| `ChainOpsAIAssistantPage.js` | Wraps ChatPanel – AI chat interface |
| `ChatPanel.js` | Chat UI, sends messages to `/api/query`, displays responses |
| `Reports.js` | Lists reports from context, download via `/api/reports/{id}/download` |
| `ThinkingLogs.js` | Shows chatMessages (AI reasoning log) |
| `SessionManagerPage.js` | Session list, create/switch/delete sessions |
| `MultiPortRoutePlanner.js` | Route planning form, calls `/api/route/plan-multi-port`, `/api/route/ports` |

### Map Components
| File | Responsibility |
|------|----------------|
| `GlobalShippingMap.js` | Home-page ECDIS-style map. Fetches weather, risk-zones, ports, vessels from backend. Shows chokepoints, disruptions, voyage route |
| `WorldMap.js` | Dashboard heatmap – country-level risk from world_risk_data |

### UI Components
| File | Responsibility |
|------|----------------|
| `Navbar.js` | Top nav: Dashboard, Assistant, Reports, Session Manager. Thinking Logs only in dev mode |
| `IntroAnimation.js` | Landing intro animation |
| `ThemeToggle.js` | Light/dark switch |
| `LoadingSpinner.js` | Loading indicator |
| `RiskCharts.js` | Charts for risk distribution |
| `RiskTables.js` | Tables for risk data |
| `DisruptionAlerts.js` | Disruption alert list |
| `utils/developerMode.js` | `isDeveloperModeEnabled()` – localStorage/query param check for Thinking Logs |

### Data Flow (Frontend)
```
User action → Component → useDashboard() or direct axios
    → config.API_URL + endpoint (e.g. /api/shipping-intelligence)
    → Backend responds → setState → UI re-renders
```

---

## 2. Backend Structure

### Entry Point
| File | Responsibility |
|------|----------------|
| `backend/main.py` | FastAPI app, CORS, all routes. Imports agents, DB, services. Startup: connect DB, start news fetch loop |

### API Endpoints (main.py)
| Endpoint | Purpose |
|----------|---------|
| `GET /api/dashboard` | World risk data, political risks, disruption alerts |
| `GET /api/shipping-intelligence` | Maritime metrics: chokepoints, critical alerts, world_risk_data |
| `GET /api/weather` | Marine weather events (OpenWeather or fallback) |
| `GET /api/risk-zones` | Dynamic risk zones from intelligence |
| `GET /api/ports` | Port list with congestion, ships waiting |
| `GET /api/vessels` | Vessel positions (AIS sample or live) |
| `POST /api/query` | AI assistant – routes to ChatbotManager |
| `GET /api/reports` | List reports |
| `GET /api/reports/{id}/download` | Download report PDF |
| `POST /api/route/plan-multi-port` | Multi-port route planning |
| `GET /api/route/ports` | Available ports |
| `POST /api/sessions`, `GET /api/sessions`, etc. | Session CRUD |

### Agents
| File | Responsibility |
|------|----------------|
| `assistant_agent.py` | Handles greetings, help, general queries. Routes to other agents |
| `chatbot_manager.py` | Orchestrates chat flow, calls assistant + specialized agents |
| `political_risk_agent.py` | Fetches news (NewsAPI, GNews, NewsData), scores political risk by country |
| `scheduler_agent.py` | Schedule risk analysis, equipment delays |
| `reporting_agent.py` | Builds RiskReport, generates PDFs. Writes to `reports/` |
| `route_planner_agent.py` | Multi-port route planning: legs, distances, chokepoints, risk |

### Services
| File | Responsibility |
|------|----------------|
| `supply_chain_news_service.py` | Fetches news (NewsAPI, Mediastack, GNews), filters by logistics keywords, stores in DB |
| `news_nlp_processor.py` | NLP on news: disruption detection, risk scoring, chokepoint extraction, `store_disruption_alert` |

### Data Modules
| File | Responsibility |
|------|----------------|
| `data/ports.py` | MAJOR_PORTS (global ports with coords, capacity). Used by route planner, `/api/ports` |
| `data/logistics_regions.py` | Countries, chokepoint mappings, `build_world_risk_from_alerts()` |
| `data/ais_sample.py` | Sample vessels for map. `project_position()` for simulated movement |

### Database
| File | Responsibility |
|------|----------------|
| `database/mongodb.py` | MongoDBClient. Connects to MongoDB. Fallback: file storage for reports (`reports_data/`), news, sessions |

### Models
| File | Responsibility |
|------|----------------|
| `models/schemas.py` | Pydantic models: RiskReport, PoliticalRisk, ScheduleRisk, Session, etc. |

### Backend Data Flow
```
Request → main.py endpoint
    → agents / services / db_client
    → build_world_risk_from_alerts (logistics_regions)
    → MAJOR_PORTS, AIS_SAMPLE_VESSELS
    → Return JSON (or FileResponse for PDF)
```

### Background Tasks (main.py)
- `_news_fetch_loop`: Every 10 min, `news_service.run_fetch_and_store()` → `_refresh_disruption_cache`
- `_run_initial_news_fetch`: Runs once 5s after startup

---

## 3. How Pages Connect to Backend

| Page | Backend Endpoints Used |
|------|------------------------|
| **Home** | `/api/shipping-intelligence` (via DashboardContext), `/api/weather`, `/api/risk-zones`, `/api/ports`, `/api/vessels` (GlobalShippingMap) |
| **Dashboard** | `/api/dashboard` (via DashboardContext) |
| **Assistant** | `/api/query` (ChatPanel) |
| **Reports** | `/api/reports`, `/api/reports/{id}/download` |
| **Route Planner** | `/api/route/ports`, `/api/route/plan-multi-port` |
| **Session Manager** | `/api/sessions` (CRUD) |

---

## 4. Imports & Dependencies – Explained Simply 🧒

Think of imports like **toys in a toy box**. Each toy (library) helps us do one special thing. Here's what each one does in very simple words:

---

### Frontend Imports (JavaScript/React)

| Import / Package | What it does (simple) |
|------------------|------------------------|
| **React** | The main LEGO set. Lets us build pieces of a webpage (buttons, lists, maps) that we can reuse and put together. |
| **react-dom** | Takes the LEGO pieces we built and actually shows them on the screen so people can see them. |
| **react-router-dom** | Like a map of our website. When you click "Dashboard" or "Reports", it knows which page to show (like turning to the right page in a book). |
| **axios** | A mailman that carries messages between our website and the backend. We send a request ("Give me reports!") and it brings back the answer. |
| **react-simple-maps** | Draws the world map with countries and markers. Used for the big map on Home and Dashboard. |
| **recharts** | Draws charts and graphs (bars, lines, pies) so we can see numbers in a pretty way. |
| **lucide-react** | A box of small pictures (icons): ship, shield, chart, folder, etc. We use them on buttons and next to labels. |
| **Tailwind CSS** | A helper that makes things pretty without writing lots of CSS. Like saying "make this blue and round" in short words. |
| **react-scripts** | The helper that builds and runs our React app. It compiles our code and starts the dev server. |

---

### Backend Imports (Python)

| Import / Package | What it does (simple) |
|------------------|------------------------|
| **FastAPI** | The waiter in a restaurant. It listens for requests (e.g. "Give me dashboard data") and sends back the right answer (JSON or files). |
| **uvicorn** | The restaurant itself – it runs the server so people can knock on the door (port 8000) and ask for things. |
| **pydantic** | A checklist. It makes sure the data we receive or send has the right shape (e.g. "report must have a title and an ID"). |
| **pymongo / motor** | Talk to the database (MongoDB). Like a librarian: we can save reports and news, and ask to get them back later. Motor is the async version so we don't block while waiting. |
| **aiohttp** | An async mailman. Fetches news from other websites (NewsAPI, OpenWeather, etc.) without slowing down the rest of the app. |
| **python-dotenv** | Reads the .env file. It's like a secret notebook with API keys so we don't put them in the code. |
| **requests** | Another way to send HTTP requests (some older code might use it). |
| **reportlab** | Makes PDF files. Like a printer that creates report documents from our data. |
| **python-docx** | Creates Word (.docx) documents. Used for some report formats. |
| **beautifulsoup4 / lxml** | Reads and parses HTML from web pages. Like opening a webpage and pulling out only the text we need. |
| **openai / anthropic** | Talk to AI models (GPT, Claude) for summaries and smart answers in the chat. |
| **sse-starlette** | Lets us push updates to the frontend in real time (e.g. streaming) – currently not heavily used. |

---

### How They Connect

- **axios** (frontend) sends a request → **FastAPI** (backend) receives it → **pymongo/motor** or **aiohttp** get data → **FastAPI** sends JSON back → **axios** gives it to React → **React** updates the screen.
- **react-simple-maps** and **recharts** use that data to draw the map and charts.
- **lucide-react** and **Tailwind** make everything look nice.

---

## 5. Key Dependencies (Quick List)

**Frontend:** react, react-dom, react-router-dom, axios, react-simple-maps, recharts, lucide-react, tailwindcss  
**Backend:** FastAPI, uvicorn, pydantic, pymongo, motor, aiohttp, python-dotenv, reportlab, python-docx  

---

## 6. Environment Variables

| Variable | Used By | Purpose |
|----------|---------|---------|
| `REACT_APP_API_URL` | Frontend (config.js) | Backend base URL |
| `MONGODB_URI` | Backend | MongoDB connection |
| `OPENWEATHER_API_KEY` | Backend | Marine weather |
| `NEWSAPI_KEY`, `MEDIASTACK_API_KEY`, `GNEWS_API_KEY` | Backend | News sources |
| `OPENAI_API_KEY` | Backend | AI summaries (optional) |

---

## 7. Run Order

1. `npm run dev` starts backend (port 8000) and frontend (port 3000)
2. Backend connects to MongoDB (or uses file fallback)
3. News fetch loop runs every 10 min
4. Frontend loads → DashboardContext fetches dashboard + shipping-intelligence
5. User navigates → pages fetch their data from respective endpoints
re