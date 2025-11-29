"""
Exercises screen with exercise cards and session history.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QTableView, QHeaderView, QComboBox,
    QMessageBox, QDialog, QGridLayout
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont
from typing import List, Dict, Any

from app.config.translation_manager import TranslationManager
from app.config.date_utils import format_date_for_display
from app.ui.screens.exercise_timer_dialog import ExerciseTimerDialog


class ExerciseCard(QFrame):
    """Exercise card widget with improved responsive design."""
    
    def __init__(self, exercise: dict, translation_manager: TranslationManager,
                 on_start_callback) -> None:
        """Initialize exercise card."""
        super().__init__()
        self.exercise = exercise
        self.t = translation_manager.t
        self.on_start_callback = on_start_callback
        
        self._init_ui()
    
    def _get_exercise_type_translation_key(self, exercise_type: str) -> str:
        """Get translation key for exercise type."""
        # Map exercise types to translation keys
        type_map = {
            "breathing": "exercise_type_breathing",
            "meditation": "exercise_type_meditation",
            "guided_relaxation": "exercise_type_guided_relaxation",
            "music_therapy": "exercise_type_music_therapy",
            "relaxation": "exercise_type_guided_relaxation",  # Legacy support
            "journaling": "exercise_type_journaling",
            "activity": "exercise_type_activity",
            "stretching": "exercise_type_stretching"
        }
        
        return type_map.get(exercise_type, f"exercise_type_{exercise_type}")
    
    def _get_exercise_type_text(self, exercise_type: str) -> str:
        """Get translated exercise type text."""
        translation_key = self._get_exercise_type_translation_key(exercise_type)
        translated = self.t(translation_key)
        
        # If translation key not found, return the type as-is
        if translated == translation_key:
            return exercise_type.replace("_", " ").title()
        return translated
    
    def _init_ui(self) -> None:
        """Initialize UI with responsive design."""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                border: 2px solid #3498db;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Exercise name
        name_label = QLabel(self.exercise.get('name', ''))
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        name_label.setStyleSheet("color: #2c3e50; padding-bottom: 5px;")
        layout.addWidget(name_label)
        
        # Description (if available)
        description = self.exercise.get('description', '')
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            desc_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding-bottom: 8px;")
            layout.addWidget(desc_label)
        
        # Details - Use vertical layout for small screens, or wrap in a container
        details_container = QWidget()
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(6)
        
        # Exercise type
        exercise_type = self.exercise.get('type', '')
        type_text = self._get_exercise_type_text(exercise_type)
        type_label = QLabel(f"{self.t('exercise_type')}: {type_text}")
        type_label.setWordWrap(True)
        type_label.setStyleSheet("color: #555555; font-size: 11px;")
        details_layout.addWidget(type_label)
        
        # Duration
        duration = self.exercise.get('duration', 0)
        duration_label = QLabel(f"{self.t('exercise_duration')}: {duration} {self.t('minutes')}")
        duration_label.setWordWrap(True)
        duration_label.setStyleSheet("color: #555555; font-size: 11px;")
        details_layout.addWidget(duration_label)
        
        details_container.setLayout(details_layout)
        layout.addWidget(details_container)
        
        # Start button
        start_button = QPushButton(self.t("start_exercise"))
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        start_button.clicked.connect(lambda: self.on_start_callback(self.exercise))
        layout.addWidget(start_button)
        
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumHeight(150)


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
            self.t("session_status")
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
                return f"{session.get('duration', 0)} {self.t('minutes')}"
            elif col == 3:
                status = session.get('completion_status', '')
                return self.t(f"session_{status}")
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> Any:
        """Return header data."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None


