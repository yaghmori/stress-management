"""
Admin panel window with all administrative features.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QTableView, QHeaderView, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QTextEdit, QFileDialog, QTabWidget, QMenuBar, QMenu, QStatusBar
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont, QAction
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.config.translation_manager import TranslationManager
from app.services.user_service import UserService
from app.services.exercise_service import ExerciseService
from app.services.anxiety_test_service import AnxietyTestService
from app.services.admin_service import AdminService
from app.data.repositories.stress_repository import StressRepository
from app.data.repositories.session_repository import SessionRepository
from app.config.config import (
    ROLE_USER, ROLE_ADMIN,
    EXERCISE_TYPE_BREATHING, EXERCISE_TYPE_MEDITATION,
    EXERCISE_TYPE_GUIDED_RELAXATION, EXERCISE_TYPE_MUSIC_THERAPY
)


class GenericTableModel(QAbstractTableModel):
    """Generic table model for admin tables."""
    
    def __init__(self, data: List[Dict[str, Any]], headers: List[str]) -> None:
        """Initialize model."""
        super().__init__()
        self._data = data
        self.headers = headers
    
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
            if row < len(self._data) and col < len(self.headers):
                row_data = self._data[row]
                keys = list(row_data.keys())
                if col < len(keys):
                    value = row_data[keys[col]]
                    if isinstance(value, bool):
                        return "Yes" if value else "No"
                    if value is None:
                        return ""
                    return str(value)
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> Any:
        """Return header data."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section < len(self.headers):
                return self.headers[section]
        return None


