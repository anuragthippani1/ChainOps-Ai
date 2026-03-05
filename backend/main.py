from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
# from sse_starlette.sse import EventSourceResponse  # Temporarily disabled
from dotenv import load_dotenv
import uvicorn
from typing import List, Dict, Any, Optional
import asyncio
import json
import re
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
from services.supply_chain_news_service import SupplyChainNewsService
from data.logistics_regions import build_world_risk_from_alerts, get_canonical_country

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

# Real-time supply chain news service (fetch every 10 min)
news_service = SupplyChainNewsService(db_client=db_client)
_news_scheduler_task = None
_disruption_cache: Dict[str, Any] = {"alerts": [], "ts": 0}
_DISRUPTION_CACHE_TTL = 60  # seconds
DEFAULT_DASHBOARD_POLITICAL_COUNTRIES = [
    "Russia",
    "China",
    "Iran",
    "Pakistan",
    "Venezuela",
    "India",
    "United States",
    "Saudi Arabia",
    "Germany",
    "Japan",
]

latest_world_data: Dict[str, Any] = {"world_risk_data": {}, "political_risks": [], "schedule_risks": []}
_subscribers: set = set()
_poll_task = None

async def _news_fetch_loop():
    """Fetch supply chain news every 10 minutes, filter keywords, store in MongoDB."""
    while True:
        try:
            await news_service.run_fetch_and_store()
        except Exception as e:
            print(f"News fetch error: {e}")
        await asyncio.sleep(600)  # 10 minutes


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
    global _news_scheduler_task
    _news_scheduler_task = asyncio.create_task(_news_fetch_loop())
    # Trigger initial fetch after 5 seconds (non-blocking)
    asyncio.create_task(_run_initial_news_fetch())

@app.on_event("shutdown")
async def shutdown_event():
    await db_client.disconnect()
    global _news_scheduler_task
    if _news_scheduler_task:
        _news_scheduler_task.cancel()
        try:
            await _news_scheduler_task
        except asyncio.CancelledError:
            pass


async def _run_initial_news_fetch():
    await asyncio.sleep(5)
    try:
        await news_service.run_fetch_and_store()
    except Exception as e:
        print(f"Initial news fetch: {e}")

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


def _response_payload(session_id: str, response_type: str, message: str, data: Optional[Dict[str, Any]] = None, **extras):
    payload = {
        "session_id": session_id,
        "type": response_type,
        "response": {
            "message": message,
        },
    }
    if data is not None:
        payload["response"]["data"] = data
    if extras:
        payload.update(extras)
    return payload


def _summarize_disruption_alerts(disruption_alerts: List[Dict[str, Any]]) -> tuple[str, Dict[str, Any]]:
    alerts = disruption_alerts or []
    if not alerts:
        msg = (
            "No major shipping disruptions are detected right now. "
            "Core trade lanes look stable, but continue monitoring weather, congestion, and labor actions."
        )
        return msg, {
            "affected_ports": [],
            "affected_countries": [],
            "disruption_types": [],
            "estimated_impact": "low",
            "disruption_count": 0,
            "latest_alert": None,
            "alerts": [],
        }

    affected_ports = sorted({a.get("port") for a in alerts if a.get("port")})
    affected_countries = sorted({a.get("country") for a in alerts if a.get("country")})
    disruption_types = sorted({
        sig
        for a in alerts
        for sig in (a.get("risk_signals") or [])
        if sig
    })
    risk_scores = [a.get("risk_score", 1) for a in alerts if isinstance(a.get("risk_score"), (int, float))]
    max_score = max(risk_scores) if risk_scores else 1
    avg_score = (sum(risk_scores) / len(risk_scores)) if risk_scores else 1
    latest_alert = sorted(
        alerts,
        key=lambda a: str(a.get("published_at") or ""),
        reverse=True,
    )[0]

    if max_score >= 4 or len(alerts) >= 10:
        impact = "high"
    elif max_score >= 3 or len(alerts) >= 5:
        impact = "medium"
    else:
        impact = "low"

    msg = (
        "Current shipping disruptions detected across global supply chains.\n"
        f"• Affected ports: {', '.join(affected_ports[:5]) if affected_ports else 'Not specified'}\n"
        f"• Affected countries: {', '.join(affected_countries[:6]) if affected_countries else 'Not specified'}\n"
        f"• Disruption types: {', '.join(disruption_types[:6]) if disruption_types else 'General logistics disruption'}\n"
        f"• Estimated impact on shipping: {impact} (avg risk {avg_score:.2f}/5, max {max_score}/5)"
    )
    return msg, {
        "affected_ports": affected_ports,
        "affected_countries": affected_countries,
        "disruption_types": disruption_types,
        "estimated_impact": impact,
        "avg_risk_score": round(avg_score, 2),
        "max_risk_score": max_score,
        "disruption_count": len(alerts),
        "latest_alert": latest_alert,
        "alerts": alerts,
    }


