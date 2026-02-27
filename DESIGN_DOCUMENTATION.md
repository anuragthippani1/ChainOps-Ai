# SentriX - Design Documentation

## Project Overview

**SentriX** is a Real-Time Supply Chain Risk Intelligence Platform that provides comprehensive geopolitical and supply chain risk analysis powered by AI. The system monitors global risks, analyzes shipping routes, and generates detailed risk reports to support informed decision-making.

---

## Table of Contents

1. [System Architecture Diagram](#1-system-architecture-diagram)
2. [Overall Block Diagram](#2-overall-block-diagram)
3. [Data Flow Diagram](#3-data-flow-diagram)
4. [Component Architecture](#4-component-architecture)
5. [UML Diagrams](#5-uml-diagrams)
6. [Database Schema](#6-database-schema)
7. [API Architecture](#7-api-architecture)
8. [Agent System Architecture](#8-agent-system-architecture)

---

## 1. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          SENTRIX PLATFORM                                │
│                   Real-Time Risk Intelligence System                     │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                            PRESENTATION LAYER                              │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Home Page  │  │  Dashboard   │  │   Reports    │  │   Assistant  │ │
│  │              │  │              │  │              │  │              │ │
│  │ - Welcome    │  │ - Heatmap    │  │ - Report     │  │ - Chat UI    │ │
│  │ - Stats      │  │ - Charts     │  │   List       │  │ - Streaming  │ │
│  │ - Quick      │  │ - Risk       │  │ - Details    │  │ - Route      │ │
│  │   Actions    │  │   Tables     │  │ - Download   │  │   Analysis   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │ Thinking     │  │  Session     │  │  World Map   │                   │
│  │   Logs       │  │  Manager     │  │  Component   │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
│                                                                            │
│  Technology: React.js, React Router, Tailwind CSS, Context API            │
└───────────────────────────────────────────────────────────────────────────┘
                                      ▲
                                      │
                                      │ REST API / SSE
                                      │ (HTTP/HTTPS)
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY LAYER                               │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│                          FastAPI Application                               │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                         API Endpoints                               │  │
│  │                                                                     │  │
│  │  /api/query              - Process natural language queries        │  │
│  │  /api/query/stream       - Streaming text responses (SSE)          │  │
│  │  /api/dashboard          - Get dashboard data                      │  │
│  │  /api/reports            - Manage risk reports                     │  │
│  │  /api/sessions           - Session management                      │  │
│  │  /api/shipment/upload    - Upload shipment data                    │  │
│  │  /api/reports/download   - Download reports (PDF/DOCX)            │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  Technology: FastAPI, Uvicorn, Python 3.13, CORS, SSE                     │
└───────────────────────────────────────────────────────────────────────────┘
                                      ▲
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          BUSINESS LOGIC LAYER                              │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                      AI AGENT SYSTEM                                │  │
│  │                                                                     │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │  │
│  │  │   Assistant     │  │   Political     │  │   Scheduler     │  │  │
│  │  │     Agent       │  │   Risk Agent    │  │     Agent       │  │  │
│  │  │                 │  │                 │  │                 │  │  │
│  │  │ - NL Query      │  │ - Geopolitical  │  │ - Schedule      │  │  │
│  │  │   Processing    │  │   Analysis      │  │   Analysis      │  │  │
│  │  │ - Route         │  │ - News Data     │  │ - Delay         │  │  │
│  │  │   Analysis      │  │ - Risk Scoring  │  │   Detection     │  │  │
│  │  │ - Streaming     │  │ - Country       │  │ - Equipment     │  │  │
│  │  │   Response      │  │   Assessment    │  │   Tracking      │  │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  │  │
│  │                                                                     │  │
│  │  ┌─────────────────┐  ┌─────────────────┐                        │  │
│  │  │   Reporting     │  │    Chatbot      │                        │  │
│  │  │     Agent       │  │    Manager      │                        │  │
│  │  │                 │  │                 │                        │  │
│  │  │ - Report        │  │ - Intent        │                        │  │
│  │  │   Generation    │  │   Classification│                        │  │
│  │  │ - PDF/DOCX      │  │ - Query         │                        │  │
│  │  │   Export        │  │   Routing       │                        │  │
│  │  │ - Executive     │  │ - Context       │                        │  │
│  │  │   Summary       │  │   Management    │                        │  │
│  │  └─────────────────┘  └─────────────────┘                        │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  Technology: Python, Anthropic Claude API, OpenAI API, Async Processing   │
└───────────────────────────────────────────────────────────────────────────┘
                                      ▲
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          DATA PERSISTENCE LAYER                            │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                      MongoDB Database                               │  │
│  │                                                                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
│  │  │   Reports    │  │   Sessions   │  │  World Risk  │            │  │
│  │  │  Collection  │  │  Collection  │  │     Data     │            │  │
│  │  │              │  │              │  │              │            │  │
│  │  │ - Political  │  │ - Session    │  │ - Country    │            │  │
│  │  │   Risks      │  │   Metadata   │  │   Risk Data  │            │  │
│  │  │ - Schedule   │  │ - Activity   │  │ - Risk       │            │  │
│  │  │   Risks      │  │   Tracking   │  │   Factors    │            │  │
│  │  │ - Reports    │  │ - Report     │  │ - Scores     │            │  │
│  │  │   History    │  │   Counts     │  │              │            │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                     File System Storage                             │  │
│  │                                                                     │  │
│  │  - Generated Reports (PDF/DOCX)                                    │  │
│  │  - Report Metadata (JSON)                                          │  │
│  │  - Shipment Data Files                                             │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  Technology: MongoDB (Motor), AsyncIO, JSON File Storage                  │
└───────────────────────────────────────────────────────────────────────────┘
                                      ▲
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES LAYER                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  Anthropic API  │  │   OpenAI API    │  │   News APIs     │          │
│  │   (Claude)      │  │   (GPT-4)       │  │                 │          │
│  │                 │  │                 │  │ - World Events  │          │
│  │ - Advanced      │  │ - NL Processing │  │ - Political     │          │
│  │   Analysis      │  │ - Embeddings    │  │   News          │          │
│  │ - Reasoning     │  │ - Completions   │  │ - Trade Data    │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Overall Block Diagram

```
                    ╔═══════════════════════════════════════╗
                    ║         USER INTERFACE LAYER          ║
                    ╚═══════════════════════════════════════╝
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
         ┌──────▼──────┐      ┌─────▼──────┐     ┌──────▼──────┐
         │  Dashboard  │      │  Assistant │     │   Reports   │
         │  Component  │      │    Chat    │     │   Manager   │
         └──────┬──────┘      └─────┬──────┘     └──────┬──────┘
                │                    │                    │
                └────────────────────┼────────────────────┘
                                     │
                                     │ REST/SSE
                                     │
                    ╔═══════════════════════════════════════╗
                    ║          API GATEWAY LAYER            ║
                    ║          (FastAPI Router)             ║
                    ╚═══════════════════════════════════════╝
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
         ┌──────▼──────┐      ┌─────▼──────┐     ┌──────▼──────┐
         │   Query     │      │  Session   │     │  Dashboard  │
         │  Processor  │      │  Manager   │     │   Service   │
         └──────┬──────┘      └─────┬──────┘     └──────┬──────┘
                │                    │                    │
                └────────────────────┼────────────────────┘
                                     │
                    ╔═══════════════════════════════════════╗
                    ║       BUSINESS LOGIC LAYER            ║
                    ║         (AI Agent System)             ║
                    ╚═══════════════════════════════════════╝
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
         ┌──────▼──────┐      ┌─────▼──────┐     ┌──────▼──────┐
         │  Chatbot    │      │ Assistant  │     │ Political   │
         │  Manager    │      │   Agent    │     │ Risk Agent  │
         └──────┬──────┘      └─────┬──────┘     └──────┬──────┘
                │                    │                    │
         ┌──────▼──────┐      ┌─────▼──────┐            │
         │ Scheduler   │      │ Reporting  │            │
         │   Agent     │      │   Agent    │            │
         └──────┬──────┘      └─────┬──────┘            │
                │                    │                    │
                └────────────────────┼────────────────────┘
                                     │
                    ╔═══════════════════════════════════════╗
                    ║        DATA PERSISTENCE LAYER         ║
                    ╚═══════════════════════════════════════╝
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
         ┌──────▼──────┐      ┌─────▼──────┐     ┌──────▼──────┐
         │   MongoDB   │      │ File System│     │   Cache     │
         │  Database   │      │  Storage   │     │   Layer     │
         └─────────────┘      └────────────┘     └─────────────┘
```

---

## 3. Data Flow Diagram

### 3.1 User Query Processing Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │
     │ 1. Enter Query
     ▼
┌─────────────────┐
│   Chat Panel    │
│   (Frontend)    │
└────┬────────────┘
     │
     │ 2. HTTP POST /api/query
     │    {query: "...", session_id: "..."}
     ▼
┌─────────────────┐
│  API Gateway    │
│   (FastAPI)     │
└────┬────────────┘
     │
     │ 3. Route to Chatbot Manager
     ▼
┌─────────────────┐
│    Chatbot      │
│    Manager      │
└────┬────────────┘
     │
     │ 4. Classify Intent
     │    (assistant | political | schedule | combined | reject)
     ▼
     ├──────────────┬──────────────┬──────────────┬──────────────┐
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│Assistant│   │Political│   │Schedule │   │Combined │   │ Reject  │
│  Agent  │   │Risk Agnt│   │  Agent  │   │ Report  │   │Response │
└────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
     │             │             │             │             │
     │ 5. Process  │ 5. Analyze  │ 5. Analyze  │ 5. Generate │ 5. Return
     │    Query    │    Risks    │   Schedule  │   Combined  │    Error
     │             │             │             │    Report   │
     ▼             ▼             ▼             ▼             │
┌─────────────────────────────────────────────────────┐     │
│            LLM Service (Claude/GPT-4)               │     │
│                                                     │     │
│  - Natural Language Understanding                   │     │
│  - Risk Analysis                                    │     │
│  - Report Generation                                │     │
│  - Recommendations                                  │     │
└────┬────────────────────────────────────────────────┘     │
     │                                                       │
     │ 6. Store Results                                      │
     ▼                                                       │
┌─────────────────┐                                         │
│    MongoDB      │                                         │
│   Database      │                                         │
└────┬────────────┘                                         │
     │                                                       │
     │ 7. Return Response                                    │
     ▼                                                       │
┌─────────────────┐                                         │
│  API Gateway    │◄────────────────────────────────────────┘
└────┬────────────┘
     │
     │ 8. Send Response to Frontend
     │    {session_id, response/report, type}
     ▼
┌─────────────────┐
│   Chat Panel    │
│   (Frontend)    │
└────┬────────────┘
     │
     │ 9. Display Result
     ▼
┌─────────┐
│  User   │
└─────────┘
```

### 3.2 Dashboard Data Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │
     │ 1. Navigate to Dashboard
     ▼
┌──────────────────┐
│   Dashboard      │
│   Component      │
│   (React)        │
└────┬─────────────┘
     │
     │ 2. useEffect() - Load Data
     │    GET /api/dashboard
     ▼
┌──────────────────┐
│   API Gateway    │
└────┬─────────────┘
     │
     │ 3. Fetch Dashboard Data
     ▼
┌──────────────────┐         ┌──────────────────┐
│   Dashboard      │────────▶│   MongoDB        │
│   Service        │◄────────│   Database       │
└────┬─────────────┘         └──────────────────┘
     │                        4. Query Collections
     │                           - World Risk Data
     │                           - Political Risks
     │                           - Schedule Risks
     │
     │ 5. Aggregate & Format Data
     │    {
     │      world_risk_data: {...},
     │      political_risks: [...],
     │      schedule_risks: [...]
     │    }
     ▼
┌──────────────────┐
│   API Gateway    │
└────┬─────────────┘
     │
     │ 6. Return JSON Response
     ▼
┌──────────────────┐
│   Dashboard      │
│   Context        │
└────┬─────────────┘
     │
     │ 7. Update State
     │    setState(dashboardData)
     ▼
┌──────────────────┬──────────────────┬──────────────────┐
│   World Map      │   Risk Tables    │   Risk Charts    │
│   Component      │   Component      │   Component      │
└────┬─────────────┴────┬─────────────┴────┬─────────────┘
     │                   │                   │
     │ 8. Render Visualizations              │
     │    - Heatmap                          │
     │    - Tables                           │
     │    - Charts                           │
     ▼                   ▼                   ▼
┌─────────────────────────────────────────────────┐
│            User sees Dashboard                   │
└─────────────────────────────────────────────────┘
```

### 3.3 Report Generation Flow

```
User Query → Chatbot Manager → Political Risk Agent
                    │                    │
                    │                    ├──→ Extract Countries
                    │                    │
                    ▼                    ▼
            Scheduler Agent         News/Data APIs
                    │                    │
                    ├──→ Extract         │
                    │    Countries       │
                    │                    │
                    ▼                    ▼
            Analyze Schedule      Analyze Political
            Risks                 Risks
                    │                    │
                    └──────┬─────────────┘
                           │
                           ▼
                    Reporting Agent
                           │
                           ├──→ Generate Report
                           │    - Executive Summary
                           │    - Risk Analysis
                           │    - Recommendations
                           │
                           ▼
                    MongoDB Database
                           │
                           ├──→ Store Report
                           │
                           ▼
                    File System
                           │
                           ├──→ Generate PDF/DOCX
                           │
                           ▼
                    Return to User
```

---

## 4. Component Architecture

### 4.1 Frontend Component Hierarchy

```
App.js
│
├── DashboardProvider (Context)
│   │
│   ├── Navbar.js
│   │   ├── Logo
│   │   ├── Navigation Items
│   │   └── Session Info
│   │
│   ├── Routes
│   │   │
│   │   ├── Home.js
│   │   │   ├── Hero Section
│   │   │   ├── Stats Cards
│   │   │   ├── Quick Actions
│   │   │   ├── Features
│   │   │   └── Footer
│   │   │
│   │   ├── Dashboard.js
│   │   │   ├── WorldMap.js
│   │   │   │   ├── SVG Map
│   │   │   │   ├── Country Highlighting
│   │   │   │   ├── Route Plotting
│   │   │   │   └── Tooltips
│   │   │   │
│   │   │   ├── RiskTables.js
│   │   │   │   ├── Political Risk Table
│   │   │   │   └── Schedule Risk Table
│   │   │   │
│   │   │   └── RiskCharts.js
│   │   │       ├── Bar Charts
│   │   │       └── Pie Charts
│   │   │
│   │   ├── SentriXAssistantPage.js
│   │   │   ├── ChatPanel.js
│   │   │   │   ├── Message List
│   │   │   │   ├── Input Box
│   │   │   │   └── Streaming Handler
│   │   │   │
│   │   │   └── ThinkingLogs.js
│   │   │
│   │   ├── Reports.js
│   │   │   ├── Report List
│   │   │   ├── Report Details
│   │   │   └── Download Buttons
│   │   │
│   │   ├── ThinkingLogs.js
│   │   │   └── Message History
│   │   │
│   │   └── SessionManagerPage.js
│   │       ├── SessionManager.js
│   │       │   ├── Session List
│   │       │   ├── Create Session
│   │       │   └── Session Details
│   │       │
│   │       └── Session Stats
│   │
│   └── LoadingSpinner.js
```

### 4.2 Backend Component Structure

```
main.py (FastAPI App)
│
├── Middleware
│   └── CORS Configuration
│
├── API Endpoints
│   ├── /api/query
│   ├── /api/query/stream
│   ├── /api/dashboard
│   ├── /api/reports
│   ├── /api/sessions
│   └── /api/shipment/upload
│
├── Agent System
│   │
│   ├── chatbot_manager.py
│   │   ├── classify_intent()
│   │   └── route_query()
│   │
│   ├── assistant_agent.py
│   │   ├── process_query()
│   │   ├── process_query_streaming()
│   │   ├── _analyze_route()
│   │   └── _generate_response()
│   │
│   ├── political_risk_agent.py
│   │   ├── analyze_risks()
│   │   ├── fetch_news_data()
│   │   └── score_risk()
│   │
│   ├── scheduler_agent.py
│   │   ├── analyze_schedule_risks()
│   │   ├── extract_countries()
│   │   └── calculate_delays()
│   │
│   └── reporting_agent.py
│       ├── generate_combined_report()
│       ├── generate_political_report()
│       ├── generate_schedule_report()
│       ├── create_pdf()
│       └── create_docx()
│
├── Database Layer
│   └── mongodb.py
│       ├── store_report()
│       ├── get_all_reports()
│       ├── create_session()
│       └── get_all_sessions()
│
└── Data Models
    └── schemas.py
        ├── QueryRequest
        ├── PoliticalRisk
        ├── ScheduleRisk
        ├── RiskReport
        ├── Session
        └── DashboardData
```

---

## 5. UML Diagrams

### 5.1 Class Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      << Pydantic Model >>                    │
│                        QueryRequest                          │
├─────────────────────────────────────────────────────────────┤
│ - query: str                                                 │
│ - session_id: Optional[str]                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      << Pydantic Model >>                    │
│                       PoliticalRisk                          │
├─────────────────────────────────────────────────────────────┤
│ - country: str                                               │
│ - risk_type: str                                             │
│ - likelihood_score: int                                      │
│ - reasoning: str                                             │
│ - publication_date: str                                      │
│ - source_title: str                                          │
│ - source_url: str                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      << Pydantic Model >>                    │
│                       ScheduleRisk                           │
├─────────────────────────────────────────────────────────────┤
│ - equipment_id: str                                          │
│ - country: str                                               │
│ - original_delivery_date: str                                │
│ - current_delivery_date: str                                 │
│ - delay_days: int                                            │
│ - risk_level: int                                            │
│ - risk_factors: List[str]                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      << Pydantic Model >>                    │
│                         RiskReport                           │
├─────────────────────────────────────────────────────────────┤
│ - report_id: str                                             │
│ - session_id: str                                            │
│ - report_type: str                                           │
│ - created_at: datetime                                       │
│ - title: str                                                 │
│ - executive_summary: str                                     │
│ - political_risks: Optional[List[PoliticalRisk]]             │
│ - schedule_risks: Optional[List[ScheduleRisk]]               │
│ - world_risk_data: Optional[Dict]                            │
│ - recommendations: List[str]                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                           Session                            │
├─────────────────────────────────────────────────────────────┤
│ - session_id: str                                            │
│ - name: str                                                  │
│ - description: Optional[str]                                 │
│ - created_at: datetime                                       │
│ - updated_at: datetime                                       │
│ - is_active: bool                                            │
│ - report_count: int                                          │
│ - last_activity: Optional[datetime]                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      ChatbotManager                          │
├─────────────────────────────────────────────────────────────┤
│ + classify_intent(query: str): str                           │
│ + route_query(query: str): Agent                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ uses
                            ▼
            ┌───────────────────────────────┐
            │         Agent (Abstract)      │
            ├───────────────────────────────┤
            │ + process_query()             │
            └───────────────────────────────┘
                            △
                            │ inherits
            ┌───────────────┼───────────────┐
            │               │               │
┌───────────▼─────┐ ┌───────▼────────┐ ┌──▼────────────────┐
│ AssistantAgent  │ │PoliticalRiskAgt│ │ SchedulerAgent    │
├─────────────────┤ ├────────────────┤ ├───────────────────┤
│+ process_query()│ │+ analyze_risks()│ │+ analyze_schedule│
│+ _analyze_route│ │+ fetch_news()   │ │+ extract_countries│
│+ streaming()    │ │+ score_risk()  │ │                   │
└─────────────────┘ └────────────────┘ └───────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      ReportingAgent                          │
├─────────────────────────────────────────────────────────────┤
│ + generate_combined_report(): RiskReport                     │
│ + generate_political_report(): RiskReport                    │
│ + generate_schedule_report(): RiskReport                     │
│ + create_pdf(report: RiskReport): bytes                      │
│ + create_docx(report: RiskReport): bytes                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      MongoDBClient                           │
├─────────────────────────────────────────────────────────────┤
│ - client: AsyncIOMotorClient                                 │
│ - database: Database                                         │
├─────────────────────────────────────────────────────────────┤
│ + store_report(report: RiskReport): bool                     │
│ + get_all_reports(): List[RiskReport]                        │
│ + get_report_by_id(id: str): RiskReport                      │
│ + create_session(session: Session): bool                     │
│ + get_all_sessions(): List[Session]                          │
│ + update_session(id: str, data: dict): bool                  │
│ + delete_session(id: str): bool                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Sequence Diagram - Query Processing

```
User     Frontend   API       Chatbot    Assistant   Political   MongoDB
  │         │        │         Manager      Agent      Agent       │
  │         │        │            │           │          │         │
  │──Query──▶│       │            │           │          │         │
  │         │        │            │           │          │         │
  │         │──POST──▶│           │           │          │         │
  │         │/api/qry│            │           │          │         │
  │         │        │            │           │          │         │
  │         │        │──classify──▶│          │          │         │
  │         │        │   intent   │           │          │         │
  │         │        │            │           │          │         │
  │         │        │◀──return───┤           │          │         │
  │         │        │   "politic"│           │          │         │
  │         │        │            │           │          │         │
  │         │        │────────────┼───────────┼─analyze──▶│        │
  │         │        │            │           │  risks    │        │
  │         │        │            │           │           │        │
  │         │        │            │           │           │──LLM───▶
  │         │        │            │           │           │ Call   │
  │         │        │            │           │           │        │
  │         │        │            │           │           │◀───────┤
  │         │        │            │           │           │ Result │
  │         │        │            │           │           │        │
  │         │        │◀───────────┼───────────┼───────────┤        │
  │         │        │            │           │  risks    │        │
  │         │        │            │           │           │        │
  │         │        │────────────┼─generate──▶│          │        │
  │         │        │            │   report  │           │        │
  │         │        │            │           │           │        │
  │         │        │◀───────────┼───────────┤           │        │
  │         │        │            │   report  │           │        │
  │         │        │            │           │           │        │
  │         │        │─────────────────────────┼───────────┼─store──▶
  │         │        │                         │           │ report │
  │         │        │                         │           │        │
  │         │        │◀────────────────────────┼───────────┼────────┤
  │         │        │                         │           │   ok   │
  │         │        │            │           │           │        │
  │         │◀──JSON─┤            │           │           │        │
  │         │response│            │           │           │        │
  │         │        │            │           │           │        │
  │◀─Display┤        │            │           │           │        │
  │  Report │        │            │           │           │        │
  │         │        │            │           │           │        │
```

### 5.3 State Diagram - Session Lifecycle

```
                    ┌─────────────┐
                    │   [START]   │
                    └──────┬──────┘
                           │
                           │ POST /api/sessions
                           │ {name, description}
                           ▼
                    ┌─────────────┐
            ┌───────│   CREATED   │
            │       │             │
            │       │ is_active=  │
            │       │   true      │
            │       └──────┬──────┘
            │              │
            │              │ User sends query
            │              │ report_count++
            │              ▼
            │       ┌─────────────┐
            │       │   ACTIVE    │
            │       │             │
  Update    │       │ Processing  │────┐
  session   │       │ queries     │    │ View reports
  metadata  │       └──────┬──────┘    │ GET /api/reports
            │              │            │
            │              │            │
            │              ▼            │
            │       ┌─────────────┐    │
            │       │  REPORTING  │◄───┘
            │       │             │
            │       │ Generating  │
            │       │ reports     │
            └──────▶└──────┬──────┘
                           │
                           │ PUT /api/sessions/{id}
                           │ {is_active: false}
                           ▼
                    ┌─────────────┐
                    │  INACTIVE   │
                    │             │
                    │ is_active=  │
                    │   false     │
                    └──────┬──────┘
                           │
                           │ DELETE /api/sessions/{id}
                           ▼
                    ┌─────────────┐
                    │  DELETED    │
                    └─────────────┘
```

### 5.4 Activity Diagram - Report Generation

```
                    ┌─────────────┐
                    │   [START]   │
                    │ User Query  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Parse Query │
                    │ (Chatbot)   │
                    └──────┬──────┘
                           │
                           ▼
                 ┌─────────────────────┐
                 │ Classify Intent     │
                 └─────────┬───────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌─────────┐      ┌─────────┐     ┌─────────┐
    │Political│      │Schedule │     │Combined │
    │  Only   │      │  Only   │     │  Both   │
    └────┬────┘      └────┬────┘     └────┬────┘
         │                │                │
         │                │                │
         ▼                ▼                ▼
    ┌─────────┐      ┌─────────┐     ┌─────────┐
    │Political│      │Schedule │     │Political│
    │Risk Agnt│      │  Agent  │     │+Schedule│
    └────┬────┘      └────┬────┘     └────┬────┘
         │                │                │
         │                │                │
         └────────────────┼────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Aggregate  │
                   │    Data     │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Reporting  │
                   │    Agent    │
                   └──────┬──────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
    ┌─────────┐      ┌─────────┐     ┌─────────┐
    │Generate │      │Generate │     │Generate │
    │Executive│      │  Risk   │     │  Recs   │
    │ Summary │      │Analysis │     │         │
    └────┬────┘      └────┬────┘     └────┬────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Create      │
                   │ Report      │
                   │ Object      │
                   └──────┬──────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
    ┌─────────┐      ┌─────────┐     ┌─────────┐
    │ Store   │      │ Generate│     │ Return  │
    │ MongoDB │      │ PDF/DOCX│     │   to    │
    │         │      │         │     │  User   │
    └────┬────┘      └────┬────┘     └────┬────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │    [END]    │
                    │ Report Ready│
                    └─────────────┘
```

---

## 6. Database Schema

### 6.1 MongoDB Collections

#### Reports Collection

```javascript
{
  "_id": ObjectId("..."),
  "report_id": "uuid-string",
  "session_id": "uuid-string",
  "report_type": "political" | "schedule" | "combined",
  "created_at": ISODate("2024-10-24T..."),
  "title": "Risk Report - Political Analysis",
  "executive_summary": "Summary text...",
  "political_risks": [
    {
      "country": "Russia",
      "risk_type": "Geopolitical",
      "likelihood_score": 4,
      "reasoning": "Active military conflict...",
      "publication_date": "2024-10-20",
      "source_title": "UN Security Council Report",
      "source_url": "https://..."
    }
  ],
  "schedule_risks": [
    {
      "equipment_id": "CNTX-2024-001",
      "country": "Germany",
      "original_delivery_date": "2024-10-15",
      "current_delivery_date": "2024-10-20",
      "delay_days": 5,
      "risk_level": 2,
      "risk_factors": ["Port congestion", "Labor strikes"]
    }
  ],
  "world_risk_data": {
    "Russia": {
      "risk_level": 4,
      "details": "High geopolitical risk...",
      "risk_factors": ["Military conflict", "Sanctions"]
    }
  },
  "recommendations": [
    "Consider alternative shipping routes",
    "Implement additional security measures"
  ]
}
```

#### Sessions Collection

```javascript
{
  "_id": ObjectId("..."),
  "session_id": "uuid-string",
  "name": "Morning Analysis Session",
  "description": "Risk assessment for Q4 shipments",
  "created_at": ISODate("2024-10-24T08:00:00Z"),
  "updated_at": ISODate("2024-10-24T10:30:00Z"),
  "is_active": true,
  "report_count": 5,
  "last_activity": ISODate("2024-10-24T10:30:00Z"),
  "reports": [
    "report-uuid-1",
    "report-uuid-2"
  ]
}
```

### 6.2 File System Structure

```
backend/
├── reports/                      # Generated report files
│   ├── {report_id}.pdf          # PDF reports
│   └── {report_id}.docx         # DOCX reports
│
└── reports_data/                 # Report metadata
    └── {report_id}.json         # Report JSON data
```

---

## 7. API Architecture

### 7.1 REST API Endpoints

| Method | Endpoint                     | Description           | Request Body                        | Response                                             |
| ------ | ---------------------------- | --------------------- | ----------------------------------- | ---------------------------------------------------- |
| GET    | `/`                          | Health check          | -                                   | `{message: "SentriX API is running"}`                |
| POST   | `/api/query`                 | Process user query    | `{query, session_id?}`              | `{session_id, response/report, type}`                |
| POST   | `/api/query/stream`          | Stream response (SSE) | `{query, session_id?}`              | Server-Sent Events stream                            |
| GET    | `/api/dashboard`             | Get dashboard data    | -                                   | `{world_risk_data, political_risks, schedule_risks}` |
| GET    | `/api/reports`               | Get all reports       | -                                   | `{reports: [...]}`                                   |
| GET    | `/api/reports/{id}`          | Get specific report   | -                                   | `{report: {...}}`                                    |
| GET    | `/api/reports/{id}/download` | Download report       | Query: `?format=pdf\|docx`          | File download                                        |
| POST   | `/api/sessions`              | Create new session    | `{name?, description?}`             | `{session: {...}}`                                   |
| GET    | `/api/sessions`              | Get all sessions      | -                                   | `{sessions: [...]}`                                  |
| GET    | `/api/sessions/{id}`         | Get session by ID     | -                                   | `{session: {...}}`                                   |
| PUT    | `/api/sessions/{id}`         | Update session        | `{name?, description?, is_active?}` | `{session: {...}}`                                   |
| DELETE | `/api/sessions/{id}`         | Delete session        | -                                   | `{message: "..."}`                                   |
| POST   | `/api/shipment/upload`       | Upload shipment data  | `{shipments: [...]}`                | `{status: "ok"}`                                     |
| POST   | `/api/shipment/reset`        | Reset shipment data   | -                                   | `{status: "ok"}`                                     |

### 7.2 API Request/Response Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ HTTP Request
       │ Headers: Content-Type, Authorization
       ▼
┌─────────────────────────────┐
│     FastAPI Gateway          │
│                              │
│  ┌────────────────────────┐ │
│  │   CORS Middleware      │ │
│  │  - Allow Origins       │ │
│  │  - Allow Methods       │ │
│  └───────────┬────────────┘ │
│              │               │
│  ┌───────────▼────────────┐ │
│  │   Route Handler        │ │
│  │  - Parse Request       │ │
│  │  - Validate Schema     │ │
│  └───────────┬────────────┘ │
│              │               │
│  ┌───────────▼────────────┐ │
│  │  Business Logic        │ │
│  │  - Agent Routing       │ │
│  │  - Data Processing     │ │
│  └───────────┬────────────┘ │
│              │               │
│  ┌───────────▼────────────┐ │
│  │  Response Builder      │ │
│  │  - Format JSON         │ │
│  │  - Set Status Code     │ │
│  └───────────┬────────────┘ │
└──────────────┼──────────────┘
               │
               │ HTTP Response
               │ Status: 200, 400, 500
               ▼
┌─────────────┐
│   Client    │
└─────────────┘
```

---

## 8. Agent System Architecture

### 8.1 Multi-Agent System Design

```
                  ┌─────────────────────────────┐
                  │      User Query Input       │
                  └─────────────┬───────────────┘
                                │
                                ▼
                  ┌─────────────────────────────┐
                  │    Chatbot Manager          │
                  │  (Intent Classification)    │
                  └─────────────┬───────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
  │  Assistant      │ │  Political Risk │ │  Scheduler      │
  │    Agent        │ │     Agent       │ │    Agent        │
  ├─────────────────┤ ├─────────────────┤ ├─────────────────┤
  │ - Route         │ │ - Country       │ │ - Equipment     │
  │   Analysis      │ │   Analysis      │ │   Tracking      │
  │ - General Q&A   │ │ - News Scraping │ │ - Delay Calc    │
  │ - Streaming     │ │ - Risk Scoring  │ │ - Risk Level    │
  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               │
                               ▼
                  ┌─────────────────────────────┐
                  │     Reporting Agent         │
                  │  (Report Orchestration)     │
                  ├─────────────────────────────┤
                  │ - Aggregate Results         │
                  │ - Generate Summary          │
                  │ - Create Recommendations    │
                  │ - Export PDF/DOCX           │
                  └─────────────┬───────────────┘
                                │
                                ▼
                  ┌─────────────────────────────┐
                  │      Data Persistence       │
                  │    (MongoDB + Files)        │
                  └─────────────────────────────┘
```

### 8.2 Agent Communication Pattern

```
┌──────────────────────────────────────────────────────────────┐
│                  Agent Orchestration Layer                    │
│                                                               │
│  Request → Chatbot Manager → Agent Selection → Response      │
│                                                               │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │  Request    │────▶│   Intent    │────▶│   Agent     │   │
│  │   Parser    │     │ Classifier  │     │  Selector   │   │
│  └─────────────┘     └─────────────┘     └──────┬──────┘   │
│                                                   │          │
└───────────────────────────────────────────────────┼──────────┘
                                                    │
          ┌─────────────────────────────────────────┼─────────────┐
          │                                         │             │
          ▼                                         ▼             ▼
┌─────────────────┐                       ┌─────────────┐ ┌──────────┐
│ Assistant Agent │                       │ Risk Agents │ │ Reporting│
│                 │                       │ (Political/ │ │  Agent   │
│ ┌─────────────┐ │                       │  Schedule)  │ │          │
│ │Process Query│ │                       │             │ │          │
│ └──────┬──────┘ │                       │ ┌─────────┐ │ │┌────────┐│
│        │        │                       │ │ Analyze │ │ ││Generate││
│        ▼        │                       │ │  Risks  │ │ ││ Report ││
│ ┌─────────────┐ │                       │ └────┬────┘ │ │└───┬────┘│
│ │   LLM API   │ │                       │      │      │ │    │     │
│ │   (Claude)  │ │                       │      ▼      │ │    ▼     │
│ └──────┬──────┘ │                       │ ┌─────────┐ │ │┌────────┐│
│        │        │                       │ │  Score  │ │ ││Export  ││
│        ▼        │                       │ │  Risk   │ │ ││ PDF/DOC││
│ ┌─────────────┐ │                       │ └─────────┘ │ │└────────┘│
│ │   Format    │ │                       │             │ │          │
│ │  Response   │ │                       └─────────────┘ └──────────┘
│ └─────────────┘ │
└─────────────────┘
```

### 8.3 AI/LLM Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SentriX Application                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ API Calls
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              External AI Services Layer                      │
│                                                              │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │  Anthropic Claude    │      │     OpenAI GPT-4     │    │
│  │       API            │      │        API           │    │
│  ├──────────────────────┤      ├──────────────────────┤    │
│  │                      │      │                      │    │
│  │ - Political Risk     │      │ - Natural Language   │    │
│  │   Analysis           │      │   Understanding      │    │
│  │ - Executive Summary  │      │ - Query Processing   │    │
│  │ - Recommendations    │      │ - Text Generation    │    │
│  │ - Route Analysis     │      │ - Embeddings         │    │
│  │                      │      │                      │    │
│  └──────────────────────┘      └──────────────────────┘    │
│                                                              │
│  Features:                                                   │
│  - 200K+ token context windows                              │
│  - Streaming responses                                       │
│  - Structured outputs                                        │
│  - Safety filters                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
└─────────────────────────────────────────────────────────────┘

Layer 1: Network Security
┌─────────────────────────────────────────────────────────────┐
│ - HTTPS/TLS Encryption                                       │
│ - CORS Policy (localhost:3000)                              │
│ - Rate Limiting                                              │
└─────────────────────────────────────────────────────────────┘

Layer 2: API Security
┌─────────────────────────────────────────────────────────────┐
│ - Input Validation (Pydantic Schemas)                        │
│ - SQL Injection Prevention (NoSQL)                           │
│ - XSS Prevention                                             │
│ - Request Size Limits                                        │
└─────────────────────────────────────────────────────────────┘

Layer 3: Authentication & Authorization
┌─────────────────────────────────────────────────────────────┐
│ - Session-based Access                                       │
│ - API Key Management (for LLM services)                      │
│ - Environment Variables for Secrets                          │
└─────────────────────────────────────────────────────────────┘

Layer 4: Data Security
┌─────────────────────────────────────────────────────────────┐
│ - MongoDB Connection Security                                │
│ - Data Validation                                            │
│ - Sensitive Data Sanitization                                │
│ - Secure File Storage                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Deployment                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                           │
│                   (Nginx / Cloud LB)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│   Frontend   │          │   Frontend   │
│  Instance 1  │          │  Instance 2  │
│              │          │              │
│  React App   │          │  React App   │
│  (Static)    │          │  (Static)    │
└──────────────┘          └──────────────┘

        │                         │
        └────────────┬────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                               │
│                   (FastAPI Server)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│   Backend    │          │   Backend    │
│  Instance 1  │          │  Instance 2  │
│              │          │              │
│  FastAPI +   │          │  FastAPI +   │
│  Agents      │          │  Agents      │
└──────┬───────┘          └──────┬───────┘
       │                         │
       └────────────┬────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│   MongoDB    │        │ File Storage │
│   Cluster    │        │   (S3/NFS)   │
│              │        │              │
│  - Primary   │        │ - Reports    │
│  - Secondary │        │ - Logs       │
└──────────────┘        └──────────────┘
```

---

## 11. Technology Stack Summary

### Frontend

- **Framework**: React 18+
- **Routing**: React Router v6
- **State Management**: React Context API
- **Styling**: Tailwind CSS 3.x
- **Charts**: Recharts
- **Maps**: react-simple-maps
- **HTTP Client**: Fetch API
- **Icons**: Lucide React

### Backend

- **Framework**: FastAPI 0.110+
- **Server**: Uvicorn (ASGI)
- **Language**: Python 3.13
- **Async Runtime**: AsyncIO
- **Validation**: Pydantic 2.7+

### AI/ML

- **LLM Provider**: Anthropic Claude API
- **Alternative**: OpenAI GPT-4 API
- **NLP**: Built-in LLM capabilities
- **Streaming**: Server-Sent Events (SSE)

### Database

- **Primary**: MongoDB 4.7+ (Motor driver)
- **Cache**: In-memory dictionaries
- **File Storage**: Local filesystem / S3

### DevOps

- **Package Manager**: npm (Frontend), pip (Backend)
- **Environment**: python-dotenv
- **CORS**: FastAPI CORS Middleware
- **Logging**: Python logging module

---

## 12. Performance Considerations

### Caching Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    Cache Hierarchy                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Level 1: In-Memory Cache (Frontend)               │    │
│  │  - Dashboard Data (Context API)                    │    │
│  │  - Session State                                    │    │
│  │  - Report List                                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Level 2: Application Cache (Backend)              │    │
│  │  - latest_world_data dict                          │    │
│  │  - Session lookup cache                            │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Level 3: Database (MongoDB)                       │    │
│  │  - Persistent storage                              │    │
│  │  - Historical data                                 │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Scalability Patterns

- **Horizontal Scaling**: Multiple FastAPI instances behind load balancer
- **Database Sharding**: MongoDB sharding for large datasets
- **Async Processing**: Non-blocking I/O for all operations
- **Streaming Responses**: SSE for real-time data delivery
- **Connection Pooling**: MongoDB connection reuse

---

## Conclusion

This design documentation provides a comprehensive overview of the SentriX platform architecture. The system follows modern best practices including:

1. **Microservices-oriented** agent architecture
2. **Event-driven** communication patterns
3. **Asynchronous** processing for scalability
4. **RESTful API** design with SSE streaming
5. **React-based** modern frontend
6. **NoSQL database** for flexible schema
7. **AI/LLM integration** for intelligent analysis
8. **Security-first** approach with multiple layers

The platform is designed to be:

- **Scalable**: Can handle increasing loads
- **Maintainable**: Clear separation of concerns
- **Extensible**: Easy to add new agents and features
- **Performant**: Async operations and caching
- **Secure**: Multiple security layers

---

**Document Version**: 1.0  
**Last Updated**: October 24, 2024  
**Maintained By**: SentriX Development Team



