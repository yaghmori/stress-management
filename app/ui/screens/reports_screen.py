"""
Reports screen for exporting data.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFormLayout, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import date, timedelta
from pathlib import Path
import csv
import jdatetime

from app.config.translation_manager import TranslationManager
from app.config.date_utils import format_date_for_display, get_current_shamsi_date
from app.services.pdf_service import PDFService
from app.services.excel_service import ExcelService
from app.ui.widgets.persian_date_edit import PersianDateEdit


class ReportsScreen(QWidget):
    """Reports and export screen."""
    
    def __init__(self, user: dict, translation_manager: TranslationManager,
                 stress_service) -> None:
        """
        Initialize reports screen.
        
        Args:
            user: User data
            translation_manager: Translation manager
            stress_service: Stress service instance
        """
        super().__init__()
        self.user = user
        self.translation_manager = translation_manager
        self.t = translation_manager.t
        self.stress_service = stress_service
        
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel(self.t("reports"))
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Date range form
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.date_from_input = PersianDateEdit()
        # Set date 30 days ago in Persian calendar
        today = get_current_shamsi_date()
        # Convert to Gregorian, subtract 30 days, then convert back
        gregorian_today = today.togregorian()
        gregorian_from = gregorian_today - timedelta(days=30)
        date_from_shamsi = jdatetime.date.fromgregorian(date=gregorian_from)
        self.date_from_input.setShamsiDate(date_from_shamsi)
        form_layout.addRow(self.t("reports_date_from") + ":", self.date_from_input)
        
        self.date_to_input = PersianDateEdit()
        self.date_to_input.setShamsiDate(get_current_shamsi_date())
        form_layout.addRow(self.t("reports_date_to") + ":", self.date_to_input)
        
        layout.addLayout(form_layout)
        
        # Export buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        export_csv_button = QPushButton(self.t("reports_export_csv"))
        export_csv_button.clicked.connect(self._on_export_csv)
        button_layout.addWidget(export_csv_button)
        
        export_excel_button = QPushButton(self.t("reports_export_excel"))
        export_excel_button.clicked.connect(self._on_export_excel)
        button_layout.addWidget(export_excel_button)
        
        export_pdf_button = QPushButton(self.t("reports_export_pdf"))
        export_pdf_button.clicked.connect(self._on_export_pdf)
        button_layout.addWidget(export_pdf_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def _on_export_csv(self) -> None:
        """Handle CSV export."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.t("reports_export_csv"),
            "",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        date_from = self.date_from_input.getGregorianDate()
        date_to = self.date_to_input.getGregorianDate()
        
        logs = self.stress_service.get_user_logs(
            self.user['id'],
            start_date=date_from,
            end_date=date_to
        )
        
        try:
            # Use UTF-8 with BOM for Excel compatibility
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([
                    self.t("date"),
                    self.t("stress_level"),
                    self.t("sleep_hours"),
                    self.t("physical_activity"),
                    self.t("notes")
                ])
                
                for log in logs:
                    writer.writerow([
                        format_date_for_display(log.get('date', '')),
                        str(log.get('stress_level', '')),
                        str(log.get('sleep_hours', '')) if log.get('sleep_hours') else '',
                        str(log.get('physical_activity', '')) if log.get('physical_activity') else '',
                        str(log.get('notes', '')) if log.get('notes') else ''
                    ])
            
            QMessageBox.information(
                self,
                self.t("success_title"),
                self.t("message_export_success")
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                self.t("error_title"),
                f"{self.t('message_export_failed')}: {str(e)}"
            )
    
    def _on_export_pdf(self) -> None:
        """Handle PDF export."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.t("reports_export_pdf"),
            "",
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        # Ensure .pdf extension
        if not file_path.lower().endswith('.pdf'):
            file_path += '.pdf'
        
        date_from = self.date_from_input.getGregorianDate()
        date_to = self.date_to_input.getGregorianDate()
        
        logs = self.stress_service.get_user_logs(
            self.user['id'],
            start_date=date_from,
            end_date=date_to
        )
        
        try:
            # Create PDF service
            pdf_service = PDFService(self.translation_manager)
            
            # Export to PDF
            success = pdf_service.export_stress_report(
                Path(file_path),
                self.user,
                logs,
                date_from,
                date_to
            )
            
            if success:
                QMessageBox.information(
                    self,
                    self.t("success_title"),
                    self.t("message_export_success")
                )
            else:
                QMessageBox.warning(
                    self,
                    self.t("error_title"),
                    self.t("message_export_failed")
                )
        except ImportError as e:
            QMessageBox.warning(
                self,
                self.t("error_title"),
                f"PDF export requires reportlab library. Please install it: pip install reportlab\n\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                self.t("error_title"),
                f"{self.t('message_export_failed')}: {str(e)}"
            )
    
    def _on_export_excel(self) -> None:
        """Handle Excel export."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.t("reports_export_excel"),
            "",
            "Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return
        
        # Ensure .xlsx extension
        if not file_path.lower().endswith('.xlsx'):
            file_path += '.xlsx'
        
        date_from = self.date_from_input.getGregorianDate()
        date_to = self.date_to_input.getGregorianDate()
        
        logs = self.stress_service.get_user_logs(
            self.user['id'],
            start_date=date_from,
            end_date=date_to
        )
        
        try:
            # Create Excel service
            excel_service = ExcelService(self.translation_manager)
            
            # Export to Excel
            success = excel_service.export_stress_report(
                Path(file_path),
                self.user,
                logs,
                date_from,
                date_to
            )
            
            if success:
                QMessageBox.information(
                    self,
                    self.t("success_title"),
                    self.t("message_export_success")
                )
            else:
                QMessageBox.warning(
                    self,
                    self.t("error_title"),
                    self.t("message_export_failed")
                )
        except ImportError as e:
            QMessageBox.warning(
                self,
                self.t("error_title"),
                f"Excel export requires openpyxl library. Please install it: pip install openpyxl\n\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                self.t("error_title"),
                f"{self.t('message_export_failed')}: {str(e)}"
            )
    
    def refresh(self) -> None:
        """Refresh screen."""
        pass

