"""
PDF export service for generating reports.
"""

from typing import List, Dict, Any, Optional
from datetime import date
from pathlib import Path
import logging

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

from app.config.translation_manager import TranslationManager
from app.config.date_utils import format_date_for_display


logger = logging.getLogger(__name__)

# RTL text support
try:
    import arabic_reshaper
    import bidi.algorithm as bidi_algorithm
    RTL_SUPPORT = True
except ImportError:
    RTL_SUPPORT = False
    logger.warning("arabic-reshaper or python-bidi not installed. RTL text may not render correctly.")


class PDFService:
    """Service for PDF report generation."""
    
    def __init__(self, translation_manager: TranslationManager) -> None:
        """
        Initialize PDF service.
        
        Args:
            translation_manager: Translation manager instance
        """
        self.t = translation_manager.t
        self._register_fonts()
    
    def _register_fonts(self) -> None:
        """Register fonts for PDF generation."""
        try:
            # Try to register Persian font if available
            font_path = Path(__file__).parent.parent / "config" / "fonts" / "Vazirmatn[wght].ttf"
            if font_path.exists():
                pdfmetrics.registerFont(TTFont('Vazir', str(font_path)))
                self.font_name = 'Vazir'
                self.has_persian_font = True
            else:
                # Fallback to default font
                self.font_name = 'Helvetica'
                self.has_persian_font = False
                logger.warning("Persian font not found, using default font")
        except Exception as e:
            logger.warning(f"Could not register custom font: {e}")
            self.font_name = 'Helvetica'
            self.has_persian_font = False
    
    def _prepare_rtl_text(self, text: str) -> str:
        """
        Prepare text for RTL rendering in PDF.
        
        Args:
            text: Input text (may contain Persian/Arabic characters)
            
        Returns:
            Text properly shaped and bidi-processed for RTL rendering
        """
        if not text:
            return text
        
        # If RTL support libraries are available and we have Persian font
        if RTL_SUPPORT and self.has_persian_font:
            try:
                # Check if text contains Persian/Arabic characters
                has_rtl = any('\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F' 
                             for char in text)
                
                if has_rtl:
                    # Reshape Arabic/Persian text
                    reshaped_text = arabic_reshaper.reshape(text)
                    # Apply bidirectional algorithm
                    bidi_text = bidi_algorithm.get_display(reshaped_text)
                    return bidi_text
            except Exception as e:
                logger.warning(f"Error processing RTL text: {e}")
        
        return text
    
    def export_stress_report(self, file_path: Path, user: Dict[str, Any],
                            logs: List[Dict[str, Any]], 
                            start_date: date, end_date: date) -> bool:
        """
        Export stress logs to PDF report.
        
        Args:
            file_path: Path to save PDF file
            user: User data dictionary
            logs: List of stress log entries
            start_date: Start date of report period
            end_date: End date of report period
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles for Persian text
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName=self.font_name
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=12,
                spaceBefore=12,
                alignment=TA_CENTER,
                fontName=self.font_name
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_RIGHT,
                fontName=self.font_name
            )
            
            # Title
            title_text = self._prepare_rtl_text(self.t("reports"))
            title = Paragraph(title_text, title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.5*cm))
            
            # User information - RTL order (value first, then label)
            user_info = [
                [self._prepare_rtl_text(user.get('username', 'N/A')), self._prepare_rtl_text(self.t("username") + ":")],
                [self._prepare_rtl_text(format_date_for_display(start_date)), self._prepare_rtl_text(self.t("reports_date_from") + ":")],
                [self._prepare_rtl_text(format_date_for_display(end_date)), self._prepare_rtl_text(self.t("reports_date_to") + ":")],
                [str(len(logs)), self._prepare_rtl_text("تعداد رکوردها:")]
            ]
            
            # RTL table: value column first, then label column
            user_table = Table(user_info, colWidths=[10*cm, 4*cm])
            user_table.setStyle(TableStyle([
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ecf0f1')),  # Label column
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # RTL alignment
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(user_table)
            elements.append(Spacer(1, 1*cm))
            
            # Summary statistics
            if logs:
                avg_stress = sum(log.get('stress_level', 0) for log in logs) / len(logs)
                total_sleep = sum(log.get('sleep_hours', 0) or 0 for log in logs)
                avg_sleep = total_sleep / len(logs) if logs else 0
                total_activity = sum(log.get('physical_activity', 0) or 0 for log in logs)
                avg_activity = total_activity / len(logs) if logs else 0
                
                # RTL order: value first, then label
                summary_data = [
                    [f"{avg_stress:.2f}/10", self._prepare_rtl_text(self.t("stress_level") + " " + self.t("weekly_average") + ":")],
                    [f"{avg_sleep:.2f}", self._prepare_rtl_text(self.t("sleep_hours") + " " + self.t("weekly_average") + ":")],
                    [f"{avg_activity:.2f} " + self._prepare_rtl_text(self.t("minutes")), self._prepare_rtl_text(self.t("physical_activity") + " " + self.t("weekly_average") + ":")]
                ]
                
                # RTL order: value first, then label
                summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
                summary_table.setStyle(TableStyle([
                    # Value column (column 0) - white background with dark text
                    ('BACKGROUND', (0, 0), (0, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a1a1a')),  # Dark color for numbers
                    # Label column (column 1) - blue background with white text
                    ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.whitesmoke),
                    # Common styles
                    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # RTL alignment
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.white),
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 1*cm))
            
            # Stress logs table
            if logs:
                logs_heading = Paragraph(self._prepare_rtl_text(self.t("stress_history")), heading_style)
                elements.append(logs_heading)
                
                # Table headers - RTL order (rightmost column first)
                table_data = [[
                    self._prepare_rtl_text(self.t("notes")),
                    self._prepare_rtl_text(self.t("physical_activity")),
                    self._prepare_rtl_text(self.t("sleep_hours")),
                    self._prepare_rtl_text(self.t("stress_level")),
                    self._prepare_rtl_text(self.t("date"))
                ]]
                
                # Table rows - RTL order (rightmost column first)
                for log in logs:
                    log_date = log.get('date', '')
                    if isinstance(log_date, str):
                        date_str = format_date_for_display(log_date)
                    else:
                        date_str = format_date_for_display(log_date)
                    
                    stress_level = str(log.get('stress_level', ''))
                    sleep_hours = str(log.get('sleep_hours', '')) if log.get('sleep_hours') else '-'
                    physical_activity = str(log.get('physical_activity', '')) if log.get('physical_activity') else '-'
                    notes = str(log.get('notes', '')) if log.get('notes') else '-'
                    
                    # Truncate long notes
                    if len(notes) > 50:
                        notes = notes[:47] + "..."
                    
                    # RTL order: notes, physical_activity, sleep_hours, stress_level, date
                    # Store numeric values as strings but mark them for special formatting
                    table_data.append([
                        self._prepare_rtl_text(notes),
                        str(physical_activity) if physical_activity != '-' else '-',
                        str(sleep_hours) if sleep_hours != '-' else '-',
                        str(stress_level),
                        self._prepare_rtl_text(date_str)
                    ])
                
                # Create table - RTL column widths (rightmost first)
                logs_table = Table(table_data, colWidths=[5.5*cm, 3*cm, 2.5*cm, 2*cm, 3*cm])
                logs_table.setStyle(TableStyle([
                    # Header row - centered
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center headers
                    ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),  # RTL alignment for data rows
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),  # Apply font to all cells
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    # Data rows - ensure dark text color for visibility
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1a1a1a')),  # Dark color for better visibility
                    # Numeric columns (stress_level, sleep_hours, physical_activity) - columns 1, 2, 3
                    ('TEXTCOLOR', (1, 1), (3, -1), colors.HexColor('#0d47a1')),  # Dark blue for numbers
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 8),
                    # Grid
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    # Alternating row colors
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ]))
                elements.append(logs_table)
            else:
                no_data = Paragraph(self._prepare_rtl_text(self.t("message_no_data")), normal_style)
                elements.append(no_data)
            
            # Build PDF
            doc.build(elements)
            logger.info(f"PDF report exported successfully to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting PDF report: {e}", exc_info=True)
            return False
    
    def export_combined_report(self, file_path: Path, user: Dict[str, Any],
                               stress_logs: List[Dict[str, Any]],
                               anxiety_results: List[Dict[str, Any]],
                               start_date: date, end_date: date) -> bool:
        """
        Export combined stress and anxiety reports to PDF.
        
        Args:
            file_path: Path to save PDF file
            user: User data dictionary
            stress_logs: List of stress log entries
            anxiety_results: List of anxiety test results
            start_date: Start date of report period
            end_date: End date of report period
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName=self.font_name
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=12,
                spaceBefore=12,
                alignment=TA_CENTER,
                fontName=self.font_name
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_RIGHT,
                fontName=self.font_name
            )
            
            # Style for table cells with wrapping
            cell_style = ParagraphStyle(
                'TableCell',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_RIGHT,
                fontName=self.font_name,
                leading=11  # Line spacing
            )
            
            # Title
            title_text = self._prepare_rtl_text(self.t("reports"))
            title = Paragraph(title_text, title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.5*cm))
            
            # User information
            user_info = [
                [self._prepare_rtl_text(user.get('username', 'N/A')), self._prepare_rtl_text(self.t("username") + ":")],
                [self._prepare_rtl_text(format_date_for_display(start_date)), self._prepare_rtl_text(self.t("reports_date_from") + ":")],
                [self._prepare_rtl_text(format_date_for_display(end_date)), self._prepare_rtl_text(self.t("reports_date_to") + ":")],
                [str(len(stress_logs) + len(anxiety_results)), self._prepare_rtl_text("تعداد رکوردها:")]
            ]
            
            user_table = Table(user_info, colWidths=[10*cm, 4*cm])
            user_table.setStyle(TableStyle([
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#666666')),  # Darker grid for visibility
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(user_table)
            elements.append(Spacer(1, 1*cm))
            
            # Stress logs section
            if stress_logs:
                # Summary statistics for stress
                avg_stress = sum(log.get('stress_level', 0) for log in stress_logs) / len(stress_logs)
                total_sleep = sum(log.get('sleep_hours', 0) or 0 for log in stress_logs)
                avg_sleep = total_sleep / len(stress_logs) if stress_logs else 0
                total_activity = sum(log.get('physical_activity', 0) or 0 for log in stress_logs)
                avg_activity = total_activity / len(stress_logs) if stress_logs else 0
                
                summary_data = [
                    [f"{avg_stress:.2f}/10", self._prepare_rtl_text(self.t("stress_level") + " " + self.t("weekly_average") + ":")],
                    [f"{avg_sleep:.2f}", self._prepare_rtl_text(self.t("sleep_hours") + " " + self.t("weekly_average") + ":")],
                    [f"{avg_activity:.2f} " + self._prepare_rtl_text(self.t("minutes")), self._prepare_rtl_text(self.t("physical_activity") + " " + self.t("weekly_average") + ":")]
                ]
                
                summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a1a1a')),
                    ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#666666')),  # Darker grid for visibility
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 1*cm))
                
                # Stress logs table
                logs_heading = Paragraph(self._prepare_rtl_text(self.t("stress_history")), heading_style)
                elements.append(logs_heading)
                
                table_data = [[
                    self._prepare_rtl_text(self.t("notes")),
                    self._prepare_rtl_text(self.t("physical_activity")),
                    self._prepare_rtl_text(self.t("sleep_hours")),
                    self._prepare_rtl_text(self.t("stress_level")),
                    self._prepare_rtl_text(self.t("date"))
                ]]
                
                for log in stress_logs:
                    log_date = log.get('date', '')
                    date_str = format_date_for_display(log_date)
                    
                    stress_level = str(log.get('stress_level', ''))
                    sleep_hours = str(log.get('sleep_hours', '')) if log.get('sleep_hours') else '-'
                    physical_activity = str(log.get('physical_activity', '')) if log.get('physical_activity') else '-'
                    notes = str(log.get('notes', '')) if log.get('notes') else '-'
                    
                    if len(notes) > 50:
                        notes = notes[:47] + "..."
                    
                    table_data.append([
                        self._prepare_rtl_text(notes),
                        str(physical_activity) if physical_activity != '-' else '-',
                        str(sleep_hours) if sleep_hours != '-' else '-',
                        str(stress_level),
                        self._prepare_rtl_text(date_str)
                    ])
                
                # Calculate column widths to fit page (A4 width 21cm - 4cm margins = 17cm available)
                logs_table = Table(table_data, colWidths=[5.5*cm, 3*cm, 2.5*cm, 2*cm, 3*cm])
                logs_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1a1a1a')),
                    ('TEXTCOLOR', (1, 1), (3, -1), colors.HexColor('#0d47a1')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#666666')),  # Darker grid for visibility
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#34495e')),  # Thicker line below header
                ]))
                elements.append(logs_table)
            
            # Anxiety results section - start on new page
            if anxiety_results:
                elements.append(PageBreak())
                
                # Title for anxiety section
                anxiety_title = Paragraph(self._prepare_rtl_text(self.t("reports")), title_style)
                elements.append(anxiety_title)
                elements.append(Spacer(1, 0.5*cm))
                
                # User information for anxiety section
                user_info_anxiety = [
                    [self._prepare_rtl_text(user.get('username', 'N/A')), self._prepare_rtl_text(self.t("username") + ":")],
                    [self._prepare_rtl_text(format_date_for_display(start_date)), self._prepare_rtl_text(self.t("reports_date_from") + ":")],
                    [self._prepare_rtl_text(format_date_for_display(end_date)), self._prepare_rtl_text(self.t("reports_date_to") + ":")],
                    [str(len(anxiety_results)), self._prepare_rtl_text("تعداد رکوردها:")]
                ]
                
                user_table_anxiety = Table(user_info_anxiety, colWidths=[10*cm, 4*cm])
                user_table_anxiety.setStyle(TableStyle([
                    ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ecf0f1')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#666666')),  # Darker grid for visibility
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(user_table_anxiety)
                elements.append(Spacer(1, 1*cm))
                # Summary statistics for anxiety
                avg_score = sum(result.get('score', 0) for result in anxiety_results) / len(anxiety_results)
                avg_percentage = sum(result.get('percentage', 0) for result in anxiety_results) / len(anxiety_results)
                
                summary_data = [
                    [f"{avg_score:.2f}", self._prepare_rtl_text(self.t("score") + " " + self.t("weekly_average") + ":")],
                    [f"{avg_percentage:.2f}%", self._prepare_rtl_text(self.t("percentage") + " " + self.t("weekly_average") + ":")]
                ]
                
                summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a1a1a')),
                    ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#666666')),  # Darker grid for visibility
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 1*cm))
                
                # Anxiety results table
                anxiety_heading = Paragraph(self._prepare_rtl_text(self.t("anxiety_history")), heading_style)
                elements.append(anxiety_heading)
                
                table_data = [[
                    self._prepare_rtl_text(self.t("interpretation")),
                    self._prepare_rtl_text(self.t("percentage")),
                    self._prepare_rtl_text(self.t("max_score")),
                    self._prepare_rtl_text(self.t("score")),
                    self._prepare_rtl_text(self.t("test_name")),
                    self._prepare_rtl_text(self.t("date"))
                ]]
                
                for result in anxiety_results:
                    result_date = result.get('date', '')
                    date_str = format_date_for_display(result_date)
                    
                    test_name = str(result.get('test_name', ''))
                    score = str(result.get('score', ''))
                    max_score = str(result.get('max_score', ''))
                    percentage = f"{result.get('percentage', 0):.2f}%"
                    interpretation = str(result.get('interpretation', '')) if result.get('interpretation') else '-'
                    
                    # Use Paragraph for test_name and interpretation to allow wrapping
                    test_name_para = Paragraph(self._prepare_rtl_text(test_name), cell_style)
                    interpretation_para = Paragraph(self._prepare_rtl_text(interpretation), cell_style)
                    
                    table_data.append([
                        interpretation_para,
                        percentage,
                        max_score,
                        score,
                        test_name_para,
                        self._prepare_rtl_text(date_str)
                    ])
                
                # Calculate column widths to fit page (A4 width 21cm - 4cm margins = 17cm available)
                # Adjust widths: interpretation, percentage, max_score, score, test_name, date
                # Increased test_name width to 3.5cm to allow better wrapping
                anxiety_table = Table(table_data, colWidths=[4*cm, 2.5*cm, 2*cm, 2*cm, 3.5*cm, 3*cm])
                anxiety_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),
                    ('ALIGN', (4, 1), (4, -1), 'RIGHT'),  # test_name column alignment
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1a1a1a')),
                    ('TEXTCOLOR', (1, 1), (3, -1), colors.HexColor('#0d47a1')),  # Color for numeric columns
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#666666')),  # Darker grid for visibility
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Changed to TOP to allow wrapping
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#34495e')),  # Thicker line below header
                ]))
                elements.append(anxiety_table)
            
            # Build PDF
            doc.build(elements)
            logger.info(f"Combined PDF report exported successfully to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting combined PDF report: {e}", exc_info=True)
            return False