class UserFormDialog(QDialog):
    """Dialog for adding/editing users."""
    
    def __init__(self, translation_manager: TranslationManager, user: Optional[dict] = None) -> None:
        """Initialize dialog."""
        super().__init__()
        self.t = translation_manager.t
        self.user = user
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize UI."""
        self.setWindowTitle(self.t("edit_user") if self.user else self.t("add_user"))
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        
        self.username_input = QLineEdit()
        if self.user:
            self.username_input.setText(self.user.get('username', ''))
            self.username_input.setEnabled(False)
        form.addRow(self.t("username") + ":", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form.addRow(self.t("password") + ":", self.password_input)
        
        self.email_input = QLineEdit()
        if self.user:
            self.email_input.setText(self.user.get('email', ''))
        form.addRow(self.t("email") + ":", self.email_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItem(self.t("user_role_user"), ROLE_USER)
        self.role_combo.addItem(self.t("user_role_admin"), ROLE_ADMIN)
        if self.user:
            role = self.user.get('role', ROLE_USER)
            index = self.role_combo.findData(role)
            if index >= 0:
                self.role_combo.setCurrentIndex(index)
        form.addRow(self.t("user_role") + ":", self.role_combo)
        
        self.is_active_check = QCheckBox()
        if self.user:
            self.is_active_check.setChecked(bool(self.user.get('is_active', 1)))
        else:
            self.is_active_check.setChecked(True)
        form.addRow(self.t("user_active") + ":", self.is_active_check)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        save_btn = QPushButton(self.t("save"))
        save_btn.clicked.connect(self.accept)
        buttons.addWidget(save_btn)
        
        cancel_btn = QPushButton(self.t("cancel"))
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def get_data(self) -> dict:
        """Get form data."""
        return {
            'username': self.username_input.text().strip(),
            'password': self.password_input.text(),
            'email': self.email_input.text().strip() or None,
            'role': self.role_combo.currentData(),
            'is_active': 1 if self.is_active_check.isChecked() else 0
        }


class ExerciseFormDialog(QDialog):
    """Dialog for adding/editing exercises."""
    
    def __init__(self, translation_manager: TranslationManager, exercise: Optional[dict] = None) -> None:
        """Initialize dialog."""
        super().__init__()
        self.t = translation_manager.t
        self.exercise = exercise
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize UI."""
        self.setWindowTitle(self.t("edit_exercise") if self.exercise else self.t("add_exercise"))
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        
        self.name_input = QLineEdit()
        if self.exercise:
            self.name_input.setText(self.exercise.get('name', ''))
        form.addRow(self.t("exercise_name") + ":", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        if self.exercise:
            self.description_input.setPlainText(self.exercise.get('description', ''))
        form.addRow(self.t("exercise_description") + ":", self.description_input)
        
        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(1)
        self.duration_input.setMaximum(300)
        if self.exercise:
            self.duration_input.setValue(self.exercise.get('duration', 10))
        else:
            self.duration_input.setValue(10)
        form.addRow(self.t("exercise_duration") + ":", self.duration_input)
        
        self.type_combo = QComboBox()
        self.type_combo.addItem(self.t("exercise_type_breathing"), EXERCISE_TYPE_BREATHING)
        self.type_combo.addItem(self.t("exercise_type_meditation"), EXERCISE_TYPE_MEDITATION)
        self.type_combo.addItem(self.t("exercise_type_guided_relaxation"), EXERCISE_TYPE_GUIDED_RELAXATION)
        self.type_combo.addItem(self.t("exercise_type_music_therapy"), EXERCISE_TYPE_MUSIC_THERAPY)
        if self.exercise:
            ex_type = self.exercise.get('type', EXERCISE_TYPE_BREATHING)
            index = self.type_combo.findData(ex_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        form.addRow(self.t("exercise_type") + ":", self.type_combo)
        
        self.is_active_check = QCheckBox()
        if self.exercise:
            self.is_active_check.setChecked(bool(self.exercise.get('is_active', 1)))
        else:
            self.is_active_check.setChecked(True)
        form.addRow(self.t("exercise_active") + ":", self.is_active_check)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        save_btn = QPushButton(self.t("save"))
        save_btn.clicked.connect(self.accept)
        buttons.addWidget(save_btn)
        
        cancel_btn = QPushButton(self.t("cancel"))
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def get_data(self) -> dict:
        """Get form data."""
        return {
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip() or None,
            'duration': self.duration_input.value(),
            'type': self.type_combo.currentData(),
            'is_active': 1 if self.is_active_check.isChecked() else 0
        }


class AnxietyQuestionFormDialog(QDialog):
    """Dialog for adding/editing anxiety questions."""
    
    def __init__(self, translation_manager: TranslationManager, question: Optional[dict] = None) -> None:
        """Initialize dialog."""
        super().__init__()
        self.t = translation_manager.t
        self.question = question
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize UI."""
        self.setWindowTitle(self.t("edit_anxiety_question") if self.question else self.t("add_anxiety_question"))
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        
        self.question_input = QTextEdit()
        self.question_input.setMaximumHeight(100)
        if self.question:
            self.question_input.setPlainText(self.question.get('question_text', ''))
        form.addRow(self.t("question_text") + ":", self.question_input)
        
        self.order_input = QSpinBox()
        self.order_input.setMinimum(1)
        self.order_input.setMaximum(100)
        if self.question:
            self.order_input.setValue(self.question.get('order_index', 1))
        else:
            self.order_input.setValue(1)
        form.addRow(self.t("question_order") + ":", self.order_input)
        
        self.is_active_check = QCheckBox()
        if self.question:
            self.is_active_check.setChecked(bool(self.question.get('is_active', 1)))
        else:
            self.is_active_check.setChecked(True)
        form.addRow(self.t("exercise_active") + ":", self.is_active_check)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        save_btn = QPushButton(self.t("save"))
        save_btn.clicked.connect(self.accept)
        buttons.addWidget(save_btn)
        
        cancel_btn = QPushButton(self.t("cancel"))
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def get_data(self) -> dict:
        """Get form data."""
        return {
            'question_text': self.question_input.toPlainText().strip(),
            'order_index': self.order_input.value(),
            'is_active': 1 if self.is_active_check.isChecked() else 0
        }


class AdminPanel(QMainWindow):
    """Admin panel main window."""
    
    def __init__(self, user: dict, translation_manager: TranslationManager,
                 user_service: UserService, exercise_service: ExerciseService,
                 anxiety_service: AnxietyTestService, admin_service: AdminService) -> None:
        """Initialize admin panel."""
        super().__init__()
        self.user = user
        self.t = translation_manager.t
        self.user_service = user_service
        self.exercise_service = exercise_service
        self.anxiety_service = anxiety_service
        self.admin_service = admin_service
        self.stress_repo = StressRepository()
        self.session_repo = SessionRepository()
        
        self._init_ui()
        self._load_users()
    
    def _init_ui(self) -> None:
        """Initialize UI."""
        self.setWindowTitle(self.t("admin_app_title"))
        self.setMinimumSize(1200, 800)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.t("admin_panel"))
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Content
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        self._create_screens()
        
        central.setLayout(layout)
        
        # Set RTL layout direction
        self.setLayoutDirection(Qt.RightToLeft)
    
    def _create_menu_bar(self) -> None:
        """Create standard Windows menu bar."""
        menubar = self.menuBar()
        
        # Users menu
        users_menu = menubar.addMenu(self.t("admin_users"))
        users_action = QAction(self.t("admin_users"), self)
        users_action.triggered.connect(lambda: self._navigate(0))
        users_menu.addAction(users_action)
        
        # Exercises menu
        exercises_menu = menubar.addMenu(self.t("admin_exercises"))
        exercises_action = QAction(self.t("admin_exercises"), self)
        exercises_action.triggered.connect(lambda: self._navigate(1))
        exercises_menu.addAction(exercises_action)
        
        # Anxiety Questions menu
        questions_menu = menubar.addMenu(self.t("admin_anxiety_questions"))
        questions_action = QAction(self.t("admin_anxiety_questions"), self)
        questions_action.triggered.connect(lambda: self._navigate(2))
        questions_menu.addAction(questions_action)
        
        # Data menu
        data_menu = menubar.addMenu(self.t("data"))
        stress_logs_action = QAction(self.t("admin_stress_logs"), self)
        stress_logs_action.triggered.connect(lambda: self._navigate(3))
        data_menu.addAction(stress_logs_action)
        
        sessions_action = QAction(self.t("admin_sessions"), self)
        sessions_action.triggered.connect(lambda: self._navigate(4))
        data_menu.addAction(sessions_action)
        
        anxiety_tests_action = QAction(self.t("admin_anxiety_tests"), self)
        anxiety_tests_action.triggered.connect(lambda: self._navigate(5))
        data_menu.addAction(anxiety_tests_action)
        
        # Database menu
        database_menu = menubar.addMenu(self.t("admin_database"))
        database_action = QAction(self.t("admin_database"), self)
        database_action.triggered.connect(lambda: self._navigate(6))
        database_menu.addAction(database_action)
        
        # User menu
        user_menu = menubar.addMenu(self.user['username'])
        logout_action = QAction(self.t("logout"), self)
        logout_action.triggered.connect(self.close)
        user_menu.addAction(logout_action)
        
        # Store actions for navigation tracking
        self.nav_actions = {
            "admin_users": users_action,
            "admin_exercises": exercises_action,
            "admin_anxiety_questions": questions_action,
            "admin_stress_logs": stress_logs_action,
            "admin_sessions": sessions_action,
            "admin_anxiety_tests": anxiety_tests_action,
            "admin_database": database_action
        }
    
    def _create_screens(self) -> None:
        """Create admin screens."""
        # Users
        self.users_screen = self._create_users_screen()
        self.stacked_widget.addWidget(self.users_screen)
        
        # Exercises
        self.exercises_screen = self._create_exercises_screen()
        self.stacked_widget.addWidget(self.exercises_screen)
        
        # Anxiety Questions
        self.questions_screen = self._create_questions_screen()
        self.stacked_widget.addWidget(self.questions_screen)
        
        # Stress Logs
        self.stress_logs_screen = self._create_table_screen("stress_logs")
        self.stacked_widget.addWidget(self.stress_logs_screen)
        
        # Sessions
        self.sessions_screen = self._create_table_screen("sessions")
        self.stacked_widget.addWidget(self.sessions_screen)
        
        # Anxiety Tests
        self.anxiety_tests_screen = self._create_table_screen("anxiety_tests")
        self.stacked_widget.addWidget(self.anxiety_tests_screen)
        
        # Database
        self.database_screen = self._create_database_screen()
        self.stacked_widget.addWidget(self.database_screen)
    
    def _create_users_screen(self) -> QWidget:
        """Create users management screen."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        header = QHBoxLayout()
        title = QLabel(self.t("user_management"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header.addWidget(title)
        header.addStretch()
        
        add_btn = QPushButton(self.t("add_user"))
        add_btn.clicked.connect(self._add_user)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        self.users_table = QTableView()
        self.users_table.setAlternatingRowColors(True)
        self.users_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.users_table)
        
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        edit_btn = QPushButton(self.t("edit_user"))
        edit_btn.clicked.connect(self._edit_user)
        buttons.addWidget(edit_btn)
        
        delete_btn = QPushButton(self.t("delete_user"))
        delete_btn.clicked.connect(self._delete_user)
        buttons.addWidget(delete_btn)
        
        reset_pwd_btn = QPushButton(self.t("reset_password"))
        reset_pwd_btn.clicked.connect(self._reset_password)
        buttons.addWidget(reset_pwd_btn)
        
        enable_btn = QPushButton(self.t("enable_user"))
        enable_btn.clicked.connect(self._enable_user)
        buttons.addWidget(enable_btn)
        
        disable_btn = QPushButton(self.t("disable_user"))
        disable_btn.clicked.connect(self._disable_user)
        buttons.addWidget(disable_btn)
        
        refresh_btn = QPushButton(self.t("refresh"))
        refresh_btn.clicked.connect(self._load_users)
        buttons.addWidget(refresh_btn)
        
        layout.addLayout(buttons)
        widget.setLayout(layout)
        return widget
    
    def _create_exercises_screen(self) -> QWidget:
        """Create exercises management screen."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        header = QHBoxLayout()
        title = QLabel(self.t("exercise_management"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header.addWidget(title)
        header.addStretch()
        
        add_btn = QPushButton(self.t("add_exercise"))
        add_btn.clicked.connect(self._add_exercise)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        self.exercises_table = QTableView()
        self.exercises_table.setAlternatingRowColors(True)
        self.exercises_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.exercises_table)
        
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        edit_btn = QPushButton(self.t("edit_exercise"))
        edit_btn.clicked.connect(self._edit_exercise)
        buttons.addWidget(edit_btn)
        
        delete_btn = QPushButton(self.t("delete_exercise"))
        delete_btn.clicked.connect(self._delete_exercise)
        buttons.addWidget(delete_btn)
        
        refresh_btn = QPushButton(self.t("refresh"))
        refresh_btn.clicked.connect(self._load_exercises)
        buttons.addWidget(refresh_btn)
        
        layout.addLayout(buttons)
        widget.setLayout(layout)
        return widget
    
    def _create_questions_screen(self) -> QWidget:
        """Create anxiety questions management screen."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        header = QHBoxLayout()
        title = QLabel(self.t("anxiety_question_management"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header.addWidget(title)
        header.addStretch()
        
        add_btn = QPushButton(self.t("add_anxiety_question"))
        add_btn.clicked.connect(self._add_question)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        self.questions_table = QTableView()
        self.questions_table.setAlternatingRowColors(True)
        self.questions_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.questions_table)
        
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        edit_btn = QPushButton(self.t("edit_anxiety_question"))
        edit_btn.clicked.connect(self._edit_question)
        buttons.addWidget(edit_btn)
        
        delete_btn = QPushButton(self.t("delete_anxiety_question"))
        delete_btn.clicked.connect(self._delete_question)
        buttons.addWidget(delete_btn)
        
        refresh_btn = QPushButton(self.t("refresh"))
        refresh_btn.clicked.connect(self._load_questions)
        buttons.addWidget(refresh_btn)
        
        layout.addLayout(buttons)
        widget.setLayout(layout)
        return widget
    
    def _create_table_screen(self, table_name: str) -> QWidget:
        """Create generic table viewer screen."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel(self.t(f"admin_{table_name}"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        table = QTableView()
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)
        
        refresh_btn = QPushButton(self.t("refresh"))
        refresh_btn.clicked.connect(lambda: self._load_table(table, table_name))
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        widget.table = table
        widget.table_name = table_name
        return widget
    
    def _create_database_screen(self) -> QWidget:
        """Create database management screen."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel(self.t("admin_database"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        backup_btn = QPushButton(self.t("database_backup"))
        backup_btn.clicked.connect(self._backup_database)
        layout.addWidget(backup_btn)
        
        restore_btn = QPushButton(self.t("database_restore"))
        restore_btn.clicked.connect(self._restore_database)
        layout.addWidget(restore_btn)
        
        export_btn = QPushButton(self.t("database_export"))
        export_btn.clicked.connect(self._export_database)
        layout.addWidget(export_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _navigate(self, index: int) -> None:
        """Navigate to screen."""
        self.stacked_widget.setCurrentIndex(index)
        
        # Update status bar
        nav_items = ["admin_users", "admin_exercises", "admin_anxiety_questions",
                     "admin_stress_logs", "admin_sessions", "admin_anxiety_tests", "admin_database"]
        if 0 <= index < len(nav_items):
            key = nav_items[index]
            self.status_bar.showMessage(self.t(key))
        
        # Refresh current screen
        if index == 0:
            self._load_users()
        elif index == 1:
            self._load_exercises()
        elif index == 2:
            self._load_questions()
        elif index == 3:
            self._load_table(self.stress_logs_screen.table, "stress_logs")
        elif index == 4:
            self._load_table(self.sessions_screen.table, "sessions")
        elif index == 5:
            self._load_table(self.anxiety_tests_screen.table, "anxiety_tests")
    
    def _load_users(self) -> None:
        """Load users table."""
        users = self.user_service.get_all_users(include_inactive=True)
        if users:
            headers = list(users[0].keys())
            model = GenericTableModel(users, headers)
            self.users_table.setModel(model)
    
    def _load_exercises(self) -> None:
        """Load exercises table."""
        exercises = self.exercise_service.get_all_exercises(include_inactive=True)
        if exercises:
            headers = list(exercises[0].keys())
            model = GenericTableModel(exercises, headers)
            self.exercises_table.setModel(model)
    
    def _load_questions(self) -> None:
        """Load questions table."""
        questions = self.anxiety_service.get_questions(include_inactive=True)
        if questions:
            headers = list(questions[0].keys())
            model = GenericTableModel(questions, headers)
            self.questions_table.setModel(model)
    
    def _load_table(self, table: QTableView, table_name: str) -> None:
        """Load generic table."""
        all_data = self.admin_service.get_all_tables_data()
        data = all_data.get(table_name, [])
        if data:
            headers = list(data[0].keys())
            model = GenericTableModel(data, headers)
            table.setModel(model)
    
    def _add_user(self) -> None:
        """Add new user."""
        from app.config.translation_manager import TranslationManager
        tm = TranslationManager()
        dialog = UserFormDialog(tm, None)
        if dialog.exec():
            data = dialog.get_data()
            if not data['username'] or not data['password']:
                QMessageBox.warning(self, self.t("error_title"), self.t("message_validation_error"))
                return
            user_id = self.user_service.register(data['username'], data['password'], data['email'])
            if user_id:
                self.user_service.update_user(user_id, role=data['role'], is_active=data['is_active'])
                QMessageBox.information(self, self.t("success_title"), self.t("message_save_success"))
                self._load_users()
            else:
                QMessageBox.warning(self, self.t("error_title"), self.t("message_username_exists"))
    
    def _edit_user(self) -> None:
        """Edit selected user."""
        index = self.users_table.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, self.t("warning_title"), "Please select a user")
            return
        
        model = self.users_table.model()
        user_id = model.data(model.index(index.row(), 0), Qt.DisplayRole)
        user = self.user_service.get_user(int(user_id))
        if not user:
            return
        
        from app.config.translation_manager import TranslationManager
        tm = TranslationManager()
        dialog = UserFormDialog(tm, user)
        if dialog.exec():
            data = dialog.get_data()
            if data['password']:
                self.user_service.reset_password(user_id, data['password'])
            self.user_service.update_user(user_id, email=data['email'], role=data['role'], is_active=data['is_active'])
            QMessageBox.information(self, self.t("success_title"), self.t("message_save_success"))
            self._load_users()
    
    def _delete_user(self) -> None:
        """Delete selected user."""
        index = self.users_table.currentIndex()
        if not index.isValid():
            return
        
        reply = QMessageBox.question(
            self, self.t("confirm_title"), self.t("message_delete_confirm"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            model = self.users_table.model()
            user_id = int(model.data(model.index(index.row(), 0), Qt.DisplayRole))
            if self.user_service.delete_user(user_id):
                QMessageBox.information(self, self.t("success_title"), self.t("message_delete_success"))
                self._load_users()
    
    def _reset_password(self) -> None:
        """Reset user password."""
        index = self.users_table.currentIndex()
        if not index.isValid():
            return
        
        from PySide6.QtWidgets import QInputDialog
        password, ok = QInputDialog.getText(self, self.t("reset_password"), self.t("password") + ":")
        if ok and password:
            model = self.users_table.model()
            user_id = int(model.data(model.index(index.row(), 0), Qt.DisplayRole))
            if self.user_service.reset_password(user_id, password):
                QMessageBox.information(self, self.t("success_title"), self.t("message_password_reset"))
    
    def _enable_user(self) -> None:
        """Enable user."""
        index = self.users_table.currentIndex()
        if not index.isValid():
            return
        model = self.users_table.model()
        user_id = int(model.data(model.index(index.row(), 0), Qt.DisplayRole))
        if self.user_service.enable_user(user_id):
            QMessageBox.information(self, self.t("success_title"), self.t("message_user_enabled"))
            self._load_users()
    
    def _disable_user(self) -> None:
        """Disable user."""
        index = self.users_table.currentIndex()
        if not index.isValid():
            return
        model = self.users_table.model()
        user_id = int(model.data(model.index(index.row(), 0), Qt.DisplayRole))
        if self.user_service.disable_user(user_id):
            QMessageBox.information(self, self.t("success_title"), self.t("message_user_disabled"))
            self._load_users()
    
    def _add_exercise(self) -> None:
        """Add new exercise."""
        from app.config.translation_manager import TranslationManager
        tm = TranslationManager()
        dialog = ExerciseFormDialog(tm, None)
        if dialog.exec():
            data = dialog.get_data()
            ex_id = self.exercise_service.create_exercise(
                data['name'], data['description'], data['duration'], data['type']
            )
            if ex_id:
                self.exercise_service.update_exercise(ex_id, is_active=data['is_active'])
                QMessageBox.information(self, self.t("success_title"), self.t("message_save_success"))
                self._load_exercises()
    
    def _edit_exercise(self) -> None:
        """Edit selected exercise."""
        index = self.exercises_table.currentIndex()
        if not index.isValid():
            return
        model = self.exercises_table.model()
        ex_id = int(model.data(model.index(index.row(), 0), Qt.DisplayRole))
        exercise = self.exercise_service.get_exercise(ex_id)
        if not exercise:
            return
        
        from app.config.translation_manager import TranslationManager
        tm = TranslationManager()
        dialog = ExerciseFormDialog(tm, exercise)
        if dialog.exec():
            data = dialog.get_data()
            self.exercise_service.update_exercise(
                ex_id, name=data['name'], description=data['description'],
                duration=data['duration'], type=data['type'], is_active=data['is_active']
            )
            QMessageBox.information(self, self.t("success_title"), self.t("message_save_success"))
            self._load_exercises()
    
    def _delete_exercise(self) -> None:
        """Delete selected exercise."""
        index = self.exercises_table.currentIndex()
        if not index.isValid():
            return
        reply = QMessageBox.question(
            self, self.t("confirm_title"), self.t("message_delete_confirm"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            model = self.exercises_table.model()
            ex_id = int(model.data(model.index(index.row(), 0), Qt.DisplayRole))
            if self.exercise_service.delete_exercise(ex_id):
                QMessageBox.information(self, self.t("success_title"), self.t("message_delete_success"))
                self._load_exercises()
    
    def _add_question(self) -> None:
        """Add new anxiety question."""
        from app.config.translation_manager import TranslationManager
        tm = TranslationManager()
        dialog = AnxietyQuestionFormDialog(tm, None)
        if dialog.exec():
            data = dialog.get_data()
            q_id = self.anxiety_service.create_question(data['question_text'], data['order_index'])
            if q_id:
                self.anxiety_service.update_question(q_id, is_active=data['is_active'])
                QMessageBox.information(self, self.t("success_title"), self.t("message_save_success"))
                self._load_questions()
    
    def _edit_question(self) -> None:
        """Edit selected question."""
        index = self.questions_table.currentIndex()
        if not index.isValid():
            return
        model = self.questions_table.model()
        q_id = int(model.data(model.index(index.row(), 0), Qt.DisplayRole))
        question = self.anxiety_service.get_questions(include_inactive=True)
        question = next((q for q in question if q['id'] == q_id), None)
        if not question:
            return
        
        from app.config.translation_manager import TranslationManager
        tm = TranslationManager()
        dialog = AnxietyQuestionFormDialog(tm, question)
        if dialog.exec():
            data = dialog.get_data()
            self.anxiety_service.update_question(
                q_id, question_text=data['question_text'],
                order_index=data['order_index'], is_active=data['is_active']
            )
            QMessageBox.information(self, self.t("success_title"), self.t("message_save_success"))
            self._load_questions()
    
    def _delete_question(self) -> None:
        """Delete selected question."""
        index = self.questions_table.currentIndex()
        if not index.isValid():
            return
        reply = QMessageBox.question(
            self, self.t("confirm_title"), self.t("message_delete_confirm"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            model = self.questions_table.model()
            q_id = int(model.data(model.index(index.row(), 0), Qt.DisplayRole))
            if self.anxiety_service.delete_question(q_id):
                QMessageBox.information(self, self.t("success_title"), self.t("message_delete_success"))
                self._load_questions()
    
    def _backup_database(self) -> None:
        """Backup database."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, self.t("database_backup"), "", "Database Files (*.db)"
        )
        if file_path:
            if self.admin_service.export_database(Path(file_path)):
                QMessageBox.information(self, self.t("success_title"), self.t("message_backup_success"))
    
    def _restore_database(self) -> None:
        """Restore database."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.t("database_restore"), "", "Database Files (*.db)"
        )
        if file_path:
            reply = QMessageBox.warning(
                self, self.t("warning_title"),
                "This will replace the current database. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if self.admin_service.restore_database(Path(file_path)):
                    QMessageBox.information(self, self.t("success_title"), self.t("message_restore_success"))
    
    def _export_database(self) -> None:
        """Export database."""
        self._backup_database()

