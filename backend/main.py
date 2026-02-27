from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
# from sse_starlette.sse import EventSourceResponse  # Temporarily disabled
from dotenv import load_dotenv
import uvicorn
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime
import uuid

from agents.assistant_agent import AssistantAgent
from agents.chatbot_manager import ChatbotManager
from agents.scheduler_agent import SchedulerAgent
from agents.political_risk_agent import PoliticalRiskAgent
from agents.reporting_agent import ReportingAgent
from agents.route_planner_agent import RoutePlannerAgent
from database.mongodb import MongoDBClient
from models.schemas import QueryRequest, RiskReport, PoliticalRisk, ScheduleRisk, Session, SessionCreate, SessionUpdate

load_dotenv()  # load variables from backend/.env if present

app = FastAPI(title="ChainOps AI API", version="1.0.0")

# CORS middleware - Allow frontend origins
# For development/testing, allow all origins. For production, specify exact domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this later with specific Vercel URLs)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize agents
assistant_agent = AssistantAgent()
scheduler_agent = SchedulerAgent()
political_risk_agent = PoliticalRiskAgent()
reporting_agent = ReportingAgent()
chatbot_manager = ChatbotManager()
route_planner_agent = RoutePlannerAgent()

# Initialize database
db_client = MongoDBClient()

latest_world_data: Dict[str, Any] = {"world_risk_data": {}, "political_risks": [], "schedule_risks": []}
_subscribers: set = set()
_poll_task = None

async def _poll_world_data():
    global latest_world_data
    while True:
        try:
            countries = await scheduler_agent.extract_countries()
            political_risks = await political_risk_agent.analyze_risks(countries)
            schedule_risks = await scheduler_agent.analyze_schedule_risks()
            # combine
            world_risk_data = reporting_agent._create_combined_world_risk_data(political_risks, schedule_risks)
            latest_world_data = {
                "world_risk_data": world_risk_data,
                "political_risks": [r.dict() for r in political_risks],
                "schedule_risks": [r.dict() for r in schedule_risks],
                "timestamp": datetime.utcnow().isoformat()
            }
            # notify subscribers (they pull via SSE generator)
        except Exception as e:
            print("Polling error:", e)
        await asyncio.sleep(60)  # poll every minute

@app.on_event("startup")
async def startup_event():
    await db_client.connect()
    # global _poll_task
    # _poll_task = asyncio.create_task(_poll_world_data())  # Disabled for now

@app.on_event("shutdown")
async def shutdown_event():
    await db_client.disconnect()
    # global _poll_task
    # if _poll_task:
    #     _poll_task.cancel()

@app.get("/")
async def root():
    return {"message": "ChainOps AI API is running"}

