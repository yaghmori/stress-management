"""
Exercise timer dialog for tracking exercise duration.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from datetime import datetime, timedelta

from app.config.translation_manager import TranslationManager


class ExerciseTimerDialog(QDialog):
    """Dialog for tracking exercise duration with timer."""
    
    def __init__(self, exercise: dict, translation_manager: TranslationManager,
                 user_id: int, session_service) -> None:
        """
        Initialize exercise timer dialog.
        
        Args:
            exercise: Exercise data
            translation_manager: Translation manager
            user_id: User ID
            session_service: Session service instance
        """
        super().__init__()
        self.exercise = exercise
        self.t = translation_manager.t
        self.user_id = user_id
        self.session_service = session_service
        
        self.start_time = None
        self.elapsed_seconds = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)
        self.is_running = False
        self.session_id = None
        
        self._init_ui()
        self._start_timer()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle(self.exercise.get('name', self.t("start_exercise")))
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Exercise name
        name_label = QLabel(self.exercise.get('name', ''))
        name_font = QFont()
        name_font.setPointSize(20)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # Exercise description
        description = self.exercise.get('description', '')
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(desc_label)
        
        # Timer display - keep custom font for monospace timer
        self.timer_label = QLabel("00:00:00")
        timer_font = QFont()
        timer_font.setPointSize(48)
        timer_font.setBold(True)
        timer_font.setFamily("Courier")
        self.timer_label.setFont(timer_font)
        self.timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timer_label)
        
        # Instructions - use native Windows styling
        instructions = QLabel(self.t("exercise_timer_instructions"))
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)
        
        layout.addStretch()
        
        # Buttons - use native Windows styling
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.stop_button = QPushButton(self.t("stop_exercise"))
        self.stop_button.setMinimumHeight(40)
        self.stop_button.clicked.connect(self._stop_timer)
        button_layout.addWidget(self.stop_button)
        
        cancel_button = QPushButton(self.t("cancel"))
        cancel_button.setMinimumHeight(40)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def _start_timer(self) -> None:
        """Start the exercise timer."""
        self.start_time = datetime.now()
        self.is_running = True
        self.timer.start(1000)  # Update every second
        self._update_timer()
    
    def _update_timer(self) -> None:
        """Update timer display."""
        if self.is_running:
            self.elapsed_seconds += 1
        
        hours = self.elapsed_seconds // 3600
        minutes = (self.elapsed_seconds % 3600) // 60
        seconds = self.elapsed_seconds % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.timer_label.setText(time_str)
    
    def _stop_timer(self) -> None:
        """Stop the timer and save session."""
        if not self.is_running:
            return
        
        self.is_running = False
        self.timer.stop()
        
        # Calculate duration in minutes (round up)
        duration_minutes = max(1, (self.elapsed_seconds + 59) // 60)
        
        # Create session with actual duration
        self.session_id = self.session_service.create_session(
            self.user_id,
            self.exercise['id'],
            duration_minutes,
            'completed'
        )
        
        if self.session_id:
            self.accept()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                self.t("error_title"),
                self.t("message_save_failed")
            )
    
    def get_duration_minutes(self) -> int:
        """Get elapsed duration in minutes."""
        return max(1, (self.elapsed_seconds + 59) // 60)
    
    def closeEvent(self, event) -> None:
        """Handle dialog close event."""
        if self.is_running:
            self._stop_timer()
        super().closeEvent(event)

