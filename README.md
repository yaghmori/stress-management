# Stress Management & Relaxation Training System

A complete production-grade Python desktop application using PySide6 (Qt for Python) with full RTL Persian UI support.

## Features

- **Full RTL Persian UI**: Complete right-to-left layout with Persian text loaded from JSON translations
- **Translation System**: All UI text stored in JSON files - no Persian characters in Python source code
- **User & Admin Roles**: Separate interfaces for regular users and administrators
- **Stress Logging**: Daily stress level tracking with notes, sleep hours, and physical activity
- **Exercise Management**: Breathing exercises, meditation, guided relaxation, and music therapy
- **Session Tracking**: Track completed exercise sessions
- **Anxiety Testing**: GAD-7 style anxiety assessment (7 questions, 0-21 score)
- **Reports & Export**: Export stress logs to CSV format
- **Admin Panel**: Complete CRUD operations for users, exercises, and anxiety questions
- **Database Management**: Backup, restore, and export database functionality

## Architecture

The application follows a clean layered architecture:

```
/app
  /ui              # UI Layer (PySide6 widgets)
  /services        # Business Logic Layer
  /data            # Data Access Layer (SQLite + Repositories)
  /config          # Configuration (Translation Manager, Config)
/translations      # Translation JSON files
main.py            # User application entry point
admin_main.py      # Admin application entry point
```

## Translation System

All UI text is stored in `/translations/fa.json`. The application uses a `TranslationManager` class to load and retrieve translated strings.

**Key Features:**

- All Persian text in JSON files only
- Zero Persian characters in Python source code
- Easy language switching support
- Type-safe translation key lookup

**Usage in code:**

```python
from app.config.translation_manager import TranslationManager

tm = TranslationManager()
label.setText(tm.t("login"))  # Returns Persian text from JSON
```

## Installation

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run user application:**

   ```bash
   python main.py
   ```

3. **Run admin panel:**
   ```bash
   python admin_main.py
   ```

## Default Credentials

**Admin Account:**

- Username: `admin`
- Password: `admin123`

_Note: Change the default admin password after first login for security._

## Database

The application uses SQLite database stored in `/data/stress_management.db`. The database schema is automatically created on first run.

**Tables:**

- `users`: User accounts and authentication
- `stress_logs`: Daily stress level entries
- `exercises`: Available exercises
- `sessions`: Exercise session history
- `anxiety_tests`: GAD-7 test results
- `anxiety_questions`: Anxiety test questions (manageable by admin)

## RTL Support

The application is fully RTL (Right-To-Left) compatible:

- All widgets use `Qt.RightToLeft` layout direction
- Form labels appear on the right side
- Table headers and content are RTL
- Persian font support (Vazir/IRANSans with fallback)

## Windows Native Styling

The application uses Windows native "windowsvista" style for a native look and feel on Windows.

## Code Quality

- **English-only code**: All Python source code is in English
- **Type hints**: Full type annotations throughout
- **Docstrings**: Comprehensive documentation
- **PEP8 compliant**: Follows Python style guidelines
- **Logging**: Rotating file logs for debugging
- **Error handling**: User-friendly error messages (translated)

## Admin Panel Features

The admin panel provides:

- **User Management**: Create, edit, delete users; reset passwords; enable/disable accounts
- **Exercise Management**: CRUD operations for exercises
- **Anxiety Questions Management**: Manage GAD-7 questions
- **Table Viewers**: Browse all database tables
- **Database Operations**: Backup, restore, and export database

## Development

### Adding New Translations

1. Add new key-value pairs to `/translations/fa.json`
2. Use the key in code: `tm.t("your_new_key")`

### Adding New Screens

1. Create screen widget in `/app/ui/screens/`
2. Add to `MainWindow._create_screens()`
3. Add navigation button in sidebar

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions, please refer to the code documentation and inline comments.