@app.post("/api/shipment/upload")
async def upload_shipment_data(payload: Dict[str, Any]):
    """Accept shipment/equipment JSON array and load into SchedulerAgent."""
    try:
        data = payload.get("data") if isinstance(payload, dict) else None
        if data is None:
            # allow raw list body too
            if isinstance(payload, list):
                data = payload
        if not isinstance(data, list):
            raise HTTPException(status_code=400, detail="Body must contain a 'data' array or be an array itself")
        scheduler_agent.set_shipment_data(data)
        return {"status": "ok", "items": len(data)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/report/combined")
async def generate_combined_report():
    """Generate a combined report from current political + schedule risks."""
    try:
        session_id = str(uuid.uuid4())
        countries = await scheduler_agent.extract_countries()
        political_risks = await political_risk_agent.analyze_risks(countries)
        schedule_risks = await scheduler_agent.analyze_schedule_risks()
        report = await reporting_agent.generate_combined_report(political_risks, schedule_risks, session_id)
        await db_client.store_report(report)
        return {"session_id": session_id, "report": report, "type": "report"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/shipment/reset")
async def reset_shipment_data():
    scheduler_agent.clear_custom_data()
    return {"status": "ok"}

@app.post("/api/query")
async def process_query(request: QueryRequest):
    """Process natural language queries and route to appropriate agents"""
    try:
        # Use the session_id from the request, or generate a new one if not provided
        session_id = request.session_id or str(uuid.uuid4())
        text = request.query.lower()
        intent = chatbot_manager.classify_intent(text)
        
        if intent == "reject":
            response = await assistant_agent.process_query("offtopic")
            return {"session_id": session_id, "response": response, "type": "assistant"}
        
        message = ""  # Initialize message variable
        report = None
        
        if intent == "combined":
            countries = await scheduler_agent.extract_countries()
            political_risks = await political_risk_agent.analyze_risks(countries)
            schedule_risks = await scheduler_agent.analyze_schedule_risks()
            report = await reporting_agent.generate_combined_report(political_risks, schedule_risks, session_id)
            
            # Generate summary message
            high_pol_risk = sum(1 for r in political_risks if r.likelihood_score >= 3)
            high_sch_risk = sum(1 for r in schedule_risks if r.severity == "High")
            message = f"I've completed a comprehensive analysis covering {len(political_risks)} countries and {len(schedule_risks)} routes. "
            if high_pol_risk > 0:
                message += f"⚠️ {high_pol_risk} countries show high political risks. "
            if high_sch_risk > 0:
                message += f"🚨 {high_sch_risk} routes face severe delays. "
            message += f"The full combined report includes risk assessments, mitigation strategies, and actionable recommendations."
        elif intent == "political":
            countries = await scheduler_agent.extract_countries()
            political_risks = await political_risk_agent.analyze_risks(countries)
            report = await reporting_agent.generate_political_report(political_risks, session_id)
            
            # Generate detailed message with country information
            high_risk_countries = [r for r in political_risks if r.likelihood_score >= 3]
            medium_risk_countries = [r for r in political_risks if r.likelihood_score == 2]
            low_risk_countries = [r for r in political_risks if r.likelihood_score < 2]
            
            message = f"📊 **Political Risk Analysis for {len(political_risks)} Countries**\n\n"
            
            if high_risk_countries:
                message += f"🔴 **High Risk ({len(high_risk_countries)} countries):**\n"
                for risk in high_risk_countries[:5]:  # Show top 5
                    message += f"  • {risk.country}: {risk.risk_type} (Score: {risk.likelihood_score}/5)\n"
                if len(high_risk_countries) > 5:
                    message += f"  ... and {len(high_risk_countries) - 5} more\n"
                message += "\n"
            
            if medium_risk_countries:
                message += f"🟡 **Medium Risk ({len(medium_risk_countries)} countries):**\n"
                for risk in medium_risk_countries[:3]:  # Show top 3
                    message += f"  • {risk.country}: {risk.risk_type}\n"
                if len(medium_risk_countries) > 3:
                    message += f"  ... and {len(medium_risk_countries) - 3} more\n"
                message += "\n"
            
            if low_risk_countries:
                message += f"🟢 **Low Risk ({len(low_risk_countries)} countries)**\n\n"
            
            message += f"📋 A comprehensive report with detailed analysis and mitigation strategies has been generated."
            
        elif intent == "schedule":
            schedule_risks = await scheduler_agent.analyze_schedule_risks()
            report = await reporting_agent.generate_schedule_report(schedule_risks, session_id)
            
            # Generate detailed message with route information
            high_severity = [r for r in schedule_risks if r.severity == "High"]
            medium_severity = [r for r in schedule_risks if r.severity == "Medium"]
            low_severity = [r for r in schedule_risks if r.severity == "Low"]
            
            message = f"📊 **Schedule Risk Analysis for {len(schedule_risks)} Routes**\n\n"
            
            if high_severity:
                message += f"🔴 **High Severity Delays ({len(high_severity)} routes):**\n"
                for risk in high_severity[:5]:  # Show top 5
                    message += f"  • Route {risk.equipment_id}: {risk.delay_days} days delay\n"
                    message += f"    Reason: {risk.reason}\n"
                if len(high_severity) > 5:
                    message += f"  ... and {len(high_severity) - 5} more\n"
                message += "\n"
            
            if medium_severity:
                message += f"🟡 **Medium Severity ({len(medium_severity)} routes):**\n"
                for risk in medium_severity[:3]:  # Show top 3
                    message += f"  • Route {risk.equipment_id}: {risk.delay_days} days\n"
                if len(medium_severity) > 3:
                    message += f"  ... and {len(medium_severity) - 3} more\n"
                message += "\n"
            
            if low_severity:
                message += f"🟢 **Low Severity ({len(low_severity)} routes)**\n\n"
            
            message += f"📋 Common issues: Port congestion, weather delays, and customs processing. Full report generated."
            
        else:
            # Check if it's a route query
            if assistant_agent._is_route_query(text):
                # Get the detailed route analysis
                response_obj = await assistant_agent.process_query(request.query)
                # Extract just the message string from the response object
                message = response_obj.get("message", str(response_obj)) if isinstance(response_obj, dict) else str(response_obj)
                
                # Extract origin and destination for report generation
                words = text.split()
                origin = None
                destination = None
                if "from" in words and "to" in words:
                    from_idx = words.index("from")
                    to_idx = words.index("to")
                    if from_idx < to_idx and to_idx < len(words):
                        origin = " ".join(words[from_idx+1:to_idx])
                        destination = " ".join(words[to_idx+1:])
                
                # Generate route report if we have origin and destination
                if origin and destination:
                    report = await reporting_agent.generate_route_report(origin, destination, message, session_id)
                    await db_client.store_report(report)
                    return {"session_id": session_id, "report": report, "type": "route", "response": {"message": message}}
                else:
                    # Return just the message if we can't parse route
                    return {"session_id": session_id, "response": {"message": message}, "type": "assistant"}
            else:
                # For non-route queries, just return assistant response
                response_obj = await assistant_agent.process_query(request.query)
                # Extract just the message string from the response object
                message = response_obj.get("message", str(response_obj)) if isinstance(response_obj, dict) else str(response_obj)
                return {"session_id": session_id, "response": {"message": message}, "type": "assistant"}
        
        # Store report and return
        if report:
            await db_client.store_report(report)
            return {"session_id": session_id, "report": report, "type": "report", "response": {"message": message}}
        else:
            return {"session_id": session_id, "response": {"message": "Unable to generate report"}, "type": "error"}
            
    except Exception as e:
        print(f"❌ Error in process_query: {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()  # Print full traceback
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports")
async def get_reports():
    """Get all stored reports"""
    try:
        reports = await db_client.get_all_reports()
        return {"reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get specific report by ID"""
    try:
        report = await db_client.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/{report_id}/download")
async def download_report(report_id: str):
    """Download report as PDF/DOCX"""
    try:
        print(f"📥 Download request for report: {report_id}")
        report = await db_client.get_report(report_id)
        if not report:
            print(f"❌ Report not found: {report_id}")
            raise HTTPException(status_code=404, detail="Report not found")
        
        print(f"✅ Report found, generating PDF...")
        # Generate downloadable file
        file_path = await reporting_agent.generate_downloadable_report(report)
        print(f"✅ PDF generated at: {file_path}")
        
        import os
        if not os.path.exists(file_path):
            print(f"❌ File not found at path: {file_path}")
            raise HTTPException(status_code=500, detail="Generated file not found")
            
        return FileResponse(file_path, filename=f"chainops_report_{report_id}.pdf", media_type="application/pdf")
        
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/stream/dashboard")
# async def stream_dashboard():
#     # Temporarily disabled - requires sse_starlette
#     pass

def _serialize_risk(r):
    """Serialize Pydantic risk model to dict (v1 .dict() or v2 .model_dump())."""
    if hasattr(r, "model_dump"):
        try:
            return r.model_dump(mode="json")
        except TypeError:
            return r.model_dump()
    return r.dict()


# Additional countries for dashboard political risk coverage (Europe, South America, Africa)
# Merged with scheduler countries so live/sample data covers more regions
DASHBOARD_COUNTRIES_EUROPE = [
    "United Kingdom", "France", "Germany", "Italy", "Spain", "Netherlands", "Belgium", "Poland",
    "Sweden", "Austria", "Portugal", "Greece", "Romania", "Czech Republic", "Hungary", "Ireland",
    "Norway", "Finland", "Denmark", "Switzerland", "Ukraine", "Russia", "Belarus", "Serbia",
    "Croatia", "Bulgaria", "Slovakia", "Slovenia", "Lithuania", "Latvia", "Estonia", "Moldova",
    "Bosnia and Herzegovina", "Albania", "North Macedonia", "Montenegro", "Kosovo", "Luxembourg",
]
DASHBOARD_COUNTRIES_SOUTH_AMERICA = [
    "Brazil", "Argentina", "Chile", "Colombia", "Peru", "Ecuador", "Bolivia", "Venezuela",
    "Uruguay", "Paraguay", "Guyana", "Suriname",
]
DASHBOARD_COUNTRIES_AFRICA = [
    "South Africa", "Nigeria", "Kenya", "Egypt", "Morocco", "Ghana", "Tanzania", "Ethiopia",
    "Algeria", "Tunisia", "Angola", "Cameroon", "Senegal", "Ivory Coast", "Uganda", "Sudan",
    "Libya", "Zimbabwe", "Zambia", "Mozambique", "Madagascar", "Mali", "Burkina Faso", "Niger",
    "Chad", "Somalia", "Democratic Republic of the Congo", "Republic of the Congo", "Rwanda",
    "Botswana", "Namibia", "Mauritius", "Gabon", "Benin", "Togo", "Malawi", "Mauritania",
]


def _dashboard_static_response(static_world: Dict[str, Any]) -> Dict[str, Any]:
    """Return static dashboard payload when live fetch times out or fails."""
    return {
        "world_risk_data": static_world,
        "political_risks": [
            {"country": "Russia", "risk_type": "Geopolitical", "likelihood_score": 4, "reasoning": "Active military conflict in Ukraine with ongoing international sanctions.", "publication_date": datetime.utcnow().isoformat(), "source_title": "", "source_url": ""},
            {"country": "China", "risk_type": "Trade Policy", "likelihood_score": 3, "reasoning": "Ongoing trade tensions with Western countries.", "publication_date": datetime.utcnow().isoformat(), "source_title": "", "source_url": ""},
            {"country": "Iran", "risk_type": "Sanctions", "likelihood_score": 4, "reasoning": "Comprehensive international sanctions.", "publication_date": datetime.utcnow().isoformat(), "source_title": "", "source_url": ""},
            {"country": "Venezuela", "risk_type": "Political", "likelihood_score": 4, "reasoning": "Political and economic crisis.", "publication_date": datetime.utcnow().isoformat(), "source_title": "", "source_url": ""},
            {"country": "Pakistan", "risk_type": "Political", "likelihood_score": 3, "reasoning": "Political instability affecting trade.", "publication_date": datetime.utcnow().isoformat(), "source_title": "", "source_url": ""},
        ],
        "schedule_risks": [
            {"equipment_id": "EQ001", "country": "China", "original_delivery_date": "2024-02-15", "current_delivery_date": "2024-02-28", "delay_days": 13, "risk_level": 2, "risk_factors": ["Port congestion", "Customs delays"]},
            {"equipment_id": "EQ002", "country": "Germany", "original_delivery_date": "2024-01-30", "current_delivery_date": "2024-01-30", "delay_days": 0, "risk_level": 1, "risk_factors": ["On time"]},
            {"equipment_id": "EQ003", "country": "India", "original_delivery_date": "2024-03-01", "current_delivery_date": "2024-03-15", "delay_days": 14, "risk_level": 3, "risk_factors": ["Documentation issues", "Infrastructure delays"]},
            {"equipment_id": "EQ004", "country": "Japan", "original_delivery_date": "2024-02-20", "current_delivery_date": "2024-02-20", "delay_days": 0, "risk_level": 1, "risk_factors": ["On time"]},
            {"equipment_id": "EQ005", "country": "Brazil", "original_delivery_date": "2024-01-15", "current_delivery_date": "2024-02-05", "delay_days": 21, "risk_level": 2, "risk_factors": ["Port strikes", "Bureaucratic delays"]},
        ],
    }


@app.get("/api/dashboard")
async def get_dashboard_data():
    # Static base for full map coverage; live data overwrites where available
    static_world = {
        "Russia": {"risk_level": 4, "type": "political", "details": "Active conflict in Ukraine, international sanctions", "risk_factors": ["Sanctions", "Geopolitical Risk", "War"]},
        "Ukraine": {"risk_level": 4, "type": "political", "details": "Active military conflict", "risk_factors": ["Active Conflict", "Infrastructure Damage"]},
        "Iran": {"risk_level": 4, "type": "political", "details": "International sanctions, regional tensions", "risk_factors": ["Sanctions", "Political Instability"]},
        "North Korea": {"risk_level": 4, "type": "political", "details": "International isolation, sanctions", "risk_factors": ["Sanctions", "Political Risk"]},
        "Syria": {"risk_level": 4, "type": "political", "details": "Ongoing civil conflict", "risk_factors": ["Conflict", "Political Instability"]},
        "Afghanistan": {"risk_level": 4, "type": "political", "details": "Political instability, security concerns", "risk_factors": ["Political Instability", "Security Risk"]},
        "Yemen": {"risk_level": 4, "type": "political", "details": "Civil conflict, humanitarian crisis", "risk_factors": ["Conflict", "Humanitarian Crisis"]},
        "Myanmar": {"risk_level": 4, "type": "political", "details": "Political crisis, military rule", "risk_factors": ["Political Crisis", "Humanitarian Crisis"]},
        "Venezuela": {"risk_level": 4, "type": "political", "details": "Political and economic crisis", "risk_factors": ["Political Crisis", "Economic Crisis"]},
        "China": {"risk_level": 3, "type": "political", "details": "Trade tensions, regulatory changes", "risk_factors": ["Trade Policy", "Regulatory Changes"]},
        "Somalia": {"risk_level": 3, "type": "political", "details": "Security concerns, piracy risk", "risk_factors": ["Security Risk", "Political Instability"]},
        "Libya": {"risk_level": 3, "type": "political", "details": "Political instability", "risk_factors": ["Political Instability"]},
        "Sudan": {"risk_level": 3, "type": "political", "details": "Political transition", "risk_factors": ["Political Transition"]},
        "South Sudan": {"risk_level": 3, "type": "political", "details": "Internal conflict", "risk_factors": ["Internal Conflict"]},
        "Central African Republic": {"risk_level": 3, "type": "political", "details": "Security challenges", "risk_factors": ["Security Risk"]},
        "Mali": {"risk_level": 3, "type": "political", "details": "Security concerns", "risk_factors": ["Security Risk"]},
        "Burkina Faso": {"risk_level": 3, "type": "political", "details": "Security challenges", "risk_factors": ["Security Risk"]},
        "Niger": {"risk_level": 3, "type": "political", "details": "Regional instability", "risk_factors": ["Regional Instability"]},
        "Pakistan": {"risk_level": 3, "type": "political", "details": "Political instability", "risk_factors": ["Political Instability"]},
        "Lebanon": {"risk_level": 3, "type": "political", "details": "Economic crisis", "risk_factors": ["Economic Crisis"]},
        "Belarus": {"risk_level": 3, "type": "political", "details": "Political tensions", "risk_factors": ["Political Tensions"]},
        "Palestine": {"risk_level": 3, "type": "political", "details": "Political instability", "risk_factors": ["Political Instability"]},
        "Haiti": {"risk_level": 3, "type": "political", "details": "Political instability, security concerns", "risk_factors": ["Political Instability", "Security Risk"]},
        "United States": {"risk_level": 2, "type": "political", "details": "Policy uncertainty", "risk_factors": ["Policy Changes"]},
        "Germany": {"risk_level": 2, "type": "schedule", "details": "Supply chain delays", "risk_factors": ["Logistics Delays"]},
        "India": {"risk_level": 2, "type": "political", "details": "Regional tensions", "risk_factors": ["Regional Tensions"]},
        "Bangladesh": {"risk_level": 2, "type": "political", "details": "Political uncertainty", "risk_factors": ["Political Uncertainty"]},
        "Sri Lanka": {"risk_level": 2, "type": "political", "details": "Economic crisis", "risk_factors": ["Economic Crisis"]},
        "Nigeria": {"risk_level": 2, "type": "political", "details": "Security concerns", "risk_factors": ["Security Risk"]},
        "Japan": {"risk_level": 1, "type": "political", "details": "Stable environment", "risk_factors": ["Stable"]},
        "Brazil": {"risk_level": 2, "type": "political", "details": "Political uncertainty", "risk_factors": ["Political Uncertainty"]},
        "Canada": {"risk_level": 1, "type": "political", "details": "Stable environment", "risk_factors": ["Stable"]},
        "United Kingdom": {"risk_level": 1, "type": "political", "details": "Stable environment", "risk_factors": ["Stable"]},
        "France": {"risk_level": 1, "type": "political", "details": "Stable environment", "risk_factors": ["Stable"]},
        "Australia": {"risk_level": 1, "type": "political", "details": "Stable environment", "risk_factors": ["Stable"]},
        "Singapore": {"risk_level": 1, "type": "political", "details": "Stable environment", "risk_factors": ["Stable"]},
        "Mexico": {"risk_level": 2, "type": "political", "details": "Security concerns", "risk_factors": ["Security Risk"]},
        "South Africa": {"risk_level": 2, "type": "political", "details": "Economic challenges", "risk_factors": ["Economic Challenges"]},
    }
    # Return static dashboard data immediately so the UI always loads quickly.
    # Live data is used by /api/query and /api/report/combined when the user asks for reports.
    return _dashboard_static_response(static_world)


# Session Management Endpoints
@app.post("/api/sessions")
async def create_session(session_data: SessionCreate | None = None):
    """Create a new session. Name/description are optional; a random ID is always generated."""
    try:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()

        name = (session_data.name if session_data and session_data.name else f"Session {now.strftime('%H:%M:%S')}")
        description = (session_data.description if session_data else None)

        session = Session(
            session_id=session_id,
            name=name,
            description=description,
            created_at=now,
            updated_at=now,
            is_active=True,
            report_count=0,
            last_activity=now,
        )

        success = await db_client.create_session(session)
        if success:
            return {"session": session, "message": "Session created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create session")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
async def get_all_sessions():
    """Get all sessions"""
    try:
        sessions = await db_client.get_all_sessions()
        # Update report counts for each session
        for session in sessions:
            session.report_count = await db_client.get_session_report_count(session.session_id)
        
        return {"sessions": [session.dict() for session in sessions]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session"""
    try:
        session = await db_client.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update report count
        session.report_count = await db_client.get_session_report_count(session.session_id)
        
        return {"session": session.dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, session_data: SessionUpdate):
    """Update a session"""
    try:
        # Check if session exists
        existing_session = await db_client.get_session(session_id)
        if not existing_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Prepare updates
        updates = {}
        if session_data.name is not None:
            updates["name"] = session_data.name
        if session_data.description is not None:
            updates["description"] = session_data.description
        if session_data.is_active is not None:
            updates["is_active"] = session_data.is_active
        
        if updates:
            success = await db_client.update_session(session_id, updates)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to update session")
        
        # Return updated session
        updated_session = await db_client.get_session(session_id)
        updated_session.report_count = await db_client.get_session_report_count(session_id)
        
        return {"session": updated_session.dict(), "message": "Session updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        # Check if session exists
        existing_session = await db_client.get_session(session_id)
        if not existing_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        success = await db_client.delete_session(session_id)
        if success:
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete session")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}/reports")
async def get_session_reports(session_id: str):
    """Get all reports for a specific session"""
    try:
        # Check if session exists
        session = await db_client.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all reports for this session
        all_reports = await db_client.get_all_reports()
        session_reports = [report for report in all_reports if report.get('session_id') == session_id]
        
        return {"reports": session_reports, "session": session.dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# MULTI-PORT ROUTE PLANNING ENDPOINTS
# ============================================================

@app.post("/api/route/plan-multi-port")
async def plan_multi_port_route(request: Dict[str, Any]):
    """
    Plan a multi-port shipping route.
    
    Request body:
    {
        "ports": ["Port1", "Port2", "Port3", ...],
        "optimization": "fastest|cheapest|balanced|safest",
        "session_id": "optional"
    }
    """
    try:
        ports = request.get("ports", [])
        optimization = request.get("optimization", "balanced")
        session_id = request.get("session_id")
        
        if not ports or len(ports) < 2:
            raise HTTPException(status_code=400, detail="At least 2 ports are required")
        
        # Plan the route
        route_analysis = route_planner_agent.plan_multi_port_route(ports, optimization)
        
        if "error" in route_analysis:
            raise HTTPException(status_code=400, detail=route_analysis["error"])
        
        # Generate a report for this route
        report_id = str(uuid.uuid4())
        route_report = RiskReport(
            report_id=report_id,
            session_id=session_id or "default",
            report_type="multi_port_route",
            created_at=datetime.now(),
            title=f"Multi-Port Route: {' → '.join(ports)}",
            executive_summary=f"Multi-port route analysis for {len(ports)} ports: {' → '.join(ports)}. Total distance: {route_analysis['summary']['total_distance_nm']} nm, Estimated time: {route_analysis['summary']['total_time_days']} days, Total cost: ${route_analysis['summary']['total_cost_usd']:,.2f}.",
            recommendations=[
                f"Recommended optimization strategy: {optimization}",
                "Monitor weather conditions along the route",
                "Pre-book port slots to minimize wait times",
                "Consider alternative routes if delays occur"
            ],
            political_risks=[],
            schedule_risks=[],
            route_analysis=json.dumps(route_analysis)  # Store full route data as JSON
        )
        
        # Store report
        await db_client.store_report(route_report)
        
        return {
            "success": True,
            "report_id": report_id,
            "route_analysis": route_analysis,
            "message": f"Multi-port route planned successfully with {len(ports)} ports"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/route/optimize-order")
async def optimize_route_order(request: Dict[str, Any]):
    """
    Optimize the order of waypoints for a multi-port route.
    
    Request body:
    {
        "origin": "OriginPort",
        "destination": "DestinationPort",
        "waypoints": ["Port1", "Port2", "Port3", ...],
        "optimization": "fastest|cheapest|balanced"
    }
    """
    try:
        origin = request.get("origin")
        destination = request.get("destination")
        waypoints = request.get("waypoints", [])
        optimization = request.get("optimization", "balanced")
        
        if not origin or not destination:
            raise HTTPException(status_code=400, detail="Origin and destination are required")
        
        # Optimize the route order
        optimized_route = route_planner_agent.optimize_route_order(
            origin, destination, waypoints, optimization
        )
        
        # Get full analysis for optimized route
        route_analysis = route_planner_agent.plan_multi_port_route(optimized_route, optimization)
        
        return {
            "success": True,
            "original_ports": [origin] + waypoints + [destination],
            "optimized_ports": optimized_route,
            "route_analysis": route_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/route/compare")
async def compare_routes(request: Dict[str, Any]):
    """
    Compare two different multi-port routes.
    
    Request body:
    {
        "route1": ["Port1", "Port2", ...],
        "route2": ["Port1", "Port3", ...]
    }
    """
    try:
        route1 = request.get("route1", [])
        route2 = request.get("route2", [])
        
        if not route1 or not route2:
            raise HTTPException(status_code=400, detail="Both routes are required")
        
        if len(route1) < 2 or len(route2) < 2:
            raise HTTPException(status_code=400, detail="Each route must have at least 2 ports")
        
        # Compare the routes
        comparison = route_planner_agent.compare_routes(route1, route2)
        
        if "error" in comparison:
            raise HTTPException(status_code=400, detail=comparison["error"])
        
        return {
            "success": True,
            "comparison": comparison
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/route/ports")
async def get_available_ports():
    """Get list of all available ports"""
    try:
        from data.ports import get_all_port_names
        ports = get_all_port_names()
        return {"ports": ports, "total": len(ports)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/route/ports/search")
async def search_ports(query: str):
    """Search for ports by name or country"""
    try:
        from data.ports import search_ports
        results = search_ports(query)
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
