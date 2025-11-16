"""
Reports screen for exporting data.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFormLayout, QDateEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from datetime import date
from pathlib import Path
import csv

from app.config.translation_manager import TranslationManager
from app.config.date_utils import format_date_for_display


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
        
        self.date_from_input = QDateEdit()
        self.date_from_input.setDate(QDate.currentDate().addDays(-30))
        self.date_from_input.setCalendarPopup(True)
        form_layout.addRow(self.t("reports_date_from") + ":", self.date_from_input)
        
        self.date_to_input = QDateEdit()
        self.date_to_input.setDate(QDate.currentDate())
        self.date_to_input.setCalendarPopup(True)
        form_layout.addRow(self.t("reports_date_to") + ":", self.date_to_input)
        
        layout.addLayout(form_layout)
        
        # Export buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        export_csv_button = QPushButton(self.t("reports_export_csv"))
        export_csv_button.clicked.connect(self._on_export_csv)
        button_layout.addWidget(export_csv_button)
        
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
        
        date_from = self.date_from_input.date().toPython()
        date_to = self.date_to_input.date().toPython()
        
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
        QMessageBox.information(
            self,
            self.t("info_title"),
            "PDF export feature requires reportlab library. CSV export is available."
        )
    
    def refresh(self) -> None:
        """Refresh screen."""
        pass

