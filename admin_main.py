"""
Main entry point for admin application.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtCore import Qt

from app.config.config import setup_logging
from app.config.translation_manager import TranslationManager
from app.config.font_manager import FontManager
from app.data.database import get_database
from app.services.user_service import UserService
from app.services.exercise_service import ExerciseService
from app.services.anxiety_test_service import AnxietyTestService
from app.services.admin_service import AdminService
from app.ui.login_window import LoginWindow
from app.ui.admin_panel import AdminPanel


def main() -> None:
    """Main admin application entry point."""
    # Setup logging
    setup_logging()
    
    # Initialize database
    db = get_database()
    
    # Create application
    app = QApplication(sys.argv)
    
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
    exercise_service = ExerciseService()
    anxiety_service = AnxietyTestService()
    admin_service = AdminService()
    
    # Show admin login window
    login_window = LoginWindow(translation_manager, is_admin=True)
    
    def on_login(username: str, password: str):
        """Handle admin login."""
        user = user_service.authenticate(username, password)
        if user and user.get('role') == 'admin':
            return user
        return None
    
    login_window.set_login_callback(on_login)
    
    if login_window.exec() == LoginWindow.Accepted:
        user = login_window.get_authenticated_user()
        if user:
            # Show admin panel
            admin_panel = AdminPanel(
                user,
                translation_manager,
                user_service,
                exercise_service,
                anxiety_service,
                admin_service
            )
            admin_panel.show()
            
            sys.exit(app.exec())
    
    # Cleanup
    db.close()


if __name__ == "__main__":
    main()

