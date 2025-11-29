"""
Dashboard screen showing overview and statistics.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QGroupBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis, QCategoryAxis
from PySide6.QtGui import QPen, QColor, QPainter
from datetime import date, timedelta, datetime, time
import jdatetime

from app.config.translation_manager import TranslationManager
from app.config.date_utils import format_date_for_display, gregorian_to_shamsi


class DashboardScreen(QWidget):
    """Dashboard screen widget."""
    
    # Persian month names
    PERSIAN_MONTHS = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    
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
    
    def _get_persian_month_name(self, gregorian_date: date) -> str:
        """Get Persian month name for a Gregorian date."""
        try:
            shamsi_date = gregorian_to_shamsi(gregorian_date)
            if isinstance(shamsi_date, jdatetime.datetime):
                month_num = shamsi_date.month
            elif isinstance(shamsi_date, jdatetime.date):
                month_num = shamsi_date.month
            else:
                return ""
            if 1 <= month_num <= 12:
                return self.PERSIAN_MONTHS[month_num - 1]
        except:
            pass
        return ""
    
    def _format_persian_date_label(self, gregorian_date: date) -> str:
        """Format date label with Persian month name."""
        try:
            shamsi_date = gregorian_to_shamsi(gregorian_date)
            if isinstance(shamsi_date, jdatetime.datetime):
                return f"{shamsi_date.day} {self._get_persian_month_name(gregorian_date)}"
            elif isinstance(shamsi_date, jdatetime.date):
                return f"{shamsi_date.day} {self._get_persian_month_name(gregorian_date)}"
        except:
            pass
        return format_date_for_display(gregorian_date, "%d/%m")
    
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
        
        # Charts Section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(10)
        
        # Stress Chart
        stress_chart_group = QGroupBox(self.t("stress_level") + " - " + self.t("progress_overview"))
        stress_chart_layout = QVBoxLayout()
        self.stress_chart_view = QChartView()
        self.stress_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.stress_chart_view.setMinimumHeight(300)
        stress_chart_layout.addWidget(self.stress_chart_view)
        stress_chart_group.setLayout(stress_chart_layout)
        charts_layout.addWidget(stress_chart_group, 1)
        
        # Anxiety Chart
        anxiety_chart_group = QGroupBox(self.t("anxiety_test") + " - " + self.t("progress_overview"))
        anxiety_chart_layout = QVBoxLayout()
        self.anxiety_chart_view = QChartView()
        self.anxiety_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.anxiety_chart_view.setMinimumHeight(300)
        anxiety_chart_layout.addWidget(self.anxiety_chart_view)
        anxiety_chart_group.setLayout(anxiety_chart_layout)
        charts_layout.addWidget(anxiety_chart_group, 1)
        
        main_layout.addLayout(charts_layout)
        
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
        
        # Update charts
        self._update_stress_chart(user_id)
        if self.anxiety_service:
            self._update_anxiety_chart(user_id)
            # Check for high anxiety warning
            self._check_anxiety_warning(user_id)
    
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
        
        results = self.anxiety_service.get_user_results(user_id)
        
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
    
    def _update_stress_chart(self, user_id: int) -> None:
        """Update stress level chart."""
        # Get data for last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=29)
        
        logs = self.stress_service.get_user_logs(
            user_id, limit=100, start_date=start_date, end_date=end_date
        )
        
        # Create chart
        chart = QChart()
        chart.setTitle(self.t("stress_level") + " - " + self.t("progress_overview"))
        
        # Create series
        series = QLineSeries()
        series.setName(self.t("stress_level"))
        
        # Group logs by date and calculate average per day
        log_dates = {}
        for log in logs:
            log_date = log.get('date')
            if not log_date:
                continue
                
            # Parse date - handle different formats
            if isinstance(log_date, str):
                try:
                    # Try ISO format first
                    if 'T' in log_date:
                        log_date = datetime.fromisoformat(log_date.split('T')[0]).date()
                    else:
                        log_date = date.fromisoformat(log_date)
                except (ValueError, AttributeError):
                    try:
                        # Try other common formats
                        log_date = datetime.strptime(log_date, '%Y-%m-%d').date()
                    except (ValueError, AttributeError):
                        continue
            elif isinstance(log_date, datetime):
                log_date = log_date.date()
            elif not isinstance(log_date, date):
                continue
            
            date_key = log_date.isoformat()
            if date_key not in log_dates:
                log_dates[date_key] = []
            log_dates[date_key].append(log)
        
        # Add data points for each day in range
        for i in range(30):
            check_date = end_date - timedelta(days=29-i)
            date_key = check_date.isoformat()
            day_logs = log_dates.get(date_key, [])
            
            # Convert date to QDateTime (set to noon for better display)
            dt = datetime.combine(check_date, time(hour=12))
            qdt = QDateTime.fromSecsSinceEpoch(int(dt.timestamp()))
            
            if day_logs:
                avg_level = sum(log.get('stress_level', 0) for log in day_logs) / len(day_logs)
                series.append(qdt.toMSecsSinceEpoch(), float(avg_level))
            # Don't add points for days with no data - this creates gaps in the line
        
        # Always add series to chart
        chart.addSeries(series)
        
        # Create axes - always show them even with no data
        axis_x = QDateTimeAxis()
        axis_x.setTitleText(self.t("date"))
        start_dt = datetime.combine(start_date, time(hour=12))
        end_dt = datetime.combine(end_date, time(hour=12))
        axis_x.setMin(QDateTime.fromSecsSinceEpoch(int(start_dt.timestamp())))
        axis_x.setMax(QDateTime.fromSecsSinceEpoch(int(end_dt.timestamp())))
        
        # Try to use Persian month names - Qt's locale should handle this if set correctly
        # Format: day and abbreviated month name
        # If Persian locale is set, this should show Persian months
        axis_x.setFormat("d MMM")
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        if series.count() > 0:
            series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText(self.t("stress_level"))
        axis_y.setRange(0, 10)
        axis_y.setTickCount(11)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        if series.count() > 0:
            series.attachAxis(axis_y)
        
        if series.count() > 0:
            # Set line color
            pen = QPen(QColor(255, 100, 100))
            pen.setWidth(2)
            series.setPen(pen)
        else:
            # Show message when no data
            chart.setTitle(self.t("stress_level") + " - " + self.t("progress_overview") + " (" + self.t("message_no_data") + ")")
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # Set chart to view and update
        self.stress_chart_view.setChart(chart)
        self.stress_chart_view.update()
    
    def _update_anxiety_chart(self, user_id: int) -> None:
        """Update anxiety test chart."""
        if not self.anxiety_service:
            return
        
        # Get anxiety test results
        results = self.anxiety_service.get_user_results(user_id, limit=30)
        
        # Create chart
        chart = QChart()
        chart.setTitle(self.t("anxiety_test") + " - " + self.t("progress_overview"))
        
        # Create series for percentage
        series = QLineSeries()
        series.setName(self.t("anxiety_score") + " (%)")
        
        if results:
            # Try to use 'date' field first, then 'created_at'
            for result in results:
                # Try 'date' field first (stored as YYYY-MM-DD string)
                date_str = result.get('date') or result.get('created_at', '')
                percentage = result.get('percentage', 0)
                
                if not date_str:
                    continue
                
                # Parse date - handle different formats
                dt = None
                if isinstance(date_str, str):
                    try:
                        # Try ISO format first (YYYY-MM-DD)
                        if 'T' in date_str:
                            # Timestamp format: YYYY-MM-DDTHH:MM:SS
                            dt = datetime.fromisoformat(date_str.split('.')[0].replace('Z', ''))
                        elif ' ' in date_str:
                            # Format: YYYY-MM-DD HH:MM:SS
                            dt = datetime.strptime(date_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                        else:
                            # Format: YYYY-MM-DD
                            dt = datetime.strptime(date_str, '%Y-%m-%d')
                    except (ValueError, AttributeError) as e:
                        # Try alternative formats
                        try:
                            dt = datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d')
                        except:
                            continue
                elif isinstance(date_str, date):
                    dt = datetime.combine(date_str, time(hour=12))
                elif isinstance(date_str, datetime):
                    dt = date_str
                
                if dt:
                    qdt = QDateTime.fromSecsSinceEpoch(int(dt.timestamp()))
                    series.append(qdt.toMSecsSinceEpoch(), float(percentage))
        
        # Always add series to chart
        chart.addSeries(series)
        
        # Create axes - always show them
        axis_x = QDateTimeAxis()
        # Try to use Persian month names - Qt's locale should handle this if set correctly
        axis_x.setFormat("d MMM")
        axis_x.setTitleText(self.t("date"))
        
        if series.count() > 0:
            # Set min/max from data
            first_point = series.points()[0]
            last_point = series.points()[-1]
            axis_x.setMin(QDateTime.fromMSecsSinceEpoch(int(first_point.x())))
            axis_x.setMax(QDateTime.fromMSecsSinceEpoch(int(last_point.x())))
        else:
            # No data - set default range (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=29)
            start_dt = datetime.combine(start_date, time(hour=12))
            end_dt = datetime.combine(end_date, time(hour=12))
            axis_x.setMin(QDateTime.fromSecsSinceEpoch(int(start_dt.timestamp())))
            axis_x.setMax(QDateTime.fromSecsSinceEpoch(int(end_dt.timestamp())))
            chart.setTitle(self.t("anxiety_test") + " - " + self.t("progress_overview") + " (" + self.t("message_no_data") + ")")
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        if series.count() > 0:
            series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText(self.t("anxiety_score") + " (%)")
        axis_y.setRange(0, 100)
        axis_y.setTickCount(11)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        if series.count() > 0:
            series.attachAxis(axis_y)
        
        if series.count() > 0:
            # Set line color
            pen = QPen(QColor(100, 150, 255))
            pen.setWidth(2)
            series.setPen(pen)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # Set chart to view
        self.anxiety_chart_view.setChart(chart)
        self.anxiety_chart_view.update()
    
    def _check_anxiety_warning(self, user_id: int) -> None:
        """Check if average of last 3 anxiety tests is higher than normal and show warning."""
        if not self.anxiety_service:
            return
        
        # Get last 3 anxiety test results
        results = self.anxiety_service.get_user_results(user_id, limit=3)
        
        # Need at least 3 results to check
        if len(results) < 3:
            return
        
        # Calculate average percentage of last 3 tests
        percentages = []
        for result in results:
            percentage = result.get('percentage', 0)
            if percentage is not None:
                percentages.append(float(percentage))
        
        if not percentages:
            return
        
        avg_percentage = sum(percentages) / len(percentages)
        
        # Check if average is higher than normal (above 50%)
        if avg_percentage > 50:
            # Format message with average
            message = self.t("anxiety_warning_message").format(
                average=f"{avg_percentage:.1f}%"
            )
            QMessageBox.warning(
                self,
                self.t("warning_title"),
                message
            )
