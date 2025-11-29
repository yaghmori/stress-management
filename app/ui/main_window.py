"""
Main application window with navigation and stacked screens.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QMenuBar, QMenu, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QAction

from app.config.translation_manager import TranslationManager
from app.ui.screens.dashboard_screen import DashboardScreen
from app.ui.screens.stress_log_screen import StressLogScreen
from app.ui.screens.exercises_screen import ExercisesScreen
from app.ui.screens.anxiety_test_screen import AnxietyTestScreen
from app.ui.screens.reports_screen import ReportsScreen


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, user: dict, translation_manager: TranslationManager,
                 user_service, stress_service, exercise_service,
                 session_service, anxiety_service) -> None:
        """
        Initialize main window.
        
        Args:
            user: Authenticated user data
            translation_manager: Translation manager instance
            user_service: User service instance
            stress_service: Stress service instance
            exercise_service: Exercise service instance
            session_service: Session service instance
            anxiety_service: Anxiety test service instance
        """
        super().__init__()
        self.user = user
        self.translation_manager = translation_manager
        self.t = translation_manager.t
        self.user_service = user_service
        self.stress_service = stress_service
        self.exercise_service = exercise_service
        self.session_service = session_service
        self.anxiety_service = anxiety_service
        
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle(self.t("app_title"))
        self.setMinimumSize(1000, 700)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.t("welcome_user").format(username=self.user['username']))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Content area with stacked widget
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create screens
        self._create_screens()
        
        central_widget.setLayout(main_layout)
        
        # Set RTL layout direction
        self.setLayoutDirection(Qt.RightToLeft)
    
    def _create_menu_bar(self) -> None:
        """Create standard Windows menu bar."""
        menubar = self.menuBar()
        
        # Home menu
        home_menu = menubar.addMenu(self.t("dashboard"))
        dashboard_action = QAction(self.t("dashboard"), self)
        dashboard_action.triggered.connect(lambda: self._navigate_to_screen(0))
        home_menu.addAction(dashboard_action)
        
        # Stress menu (includes history)
        stress_menu = menubar.addMenu(self.t("stress"))
        stress_log_action = QAction(self.t("stress_log"), self)
        stress_log_action.triggered.connect(lambda: self._navigate_to_screen(1))
        stress_menu.addAction(stress_log_action)
        
        # Exercises menu (includes history)
        exercises_menu = menubar.addMenu(self.t("exercises"))
        exercises_action = QAction(self.t("exercises"), self)
        exercises_action.triggered.connect(lambda: self._navigate_to_screen(2))
        exercises_menu.addAction(exercises_action)
        
        # Anxiety menu (includes history)
        anxiety_menu = menubar.addMenu(self.t("anxiety"))
        anxiety_test_action = QAction(self.t("anxiety_test"), self)
        anxiety_test_action.triggered.connect(lambda: self._navigate_to_screen(3))
        anxiety_menu.addAction(anxiety_test_action)
        
        # Reports menu
        reports_menu = menubar.addMenu(self.t("reports"))
        reports_action = QAction(self.t("reports"), self)
        reports_action.triggered.connect(lambda: self._navigate_to_screen(4))
        reports_menu.addAction(reports_action)
        
        # User menu
        user_menu = menubar.addMenu(self.user['username'])
        logout_action = QAction(self.t("logout"), self)
        logout_action.triggered.connect(self._on_logout)
        user_menu.addAction(logout_action)
        
        # Store actions for navigation tracking
        self.nav_actions = {
            "dashboard": dashboard_action,
            "stress_log": stress_log_action,
            "exercises": exercises_action,
            "anxiety_test": anxiety_test_action,
            "reports": reports_action
        }
    
    def _create_screens(self) -> None:
        """Create and add all screens to stacked widget."""
        # Dashboard
        self.dashboard_screen = DashboardScreen(
            self.user, self.translation_manager, self.stress_service, 
            self.session_service, self.anxiety_service
        )
        self.stacked_widget.addWidget(self.dashboard_screen)
        
        # Stress Log (includes history)
        self.stress_log_screen = StressLogScreen(
            self.user, self.translation_manager, self.stress_service
        )
        self.stacked_widget.addWidget(self.stress_log_screen)
        
        # Exercises (includes history)
        self.exercises_screen = ExercisesScreen(
            self.user, self.translation_manager, self.exercise_service, self.session_service
        )
        self.stacked_widget.addWidget(self.exercises_screen)
        
        # Anxiety Test (includes history)
        self.anxiety_test_screen = AnxietyTestScreen(
            self.user, self.translation_manager, self.anxiety_service
        )
        self.stacked_widget.addWidget(self.anxiety_test_screen)
        
        # Reports
        self.reports_screen = ReportsScreen(
            self.user, self.translation_manager, self.stress_service, self.anxiety_service
        )
        self.stacked_widget.addWidget(self.reports_screen)
    
    def _navigate_to_screen(self, index: int) -> None:
        """Navigate to screen by index."""
        self.stacked_widget.setCurrentIndex(index)
        
        # Update status bar
        nav_items = ["dashboard", "stress_log", "exercises", "anxiety_test", "reports"]
        if 0 <= index < len(nav_items):
            key = nav_items[index]
            self.status_bar.showMessage(self.t(key))
        
        # Refresh current screen
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'refresh'):
            current_widget.refresh()
    
    def _on_logout(self) -> None:
        """Handle logout."""
        self.close()

