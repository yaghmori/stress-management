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

