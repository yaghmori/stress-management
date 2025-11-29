"""
Anxiety test screen with test cards and history table.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QTableView, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont
from typing import List, Dict, Any

from app.config.translation_manager import TranslationManager
from app.config.date_utils import format_date_for_display
from app.ui.screens.anxiety_test_dialog import AnxietyTestDialog


class AnxietyTestCard(QFrame):
    """Anxiety test card widget with improved responsive design."""
    
    def __init__(self, test: dict, translation_manager: TranslationManager,
                 on_start_callback) -> None:
        """Initialize anxiety test card."""
        super().__init__()
        self.test = test
        self.t = translation_manager.t
        self.on_start_callback = on_start_callback
        
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
                border: 2px solid #3498db;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Test name
        name_label = QLabel(self.test.get('test_name', ''))
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        name_label.setStyleSheet("color: #2c3e50; padding-bottom: 5px;")
        layout.addWidget(name_label)
        
        # Description (if available)
        description = self.test.get('description', '')
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            desc_label.setStyleSheet("color: #7f8c8d; font-size: 11px; padding-bottom: 8px;")
            layout.addWidget(desc_label)
        
        # Details - Use vertical layout
        details_container = QWidget()
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(6)
        
        # Questions count
        questions_label = QLabel(f"{self.t('questions')}: {self.test.get('question_count', 0)}")
        questions_label.setWordWrap(True)
        questions_label.setStyleSheet("color: #555555; font-size: 11px;")
        details_layout.addWidget(questions_label)
        
        # Max score
        score_label = QLabel(f"{self.t('max_score')}: {self.test.get('max_score', 0)}")
        score_label.setWordWrap(True)
        score_label.setStyleSheet("color: #555555; font-size: 11px;")
        details_layout.addWidget(score_label)
        
        details_container.setLayout(details_layout)
        layout.addWidget(details_container)
        
        # Start button
        start_button = QPushButton(self.t("start_test"))
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
        start_button.clicked.connect(lambda: self.on_start_callback(self.test))
        layout.addWidget(start_button)
        
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumHeight(150)


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
                date_str = test.get('date', '')
                return format_date_for_display(date_str)
            elif col == 1:
                return test.get('test_name', '')
            elif col == 2:
                score = test.get('score', 0)
                max_score = test.get('max_score', 0)
                return f"{score}/{max_score}"
            elif col == 3:
                percentage = test.get('percentage', 0)
                return f"{percentage}%"
            elif col == 4:
                return test.get('interpretation', '') or ''
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> Any:
        """Return header data."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section < len(self.headers):
                return self.headers[section]
        return None


class AnxietyTestScreen(QWidget):
    """Anxiety test screen with cards and history."""
    
    def __init__(self, user: dict, translation_manager: TranslationManager,
                 anxiety_service) -> None:
        """
        Initialize anxiety test screen.
        
        Args:
            user: User data
            translation_manager: Translation manager
            anxiety_service: Anxiety test service instance
        """
        super().__init__()
        self.user = user
        self.translation_manager = translation_manager
        self.t = translation_manager.t
        self.anxiety_service = anxiety_service
        self.available_tests = []
        
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
        
        tests_title = QLabel(self.t("anxiety_test_title"))
        tests_title.setFont(title_font)
        tests_title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(tests_title)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Main content area - horizontal split
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side - Test cards in scrollable grid
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
        
        # Right side - Results table
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # Title
        history_title = QLabel(self.t("anxiety_test_history"))
        history_title.setFont(title_font)
        history_title.setStyleSheet("color: #2c3e50;")
        right_layout.addWidget(history_title)
        
        # Table
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
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
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
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
        button_layout.addWidget(refresh_button)
        
        delete_button = QPushButton(self.t("delete"))
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_button.clicked.connect(self._on_delete)
        button_layout.addWidget(delete_button)
        
        right_layout.addLayout(button_layout)
        
        right_widget.setLayout(right_layout)
        content_layout.addWidget(right_widget, 3)  # 3/5 of space
        
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("background-color: #f8f9fa;")
    
    def refresh(self) -> None:
        """Refresh tests and history."""
        # Refresh test cards
        self._refresh_cards()
        
        # Refresh history table
        self._refresh_table()
    
    def _refresh_cards(self) -> None:
        """Refresh test cards in responsive grid."""
        # Clear existing cards
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        
        # Get available tests
        try:
            self.available_tests = self.anxiety_service.get_available_tests()
            
            if not self.available_tests:
                no_tests_label = QLabel(self.t("message_no_data"))
                no_tests_label.setAlignment(Qt.AlignCenter)
                self.cards_layout.addWidget(no_tests_label, 0, 0)
            else:
                # Create cards in grid layout - one item per row
                cols = 1
                for idx, test in enumerate(self.available_tests):
                    card = AnxietyTestCard(test, self.translation_manager, self._on_start_test)
                    row = idx // cols
                    col = idx % cols
                    self.cards_layout.addWidget(card, row, col)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading anxiety tests: {e}", exc_info=True)
            error_label = QLabel(f"Error loading tests: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            self.cards_layout.addWidget(error_label, 0, 0)
    
    def _refresh_table(self) -> None:
        """Refresh history table."""
        tests = self.anxiety_service.get_user_results(self.user['id'])
        
        # Create translation manager wrapper
        class TM:
            def __init__(self, t_func):
                self.t = t_func
        tm = TM(self.t)
        
        model = AnxietyHistoryTableModel(tests, tm)
        self.table_view.setModel(model)
    
    def _on_start_test(self, test: dict) -> None:
        """Handle start test button."""
        # Get questions for the test
        questions = self.anxiety_service.get_test_questions(test['id'])
        if not questions:
            QMessageBox.warning(
                self,
                self.t("error_title"),
                self.t("message_no_data")
            )
            return
        
        # Open test dialog
        dialog = AnxietyTestDialog(test, questions, self.translation_manager, self)
        if dialog.exec() == AnxietyTestDialog.Accepted:
            answers = dialog.get_answers()
            
            # Save result
            result_id = self.anxiety_service.create_test_result(
                self.user['id'],
                self.user['username'],
                test['id'],
                answers
            )
            
            if result_id:
                # Get result to show details
                result = self.anxiety_service.get_result(result_id)
                if result:
                    score = result['score']
                    max_score = result['max_score']
                    percentage = result['percentage']
                    interpretation = result.get('interpretation', '')
                    
                    message = f"{self.t('anxiety_score')}: {score}/{max_score} ({percentage}%)\n"
                    if interpretation:
                        message += f"\n{interpretation}"
                    
                    QMessageBox.information(
                        self,
                        self.t("success_title"),
                        message
                    )
                    
                    # Refresh table immediately
                    self._refresh_table()
            else:
                QMessageBox.warning(
                    self,
                    self.t("error_title"),
                    self.t("message_save_failed")
                )
    
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
                    self._refresh_table()
                else:
                    QMessageBox.warning(
                        self,
                        self.t("error_title"),
                        self.t("message_delete_failed")
                    )
