"""
Login and registration window.
"""

from typing import Optional, Callable
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QMessageBox, QTabWidget, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.config.translation_manager import TranslationManager


class LoginWindow(QDialog):
    """Login and registration dialog."""
    
    def __init__(self, translation_manager: TranslationManager,
                 parent=None, is_admin: bool = False) -> None:
        """
        Initialize login window.
        
        Args:
            translation_manager: Translation manager instance
            parent: Parent widget
            is_admin: If True, show admin login only
        """
        super().__init__(parent)
        self.t = translation_manager.t
        self.is_admin = is_admin
        self.authenticated_user: Optional[dict] = None
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle(self.t("admin_login") if self.is_admin else self.t("login"))
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # App Name
        app_name = QLabel(self.t("app_title"))
        app_name_font = QFont()
        app_name_font.setPointSize(20)
        app_name_font.setBold(True)
        app_name.setFont(app_name_font)
        app_name.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_name)
        
        # App Description
        app_description = QLabel(self.t("app_description"))
        description_font = QFont()
        description_font.setPointSize(10)
        app_description.setFont(description_font)
        app_description.setAlignment(Qt.AlignCenter)
        app_description.setWordWrap(True)
        app_description.setStyleSheet("color: #666666; margin-bottom: 10px;")
        layout.addWidget(app_description)
        
        # Section Title
        title = QLabel(self.t("admin_login") if self.is_admin else self.t("login"))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(5)
        
        if self.is_admin:
            # Admin login - no tabs needed
            form_layout = QFormLayout()
            form_layout.setLabelAlignment(Qt.AlignRight)
            
            self.username_input = QLineEdit()
            self.username_input.setPlaceholderText(self.t("username"))
            form_layout.addRow(self.t("username") + ":", self.username_input)
            
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setPlaceholderText(self.t("password"))
            form_layout.addRow(self.t("password") + ":", self.password_input)
            
            layout.addLayout(form_layout)
            
            # Login button
            self.login_button = QPushButton(self.t("login_button"))
            self.login_button.clicked.connect(self._on_login)
            self.login_button.setDefault(True)
            layout.addWidget(self.login_button)
        else:
            # User login/register - use tabs
            tab_widget = QTabWidget()
            
            # Login tab
            login_tab = QWidget()
            login_layout = QVBoxLayout()
            login_layout.setSpacing(15)
            login_layout.setContentsMargins(20, 20, 20, 20)
            
            login_form = QFormLayout()
            login_form.setLabelAlignment(Qt.AlignRight)
            
            self.username_input = QLineEdit()
            self.username_input.setPlaceholderText(self.t("username"))
            login_form.addRow(self.t("username") + ":", self.username_input)
            
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setPlaceholderText(self.t("password"))
            login_form.addRow(self.t("password") + ":", self.password_input)
            
            login_layout.addLayout(login_form)
            login_layout.addStretch()
            
            self.login_button = QPushButton(self.t("login_button"))
            self.login_button.clicked.connect(self._on_login)
            self.login_button.setDefault(True)
            login_layout.addWidget(self.login_button)
            
            login_tab.setLayout(login_layout)
            tab_widget.addTab(login_tab, self.t("login"))
            
            # Register tab
            register_tab = QWidget()
            register_layout = QVBoxLayout()
            register_layout.setSpacing(15)
            register_layout.setContentsMargins(20, 20, 20, 20)
            
            register_form = QFormLayout()
            register_form.setLabelAlignment(Qt.AlignRight)
            
            self.register_username_input = QLineEdit()
            self.register_username_input.setPlaceholderText(self.t("username"))
            register_form.addRow(self.t("username") + ":", self.register_username_input)
            
            self.email_input = QLineEdit()
            self.email_input.setPlaceholderText(self.t("email"))
            register_form.addRow(self.t("email") + ":", self.email_input)
            
            self.register_password_input = QLineEdit()
            self.register_password_input.setEchoMode(QLineEdit.Password)
            self.register_password_input.setPlaceholderText(self.t("password"))
            register_form.addRow(self.t("password") + ":", self.register_password_input)
            
            self.confirm_password_input = QLineEdit()
            self.confirm_password_input.setEchoMode(QLineEdit.Password)
            self.confirm_password_input.setPlaceholderText(self.t("confirm_password"))
            register_form.addRow(self.t("confirm_password") + ":", self.confirm_password_input)
            
            register_layout.addLayout(register_form)
            register_layout.addStretch()
            
            self.register_button = QPushButton(self.t("register_button"))
            self.register_button.clicked.connect(self._on_register)
            register_layout.addWidget(self.register_button)
            
            register_tab.setLayout(register_layout)
            tab_widget.addTab(register_tab, self.t("register_button"))
            
            layout.addWidget(tab_widget)
        
        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def _on_login(self) -> None:
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(
                self,
                self.t("warning_title"),
                self.t("message_validation_error")
            )
            return
        
        # Emit signal or call callback
        if hasattr(self, 'login_callback'):
            user = self.login_callback(username, password)
            if user:
                if self.is_admin and user.get('role') != 'admin':
                    QMessageBox.warning(
                        self,
                        self.t("error_title"),
                        "Access denied. Admin role required."
                    )
                    return
                self.authenticated_user = user
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    self.t("error_title"),
                    self.t("message_login_failed")
                )
    
    def _on_register(self) -> None:
        """Handle register button click."""
        username = self.register_username_input.text().strip()
        password = self.register_password_input.text()
        confirm_password = self.confirm_password_input.text()
        email = self.email_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(
                self,
                self.t("warning_title"),
                self.t("message_validation_error")
            )
            return
        
        if password != confirm_password:
            QMessageBox.warning(
                self,
                self.t("error_title"),
                self.t("message_password_mismatch")
            )
            return
        
        # Emit signal or call callback
        if hasattr(self, 'register_callback'):
            user_id = self.register_callback(username, password, email)
            if user_id:
                QMessageBox.information(
                    self,
                    self.t("success_title"),
                    self.t("message_register_success")
                )
                # Clear form
                self.register_username_input.clear()
                self.register_password_input.clear()
                self.confirm_password_input.clear()
                self.email_input.clear()
            else:
                QMessageBox.warning(
                    self,
                    self.t("error_title"),
                    self.t("message_username_exists")
                )
    
    def set_login_callback(self, callback: Callable[[str, str], Optional[dict]]) -> None:
        """Set login callback function."""
        self.login_callback = callback
    
    def set_register_callback(self, callback: Callable[[str, str, Optional[str]], Optional[int]]) -> None:
        """Set register callback function."""
        self.register_callback = callback
    
    def get_authenticated_user(self) -> Optional[dict]:
        """Get authenticated user data."""
        return self.authenticated_user

