"""
Dashboard screen showing overview and statistics.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QGroupBox, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from datetime import date, timedelta

from app.config.translation_manager import TranslationManager
from app.config.date_utils import format_date_for_display


class DashboardScreen(QWidget):
    """Dashboard screen widget."""
    
    def __init__(self, user: dict, translation_manager: TranslationManager,
                 stress_service, session_service, anxiety_service=None) -> None:
        """
        Initialize dashboard screen.
        
        Args:
            user: User data
            translation_manager: Translation manager
            stress_service: Stress service instance
            session_service: Session service instance
            anxiety_service: Anxiety service instance (optional)
        """
        super().__init__()
        self.user = user
        self.t = translation_manager.t
        self.stress_service = stress_service
        self.session_service = session_service
        self.anxiety_service = anxiety_service
        
        self._init_ui()
        self.refresh()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Welcome message
        welcome_text = self.t("welcome_user").format(username=self.user['username'])
        welcome_label = QLabel(welcome_text)
        main_layout.addWidget(welcome_label)
        
        # Statistics Grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(10)
        
        # Today's Stress
        today_stress_group = QGroupBox(self.t("today_stress"))
        today_stress_layout = QVBoxLayout()
        self.today_stress_label = QLabel("---")
        self.today_stress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        today_stress_layout.addWidget(self.today_stress_label)
        today_stress_group.setLayout(today_stress_layout)
        stats_layout.addWidget(today_stress_group, 0, 0)
        
        # Weekly Average
        weekly_avg_group = QGroupBox(self.t("weekly_average"))
        weekly_avg_layout = QVBoxLayout()
        self.weekly_avg_label = QLabel("---")
        self.weekly_avg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        weekly_avg_layout.addWidget(self.weekly_avg_label)
        weekly_avg_group.setLayout(weekly_avg_layout)
        stats_layout.addWidget(weekly_avg_group, 0, 1)
        
        # Total Sessions
        total_sessions_group = QGroupBox(self.t("total_sessions"))
        total_sessions_layout = QVBoxLayout()
        self.total_sessions_label = QLabel("0")
        self.total_sessions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_sessions_layout.addWidget(self.total_sessions_label)
        total_sessions_group.setLayout(total_sessions_layout)
        stats_layout.addWidget(total_sessions_group, 0, 2)
        
        # Completed Exercises
        completed_exercises_group = QGroupBox(self.t("completed_exercises"))
        completed_exercises_layout = QVBoxLayout()
        self.completed_exercises_label = QLabel("0")
        self.completed_exercises_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        completed_exercises_layout.addWidget(self.completed_exercises_label)
        completed_exercises_group.setLayout(completed_exercises_layout)
        stats_layout.addWidget(completed_exercises_group, 0, 3)
        
        main_layout.addLayout(stats_layout)
        
        # Analysis Section
        analysis_layout = QHBoxLayout()
        analysis_layout.setSpacing(10)
        
        # Stress Trend Table
        stress_trend_group = QGroupBox(self.t("stress_trend"))
        stress_trend_layout = QVBoxLayout()
        self.stress_trend_table = QTableWidget()
        self.stress_trend_table.setColumnCount(2)
        self.stress_trend_table.setHorizontalHeaderLabels([self.t("date"), self.t("stress_level")])
        self.stress_trend_table.horizontalHeader().setStretchLastSection(True)
        self.stress_trend_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.stress_trend_table.setAlternatingRowColors(True)
        stress_trend_layout.addWidget(self.stress_trend_table)
        stress_trend_group.setLayout(stress_trend_layout)
        analysis_layout.addWidget(stress_trend_group, 1)
        
        # Recent Anxiety Tests
        anxiety_group = QGroupBox(self.t("anxiety_test") + " - " + self.t("recent_activity"))
        anxiety_layout = QVBoxLayout()
        self.anxiety_results_table = QTableWidget()
        self.anxiety_results_table.setColumnCount(3)
        self.anxiety_results_table.setHorizontalHeaderLabels([self.t("date"), self.t("anxiety_score"), self.t("interpretation")])
        self.anxiety_results_table.horizontalHeader().setStretchLastSection(True)
        self.anxiety_results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.anxiety_results_table.setAlternatingRowColors(True)
        anxiety_layout.addWidget(self.anxiety_results_table)
        anxiety_group.setLayout(anxiety_layout)
        analysis_layout.addWidget(anxiety_group, 1)
        
        main_layout.addLayout(analysis_layout)
        
        # Recent Activity Section
        recent_group = QGroupBox(self.t("recent_activity"))
        recent_layout = QVBoxLayout()
        self.recent_activity_list = QListWidget()
        self.recent_activity_list.setAlternatingRowColors(True)
        recent_layout.addWidget(self.recent_activity_list)
        recent_group.setLayout(recent_layout)
        main_layout.addWidget(recent_group)
        
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def refresh(self) -> None:
        """Refresh dashboard data."""
        user_id = self.user['id']
        
        # Today's stress
        today_stress = self.stress_service.get_today_stress(user_id)
        if today_stress:
            stress_level = today_stress['stress_level']
            stress_text = f"{stress_level}/10"
            self.today_stress_label.setText(stress_text)
        else:
            self.today_stress_label.setText(self.t("message_no_data"))
        
        # Weekly average
        weekly_avg = self.stress_service.get_average_stress(user_id, days=7)
        if weekly_avg:
            avg_text = f"{weekly_avg:.1f}/10"
            self.weekly_avg_label.setText(avg_text)
        else:
            self.weekly_avg_label.setText(self.t("message_no_data"))
        
        # Total sessions
        session_count = self.session_service.get_user_session_count(user_id)
        self.total_sessions_label.setText(str(session_count))
        
        # Completed exercises
        sessions = self.session_service.get_user_sessions(user_id, limit=100)
        completed = sum(1 for s in sessions if s.get('completion_status') == 'completed')
        self.completed_exercises_label.setText(str(completed))
        
        # Stress trend (last 7 days)
        self._update_stress_trend(user_id)
        
        # Anxiety test results
        if self.anxiety_service:
            self._update_anxiety_results(user_id)
        
        # Recent activity
        self._update_recent_activity(user_id)
    
    def _update_stress_trend(self, user_id: int) -> None:
        """Update stress trend display."""
        end_date = date.today()
        start_date = end_date - timedelta(days=6)  # Last 7 days
        
        logs = self.stress_service.get_user_logs(
            user_id, limit=30, start_date=start_date, end_date=end_date
        )
        
        # Clear table
        self.stress_trend_table.setRowCount(0)
        
        if not logs:
            return
        
        # Normalize dates from logs
        log_dates = {}
        for log in logs:
            log_date = log['date']
            if isinstance(log_date, str):
                try:
                    log_date = date.fromisoformat(log_date)
                except (ValueError, AttributeError):
                    continue
            elif not isinstance(log_date, date):
                continue
            
            date_key = log_date.isoformat()
            if date_key not in log_dates:
                log_dates[date_key] = []
            log_dates[date_key].append(log)
        
        # Populate table
        for i in range(7):
            check_date = end_date - timedelta(days=6-i)
            date_key = check_date.isoformat()
            day_logs = log_dates.get(date_key, [])
            
            row = self.stress_trend_table.rowCount()
            self.stress_trend_table.insertRow(row)
            
            date_str = format_date_for_display(check_date)
            date_item = QTableWidgetItem(date_str)
            self.stress_trend_table.setItem(row, 0, date_item)
            
            if day_logs:
                avg_level = sum(log['stress_level'] for log in day_logs) / len(day_logs)
                level_item = QTableWidgetItem(f"{avg_level:.1f}/10")
            else:
                level_item = QTableWidgetItem("-")
            self.stress_trend_table.setItem(row, 1, level_item)
    
    def _update_anxiety_results(self, user_id: int) -> None:
        """Update anxiety test results display."""
        # Clear table
        self.anxiety_results_table.setRowCount(0)
        
        if not self.anxiety_service:
            return
        
        results = self.anxiety_service.get_user_results(user_id, limit=3)
        
        if not results:
            return
        
        for result in results:
            row = self.anxiety_results_table.rowCount()
            self.anxiety_results_table.insertRow(row)
            
            date_str = result.get('created_at', '')
            formatted_date = format_date_for_display(date_str)
            date_item = QTableWidgetItem(formatted_date)
            self.anxiety_results_table.setItem(row, 0, date_item)
            
            score = result.get('score', 0)
            max_score = result.get('max_score', 0)
            percentage = result.get('percentage', 0)
            score_item = QTableWidgetItem(f"{score}/{max_score} ({percentage:.1f}%)")
            self.anxiety_results_table.setItem(row, 1, score_item)
            
            interpretation = result.get('interpretation', '')
            interpretation_item = QTableWidgetItem(interpretation)
            self.anxiety_results_table.setItem(row, 2, interpretation_item)
    
    def _update_recent_activity(self, user_id: int) -> None:
        """Update recent activity list."""
        self.recent_activity_list.clear()
        
        recent_logs = self.stress_service.get_user_logs(user_id, limit=5)
        if not recent_logs:
            item = QListWidgetItem(self.t("message_no_data"))
            self.recent_activity_list.addItem(item)
            return
        
        for log in recent_logs:
            log_date = log['date']
            date_str = format_date_for_display(log_date)
            
            level = log['stress_level']
            activity_text = f"{date_str}: {self.t('stress_level')} {level}/10"
            item = QListWidgetItem(activity_text)
            self.recent_activity_list.addItem(item)
