"""
Main entry point for user application.
"""

import sys
import locale
from pathlib import Path

from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtCore import Qt, QLocale

from app.config.config import setup_logging
from app.config.translation_manager import TranslationManager
from app.config.font_manager import FontManager
from app.data.database import get_database
from app.services.user_service import UserService
from app.services.stress_service import StressService
from app.services.exercise_service import ExerciseService
from app.services.session_service import SessionService
from app.services.anxiety_test_service import AnxietyTestService
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow


def main() -> None:
    """Main application entry point."""
    # Setup logging
    setup_logging()
    
    # Initialize database
    db = get_database()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set locale to Iran (Persian/Farsi)
    try:
        locale.setlocale(locale.LC_ALL, 'fa_IR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'fa_IR')
        except locale.Error:
            # Fallback if locale not available
            pass
    
    # Set Qt locale to Persian
    qt_locale = QLocale(QLocale.Persian, QLocale.Iran)
    QLocale.setDefault(qt_locale)
    
    # Set RTL layout direction
    app.setLayoutDirection(Qt.RightToLeft)
    
    # Set Windows native style (Windows 10/11 native look)
    # Try windowsvista first (modern look), fallback to Windows if not available
    available_styles = QStyleFactory.keys()
    if "windowsvista" in available_styles:
        app.setStyle(QStyleFactory.create("windowsvista"))
    elif "Windows" in available_styles:
        app.setStyle(QStyleFactory.create("Windows"))
    
    # Load and set custom fonts
    FontManager.load_fonts()
    if FontManager.is_font_loaded():
        font = FontManager.get_font()
        app.setFont(font)
    
    # Load translations
    translation_manager = TranslationManager()
    
    # Initialize services
    user_service = UserService()
    stress_service = StressService()
    exercise_service = ExerciseService()
    session_service = SessionService()
    anxiety_service = AnxietyTestService()
    
    # Show login window
    login_window = LoginWindow(translation_manager)
    
    def on_login(username: str, password: str):
        """Handle login."""
        return user_service.authenticate(username, password)
    
    def on_register(username: str, password: str, email: str = None):
        """Handle registration."""
        return user_service.register(username, password, email)
    
    login_window.set_login_callback(on_login)
    login_window.set_register_callback(on_register)
    
    if login_window.exec() == LoginWindow.Accepted:
        user = login_window.get_authenticated_user()
        if user:
            # Show main window
            main_window = MainWindow(
                user,
                translation_manager,
                user_service,
                stress_service,
                exercise_service,
                session_service,
                anxiety_service
            )
            main_window.show()
            
            sys.exit(app.exec())
    
    # Cleanup
    db.close()


if __name__ == "__main__":
    main()

