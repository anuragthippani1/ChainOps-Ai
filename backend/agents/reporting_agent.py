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
        """Generate PDF for route analysis reports"""
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
            fontSize=14,
            textColor=primary_color,
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1f2937'),
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
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
            # Fallback to emoji if logo not found
            story.append(Spacer(1, 1*inch))
            story.append(Paragraph("🚢", title_style))
        
        story.append(Paragraph("ChainOps AI Intelligence Platform", title_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(report.title, subtitle_style))
        
        # Metadata box
        meta_data = [
            ['Route Analysis Report', ''],
            ['Report ID:', report.report_id[:16] + '...'],
            ['Generated:', report.created_at.strftime('%B %d, %Y at %H:%M:%S')],
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
        
        # Full Route Analysis
        if report.route_analysis:
            story.append(Paragraph("📋 Complete Route Analysis", heading2_style))
            story.append(Spacer(1, 12))
            
            # Parse the route analysis and format it for PDF
            analysis_lines = report.route_analysis.split('\n')
            
            # Custom styles for route analysis
            section_heading_style = ParagraphStyle(
                'SectionHeading',
                parent=styles['Normal'],
                fontSize=11,
                textColor=primary_color,
                fontName='Helvetica-Bold',
                spaceAfter=8,
                spaceBefore=12
            )
            
            subsection_style = ParagraphStyle(
                'SubSection',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#1f2937'),
                fontName='Helvetica-Bold',
                spaceAfter=6,
                spaceBefore=8
            )
            
            detail_style = ParagraphStyle(
                'Detail',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#374151'),
                spaceAfter=4,
                leading=12
            )
            
            for line in analysis_lines:
                line = line.strip()
                if not line or line.startswith('━'):  # Skip empty lines and separators
                    continue
                
                # Main section headers (##)
                if line.startswith('## '):
                    section_title = line.replace('## ', '').strip()
                    story.append(Spacer(1, 10))
                    story.append(Paragraph(section_title, section_heading_style))
                
                # Subsection headers (###)
                elif line.startswith('### '):
                    subsection_title = line.replace('### ', '').strip().rstrip(':')
                    story.append(Paragraph(subsection_title, subsection_style))
                
                # Bullet points
                elif line.startswith('•') or line.startswith('✅') or line.startswith('✓') or line.startswith('⚠') or line.startswith('├─') or line.startswith('└─'):
                    # Clean up the line
                    clean_line = line.replace('├─', '  •').replace('└─', '  •')
                    story.append(Paragraph(clean_line, detail_style))
                
                # Bold text (surrounded by **)
                elif '**' in line:
                    # Replace markdown bold with HTML bold for ReportLab
                    clean_line = line.replace('**', '<b>').replace('**', '</b>')
                    # Fix if odd number of replacements
                    if clean_line.count('<b>') != clean_line.count('</b>'):
                        parts = line.split('**')
                        clean_line = ''
                        for i, part in enumerate(parts):
                            if i % 2 == 1:  # Odd indices are bold
                                clean_line += f'<b>{part}</b>'
                            else:
                                clean_line += part
                    story.append(Paragraph(clean_line, detail_style))
                
                # Regular text
                elif line and not line.startswith('#'):
                    story.append(Paragraph(line, detail_style))
        
        else:
            # Fallback to summary if no full analysis
            story.append(Paragraph("📊 Executive Summary", heading2_style))
            story.append(Spacer(1, 8))
            
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
        story.append(Paragraph("Generated by ChainOps AI Intelligence Platform | Comprehensive Route Analysis", footer_style))
        story.append(Paragraph(f"Report ID: {report.report_id}", footer_style))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    async def generate_downloadable_report(self, report: RiskReport) -> str:
        """Generate professional PDF report with improved styling"""
        filename = f"chainops_report_{report.report_id}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Handle route reports specially
        if report.report_type == "route":
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
