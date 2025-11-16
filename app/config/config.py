"""
Application configuration and constants.
"""

from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler


# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
APP_DIR = BASE_DIR / "app"
TRANSLATIONS_DIR = BASE_DIR / "translations"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Database
DATABASE_PATH = DATA_DIR / "stress_management.db"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Logging configuration
LOG_FILE = LOGS_DIR / "app.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5


def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                LOG_FILE,
                maxBytes=LOG_MAX_BYTES,
                backupCount=LOG_BACKUP_COUNT,
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ]
    )


# Application constants
DEFAULT_LANGUAGE = "fa"
STRESS_LEVEL_MIN = 1
STRESS_LEVEL_MAX = 10
ANXIETY_SCORE_MIN = 0
ANXIETY_SCORE_MAX = 21
ANXIETY_QUESTION_MIN = 0
ANXIETY_QUESTION_MAX = 3

# User roles
ROLE_USER = "user"
ROLE_ADMIN = "admin"

# Exercise types
EXERCISE_TYPE_BREATHING = "breathing"
EXERCISE_TYPE_MEDITATION = "meditation"
EXERCISE_TYPE_GUIDED_RELAXATION = "guided_relaxation"
EXERCISE_TYPE_MUSIC_THERAPY = "music_therapy"

# Session status
SESSION_COMPLETED = "completed"
SESSION_INCOMPLETE = "incomplete"
SESSION_ABANDONED = "abandoned"