async def _build_assistant_context(query: str) -> Dict[str, Any]:
    q = (query or "").lower()
    context: Dict[str, Any] = {}

    if any(k in q for k in ["disruption", "delay", "congestion", "strike", "blockade", "weather", "typhoon", "hurricane", "cyclone"]):
        try:
            disruption_alerts = _get_disruption_alerts_cached()
            if not disruption_alerts:
                await _refresh_disruption_cache()
                disruption_alerts = _disruption_cache["alerts"]
            _, disruption_data = _summarize_disruption_alerts(disruption_alerts)
            context["disruption_summary"] = disruption_data
        except Exception as disruption_error:
            print(f"Assistant disruption context failed: {disruption_error}")

    if any(k in q for k in ["political", "geopolit", "sanction", "tariff", "middle east", "suez", "hormuz", "red sea", "risk"]):
        try:
            if "middle east" in q or any(k in q for k in ["suez", "hormuz", "red sea"]):
                countries = ["Saudi Arabia", "United Arab Emirates", "Qatar", "Kuwait", "Oman", "Iraq", "Iran", "Egypt", "Turkey", "Yemen"]
            else:
                countries = await scheduler_agent.extract_countries()
            political_risks = await political_risk_agent.analyze_risks(countries[:20])
            high_risk = [r for r in political_risks if r.likelihood_score >= 4]
            avg_score = round(sum(r.likelihood_score for r in political_risks) / len(political_risks), 2) if political_risks else 0
            context["political_summary"] = {
                "countries_analyzed": len(political_risks),
                "high_risk_count": len(high_risk),
                "average_score": avg_score,
                "top_countries": [r.country for r in high_risk[:5]],
            }
        except Exception as political_error:
            print(f"Assistant political context failed: {political_error}")

    if any(k in q for k in ["cargo delay", "delivery", "schedule", "customs", "delay", "lead time"]):
        try:
            schedule_risks = await scheduler_agent.analyze_schedule_risks()
            high_delay = [r for r in schedule_risks if r.risk_level >= 4]
            avg_delay = round(sum(r.delay_days for r in schedule_risks) / len(schedule_risks), 2) if schedule_risks else 0
            context["schedule_summary"] = {
                "routes_analyzed": len(schedule_risks),
                "high_delay_routes": len(high_delay),
                "average_delay_days": avg_delay,
            }
        except Exception as schedule_error:
            print(f"Assistant schedule context failed: {schedule_error}")

    return context


