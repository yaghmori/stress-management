"""
Anxiety test history screen showing past test results.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableView, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont
from typing import List, Dict, Any

from app.config.translation_manager import TranslationManager
from app.config.date_utils import format_date_for_display


class AnxietyHistoryTableModel(QAbstractTableModel):
    """Table model for anxiety test history."""
    
    def __init__(self, data: List[Dict[str, Any]], translation_manager: TranslationManager) -> None:
        """Initialize model."""
        super().__init__()
        self._data = data
        self.t = translation_manager.t
        self.headers = [
            self.t("date"),
            self.t("test_type"),
            self.t("anxiety_score"),
            self.t("percentage"),
            self.t("interpretation")
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
            test = self._data[row]
            
            if col == 0:
                # Date
                date_str = test.get('date', '')
                return format_date_for_display(date_str)
            elif col == 1:
                # Test name
                return test.get('test_name', '')
            elif col == 2:
                # Score
                score = test.get('score', 0)
                max_score = test.get('max_score', 0)
                return f"{score}/{max_score}"
            elif col == 3:
                # Percentage
                percentage = test.get('percentage', 0)
                return f"{percentage}%"
            elif col == 4:
                # Interpretation
                return test.get('interpretation', '') or ''
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> Any:
        """Return header data."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section < len(self.headers):
                return self.headers[section]
        return None


class AnxietyHistoryScreen(QWidget):
    """Anxiety test history screen."""
    
    def __init__(self, user: dict, translation_manager: TranslationManager,
                 anxiety_service) -> None:
        """
        Initialize anxiety history screen.
        
        Args:
            user: User data
            translation_manager: Translation manager
            anxiety_service: Anxiety test service instance
        """
        super().__init__()
        self.user = user
        self.t = translation_manager.t
        self.anxiety_service = anxiety_service
        
        self._init_ui()
        self.refresh()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel(self.t("anxiety_test_history"))
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
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        layout.addWidget(self.table_view)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        refresh_button = QPushButton(self.t("refresh"))
        refresh_button.clicked.connect(self.refresh)
        button_layout.addWidget(refresh_button)
        
        delete_button = QPushButton(self.t("delete"))
        delete_button.clicked.connect(self._on_delete)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def refresh(self) -> None:
        """Refresh table data."""
        tests = self.anxiety_service.get_user_results(self.user['id'])
        
        # Create translation manager wrapper
        class TM:
            def __init__(self, t_func):
                self.t = t_func
        tm = TM(self.t)
        
        model = AnxietyHistoryTableModel(tests, tm)
        self.table_view.setModel(model)
    
    def _on_delete(self) -> None:
        """Handle delete button click."""
        selection = self.table_view.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(
                self,
                self.t("warning_title"),
                self.t("message_select_item")
            )
            return
        
        selected_row = selection.selectedRows()[0].row()
        tests = self.anxiety_service.get_user_results(self.user['id'])
        
        if selected_row < len(tests):
            test = tests[selected_row]
            result_id = test['id']
            
            reply = QMessageBox.question(
                self,
                self.t("confirm_title"),
                self.t("message_confirm_delete"),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.anxiety_service.delete_result(result_id):
                    QMessageBox.information(
                        self,
                        self.t("success_title"),
                        self.t("message_delete_success")
                    )
                    self.refresh()
                else:
                    QMessageBox.warning(
                        self,
                        self.t("error_title"),
                        self.t("message_delete_failed")
                    )