class ExercisesScreen(QWidget):
    """Exercises screen with cards and history."""
    
    def __init__(self, user: dict, translation_manager: TranslationManager,
                 exercise_service, session_service) -> None:
        """
        Initialize exercises screen.
        
        Args:
            user: User data
            translation_manager: Translation manager
            exercise_service: Exercise service instance
            session_service: Session service instance
        """
        super().__init__()
        self.user = user
        self.translation_manager = translation_manager
        self.t = translation_manager.t
        self.exercise_service = exercise_service
        self.session_service = session_service
        
        self._init_ui()
        self.refresh()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header with title and filter
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        
        exercises_title = QLabel(self.t("exercises"))
        exercises_title.setFont(title_font)
        exercises_title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(exercises_title)
        
        header_layout.addStretch()
        
        # Filter
        filter_label = QLabel(self.t("filter") + ":")
        filter_label.setStyleSheet("color: #555555;")
        header_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.setMinimumWidth(150)
        self._populate_filter()
        self.filter_combo.currentIndexChanged.connect(self.refresh)
        header_layout.addWidget(self.filter_combo)
        
        main_layout.addLayout(header_layout)
        
        # Main content area - horizontal split
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side - Exercise cards in scrollable grid
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # Scroll area for cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        self.cards_widget = QWidget()
        # Use grid layout for responsive card arrangement
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(15)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_widget.setLayout(self.cards_layout)
        
        scroll_area.setWidget(self.cards_widget)
        left_layout.addWidget(scroll_area)
        
        left_widget.setLayout(left_layout)
        content_layout.addWidget(left_widget, 2)  # 2/5 of space
        
        # Right side - Results table
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # Title
        results_title = QLabel(self.t("exercise_history"))
        results_title.setFont(title_font)
        results_title.setStyleSheet("color: #2c3e50;")
        right_layout.addWidget(results_title)
        
        # Table
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setStyleSheet("""
            QTableView {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: bold;
            }
        """)
        right_layout.addWidget(self.table_view)
        
        # Refresh button
        refresh_button = QPushButton(self.t("refresh"))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        refresh_button.clicked.connect(self.refresh)
        right_layout.addWidget(refresh_button)
        
        right_widget.setLayout(right_layout)
        content_layout.addWidget(right_widget, 3)  # 3/5 of space
        
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("background-color: #f8f9fa;")
    
    def _get_exercise_type_translation_key(self, exercise_type: str) -> str:
        """Get translation key for exercise type."""
        # Map exercise types to translation keys
        type_map = {
            "breathing": "exercise_type_breathing",
            "meditation": "exercise_type_meditation",
            "guided_relaxation": "exercise_type_guided_relaxation",
            "music_therapy": "exercise_type_music_therapy",
            "relaxation": "exercise_type_guided_relaxation",  # Legacy support
            "journaling": "exercise_type_journaling",
            "activity": "exercise_type_activity",
            "stretching": "exercise_type_stretching",
            "ehsan": "exercise_type_ehsan"
        }
        
        return type_map.get(exercise_type, f"exercise_type_{exercise_type}")
    
    def _populate_filter(self, preserve_selection: bool = False) -> None:
        """
        Populate filter combo box with distinct exercise types from database.
        
        Args:
            preserve_selection: If True, try to preserve the current filter selection
        """
        # Store current selection if preserving
        current_data = None
        if preserve_selection and self.filter_combo.count() > 0:
            current_data = self.filter_combo.currentData()
        
        # Temporarily disconnect signal to avoid triggering refresh during population
        self.filter_combo.currentIndexChanged.disconnect()
        
        self.filter_combo.clear()
        
        # Add "All" option
        self.filter_combo.addItem(self.t("all"), None)
        
        # Get distinct exercise types from database dynamically
        distinct_types = self.exercise_service.get_distinct_exercise_types(include_inactive=False)
        
        # Add each distinct type with proper translation
        for exercise_type in sorted(distinct_types):
            translation_key = self._get_exercise_type_translation_key(exercise_type)
            translated_text = self.t(translation_key)
            
            # If translation not found, use formatted type name
            if translated_text == translation_key:
                translated_text = exercise_type.replace("_", " ").title()
            
            self.filter_combo.addItem(translated_text, exercise_type)
        
        # Restore previous selection if preserving
        if preserve_selection and current_data is not None:
            # Find the index with matching data
            for i in range(self.filter_combo.count()):
                if self.filter_combo.itemData(i) == current_data:
                    self.filter_combo.setCurrentIndex(i)
                    break
            else:
                # If previous selection not found, default to "All"
                self.filter_combo.setCurrentIndex(0)
        else:
            # Default to "All" if not preserving
            self.filter_combo.setCurrentIndex(0)
        
        # Reconnect signal
        self.filter_combo.currentIndexChanged.connect(self.refresh)
    
    def refresh(self) -> None:
        """Refresh exercises and sessions."""
        # Refresh filter to get any new exercise types (preserve current selection)
        self._populate_filter(preserve_selection=True)
        
        # Refresh exercise cards
        self._refresh_cards()
        
        # Refresh sessions table
        self._refresh_table()
    
    def _refresh_cards(self) -> None:
        """Refresh exercise cards in responsive grid."""
        # Clear existing cards
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        # Get exercises
        filter_type = self.filter_combo.currentData()
        exercises = self.exercise_service.get_all_exercises(
            include_inactive=False,
            exercise_type=filter_type
        )
        
        # Create cards in grid layout - one item per row
        cols = 1
        for idx, exercise in enumerate(exercises):
            card = ExerciseCard(exercise, self.translation_manager, self._on_start_exercise)
            row = idx // cols
            col = idx % cols
            self.cards_layout.addWidget(card, row, col)
    
    def _refresh_table(self) -> None:
        """Refresh sessions table."""
        sessions = self.session_service.get_user_sessions(self.user['id'])
        
        # Get exercise names
        exercises = self.exercise_service.get_all_exercises()
        exercise_dict = {ex['id']: ex['name'] for ex in exercises}
        
        # Create model
        class TM:
            def __init__(self, t_func):
                self.t = t_func
        tm = TM(self.t)
        model = SessionsTableModel(sessions, exercise_dict, tm)
        self.table_view.setModel(model)
    
    def _on_start_exercise(self, exercise: dict) -> None:
        """Handle start exercise button."""
        dialog = ExerciseTimerDialog(
            exercise,
            self.translation_manager,
            self.user['id'],
            self.session_service
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh table immediately
            self._refresh_table()
            QMessageBox.information(
                self,
                self.t("success_title"),
                self.t("message_save_success")
            )