@app.post("/api/query")
async def process_query(request: QueryRequest):
    """Process natural language queries and route to appropriate agents"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        text = request.query.lower()
        intent = chatbot_manager.classify_intent(text)

        if intent == "reject":
            response = await assistant_agent.process_query("offtopic", context={"intent": "reject"})
            message = response.get("message", "I can help with logistics and supply chain questions.")
            return _response_payload(session_id, "assistant", message, {"intent": "reject"})

        if intent == "combined":
            countries = await scheduler_agent.extract_countries()
            political_risks = await political_risk_agent.analyze_risks(countries)
            schedule_risks = await scheduler_agent.analyze_schedule_risks()
            report = await reporting_agent.generate_combined_report(political_risks, schedule_risks, session_id)

            high_pol_risk = sum(1 for r in political_risks if r.likelihood_score >= 3)
            high_sch_risk = sum(1 for r in schedule_risks if r.risk_level >= 4)
            message = f"I've completed a comprehensive analysis covering {len(political_risks)} countries and {len(schedule_risks)} routes. "
            if high_pol_risk > 0:
                message += f"⚠️ {high_pol_risk} countries show high political risks. "
            if high_sch_risk > 0:
                message += f"🚨 {high_sch_risk} routes face severe delays. "
            message += "The full combined report includes risk assessments, mitigation strategies, and actionable recommendations."

            await db_client.store_report(report)
            return _response_payload(
                session_id,
                "assistant",
                message,
                {
                    "intent": "combined",
                    "report_id": report.report_id,
                    "report_type": "combined",
                    "political_risk_count": len(political_risks),
                    "schedule_risk_count": len(schedule_risks),
                },
                report=report,
            )

        elif intent == "political":
            countries = await scheduler_agent.extract_countries()
            political_risks = await political_risk_agent.analyze_risks(countries)
            report = await reporting_agent.generate_political_report(political_risks, session_id)

            high_risk_countries = [r for r in political_risks if r.likelihood_score >= 3]
            medium_risk_countries = [r for r in political_risks if r.likelihood_score == 2]
            low_risk_countries = [r for r in political_risks if r.likelihood_score < 2]

            message = f"📊 **Political Risk Analysis for {len(political_risks)} Countries**\n\n"

            if high_risk_countries:
                message += f"🔴 **High Risk ({len(high_risk_countries)} countries):**\n"
                for risk in high_risk_countries[:5]:
                    message += f"  • {risk.country}: {risk.risk_type} (Score: {risk.likelihood_score}/5)\n"
                if len(high_risk_countries) > 5:
                    message += f"  ... and {len(high_risk_countries) - 5} more\n"
                message += "\n"

            if medium_risk_countries:
                message += f"🟡 **Medium Risk ({len(medium_risk_countries)} countries):**\n"
                for risk in medium_risk_countries[:3]:
                    message += f"  • {risk.country}: {risk.risk_type}\n"
                if len(medium_risk_countries) > 3:
                    message += f"  ... and {len(medium_risk_countries) - 3} more\n"
                message += "\n"

            if low_risk_countries:
                message += f"🟢 **Low Risk ({len(low_risk_countries)} countries)**\n\n"

            message += f"📋 A comprehensive report with detailed analysis and mitigation strategies has been generated."

            await db_client.store_report(report)
            return _response_payload(
                session_id,
                "political",
                message,
                {
                    "intent": "political",
                    "report_id": report.report_id,
                    "countries_analyzed": len(political_risks),
                    "high_risk_count": len(high_risk_countries),
                },
                report=report,
            )

        elif intent == "schedule":
            schedule_risks = await scheduler_agent.analyze_schedule_risks()
            report = await reporting_agent.generate_schedule_report(schedule_risks, session_id)

            high_severity = [r for r in schedule_risks if r.risk_level >= 4]
            medium_severity = [r for r in schedule_risks if r.risk_level == 3]
            low_severity = [r for r in schedule_risks if r.risk_level <= 2]

            message = f"📊 **Schedule Risk Analysis for {len(schedule_risks)} Routes**\n\n"

            if high_severity:
                message += f"🔴 **High Severity Delays ({len(high_severity)} routes):**\n"
                for risk in high_severity[:5]:
                    factors = ", ".join(risk.risk_factors) if risk.risk_factors else "No factors available"
                    message += f"  • Route {risk.equipment_id}: {risk.delay_days} days delay\n"
                    message += f"    Risk Factors: {factors}\n"
                if len(high_severity) > 5:
                    message += f"  ... and {len(high_severity) - 5} more\n"
                message += "\n"

            if medium_severity:
                message += f"🟡 **Medium Severity ({len(medium_severity)} routes):**\n"
                for risk in medium_severity[:3]:
                    message += f"  • Route {risk.equipment_id}: {risk.delay_days} days\n"
                if len(medium_severity) > 3:
                    message += f"  ... and {len(medium_severity) - 3} more\n"
                message += "\n"

            if low_severity:
                message += f"🟢 **Low Severity ({len(low_severity)} routes)**\n\n"

            message += f"📋 Common issues: Port congestion, weather delays, and customs processing. Full report generated."

            await db_client.store_report(report)
            return _response_payload(
                session_id,
                "schedule",
                message,
                {
                    "intent": "schedule",
                    "report_id": report.report_id,
                    "route_count": len(schedule_risks),
                    "high_risk_count": len(high_severity),
                },
                report=report,
            )

        elif intent == "disruption":
            disruption_alerts = _get_disruption_alerts_cached()
            if not disruption_alerts:
                await _refresh_disruption_cache()
                disruption_alerts = _disruption_cache["alerts"]

            message, disruption_data = _summarize_disruption_alerts(disruption_alerts)
            return _response_payload(session_id, "disruption", message, disruption_data)

        else:
            if assistant_agent._is_route_query(text):
                route_resolution = assistant_agent.resolve_ports_from_query(request.query)
                origin = route_resolution.get("origin_input")
                destination = route_resolution.get("destination_input")
                origin_port = route_resolution.get("origin_port")
                destination_port = route_resolution.get("destination_port")

                if not origin or not destination:
                    return _response_payload(
                        session_id,
                        "assistant",
                        "Please specify origin and destination like: 'Route from Shanghai to Los Angeles'.",
                        {"intent": "route"},
                    )

                if not origin_port or not destination_port:
                    return _response_payload(
                        session_id,
                        "assistant",
                        (
                            f"I could not map '{origin}' and '{destination}' to known major ports. "
                            "Please specify ports directly, for example: 'Route from Hamburg to Mumbai'."
                        ),
                        {
                            "intent": "route",
                            "origin_input": origin,
                            "destination_input": destination,
                            "origin_port": origin_port,
                            "destination_port": destination_port,
                        },
                    )

                optimization = _extract_route_optimization(request.query)
                try:
                    planner_result = await plan_multi_port_route(
                        {
                            "ports": [origin_port, destination_port],
                            "optimization": optimization,
                            "session_id": session_id,
                        }
                    )
                except HTTPException as route_error:
                    fallback_context = {
                        "route_error": route_error.detail,
                        "route_origin": origin,
                        "route_destination": destination,
                    }
                    assistant_fallback = await assistant_agent.process_query(request.query, context=fallback_context)
                    fallback_message = assistant_fallback.get(
                        "message",
                        f"Unable to plan route from {origin} to {destination}: {route_error.detail}",
                    )
                    return _response_payload(
                        session_id,
                        "assistant",
                        fallback_message,
                        {
                            "intent": "route",
                            "route_error": route_error.detail,
                            "origin_input": origin,
                            "destination_input": destination,
                            "origin_port": origin_port,
                            "destination_port": destination_port,
                        },
                    )

                route_analysis = planner_result.get("route_analysis", {})
                route_data = _build_route_response(route_analysis)
                message = _summarize_route_from_planner(route_data)

                if route_resolution.get("origin_resolved_from_country") or route_resolution.get("destination_resolved_from_country"):
                    origin_country = route_resolution.get("origin_country") or origin
                    destination_country = route_resolution.get("destination_country") or destination
                    optimization_prefix = {
                        "fastest": "fastest",
                        "cheapest": "most cost-efficient",
                        "safest": "safest",
                        "balanced": "balanced",
                    }.get(optimization, "balanced")
                    canals = route_data.get("canals_crossed", []) or []
                    via_segment = f" via {canals[0]}" if canals else ""
                    country_message = (
                        f"The {optimization_prefix} maritime route from {origin_country} to {destination_country} "
                        f"typically runs from {origin_port} to {destination_port}{via_segment}."
                    )
                    message = f"{country_message} {message}"

                return _response_payload(
                    session_id,
                    "route",
                    message,
                    {
                        "intent": "route",
                        "origin_input": origin,
                        "destination_input": destination,
                        "origin_port": origin_port,
                        "destination_port": destination_port,
                        "resolved_from_country": bool(
                            route_resolution.get("origin_resolved_from_country")
                            or route_resolution.get("destination_resolved_from_country")
                        ),
                        "route_data": route_data,
                        "route_analysis": route_analysis,
                        "report_id": planner_result.get("report_id"),
                    },
                    report_id=planner_result.get("report_id"),
                    route_analysis=route_analysis,
                    route_data=route_data,
                )

            assistant_context = await _build_assistant_context(request.query)
            response_obj = await assistant_agent.process_query(request.query, context=assistant_context)
            message = response_obj.get("message", str(response_obj)) if isinstance(response_obj, dict) else str(response_obj)
            return _response_payload(
                session_id,
                "assistant",
                message,
                {"intent": "assistant", "context_keys": list(assistant_context.keys())},
            )

    except Exception as e:
        print(f"❌ Error in process_query: {str(e)}")
        import traceback
        traceback.print_exc()
        return _response_payload(
            request.session_id or str(uuid.uuid4()),
            "assistant",
            "I encountered an internal processing issue but I can still help with routes, shipping risks, or logistics questions.",
            {"error": str(e)},
        )

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


# Only show alerts with these categories (logistics/shipment only)
ALLOWED_DISRUPTION_CATEGORIES = {"maritime", "freight", "port disruption", "customs delay"}


def _get_disruption_alerts_cached() -> List[Dict[str, Any]]:
    """Get disruption alerts with 60s cache to respect API limits."""
    global _disruption_cache
    now = datetime.utcnow().timestamp()
    if _disruption_cache["alerts"] and (now - _disruption_cache["ts"]) < _DISRUPTION_CACHE_TTL:
        return _disruption_cache["alerts"]
    return []


async def _refresh_disruption_cache():
    """Refresh disruption alerts from DB (last 24h). Only maritime, freight, port, customs."""
    global _disruption_cache
    try:
        raw = await db_client.get_supply_chain_news_last_24h()
        alerts = [a for a in raw if (a.get("category") or "").lower() in ALLOWED_DISRUPTION_CATEGORIES]
        _disruption_cache["alerts"] = alerts
        _disruption_cache["ts"] = datetime.utcnow().timestamp()
    except Exception as e:
        print(f"Error refreshing disruption cache: {e}")


async def _get_dashboard_political_risks(countries: List[str]) -> List[Dict[str, Any]]:
    """
    Generate political risks for dashboard countries.
    Falls back to sample-news based generation if the main analysis fails.
    """
    selected_countries = countries or DEFAULT_DASHBOARD_POLITICAL_COUNTRIES
    try:
        risks = await political_risk_agent.analyze_risks(selected_countries)
        if risks:
            return [_serialize_risk(r) for r in risks]
    except Exception as e:
        print(f"Dashboard political risk generation failed: {e}")

    fallback_risks: List[PoliticalRisk] = []
    for country in selected_countries:
        try:
            sample_articles = political_risk_agent._get_sample_news_data(country)
            sample_country_risks = await political_risk_agent._analyze_articles_for_risks(sample_articles, country)
            if sample_country_risks:
                fallback_risks.extend(sample_country_risks)
            else:
                fallback_risks.append(
                    PoliticalRisk(
                        country=country,
                        risk_type="General Economic Risk",
                        likelihood_score=1,
                        reasoning=f"Sample monitoring data used for {country}.",
                        publication_date=datetime.utcnow().isoformat(),
                        source_title="Sample Monitoring",
                        source_url="",
                    )
                )
        except Exception as fallback_error:
            print(f"Fallback political risk generation failed for {country}: {fallback_error}")
            fallback_risks.append(
                PoliticalRisk(
                    country=country,
                    risk_type="General Economic Risk",
                    likelihood_score=1,
                    reasoning=f"Fallback monitoring used due to data fetch error for {country}.",
                    publication_date=datetime.utcnow().isoformat(),
                    source_title="Fallback Monitoring",
                    source_url="",
                )
            )

    return [_serialize_risk(r) for r in fallback_risks]


@app.get("/api/news/disruptions")
async def get_disruption_alerts():
    """
    Latest supply chain disruption alerts from last 24 hours.
    Cached for 60 seconds to respect API limits.
    Includes: summary, source link, timestamp, risk severity.
    """
    try:
        cached = _get_disruption_alerts_cached()
        if cached:
            return {"alerts": cached, "cached": True, "count": len(cached)}

        await _refresh_disruption_cache()
        return {"alerts": _disruption_cache["alerts"], "cached": False, "count": len(_disruption_cache["alerts"])}
    except Exception as e:
        return {"alerts": [], "cached": False, "count": 0, "error": str(e)}


@app.post("/api/news/refresh")
async def trigger_news_refresh():
    """Manually trigger a news fetch (respects rate limits)."""
    try:
        count = await news_service.run_fetch_and_store()
        await _refresh_disruption_cache()
        return {"status": "ok", "stored": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _dashboard_static_response(
    disruption_alerts: Optional[List[Dict]] = None,
    political_risks: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Return dashboard payload. world_risk_data = logistics disruptions + political overlay."""
    world_risk_data = build_world_risk_from_alerts(disruption_alerts or [], political_risks or [])
    payload = {
        "world_risk_data": world_risk_data,
        "political_risks": political_risks or [],
        "schedule_risks": [
            {"equipment_id": "EQ001", "country": "China", "original_delivery_date": "2024-02-15", "current_delivery_date": "2024-02-28", "delay_days": 13, "risk_level": 2, "risk_factors": ["Port congestion", "Customs delays"]},
            {"equipment_id": "EQ002", "country": "Germany", "original_delivery_date": "2024-01-30", "current_delivery_date": "2024-01-30", "delay_days": 0, "risk_level": 1, "risk_factors": ["On time"]},
            {"equipment_id": "EQ003", "country": "India", "original_delivery_date": "2024-03-01", "current_delivery_date": "2024-03-15", "delay_days": 14, "risk_level": 3, "risk_factors": ["Documentation issues", "Infrastructure delays"]},
            {"equipment_id": "EQ004", "country": "Japan", "original_delivery_date": "2024-02-20", "current_delivery_date": "2024-02-20", "delay_days": 0, "risk_level": 1, "risk_factors": ["On time"]},
            {"equipment_id": "EQ005", "country": "Brazil", "original_delivery_date": "2024-01-15", "current_delivery_date": "2024-02-05", "delay_days": 21, "risk_level": 2, "risk_factors": ["Port strikes", "Bureaucratic delays"]},
        ],
    }
    payload["disruption_alerts"] = disruption_alerts or []
    return payload


