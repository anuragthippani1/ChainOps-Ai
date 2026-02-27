import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models.schemas import ScheduleRisk

class SchedulerAgent:
    def __init__(self):
        # Sample equipment schedule data
        self.sample_data = [
            {
                "equipment_id": "EQ001",
                "description": "Industrial Pump System",
                "country": "China",
                "supplier": "Shanghai Manufacturing Co.",
                "original_delivery_date": "2024-02-15",
                "current_delivery_date": "2024-02-28",
                "status": "delayed"
            },
            {
                "equipment_id": "EQ002", 
                "description": "Control Valves",
                "country": "Germany",
                "supplier": "Munich Controls GmbH",
                "original_delivery_date": "2024-01-30",
                "current_delivery_date": "2024-01-30",
                "status": "on_time"
            },
            {
                "equipment_id": "EQ003",
                "description": "Steel Pipes",
                "country": "India",
                "supplier": "Mumbai Steel Works",
                "original_delivery_date": "2024-03-01",
                "current_delivery_date": "2024-03-15",
                "status": "delayed"
            },
            {
                "equipment_id": "EQ004",
                "description": "Electrical Components",
                "country": "Japan",
                "supplier": "Tokyo Electronics",
                "original_delivery_date": "2024-02-20",
                "current_delivery_date": "2024-02-20",
                "status": "on_time"
            },
            {
                "equipment_id": "EQ005",
                "description": "Safety Equipment",
                "country": "Brazil",
                "supplier": "São Paulo Safety",
                "original_delivery_date": "2024-01-15",
                "current_delivery_date": "2024-02-05",
                "status": "delayed"
            }
        ]
        self._custom_data = None
    
    def set_shipment_data(self, data_list):
        """Replace current dataset with provided shipment/equipment list."""
        if not isinstance(data_list, list):
            raise ValueError("Shipment data must be a list of items")
        self._custom_data = data_list
    
    def clear_custom_data(self):
        """Revert to built-in sample data."""
        self._custom_data = None
    
    def _get_active_data(self):
        return self._custom_data if self._custom_data is not None else self.sample_data
    
    async def extract_countries(self) -> List[str]:
        """Extract unique countries from equipment data"""
        countries = list(set([item["country"] for item in self._get_active_data()]))
        return countries
    
    async def analyze_schedule_risks(self) -> List[ScheduleRisk]:
        """Analyze equipment schedule data for risks"""
        risks = []
        
        for item in self._get_active_data():
            # Calculate delay days
            original_date = datetime.strptime(item["original_delivery_date"], "%Y-%m-%d")
            current_date = datetime.strptime(item["current_delivery_date"], "%Y-%m-%d")
            delay_days = (current_date - original_date).days
            
            # Determine risk level (1-5)
            risk_level = self._calculate_risk_level(delay_days, item.get("status", "on_time"))
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(item, delay_days)
            
            risk = ScheduleRisk(
                equipment_id=item["equipment_id"],
                country=item["country"],
                original_delivery_date=item["original_delivery_date"],
                current_delivery_date=item["current_delivery_date"],
                delay_days=delay_days,
                risk_level=risk_level,
                risk_factors=risk_factors
            )
            risks.append(risk)
        
        return risks
    
    def _calculate_risk_level(self, delay_days: int, status: str) -> int:
        """Calculate risk level based on delay and status"""
        if status == "on_time":
            return 1
        elif delay_days <= 7:
            return 2
        elif delay_days <= 14:
            return 3
        elif delay_days <= 30:
            return 4
        else:
            return 5
    
    def _identify_risk_factors(self, item: Dict[str, Any], delay_days: int) -> List[str]:
        """Identify potential risk factors"""
        factors = []
        
        if delay_days > 0:
            factors.append("Delivery delay")
        
        if delay_days > 14:
            factors.append("Extended delay")
        
        if item["country"] in ["China", "India", "Brazil"]:
            factors.append("Emerging market risks")
        
        if delay_days > 30:
            factors.append("Critical delay")
        
        return factors
    
    async def get_equipment_by_country(self, country: str) -> List[Dict[str, Any]]:
        """Get equipment data filtered by country"""
        return [item for item in self._get_active_data() if item["country"] == country]
    
    async def get_high_risk_equipment(self) -> List[ScheduleRisk]:
        """Get equipment with high risk levels (4-5)"""
        all_risks = await self.analyze_schedule_risks()
        return [risk for risk in all_risks if risk.risk_level >= 4]
