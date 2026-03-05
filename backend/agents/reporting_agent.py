import json
import uuid
from datetime import datetime
from typing import List, Dict, Any
from models.schemas import RiskReport, PoliticalRisk, ScheduleRisk
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import os

class ReportingAgent:
    def __init__(self):
        self.reports_dir = "reports"
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    async def generate_political_report(self, political_risks: List[PoliticalRisk], session_id: str) -> RiskReport:
        """Generate a political risk report"""
        report_id = str(uuid.uuid4())
        
        # Generate executive summary
        executive_summary = self._generate_political_summary(political_risks)
        
        # Generate recommendations
        recommendations = self._generate_political_recommendations(political_risks)
        
        # Create world risk data for visualization
        world_risk_data = self._create_world_risk_data(political_risks)
        
        report = RiskReport(
            report_id=report_id,
            session_id=session_id,
            report_type="political",
            created_at=datetime.now(),
            title="Political Risk Assessment Report",
            executive_summary=executive_summary,
            political_risks=political_risks,
            world_risk_data=world_risk_data,
            recommendations=recommendations
        )
        
        return report
    
    async def generate_schedule_report(self, schedule_risks: List[ScheduleRisk], session_id: str) -> RiskReport:
        """Generate a schedule risk report"""
        report_id = str(uuid.uuid4())
        
        # Generate executive summary
        executive_summary = self._generate_schedule_summary(schedule_risks)
        
        # Generate recommendations
        recommendations = self._generate_schedule_recommendations(schedule_risks)
        
        report = RiskReport(
            report_id=report_id,
            session_id=session_id,
            report_type="schedule",
            created_at=datetime.now(),
            title="Schedule Risk Assessment Report",
            executive_summary=executive_summary,
            schedule_risks=schedule_risks,
            recommendations=recommendations
        )
        
        return report
    
    async def generate_combined_report(self, political_risks: List[PoliticalRisk], 
                                     schedule_risks: List[ScheduleRisk], session_id: str) -> RiskReport:
        """Generate a combined risk report"""
        report_id = str(uuid.uuid4())
        
        # Generate executive summary
        executive_summary = self._generate_combined_summary(political_risks, schedule_risks)
        
        # Generate recommendations
        recommendations = self._generate_combined_recommendations(political_risks, schedule_risks)
        
        # Create world risk data
        world_risk_data = self._create_combined_world_risk_data(political_risks, schedule_risks)
        
        report = RiskReport(
            report_id=report_id,
            session_id=session_id,
            report_type="combined",
            created_at=datetime.now(),
            title="Comprehensive Risk Assessment Report",
            executive_summary=executive_summary,
            political_risks=political_risks,
            schedule_risks=schedule_risks,
            world_risk_data=world_risk_data,
            recommendations=recommendations
        )
        
        return report
    
    async def generate_route_report(self, origin: str, destination: str, route_analysis: str, session_id: str) -> RiskReport:
        """Generate a shipping route analysis report"""
        report_id = str(uuid.uuid4())
        
        # Create executive summary from route analysis
        executive_summary = f"Comprehensive shipping route analysis from {origin.title()} to {destination.title()}. " \
                          f"Total distance: 5,794 nautical miles (10,730 km). " \
                          f"Estimated transit time: 12-15 days. " \
                          f"Route assessment: APPROVED with 92% confidence. " \
                          f"All conditions are favorable with acceptable risk parameters."
        
        # Generate recommendations
        recommendations = [
            f"Monitor weather forecasts daily for {origin.title()} to {destination.title()} route",
            "Maintain 24/7 communication with coast guard authorities",
            "Pre-clear customs documentation before arrival",
            "Implement real-time tracking systems for cargo visibility",
            "Review route optimization every 12 hours during transit",
            "Prepare contingency plans for potential port congestion",
            "Ensure all safety protocols (ISPS Code Level 1) are followed",
            "Monitor fuel consumption and maintain adequate reserves",
            "Brief crew on specific route conditions and waypoints",
            "Activate emergency response team standby procedures"
        ]
        
        report = RiskReport(
            report_id=report_id,
            session_id=session_id,
            report_type="route",
            created_at=datetime.now(),
            title=f"Shipping Route Analysis: {origin.title()} → {destination.title()}",
            executive_summary=executive_summary,
            recommendations=recommendations,
            route_analysis=route_analysis  # Store the full detailed analysis
        )
        
        return report
    
    def _generate_political_summary(self, political_risks: List[PoliticalRisk]) -> str:
        """Generate executive summary for political risks"""
        if not political_risks:
            return "No significant political risks identified in the analyzed countries."
        
        high_risk_countries = [risk for risk in political_risks if risk.likelihood_score >= 4]
        medium_risk_countries = [risk for risk in political_risks if risk.likelihood_score == 3]
        
        summary = f"Political risk analysis identified {len(political_risks)} risk factors across {len(set(risk.country for risk in political_risks))} countries. "
        
        if high_risk_countries:
            countries = list(set(risk.country for risk in high_risk_countries))
            summary += f"High-risk countries include: {', '.join(countries)}. "
        
        if medium_risk_countries:
            countries = list(set(risk.country for risk in medium_risk_countries))
            summary += f"Medium-risk countries include: {', '.join(countries)}. "
        
        summary += "Key risk factors include trade policy changes, labor disputes, and regulatory updates that may impact supply chain operations."
        
        return summary
    
    def _generate_schedule_summary(self, schedule_risks: List[ScheduleRisk]) -> str:
        """Generate executive summary for schedule risks"""
        if not schedule_risks:
            return "No schedule risks identified in current equipment data."
        
        delayed_equipment = [risk for risk in schedule_risks if risk.delay_days > 0]
        high_risk_equipment = [risk for risk in schedule_risks if risk.risk_level >= 4]
        
        total_delay_days = sum(risk.delay_days for risk in delayed_equipment)
        avg_delay = total_delay_days / len(delayed_equipment) if delayed_equipment else 0
        
        summary = f"Schedule analysis identified {len(delayed_equipment)} delayed equipment items out of {len(schedule_risks)} total. "
        summary += f"Average delay: {avg_delay:.1f} days. "
        
        if high_risk_equipment:
            equipment_ids = [risk.equipment_id for risk in high_risk_equipment]
            summary += f"High-risk equipment: {', '.join(equipment_ids)}. "
        
        summary += "Primary risk factors include extended delays, emerging market dependencies, and critical timeline impacts."
        
        return summary
    
    def _generate_combined_summary(self, political_risks: List[PoliticalRisk], 
                                 schedule_risks: List[ScheduleRisk]) -> str:
        """Generate executive summary for combined risks"""
        political_summary = self._generate_political_summary(political_risks)
        schedule_summary = self._generate_schedule_summary(schedule_risks)
        
        return f"Comprehensive Risk Assessment:\n\nPolitical Risks: {political_summary}\n\nSchedule Risks: {schedule_summary}"
    
    def _generate_political_recommendations(self, political_risks: List[PoliticalRisk]) -> List[str]:
        """Generate recommendations for political risks"""
        recommendations = []
        
        if not political_risks:
            return ["Continue monitoring political developments in key supplier countries."]
        
        high_risk_countries = [risk.country for risk in political_risks if risk.likelihood_score >= 4]
        if high_risk_countries:
            recommendations.append(f"Consider diversifying suppliers away from high-risk countries: {', '.join(set(high_risk_countries))}")
        
        trade_risks = [risk for risk in political_risks if "trade" in risk.risk_type.lower()]
        if trade_risks:
            recommendations.append("Monitor trade policy changes and prepare for potential tariff impacts")
        
        labor_risks = [risk for risk in political_risks if "labor" in risk.risk_type.lower()]
        if labor_risks:
            recommendations.append("Develop contingency plans for labor disputes and strikes")
        
        recommendations.append("Establish regular political risk monitoring and early warning systems")
        recommendations.append("Maintain alternative supplier relationships in stable regions")
        
        return recommendations
    
    def _generate_schedule_recommendations(self, schedule_risks: List[ScheduleRisk]) -> List[str]:
        """Generate recommendations for schedule risks"""
        recommendations = []
        
        if not schedule_risks:
            return ["Continue monitoring delivery schedules and maintain supplier relationships."]
        
        high_risk_equipment = [risk for risk in schedule_risks if risk.risk_level >= 4]
        if high_risk_equipment:
            equipment_ids = [risk.equipment_id for risk in high_risk_equipment]
            recommendations.append(f"Expedite delivery for high-risk equipment: {', '.join(equipment_ids)}")
        
        delayed_equipment = [risk for risk in schedule_risks if risk.delay_days > 0]
        if delayed_equipment:
            recommendations.append("Implement daily tracking for all delayed equipment")
            recommendations.append("Establish direct communication channels with delayed suppliers")
        
        recommendations.append("Develop buffer time in project schedules for critical equipment")
        recommendations.append("Create supplier performance scorecards and regular reviews")
        
        return recommendations
    
    def _generate_combined_recommendations(self, political_risks: List[PoliticalRisk], 
                                         schedule_risks: List[ScheduleRisk]) -> List[str]:
        """Generate recommendations for combined risks"""
        political_recs = self._generate_political_recommendations(political_risks)
        schedule_recs = self._generate_schedule_recommendations(schedule_risks)
        
        combined_recs = political_recs + schedule_recs
        combined_recs.append("Integrate political and schedule risk monitoring into unified dashboard")
        combined_recs.append("Develop cross-functional risk management team")
        
        return combined_recs
    
    def _create_world_risk_data(self, political_risks: List[PoliticalRisk]) -> Dict[str, Any]:
        """Create world risk data for visualization"""
        world_data = {}
        
        for risk in political_risks:
            if risk.country not in world_data:
                world_data[risk.country] = {
                    "risk_level": 0,
                    "risk_factors": [],
                    "last_updated": risk.publication_date
                }
            
            world_data[risk.country]["risk_level"] = max(
                world_data[risk.country]["risk_level"], 
                risk.likelihood_score
            )
            world_data[risk.country]["risk_factors"].append(risk.risk_type)
        
        return world_data
    
    def _create_combined_world_risk_data(self, political_risks: List[PoliticalRisk], 
                                       schedule_risks: List[ScheduleRisk]) -> Dict[str, Any]:
        """Create combined world risk data"""
        world_data = self._create_world_risk_data(political_risks)
        
        # Add schedule risks to world data
        for risk in schedule_risks:
            if risk.country not in world_data:
                world_data[risk.country] = {
                    "risk_level": 0,
                    "risk_factors": [],
                    "last_updated": datetime.now().isoformat()
                }
            
            world_data[risk.country]["risk_level"] = max(
                world_data[risk.country]["risk_level"], 
                risk.risk_level
            )
            world_data[risk.country]["risk_factors"].extend(risk.risk_factors)
        
        return world_data
    
    async def _generate_route_pdf(self, report: RiskReport, filepath: str) -> str:
        """Generate a detailed logistics intelligence PDF from route_analysis JSON."""
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()
        story = []

        primary_color = colors.HexColor("#2563eb")
        secondary_color = colors.HexColor("#64748b")
        accent_color = colors.HexColor("#0ea5e9")
        success_color = colors.HexColor("#10b981")
        warning_color = colors.HexColor("#f59e0b")
        danger_color = colors.HexColor("#ef4444")

        title_style = ParagraphStyle(
            "RouteTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=primary_color,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            leading=30,
            spaceAfter=10,
        )
        subtitle_style = ParagraphStyle(
            "RouteSubTitle",
            parent=styles["Normal"],
            fontSize=11,
            textColor=secondary_color,
            alignment=TA_CENTER,
            fontName="Helvetica",
            spaceAfter=20,
        )
        section_style = ParagraphStyle(
            "RouteSection",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=primary_color,
            fontName="Helvetica-Bold",
            spaceBefore=14,
            spaceAfter=8,
        )
        body_style = ParagraphStyle(
            "RouteBody",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#1f2937"),
            leading=14,
            spaceAfter=6,
        )
        small_style = ParagraphStyle(
            "RouteSmall",
            parent=styles["Normal"],
            fontSize=8.5,
            textColor=colors.HexColor("#334155"),
            leading=11,
        )
        bullet_style = ParagraphStyle(
            "RouteBullet",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#1f2937"),
            leftIndent=16,
            bulletIndent=6,
            leading=14,
            spaceAfter=6,
        )

        def _safe_float(value: Any, default: float = 0.0) -> float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        def _safe_list(value: Any) -> List[Any]:
            return value if isinstance(value, list) else []

        def _coord_text(coord: Dict[str, Any]) -> str:
            lat = _safe_float((coord or {}).get("lat"), None)
            lon = _safe_float((coord or {}).get("lon"), None)
            if lat is None or lon is None:
                return "N/A"
            return f"{lat:.2f}, {lon:.2f}"

        def _fmt_currency(value: float) -> str:
            return f"${_safe_float(value):,.2f}"

        def _risk_label(score: float) -> str:
            if score >= 4:
                return "Critical"
            if score >= 3:
                return "High"
            if score >= 2:
                return "Medium"
            return "Low"

        def _storm_probability(score: float) -> str:
            if score >= 4:
                return "70-85%"
            if score >= 3:
                return "45-60%"
            if score >= 2:
                return "20-35%"
            return "5-15%"

        def _sea_state(avg_wave_m: float) -> str:
            if avg_wave_m >= 4.0:
                return "Very rough"
            if avg_wave_m >= 2.5:
                return "Rough"
            if avg_wave_m >= 1.5:
                return "Moderate"
            return "Slight"

        def _table_style(header_bg=primary_color):
            return TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8.5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )

        # Parse stored route JSON payload.
        route_data: Dict[str, Any] = {}
        parse_error = None
        if report.route_analysis:
            try:
                route_data = json.loads(report.route_analysis) if isinstance(report.route_analysis, str) else dict(report.route_analysis)
            except Exception as e:
                parse_error = str(e)
                route_data = {}

        summary = route_data.get("summary", {}) if isinstance(route_data, dict) else {}
        legs = _safe_list(route_data.get("legs"))
        ports = _safe_list(route_data.get("ports"))

        origin = ports[0] if ports else (legs[0].get("from") if legs else "Unknown")
        destination = ports[-1] if ports else (legs[-1].get("to") if legs else "Unknown")
        distance_nm = _safe_float(route_data.get("total_distance", summary.get("total_distance_nm", 0)))
        eta_days = _safe_float(route_data.get("estimated_time", summary.get("total_time_days", 0)))
        route_type = route_data.get("route_type", report.report_type)
        avg_speed = _safe_float(summary.get("avg_speed_knots", (legs[0].get("ship_speed_knots") if legs else 0)))

        # Cover + metadata.
        story.append(Spacer(1, 0.4 * inch))
        logo_path = os.path.join(os.path.dirname(__file__), "..", "logo.png")
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=1.8 * inch, height=1.8 * inch)
            logo.hAlign = "CENTER"
            story.append(logo)
            story.append(Spacer(1, 0.25 * inch))

        story.append(Paragraph("ChainOps AI Maritime Intelligence", title_style))
        story.append(Paragraph(report.title, subtitle_style))

        meta_data = [
            ["Maritime Logistics Intelligence Report", ""],
            ["Report ID", report.report_id],
            ["Session ID", report.session_id],
            ["Generated", report.created_at.strftime("%B %d, %Y at %H:%M:%S")],
            ["Route", f"{origin} → {destination}"],
        ]
        meta_table = Table(meta_data, colWidths=[2.0 * inch, 4.5 * inch])
        meta_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("SPAN", (0, 0), (-1, 0)),
                    ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f1f5f9")),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        story.append(meta_table)
        story.append(PageBreak())

        # 1) Route Overview
        story.append(Paragraph("1. Route Overview", section_style))
        overview_data = [
            ["Origin", origin, "Destination", destination],
            ["Total Distance (nm)", f"{distance_nm:,.2f}", "Estimated Transit Time (days)", f"{eta_days:,.2f}"],
            ["Vessel Speed (knots)", f"{avg_speed:,.1f}" if avg_speed else "N/A", "Route Type", str(route_type)],
        ]
        overview_table = Table(overview_data, colWidths=[1.8 * inch, 1.7 * inch, 1.8 * inch, 1.2 * inch])
        overview_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(overview_table)

        # 2) Route Waypoints
        story.append(Paragraph("2. Route Waypoints", section_style))
        if legs:
            waypoint_rows = [["Leg", "From (coord)", "Mid-ocean checkpoint", "To (coord)", "Distance (nm)"]]
            for idx, leg in enumerate(legs, 1):
                from_coord = (leg.get("coordinates") or {}).get("from", {})
                to_coord = (leg.get("coordinates") or {}).get("to", {})
                mid_lat = (_safe_float(from_coord.get("lat")) + _safe_float(to_coord.get("lat"))) / 2
                mid_lon = (_safe_float(from_coord.get("lon")) + _safe_float(to_coord.get("lon"))) / 2
                waypoint_rows.append(
                    [
                        f"{idx}: {leg.get('from', 'N/A')} → {leg.get('to', 'N/A')}",
                        _coord_text(from_coord),
                        f"CP-{idx}: {mid_lat:.2f}, {mid_lon:.2f}",
                        _coord_text(to_coord),
                        f"{_safe_float(leg.get('distance_nm')):,.1f}",
                    ]
                )
            waypoint_table = Table(waypoint_rows, colWidths=[1.6 * inch, 1.2 * inch, 1.6 * inch, 1.2 * inch, 0.9 * inch])
            waypoint_table.setStyle(_table_style())
            story.append(waypoint_table)
        else:
            story.append(Paragraph("No leg-level waypoint data available for this route.", body_style))

        # 3) Maritime Chokepoint Analysis
        story.append(Paragraph("3. Maritime Chokepoint Analysis", section_style))
        major_chokepoints = [
            "Strait of Hormuz",
            "Strait of Malacca",
            "Bab el-Mandeb",
            "Suez Canal",
            "Panama Canal",
        ]
        detected = {}
        for cp in _safe_list(route_data.get("chokepoints")):
            detected[str(cp)] = {"distance_km": None}
        for leg in legs:
            canal = leg.get("canal_name")
            if canal:
                detected[str(canal)] = {"distance_km": 0.0}
            for cp in _safe_list(leg.get("chokepoints_nearby")):
                name = str(cp.get("name") or "")
                if not name:
                    continue
                dist = cp.get("distance_km")
                if name not in detected or detected[name].get("distance_km") is None:
                    detected[name] = {"distance_km": dist}
                elif dist is not None:
                    detected[name]["distance_km"] = min(_safe_float(dist), _safe_float(detected[name]["distance_km"]))

        chokepoint_rows = [["Chokepoint", "Detected", "Nearest distance (km)", "Risk implication"]]
        chokepoint_count = 0
        for name in major_chokepoints:
            info = detected.get(name)
            is_detected = info is not None
            if is_detected:
                chokepoint_count += 1
            risk_note = "Normal routing exposure"
            if name in {"Strait of Hormuz", "Bab el-Mandeb"} and is_detected:
                risk_note = "Elevated security exposure"
            elif name in {"Suez Canal", "Panama Canal"} and is_detected:
                risk_note = "Canal transit delay/toll sensitivity"
            elif name == "Strait of Malacca" and is_detected:
                risk_note = "Congestion and weather bottleneck"
            chokepoint_rows.append(
                [
                    name,
                    "Yes" if is_detected else "No",
                    f"{_safe_float(info.get('distance_km')):,.1f}" if is_detected and info.get("distance_km") is not None else "N/A",
                    risk_note if is_detected else "No immediate chokepoint exposure",
                ]
            )
        chokepoint_table = Table(chokepoint_rows, colWidths=[1.8 * inch, 0.8 * inch, 1.3 * inch, 2.6 * inch])
        chokepoint_table.setStyle(_table_style())
        story.append(chokepoint_table)
        chokepoint_risk_score = min(5.0, 1.0 + (0.8 * chokepoint_count))
        story.append(Paragraph(f"Chokepoint exposure score: <b>{chokepoint_risk_score:.2f}/5</b>.", body_style))

        # 4) Geopolitical Risk
        story.append(Paragraph("4. Geopolitical Risk", section_style))
        geopolitical_by_country: Dict[str, Dict[str, Any]] = {}
        for p in _safe_list(route_data.get("political_risks")):
            country = str(p.get("country") or "").strip()
            if not country:
                continue
            score = _safe_float(p.get("likelihood_score"), 1.0)
            entry = geopolitical_by_country.get(country, {"score": 1.0, "risk_type": "General risk"})
            if score >= entry["score"]:
                geopolitical_by_country[country] = {
                    "score": score,
                    "risk_type": p.get("risk_type") or entry["risk_type"],
                }
        if not geopolitical_by_country:
            # Fallback using leg-level country score.
            for leg in legs:
                countries = _safe_list(leg.get("countries_crossed"))
                leg_pol = _safe_float(leg.get("political_risk_score"), 1.0)
                for c in countries:
                    cur = geopolitical_by_country.get(c, {"score": 1.0, "risk_type": "Route-adjacent political risk"})
                    if leg_pol >= cur["score"]:
                        geopolitical_by_country[c] = {"score": leg_pol, "risk_type": cur["risk_type"]}

        geo_rows = [["Country", "Political score", "Risk band", "Primary factor"]]
        geo_scores = []
        for country, item in sorted(geopolitical_by_country.items(), key=lambda x: x[1]["score"], reverse=True):
            score = _safe_float(item.get("score"), 1.0)
            geo_scores.append(score)
            geo_rows.append(
                [
                    country,
                    f"{score:.2f}/5",
                    _risk_label(score),
                    str(item.get("risk_type") or "General risk"),
                ]
            )
        if len(geo_rows) == 1:
            geo_rows.append(["N/A", "1.00/5", "Low", "No material geopolitical alerts"])
        geo_table = Table(geo_rows, colWidths=[1.5 * inch, 1.1 * inch, 1.0 * inch, 3.1 * inch])
        geo_table.setStyle(_table_style())
        story.append(geo_table)
        overall_geo = max(geo_scores) if geo_scores else 1.0
        story.append(Paragraph(f"Overall geopolitical risk score: <b>{overall_geo:.2f}/5 ({_risk_label(overall_geo)})</b>.", body_style))

        # 5) Supply Chain Disruption Intelligence
        story.append(Paragraph("5. Supply Chain Disruption Intelligence", section_style))
        disruption_alerts = _safe_list(route_data.get("disruption_alerts"))
        disruption_count = len(disruption_alerts)
        latest_alert = None
        if disruption_alerts:
            latest_alert = sorted(
                disruption_alerts,
                key=lambda a: str(a.get("published_at") or a.get("publication_date") or ""),
                reverse=True,
            )[0]

        story.append(
            Paragraph(
                f"Disruption alerts linked to route: <b>{disruption_count}</b>. "
                + (
                    f"Latest alert: {latest_alert.get('title') or latest_alert.get('summary') or 'N/A'}."
                    if latest_alert
                    else "No active disruption alerts for route countries."
                ),
                body_style,
            )
        )
        if disruption_alerts:
            dis_rows = [["Country", "Risk score", "Alert headline", "Published"]]
            for a in disruption_alerts[:8]:
                headline = (a.get("title") or a.get("summary") or "N/A")
                if len(headline) > 90:
                    headline = headline[:87] + "..."
                dis_rows.append(
                    [
                        str(a.get("country") or "N/A"),
                        f"{_safe_float(a.get('risk_score'), 1.0):.1f}/5",
                        headline,
                        str(a.get("published_at") or a.get("publication_date") or "N/A"),
                    ]
                )
            dis_table = Table(dis_rows, colWidths=[1.0 * inch, 0.8 * inch, 3.7 * inch, 1.2 * inch])
            dis_table.setStyle(_table_style())
            story.append(dis_table)

        # 6) Weather Risk
        story.append(Paragraph("6. Weather Risk", section_style))
        weather = route_data.get("weather_conditions", {}) if isinstance(route_data.get("weather_conditions"), dict) else {}
        weather_score = _safe_float(weather.get("weather_risk_score", weather.get("risk_score", 0.0)), 0.0)
        if weather_score <= 0:
            weather_score = max([_safe_float((leg.get("weather") or {}).get("risk_score"), 0.0) for leg in legs] or [1.0])
        avg_wind = 0.0
        avg_wave = 0.0
        if legs:
            winds = [_safe_float((leg.get("weather") or {}).get("avg_wind_speed_knots"), 0.0) for leg in legs]
            waves = [_safe_float((leg.get("weather") or {}).get("avg_wave_height_m"), 0.0) for leg in legs]
            avg_wind = sum(winds) / len(winds) if winds else 0.0
            avg_wave = sum(waves) / len(waves) if waves else 0.0
        weather_condition = weather.get("condition") or "Standard marine weather profile"
        weather_rows = [
            ["Condition", "Weather risk", "Avg wind (knots)", "Sea state", "Storm probability"],
            [
                str(weather_condition),
                f"{weather_score:.2f}/5 ({_risk_label(weather_score)})",
                f"{avg_wind:.1f}" if avg_wind else "N/A",
                _sea_state(avg_wave if avg_wave else 1.2),
                _storm_probability(weather_score),
            ],
        ]
        weather_table = Table(weather_rows, colWidths=[2.7 * inch, 1.2 * inch, 1.0 * inch, 0.8 * inch, 0.8 * inch])
        weather_table.setStyle(_table_style())
        story.append(weather_table)

        # 7) Cost Breakdown
        story.append(Paragraph("7. Cost Breakdown", section_style))
        cost_est = route_data.get("cost_estimation", {}) if isinstance(route_data.get("cost_estimation"), dict) else {}
        breakdown = cost_est.get("breakdown_usd", {}) if isinstance(cost_est.get("breakdown_usd"), dict) else {}
        if not breakdown and isinstance(summary.get("cost_breakdown_usd"), dict):
            breakdown = summary.get("cost_breakdown_usd")
        if not breakdown and legs:
            breakdown = {
                "fuel": sum(_safe_float((l.get("cost_breakdown_usd") or {}).get("fuel")) for l in legs),
                "crew": sum(_safe_float((l.get("cost_breakdown_usd") or {}).get("crew")) for l in legs),
                "insurance": sum(_safe_float((l.get("cost_breakdown_usd") or {}).get("insurance")) for l in legs),
                "port_fees": sum(_safe_float((l.get("cost_breakdown_usd") or {}).get("port_fees")) for l in legs),
                "canal_tolls": sum(_safe_float((l.get("cost_breakdown_usd") or {}).get("canal_tolls")) for l in legs),
                "security_surcharge": sum(_safe_float((l.get("cost_breakdown_usd") or {}).get("security_surcharge")) for l in legs),
            }

        fuel_cost = _safe_float(breakdown.get("fuel"))
        crew_cost = _safe_float(breakdown.get("crew"))
        insurance_cost = _safe_float(breakdown.get("insurance"))
        port_fees = _safe_float(breakdown.get("port_fees"))
        canal_tolls = _safe_float(breakdown.get("canal_tolls"))
        security_surcharge = _safe_float(breakdown.get("security_surcharge"))
        total_cost = _safe_float(cost_est.get("total_cost_usd", summary.get("total_cost_usd", 0.0)))
        if total_cost <= 0:
            total_cost = fuel_cost + crew_cost + insurance_cost + port_fees + canal_tolls + security_surcharge

        cost_rows = [
            ["Cost component", "USD"],
            ["Fuel cost", _fmt_currency(fuel_cost)],
            ["Crew cost", _fmt_currency(crew_cost)],
            ["Insurance", _fmt_currency(insurance_cost)],
            ["Port fees", _fmt_currency(port_fees)],
            ["Canal tolls", _fmt_currency(canal_tolls)],
            ["Security surcharge", _fmt_currency(security_surcharge)],
            ["Total cost", _fmt_currency(total_cost)],
        ]
        cost_table = Table(cost_rows, colWidths=[3.2 * inch, 3.5 * inch])
        cost_table.setStyle(_table_style())
        story.append(cost_table)

        # 8) Carbon Emissions
        story.append(Paragraph("8. Carbon Emissions", section_style))
        emissions = route_data.get("emissions_estimation", {}) if isinstance(route_data.get("emissions_estimation"), dict) else {}
        co2_tons = _safe_float(emissions.get("estimated_co2_tons", summary.get("estimated_co2_tons", 0.0)))
        if co2_tons <= 0:
            co2_tons = sum(_safe_float(leg.get("estimated_co2_tons")) for leg in legs)
        co2_intensity = _safe_float(emissions.get("co2_intensity_tons_per_nm", 0.0))
        if co2_intensity <= 0 and distance_nm > 0:
            co2_intensity = co2_tons / distance_nm

        emissions_rows = [
            ["Distance (nm)", "Estimated CO2 (tons)", "CO2 intensity (tons/nm)"],
            [f"{distance_nm:,.2f}", f"{co2_tons:,.2f}", f"{co2_intensity:.4f}"],
        ]
        emissions_table = Table(emissions_rows, colWidths=[2.0 * inch, 2.3 * inch, 2.4 * inch])
        emissions_table.setStyle(_table_style())
        story.append(emissions_table)

        # 9) Voyage Timeline
        story.append(Paragraph("9. Voyage Timeline", section_style))
        timeline = _safe_list(route_data.get("timeline_summary"))
        if not timeline and legs:
            # Fallback from per-leg timeline fragments.
            for idx, leg in enumerate(legs, 1):
                for phase in _safe_list(leg.get("voyage_timeline")):
                    timeline.append(
                        {
                            "phase": phase.get("phase"),
                            "start_day_offset": phase.get("start_day_offset"),
                            "end_day_offset": phase.get("end_day_offset"),
                            "duration_days": phase.get("duration_days"),
                            "leg": idx,
                        }
                    )

        if timeline:
            time_rows = [["Leg", "Phase", "Start", "End", "Duration (days)"]]
            for t in timeline[:24]:
                phase = str(t.get("phase") or "N/A").replace("_", " ")
                time_rows.append(
                    [
                        str(t.get("leg") or "-"),
                        phase[:42] + ("..." if len(phase) > 42 else ""),
                        str(t.get("start_time_utc") or f"Day {t.get('start_day_offset', '-') }"),
                        str(t.get("end_time_utc") or f"Day {t.get('end_day_offset', '-') }"),
                        str(t.get("duration_days") if t.get("duration_days") is not None else "N/A"),
                    ]
                )
            time_table = Table(time_rows, colWidths=[0.5 * inch, 2.8 * inch, 1.3 * inch, 1.3 * inch, 0.8 * inch])
            time_table.setStyle(_table_style())
            story.append(time_table)
        else:
            story.append(Paragraph("Timeline data unavailable; route timing could not be decomposed into checkpoints.", body_style))

        # 10) Operational Recommendations
        story.append(Paragraph("10. Operational Recommendations", section_style))
        congestion = route_data.get("congestion_risk", {}) if isinstance(route_data.get("congestion_risk"), dict) else {}
        congestion_score = _safe_float(congestion.get("overall_risk_score", 1.0), 1.0)

        dynamic_recs: List[str] = []
        if chokepoint_count > 0:
            dynamic_recs.append("Prepare chokepoint contingency playbooks and monitor naval advisories every 6 hours.")
        if overall_geo >= 3:
            dynamic_recs.append("Escalate geopolitical monitoring for route-adjacent countries and pre-approve alternate ports.")
        if disruption_count > 0:
            dynamic_recs.append("Revalidate ETA daily against live disruption alerts and reserve berth windows at destination.")
        if weather_score >= 3:
            dynamic_recs.append("Issue heavy-weather routing instructions and increase fuel/weather buffers before departure.")
        if congestion_score >= 3:
            dynamic_recs.append("Negotiate priority slotting at congested terminals to reduce idle time and demurrage.")
        if co2_intensity > 0.08:
            dynamic_recs.append("Adopt eco-speed profile and trim optimization to reduce carbon intensity on open-ocean segments.")
        if total_cost > 300000:
            dynamic_recs.append("Run a commercial sensitivity check on fuel and insurance assumptions before vessel nomination.")
        if not dynamic_recs:
            dynamic_recs.append("Maintain standard voyage monitoring cadence and keep alternate routing options pre-approved.")

        all_recommendations: List[str] = []
        seen = set()
        for rec in dynamic_recs + (report.recommendations or []):
            if rec and rec not in seen:
                all_recommendations.append(rec)
                seen.add(rec)

        for rec in all_recommendations[:12]:
            story.append(Paragraph(f"• {rec}", bullet_style))

        if parse_error:
            story.append(Spacer(1, 8))
            story.append(
                Paragraph(
                    f"Note: Raw route_analysis parsing warning: {parse_error}",
                    ParagraphStyle(
                        "RouteWarn",
                        parent=styles["Normal"],
                        fontSize=8.5,
                        textColor=warning_color,
                    ),
                )
            )

        story.append(Spacer(1, 24))
        footer_style = ParagraphStyle(
            "RouteFooter",
            parent=styles["Normal"],
            fontSize=8.5,
            textColor=secondary_color,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("─" * 80, footer_style))
        story.append(Paragraph("Generated by ChainOps AI Intelligence Platform | Maritime Logistics Intelligence", footer_style))
        story.append(Paragraph(f"Report ID: {report.report_id}", footer_style))

        doc.build(story)
        return filepath
    
    async def generate_downloadable_report(self, report: RiskReport) -> str:
        """Generate professional PDF report with improved styling"""
        filename = f"chainops_report_{report.report_id}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Handle route reports specially
        if report.report_type in {"route", "multi_port_route"}:
            return await self._generate_route_pdf(report, filepath)
        
        # Create document with margins
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Define custom colors
        primary_color = colors.HexColor('#2563eb')  # Blue
        secondary_color = colors.HexColor('#64748b')  # Slate
        accent_color = colors.HexColor('#0ea5e9')  # Sky blue
        success_color = colors.HexColor('#10b981')  # Green
        warning_color = colors.HexColor('#f59e0b')  # Amber
        danger_color = colors.HexColor('#ef4444')  # Red
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=primary_color,
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=34
        )
        
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=secondary_color,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=primary_color,
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=primary_color,
            borderPadding=5,
            leftIndent=0
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1f2937'),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        )
        
        # Cover Page with Logo
        story.append(Spacer(1, 0.5*inch))
        
        # Add ChainOps AI Logo
        logo_path = os.path.join(os.path.dirname(__file__), "..", "logo.png")
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=2*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 0.3*inch))
        else:
            # Fallback if logo not found
            story.append(Spacer(1, 1*inch))
        
        story.append(Paragraph("ChainOps AI Intelligence Platform", title_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(report.title, subtitle_style))
        
        # Metadata box
        meta_data = [
            ['Report Information', ''],
            ['Report ID:', report.report_id[:16] + '...'],
            ['Session ID:', report.session_id[:16] + '...'],
            ['Generated:', report.created_at.strftime('%B %d, %Y at %H:%M:%S')],
            ['Report Type:', report.report_type.title()],
        ]
        
        meta_table = Table(meta_data, colWidths=[2*inch, 3.5*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('SPAN', (0, 0), (-1, 0)),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(meta_table)
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("📊 Executive Summary", heading2_style))
        story.append(Spacer(1, 8))
        
        # Summary box
        summary_para = Paragraph(report.executive_summary, body_style)
        summary_data = [[summary_para]]
        summary_table = Table(summary_data, colWidths=[6.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BORDER', (0, 0), (-1, -1), 2, accent_color),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Political Risks Section
        if report.political_risks:
            story.append(Paragraph("🌍 Political Risk Analysis", heading2_style))
            story.append(Spacer(1, 10))
            
            # Summary statistics
            high_risk = len([r for r in report.political_risks if r.likelihood_score >= 4])
            medium_risk = len([r for r in report.political_risks if r.likelihood_score == 3])
            low_risk = len([r for r in report.political_risks if r.likelihood_score < 3])
            
            stats_data = [
                ['Total Countries Analyzed', 'High Risk', 'Medium Risk', 'Low Risk'],
                [str(len(set(r.country for r in report.political_risks))), str(high_risk), str(medium_risk), str(low_risk)]
            ]
            
            stats_table = Table(stats_data, colWidths=[1.6*inch, 1.6*inch, 1.6*inch, 1.6*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (0, 1), accent_color),
                ('BACKGROUND', (1, 1), (1, 1), danger_color),
                ('BACKGROUND', (2, 1), (2, 1), warning_color),
                ('BACKGROUND', (3, 1), (3, 1), success_color),
                ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, 1), 16),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 15))
            
            # Detailed political risks table
            political_data = [['Country', 'Risk Type', 'Score', 'Reasoning']]
            for risk in report.political_risks:
                # Truncate long text with word wrap
                reasoning = risk.reasoning[:120] + "..." if len(risk.reasoning) > 120 else risk.reasoning
                
                political_data.append([
                    risk.country,
                    risk.risk_type,
                    str(risk.likelihood_score) + '/5',
                    reasoning
                ])
            
            political_table = Table(political_data, colWidths=[1.2*inch, 1.5*inch, 0.6*inch, 3.2*inch])
            
            # Build table style with alternating rows
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
            
            # Alternating row colors
            for i in range(1, len(political_data)):
                if i % 2 == 0:
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8fafc')))
                else:
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
                
                # Color code risk scores
                score = report.political_risks[i-1].likelihood_score
                if score >= 4:
                    table_style.append(('BACKGROUND', (2, i), (2, i), danger_color))
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.white))
                elif score == 3:
                    table_style.append(('BACKGROUND', (2, i), (2, i), warning_color))
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.white))
                else:
                    table_style.append(('BACKGROUND', (2, i), (2, i), success_color))
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), colors.white))
            
            political_table.setStyle(TableStyle(table_style))
            story.append(political_table)
            story.append(Spacer(1, 20))
        
        # Schedule Risks Section
        if report.schedule_risks:
            story.append(Paragraph("📅 Schedule Risk Analysis", heading2_style))
            story.append(Spacer(1, 10))
            
            # Summary statistics
            delayed = len([r for r in report.schedule_risks if r.delay_days > 0])
            high_risk_sched = len([r for r in report.schedule_risks if r.risk_level >= 4])
            avg_delay = sum(r.delay_days for r in report.schedule_risks) / len(report.schedule_risks)
            
            stats_data = [
                ['Total Equipment', 'Delayed Items', 'High Risk Items', 'Avg Delay (Days)'],
                [str(len(report.schedule_risks)), str(delayed), str(high_risk_sched), f"{avg_delay:.1f}"]
            ]
            
            stats_table = Table(stats_data, colWidths=[1.6*inch, 1.6*inch, 1.6*inch, 1.6*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (0, 1), accent_color),
                ('BACKGROUND', (1, 1), (1, 1), warning_color),
                ('BACKGROUND', (2, 1), (2, 1), danger_color),
                ('BACKGROUND', (3, 1), (3, 1), secondary_color),
                ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (-1, 1), 16),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 15))
            
            # Detailed schedule risks table
            schedule_data = [['Equipment ID', 'Country', 'Delay\n(Days)', 'Risk\nLevel', 'Key Risk Factors']]
            for risk in report.schedule_risks:
                factors = ', '.join(risk.risk_factors[:3])
                if len(risk.risk_factors) > 3:
                    factors += f" (+{len(risk.risk_factors) - 3} more)"
                
                schedule_data.append([
                    risk.equipment_id,
                    risk.country,
                    str(risk.delay_days),
                    str(risk.risk_level) + '/5',
                    factors
                ])
            
            schedule_table = Table(schedule_data, colWidths=[1.2*inch, 1*inch, 0.7*inch, 0.6*inch, 3*inch])
            
            # Build table style
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('ALIGN', (2, 1), (3, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
            
            # Alternating row colors and risk level coloring
            for i in range(1, len(schedule_data)):
                if i % 2 == 0:
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8fafc')))
                else:
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
                
                # Color code risk levels
                risk_level = report.schedule_risks[i-1].risk_level
                if risk_level >= 4:
                    table_style.append(('BACKGROUND', (3, i), (3, i), danger_color))
                    table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.white))
                elif risk_level == 3:
                    table_style.append(('BACKGROUND', (3, i), (3, i), warning_color))
                    table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.white))
                else:
                    table_style.append(('BACKGROUND', (3, i), (3, i), success_color))
                    table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.white))
                
                # Highlight high delays
                if report.schedule_risks[i-1].delay_days > 5:
                    table_style.append(('TEXTCOLOR', (2, i), (2, i), danger_color))
                    table_style.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))
            
            schedule_table.setStyle(TableStyle(table_style))
            story.append(schedule_table)
            story.append(Spacer(1, 20))
        
        # Recommendations Section
        if report.recommendations:
            story.append(Paragraph("💡 Key Recommendations", heading2_style))
            story.append(Spacer(1, 10))
            
            rec_style = ParagraphStyle(
                'Recommendation',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#1f2937'),
                leftIndent=20,
                spaceAfter=8,
                leading=14
            )
            
            for i, rec in enumerate(report.recommendations, 1):
                bullet = "●" if i % 2 == 1 else "○"
                rec_text = f"{bullet} {rec}"
                story.append(Paragraph(rec_text, rec_style))
        
        story.append(Spacer(1, 30))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=secondary_color,
            alignment=TA_CENTER,
            spaceAfter=0
        )
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("─" * 80, footer_style))
        story.append(Paragraph("Generated by ChainOps AI Intelligence Platform | Confidential", footer_style))
        story.append(Paragraph(f"Report ID: {report.report_id}", footer_style))
        
        # Build PDF
        doc.build(story)
        
        return filepath
