"""
Multi-step dialog for anxiety test questions.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QProgressBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import List, Dict, Any, Optional

from app.config.translation_manager import TranslationManager


class AnxietyTestDialog(QDialog):
    """Multi-step dialog for anxiety test."""
    
    def __init__(self, test: Dict[str, Any], questions: List[Dict[str, Any]],
                 translation_manager: TranslationManager, parent=None) -> None:
        """
        Initialize test dialog.
        
        Args:
            test: Test definition
            questions: List of questions
            translation_manager: Translation manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.test = test
        self.questions = questions
        self.t = translation_manager.t
        self.answers = [None] * len(questions)
        self.current_question_index = 0
        self.current_button_group: Optional[QButtonGroup] = None
        
        self._init_ui()
        self._show_question(0)
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle(self.test.get('test_name', self.t("anxiety_test_title")))
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Test info
        test_name_label = QLabel(self.test.get('test_name', ''))
        test_name_font = QFont()
        test_name_font.setPointSize(16)
        test_name_font.setBold(True)
        test_name_label.setFont(test_name_font)
        test_name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(test_name_label)
        
        if self.test.get('description'):
            desc_label = QLabel(self.test['description'])
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(desc_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.questions))
        self.progress_bar.setValue(1)
        layout.addWidget(self.progress_bar)
        
        # Question container
        self.question_container = QVBoxLayout()
        self.question_container.setSpacing(15)
        
        # Question label
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        question_font = QFont()
        question_font.setPointSize(12)
        self.question_label.setFont(question_font)
        self.question_container.addWidget(self.question_label)
        
        # Options container
        self.options_container = QVBoxLayout()
        self.options_container.setSpacing(10)
        self.question_container.addLayout(self.options_container)
        
        self.question_container.addStretch()
        
        question_widget = QVBoxLayout()
        question_widget.addLayout(self.question_container)
        question_widget.addStretch()
        
        layout.addLayout(question_widget)
        
        # Navigation buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.prev_button = QPushButton(self.t("previous"))
        self.prev_button.clicked.connect(self._on_previous)
        self.prev_button.setEnabled(False)
        button_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton(self.t("next"))
        self.next_button.clicked.connect(self._on_next)
        button_layout.addWidget(self.next_button)
        
        self.finish_button = QPushButton(self.t("finish"))
        self.finish_button.clicked.connect(self._on_finish)
        self.finish_button.setVisible(False)
        button_layout.addWidget(self.finish_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def _show_question(self, index: int) -> None:
        """Show question at index."""
        if index < 0 or index >= len(self.questions):
            return
        
        self.current_question_index = index
        question = self.questions[index]
        
        # Clear previous options
        if self.current_button_group:
            for button in self.current_button_group.buttons():
                button.setParent(None)
        
        # Update question text
        question_num = question['question_number']
        self.question_label.setText(f"{question_num}. {question['question_text']}")
        
        # Create new button group
        self.current_button_group = QButtonGroup(self)
        
        # Add option buttons
        options = question.get('options', [])
        if isinstance(options, str):
            try:
                import json
                options = json.loads(options)
            except:
                options = []
        
        for i, option_text in enumerate(options):
            radio = QRadioButton(option_text)
            self.current_button_group.addButton(radio, i)
            self.options_container.addWidget(radio)
        
        # Restore previous answer if exists
        if self.answers[index] is not None:
            button = self.current_button_group.button(self.answers[index])
            if button:
                button.setChecked(True)
        
        # Update progress
        self.progress_bar.setValue(index + 1)
        
        # Update navigation buttons
        self.prev_button.setEnabled(index > 0)
        is_last = (index == len(self.questions) - 1)
        self.next_button.setVisible(not is_last)
        self.finish_button.setVisible(is_last)
    
    def _save_current_answer(self) -> bool:
        """Save answer for current question."""
        if not self.current_button_group:
            return False
        
        checked_button = self.current_button_group.checkedButton()
        if not checked_button:
            return False
        
        answer_index = self.current_button_group.id(checked_button)
        self.answers[self.current_question_index] = answer_index
        return True
    
    def _on_previous(self) -> None:
        """Handle previous button click."""
        if self.current_question_index > 0:
            self._save_current_answer()
            self._show_question(self.current_question_index - 1)
    
    def _on_next(self) -> None:
        """Handle next button click."""
        if not self._save_current_answer():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                self.t("warning_title"),
                self.t("message_validation_error")
            )
            return
        
        if self.current_question_index < len(self.questions) - 1:
            self._show_question(self.current_question_index + 1)
    
    def _on_finish(self) -> None:
        """Handle finish button click."""
        if not self._save_current_answer():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                self.t("warning_title"),
                self.t("message_validation_error")
            )
            return
        
        # Check all questions are answered
        if None in self.answers:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                self.t("warning_title"),
                self.t("message_validation_error")
            )
            return
        
        self.accept()
    
    def get_answers(self) -> List[int]:
        """Get all answers."""
        return self.answers