@app.get("/api/dashboard")
async def get_dashboard_data():
    """Dashboard: world_risk_data = full logistics regions + disruption overlays."""
    disruption_alerts = _get_disruption_alerts_cached()
    if not disruption_alerts:
        await _refresh_disruption_cache()
        disruption_alerts = _disruption_cache["alerts"]
    political_risks = await _get_dashboard_political_risks(DEFAULT_DASHBOARD_POLITICAL_COUNTRIES)
    return _dashboard_static_response(disruption_alerts, political_risks)


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

def _score_to_risk_label(score: float) -> str:
    if score >= 4:
        return "critical"
    if score >= 3:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def _level_to_score(level: Any) -> float:
    if isinstance(level, (int, float)):
        return float(level)
    return 1.0


def _extract_route_origin_destination(query: str) -> tuple[Optional[str], Optional[str]]:
    """Extract origin/destination from free text: 'from X to Y'."""
    q = (query or "").strip()
    patterns = [
        r"\bfrom\s+(.+?)\s+to\s+(.+?)(?:\s+with\b|\s+priority\b|\s*\(|$)",
        r"\broute\s+(.+?)\s+to\s+(.+?)(?:\s+with\b|\s+priority\b|\s*\(|$)",
    ]
    for pattern in patterns:
        m = re.search(pattern, q, flags=re.I)
        if m:
            origin = (m.group(1) or "").strip(" ,.;:!?")
            destination = (m.group(2) or "").strip(" ,.;:!?")
            if origin and destination:
                return origin, destination
    return None, None


