"""
Stress log screen with log cards and history table.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QTableView, QHeaderView, QMessageBox,
    QDialog, QFormLayout, QSpinBox, QTextEdit, QDoubleSpinBox,
    QGridLayout
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont
from typing import List, Dict, Any

from app.config.translation_manager import TranslationManager
from app.config.date_utils import format_date_for_display
from app.config.config import STRESS_LEVEL_MIN, STRESS_LEVEL_MAX
from app.ui.widgets.persian_date_edit import PersianDateEdit


class StressLogCard(QFrame):
    """Stress log card widget with improved responsive design."""
    
    def __init__(self, level: int, level_name: str, translation_manager: TranslationManager,
                 on_log_callback) -> None:
        """Initialize stress log card."""
        super().__init__()
        self.level = level
        self.level_name = level_name
        self.t = translation_manager.t
        self.on_log_callback = on_log_callback
        
        self._init_ui()
    
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
                border: 1px solid #3498db;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Level name
        name_label = QLabel(self.level_name)
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        name_label.setStyleSheet("color: #2c3e50; padding-bottom: 5px;")
        layout.addWidget(name_label)
        
        # Level number
        level_label = QLabel(f"{self.t('stress_level')}: {self.level}/10")
        level_label.setWordWrap(True)
        level_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        level_label.setStyleSheet("color: #555555; font-size: 11px; padding-bottom: 8px;")
        layout.addWidget(level_label)
        
        # Log button
        log_button = QPushButton(self.t("log_stress"))
        log_button.setStyleSheet("""
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
        log_button.clicked.connect(lambda: self.on_log_callback(self.level))
        layout.addWidget(log_button)
        
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumHeight(150)


class StressLogDialog(QDialog):
    """Dialog for logging stress."""
    
    def __init__(self, default_level: int, translation_manager: TranslationManager) -> None:
        """Initialize stress log dialog."""
        super().__init__()
        self.t = translation_manager.t
        self.default_level = default_level
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize UI."""
        self.setWindowTitle(self.t("stress_log"))
        self.setMinimumSize(400, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Date
        self.date_input = PersianDateEdit()
        form_layout.addRow(self.t("date") + ":", self.date_input)
        
        # Stress level
        self.stress_level_input = QSpinBox()
        self.stress_level_input.setMinimum(STRESS_LEVEL_MIN)
        self.stress_level_input.setMaximum(STRESS_LEVEL_MAX)
        self.stress_level_input.setValue(self.default_level)
        form_layout.addRow(self.t("stress_level") + ":", self.stress_level_input)
        
        # Sleep hours
        self.sleep_hours_input = QDoubleSpinBox()
        self.sleep_hours_input.setMinimum(0)
        self.sleep_hours_input.setMaximum(24)
        self.sleep_hours_input.setSuffix(" " + self.t("sleep_hours"))
        form_layout.addRow(self.t("sleep_hours") + ":", self.sleep_hours_input)
        
        # Physical activity
        self.physical_activity_input = QSpinBox()
        self.physical_activity_input.setMinimum(0)
        self.physical_activity_input.setMaximum(1440)
        self.physical_activity_input.setSuffix(" " + self.t("physical_activity"))
        form_layout.addRow(self.t("physical_activity") + ":", self.physical_activity_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow(self.t("notes") + ":", self.notes_input)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        submit_button = QPushButton(self.t("submit"))
        submit_button.clicked.connect(self.accept)
        button_layout.addWidget(submit_button)
        
        cancel_button = QPushButton(self.t("cancel"))
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def get_data(self) -> dict:
        """Get form data."""
        return {
            'date': self.date_input.getGregorianDate(),  # Convert to Gregorian for database
            'stress_level': self.stress_level_input.value(),
            'sleep_hours': self.sleep_hours_input.value() if self.sleep_hours_input.value() > 0 else None,
            'physical_activity': self.physical_activity_input.value() if self.physical_activity_input.value() > 0 else None,
            'notes': self.notes_input.toPlainText().strip() or None
        }


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


class StressLogScreen(QWidget):
    """Stress log screen with cards and history."""
    
    def __init__(self, user: dict, translation_manager: TranslationManager,
                 stress_service) -> None:
        """
        Initialize stress log screen.
        
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
        self.refresh()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header with title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        
        log_title = QLabel(self.t("stress_log"))
        log_title.setFont(title_font)
        log_title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(log_title)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Main content area - horizontal split
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side - Stress level cards in scrollable grid
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
        # Use grid layout for one item per row
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(15)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_widget.setLayout(self.cards_layout)
        
        scroll_area.setWidget(self.cards_widget)
        left_layout.addWidget(scroll_area)
        
        left_widget.setLayout(left_layout)
        content_layout.addWidget(left_widget, 2)  # 2/5 of space
        
        # Right side - History table
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # Title
        history_title = QLabel(self.t("stress_history"))
        history_title.setFont(title_font)
        history_title.setStyleSheet("color: #2c3e50;")
        right_layout.addWidget(history_title)
        
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
    
    def refresh(self) -> None:
        """Refresh cards and history."""
        # Refresh cards
        self._refresh_cards()
        
        # Refresh history table
        self._refresh_table()
    
    def _refresh_cards(self) -> None:
        """Refresh stress level cards in responsive grid."""
        # Clear existing cards
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        # Create cards for different stress levels
        stress_levels = [
            (1, self.t("stress_level_1")),
            (2, self.t("stress_level_2")),
            (3, self.t("stress_level_3")),
            (4, self.t("stress_level_4")),
            (5, self.t("stress_level_5")),
            (6, self.t("stress_level_6")),
            (7, self.t("stress_level_7")),
            (8, self.t("stress_level_8")),
            (9, self.t("stress_level_9")),
            (10, self.t("stress_level_10"))
        ]
        
        # Create cards in grid layout - one item per row
        cols = 1
        for idx, (level, level_name) in enumerate(stress_levels):
            card = StressLogCard(level, level_name, self.translation_manager, self._on_log_stress)
            row = idx // cols
            col = idx % cols
            self.cards_layout.addWidget(card, row, col)
    
    def _refresh_table(self) -> None:
        """Refresh history table."""
        logs = self.stress_service.get_user_logs(self.user['id'])
        
        # Create translation manager wrapper
        class TM:
            def __init__(self, t_func):
                self.t = t_func
        tm = TM(self.t)
        
        model = StressHistoryTableModel(logs, tm)
        self.table_view.setModel(model)
    
    def _on_log_stress(self, level: int) -> None:
        """Handle log stress button."""
        dialog = StressLogDialog(level, self.translation_manager)
        
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            log_id = self.stress_service.create_log(
                self.user['id'],
                data['stress_level'],
                data['date'],
                data['notes'],
                data['sleep_hours'],
                data['physical_activity']
            )
            
            if log_id:
                QMessageBox.information(
                    self,
                    self.t("success_title"),
                    self.t("message_save_success")
                )
                # Refresh table immediately
                self._refresh_table()
            else:
                QMessageBox.warning(
                    self,
                    self.t("error_title"),
                    self.t("message_save_failed")
                )
