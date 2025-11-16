"""
Stress history screen with table and chart.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont
from typing import List, Dict, Any

from app.config.translation_manager import TranslationManager
from app.config.date_utils import format_date_for_display


class StressHistoryTableModel(QAbstractTableModel):
    """Table model for stress history."""
    
    def __init__(self, data: List[Dict[str, Any]], translation_manager: TranslationManager) -> None:
        """Initialize model."""
        super().__init__()
        self._data = data
        self.t = translation_manager.t
        self.headers = [
            self.t("date"),
            self.t("stress_level"),
            self.t("sleep_hours"),
            self.t("physical_activity"),
            self.t("notes")
        ]
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return number of rows."""
        return len(self._data)
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return number of columns."""
        return len(self.headers)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return data for index."""
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            if row >= len(self._data):
                return None
            log = self._data[row]
            
            if col == 0:
                date_str = log.get('date', '')
                return format_date_for_display(date_str)
            elif col == 1:
                return str(log.get('stress_level', ''))
            elif col == 2:
                sleep = log.get('sleep_hours')
                return str(sleep) if sleep else ''
            elif col == 3:
                activity = log.get('physical_activity')
                return str(activity) if activity else ''
            elif col == 4:
                return log.get('notes', '') or ''
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> Any:
        """Return header data."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None


class StressHistoryScreen(QWidget):
    """Stress history screen."""
    
    def __init__(self, user: dict, translation_manager: TranslationManager,
                 stress_service) -> None:
        """
        Initialize stress history screen.
        
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
        self.refresh()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel(self.t("stress_history"))
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Table
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_view)
        
        # Refresh button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        refresh_button = QPushButton(self.t("refresh"))
        refresh_button.clicked.connect(self.refresh)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def refresh(self) -> None:
        """Refresh table data."""
        logs = self.stress_service.get_user_logs(self.user['id'])
        # Create a simple translation manager wrapper
        class TM:
            def __init__(self, t_func):
                self.t = t_func
        tm = TM(self.t)
        model = StressHistoryTableModel(logs, tm)
        self.table_view.setModel(model)

