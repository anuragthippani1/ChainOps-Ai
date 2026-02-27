from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class PoliticalRisk(BaseModel):
    country: str
    risk_type: str
    likelihood_score: int  # 0-5
    reasoning: str
    publication_date: str
    source_title: str
    source_url: str

class ScheduleRisk(BaseModel):
    equipment_id: str
    country: str
    original_delivery_date: str
    current_delivery_date: str
    delay_days: int
    risk_level: int  # 1-5
    risk_factors: List[str]

class RiskReport(BaseModel):
    report_id: str
    session_id: str
    report_type: str  # "political", "schedule", "combined", "route"
    created_at: datetime
    title: str
    executive_summary: str
    political_risks: Optional[List[PoliticalRisk]] = None
    schedule_risks: Optional[List[ScheduleRisk]] = None
    world_risk_data: Optional[Dict[str, Any]] = None
    recommendations: List[str] = []
    route_analysis: Optional[str] = None  # Full detailed route analysis (for route reports)

class DashboardData(BaseModel):
    world_risk_data: Dict[str, Any]
    political_risks: List[PoliticalRisk]
    schedule_risks: List[ScheduleRisk]
    total_reports: int
    active_sessions: int

class AgentResponse(BaseModel):
    agent_name: str
    response: Any
    confidence: float
    processing_time: float

class Session(BaseModel):
    session_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    report_count: int = 0
    last_activity: Optional[datetime] = None

class SessionCreate(BaseModel):
    # Make fields optional so backend can auto-generate when omitted
    name: Optional[str] = None
    description: Optional[str] = None

class SessionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