def _extract_route_optimization(query: str) -> str:
    """Infer optimization profile from user query text."""
    q = (query or "").lower()
    if "priority: speed" in q or "fastest" in q or "speed priority" in q:
        return "fastest"
    if "priority: cost" in q or "cheapest" in q or "cost optimization" in q:
        return "cheapest"
    if "priority: safety" in q or "safest" in q or "safety first" in q:
        return "safest"
    return "balanced"


def _build_route_response(route_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Return normalized route payload for frontend/chat consumers."""
    summary = route_analysis.get("summary", {}) if isinstance(route_analysis, dict) else {}
    final_risk_score = float(route_analysis.get("final_risk_score", 1) or 1)
    return {
        "route": route_analysis.get("route", "Unknown"),
        "total_distance": route_analysis.get("total_distance", summary.get("total_distance_nm", 0)),
        "estimated_time": route_analysis.get("estimated_time", summary.get("total_time_days", 0)),
        "legs": route_analysis.get("legs", []),
        "canals_crossed": summary.get("canals_used", []),
        "risk_level": _score_to_risk_label(final_risk_score),
        "final_risk_score": final_risk_score,
        "overall_risk_score": float(route_analysis.get("overall_risk_score", final_risk_score) or final_risk_score),
        "operational_risk_score": float(route_analysis.get("operational_risk_score", 1) or 1),
        "chokepoints": route_analysis.get("chokepoints", []),
        "disruption_alerts": route_analysis.get("disruption_alerts", []),
        "political_risks": route_analysis.get("political_risks", []),
        "cost_estimation": route_analysis.get("cost_estimation", {
            "currency": "USD",
            "total_cost_usd": summary.get("total_cost_usd", 0),
            "breakdown_usd": summary.get("cost_breakdown_usd", {}),
        }),
        "emissions_estimation": route_analysis.get("emissions_estimation", {
            "estimated_co2_tons": summary.get("estimated_co2_tons", 0),
        }),
        "weather_conditions": route_analysis.get("weather_conditions", summary.get("weather_overview", {})),
        "congestion_risk": route_analysis.get("congestion_risk", summary.get("congestion_risk", {})),
        "timeline_summary": route_analysis.get("timeline_summary", summary.get("timeline_summary", [])),
    }


def _summarize_route_from_planner(route_data: Dict[str, Any]) -> str:
    """Deterministic summary from planner output only (no fabricated values)."""
    route = route_data.get("route", "Unknown route")
    distance = route_data.get("total_distance", 0)
    eta = route_data.get("estimated_time", 0)
    final_score = route_data.get("final_risk_score", 1)
    risk_level = route_data.get("risk_level", "low")
    canals = route_data.get("canals_crossed", []) or []
    chokepoints = route_data.get("chokepoints", []) or []
    disruptions = route_data.get("disruption_alerts", []) or []
    pol_count = len(route_data.get("political_risks", []) or [])
    total_cost = (
        (route_data.get("cost_estimation") or {}).get("total_cost_usd")
        if isinstance(route_data.get("cost_estimation"), dict)
        else None
    )
    co2_tons = (
        (route_data.get("emissions_estimation") or {}).get("estimated_co2_tons")
        if isinstance(route_data.get("emissions_estimation"), dict)
        else None
    )
    canal_text = ", ".join(canals) if canals else "None"
    chokepoint_text = ", ".join(chokepoints) if chokepoints else "None"
    cost_text = f"${float(total_cost):,.0f}" if isinstance(total_cost, (int, float)) else "N/A"
    co2_text = f"{float(co2_tons):,.1f} tCO2" if isinstance(co2_tons, (int, float)) else "N/A"
    return (
        f"Route analysis complete for {route}. Distance: {distance} nm; estimated time: {eta} days; "
        f"final risk: {risk_level} ({final_score}/5). Estimated cost: {cost_text}; emissions: {co2_text}. "
        f"Canals crossed: {canal_text}. "
        f"Chokepoints: {chokepoint_text}. Related disruption alerts: {len(disruptions)}. "
        f"Related political risks: {pol_count}."
    )


def _enrich_route_with_risks(
    route_analysis: Dict[str, Any],
    disruption_alerts: List[Dict[str, Any]],
    political_risks: List[Dict[str, Any]],
    world_risk_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Overlay political/disruption risk signals onto each route leg."""
    legs = route_analysis.get("legs", [])
    if not isinstance(legs, list):
        legs = []

    political_score_by_country: Dict[str, float] = {}
    for p in political_risks or []:
        country = get_canonical_country((p.get("country") or "").strip())
        score = p.get("likelihood_score")
        if not country or not isinstance(score, (int, float)):
            continue
        political_score_by_country[country] = max(float(score), political_score_by_country.get(country, 1.0))

    disruption_score_by_country: Dict[str, float] = {}
    alerts_by_country: Dict[str, List[Dict[str, Any]]] = {}
    for a in disruption_alerts or []:
        country = get_canonical_country((a.get("country") or "").strip())
        score = a.get("risk_score")
        if not country:
            continue
        if isinstance(score, (int, float)):
            disruption_score_by_country[country] = max(float(score), disruption_score_by_country.get(country, 1.0))
        alerts_by_country.setdefault(country, []).append(a)

    existing_chokepoints = route_analysis.get("chokepoints", [])
    chokepoints = list(dict.fromkeys(existing_chokepoints if isinstance(existing_chokepoints, list) else []))
    chokepoint_country_map = {
        "Suez Canal": ["Egypt"],
        "Panama Canal": ["Panama"],
        "Strait of Hormuz": ["Iran", "United Arab Emirates"],
        "Strait of Malacca": ["Singapore", "Malaysia"],
        "Bab el-Mandeb": ["Yemen", "Djibouti"],
    }
    route_countries = set()
    final_risk_score = 1.0
    route_operational_risk = 1.0

    for leg in legs:
        from_country = get_canonical_country((leg.get("from_country") or "").strip())
        to_country = get_canonical_country((leg.get("to_country") or "").strip())
        leg["from_country"] = from_country
        leg["to_country"] = to_country

        countries_crossed = [c for c in [from_country, to_country] if c]
        canal_name = leg.get("canal_name")
        if canal_name == "Suez Canal":
            countries_crossed.append("Egypt")
            if "Suez Canal" not in chokepoints:
                chokepoints.append("Suez Canal")
        elif canal_name == "Panama Canal":
            countries_crossed.append("Panama")
            if "Panama Canal" not in chokepoints:
                chokepoints.append("Panama Canal")

        for cp in leg.get("chokepoints_nearby", []) or []:
            cp_name = cp.get("name")
            if not cp_name:
                continue
            if cp_name not in chokepoints:
                chokepoints.append(cp_name)
            for cp_country in chokepoint_country_map.get(cp_name, []):
                countries_crossed.append(cp_country)

        # Preserve order while deduping.
        countries_crossed = list(dict.fromkeys(countries_crossed))
        leg["countries_crossed"] = countries_crossed
        for c in countries_crossed:
            route_countries.add(c)

        political_scores = []
        disruption_scores = []
        for c in countries_crossed:
            world_level = _level_to_score((world_risk_data.get(c) or {}).get("risk_level", 1))
            political_scores.append(political_score_by_country.get(c, world_level))
            disruption_scores.append(disruption_score_by_country.get(c, 1.0))

        political_risk = max(political_scores) if political_scores else 1.0
        disruption_risk = max(disruption_scores) if disruption_scores else 1.0
        operational_risk = float(leg.get("operational_risk_score", 1.0) or 1.0)
        leg_risk = max(political_risk, disruption_risk, operational_risk)
        final_risk_score = max(final_risk_score, leg_risk)
        route_operational_risk = max(route_operational_risk, operational_risk)

        leg["political_risk_score"] = round(political_risk, 2)
        leg["disruption_risk_score"] = round(disruption_risk, 2)
        leg["operational_risk_score"] = round(operational_risk, 2)
        leg["leg_risk_score"] = round(leg_risk, 2)
        leg["risk_level"] = _score_to_risk_label(leg_risk)

        related_alerts = []
        for c in countries_crossed:
            for a in alerts_by_country.get(c, []):
                related_alerts.append({
                    "country": c,
                    "title": a.get("title"),
                    "summary": a.get("summary"),
                    "risk_score": a.get("risk_score"),
                    "published_at": a.get("published_at"),
                })
        leg["relevant_disruption_alerts"] = related_alerts[:3]

    relevant_disruption_alerts = []
    for c in route_countries:
        for a in alerts_by_country.get(c, []):
            relevant_disruption_alerts.append(a)

    relevant_political_risks = [
        p for p in (political_risks or [])
        if get_canonical_country((p.get("country") or "").strip()) in route_countries
    ]

    route_analysis["route"] = " → ".join(route_analysis.get("ports", []))
    route_analysis["total_distance"] = route_analysis.get("summary", {}).get("total_distance_nm", 0)
    route_analysis["estimated_time"] = route_analysis.get("summary", {}).get("total_time_days", 0)
    route_analysis["chokepoints"] = chokepoints
    route_analysis["disruption_alerts"] = relevant_disruption_alerts
    route_analysis["political_risks"] = relevant_political_risks
    route_analysis["final_risk_score"] = round(final_risk_score, 2)
    route_analysis["operational_risk_score"] = round(route_operational_risk, 2)
    route_analysis["overall_risk_score"] = round(final_risk_score, 2)

    return route_analysis


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

        # Pull current disruption + political context and fuse into route legs.
        disruption_alerts = _get_disruption_alerts_cached()
        if not disruption_alerts:
            await _refresh_disruption_cache()
            disruption_alerts = _disruption_cache["alerts"]

        route_countries = set()
        for leg in route_analysis.get("legs", []):
            from_c = get_canonical_country((leg.get("from_country") or "").strip())
            to_c = get_canonical_country((leg.get("to_country") or "").strip())
            if from_c:
                route_countries.add(from_c)
            if to_c:
                route_countries.add(to_c)
        selected_countries = list(route_countries) or DEFAULT_DASHBOARD_POLITICAL_COUNTRIES
        political_risks = await _get_dashboard_political_risks(selected_countries)
        world_risk_data = build_world_risk_from_alerts(disruption_alerts or [], political_risks or [])
        route_analysis = _enrich_route_with_risks(
            route_analysis,
            disruption_alerts or [],
            political_risks or [],
            world_risk_data or {},
        )
        
        # Generate a report for this route
        report_id = str(uuid.uuid4())
        print("Saving route report:", report_id)
        print("Session:", session_id)
        route_report = RiskReport(
            report_id=report_id,
            session_id=session_id if session_id else "default",
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
