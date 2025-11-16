"""
Sessions history screen.
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


class SessionsTableModel(QAbstractTableModel):
    """Table model for sessions."""
    
    def __init__(self, data: List[Dict[str, Any]], exercises: Dict[int, str],
                 translation_manager: TranslationManager) -> None:
        """Initialize model."""
        super().__init__()
        self._data = data
        self.exercises = exercises
        self.t = translation_manager.t
        self.headers = [
            self.t("date"),
            self.t("exercise_name"),
            self.t("session_duration"),
            self.t("session_status"),
            self.t("session_notes")
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
            session = self._data[row]
            
            if col == 0:
                date_str = session.get('date', '')
                return format_date_for_display(date_str)
            elif col == 1:
                exercise_id = session.get('exercise_id')
                return self.exercises.get(exercise_id, str(exercise_id))
            elif col == 2:
                return f"{session.get('duration', 0)} {self.t('session_duration')}"
            elif col == 3:
                status = session.get('completion_status', '')
                return self.t(f"session_{status}")
            elif col == 4:
                return session.get('notes', '') or ''
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> Any:
        """Return header data."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None


class SessionsScreen(QWidget):
    """Sessions history screen."""
    
    def __init__(self, user: dict, translation_manager: TranslationManager,
                 session_service, exercise_service) -> None:
        """
        Initialize sessions screen.
        
        Args:
            user: User data
            translation_manager: Translation manager
            session_service: Session service instance
            exercise_service: Exercise service instance
        """
        super().__init__()
        self.user = user
        self.t = translation_manager.t
        self.session_service = session_service
        self.exercise_service = exercise_service
        
        self._init_ui()
        self.refresh()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel(self.t("sessions"))
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
        sessions = self.session_service.get_user_sessions(self.user['id'])
        
        # Get exercise names
        exercises = self.exercise_service.get_all_exercises()
        exercise_dict = {ex['id']: ex['name'] for ex in exercises}
        
        # Create a simple translation manager wrapper
        class TM:
            def __init__(self, t_func):
                self.t = t_func
        tm = TM(self.t)
        model = SessionsTableModel(sessions, exercise_dict, tm)
        self.table_view.setModel(model)

