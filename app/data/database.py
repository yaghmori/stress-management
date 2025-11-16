"""
Database connection and schema management.
"""

import sqlite3
from pathlib import Path
from typing import Optional
import logging

from app.config.config import DATABASE_PATH, LOGS_DIR

logger = logging.getLogger(__name__)


class Database:
    """Manages SQLite database connection and schema."""
    
    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize database connection.
        
        Args:
            db_path: Path to database file (default: from config)
        """
        self.db_path = db_path or DATABASE_PATH
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_schema()
    
    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def _create_schema(self) -> None:
        """Create database schema if it doesn't exist."""
        cursor = self.connection.cursor()
        
        try:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Stress logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stress_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    stress_level INTEGER NOT NULL CHECK(stress_level >= 1 AND stress_level <= 10),
                    date DATE NOT NULL,
                    notes TEXT,
                    sleep_hours REAL,
                    physical_activity INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Exercises table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    duration INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exercise_id INTEGER NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration INTEGER NOT NULL,
                    completion_status TEXT NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
                )
            """)
            
            # Check if old schema exists and migrate
            try:
                # Check if old anxiety_tests table exists with old columns
                cursor.execute("PRAGMA table_info(anxiety_tests)")
                old_columns = [row[1] for row in cursor.fetchall()]
                
                # If old schema exists (has user_id column instead of test_code), drop and recreate
                if old_columns and 'user_id' in old_columns and 'test_code' not in old_columns:
                    logger.info("Migrating anxiety tables to new schema...")
                    cursor.execute("DROP TABLE IF EXISTS anxiety_test_results")
                    cursor.execute("DROP TABLE IF EXISTS anxiety_test_questions")
                    cursor.execute("DROP TABLE IF EXISTS anxiety_tests")
                    cursor.execute("DROP TABLE IF EXISTS anxiety_questions")
            except sqlite3.OperationalError:
                # Table doesn't exist, continue
                pass
            
            # Anxiety tests table (test definitions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anxiety_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_code TEXT UNIQUE NOT NULL,
                    test_name TEXT NOT NULL,
                    description TEXT,
                    question_count INTEGER NOT NULL,
                    max_score INTEGER NOT NULL,
                    interpretation_rules TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Anxiety test questions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anxiety_test_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER NOT NULL,
                    question_number INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    options TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(test_id) REFERENCES anxiety_tests(id) ON DELETE CASCADE,
                    UNIQUE(test_id, question_number)
                )
            """)
            
            # Anxiety test results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anxiety_test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    test_id INTEGER NOT NULL,
                    test_code TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    max_score INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    interpretation TEXT,
                    answers TEXT NOT NULL,
                    date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY(test_id) REFERENCES anxiety_tests(id) ON DELETE CASCADE
                )
            """)
            
            # Create default admin user if not exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            if cursor.fetchone()[0] == 0:
                import hashlib
                # Default admin: admin/admin123
                password_hash = hashlib.pbkdf2_hmac(
                    'sha256',
                    b'admin123',
                    b'salt',
                    100000
                ).hex()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)",
                    ("admin", password_hash, "admin", "admin@example.com")
                )
            
            self.connection.commit()
            logger.info("Database schema created successfully")
        except sqlite3.Error as e:
            logger.error(f"Schema creation error: {e}")
            self.connection.rollback()
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self.connection is None:
            self._connect()
        return self.connection
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def backup(self, backup_path: Path) -> None:
        """
        Create database backup.
        
        Args:
            backup_path: Path to save backup file
        """
        try:
            backup_conn = sqlite3.connect(str(backup_path))
            self.connection.backup(backup_conn)
            backup_conn.close()
            logger.info(f"Database backed up to: {backup_path}")
        except sqlite3.Error as e:
            logger.error(f"Backup error: {e}")
            raise
    
    def restore(self, backup_path: Path) -> None:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
        """
        try:
            self.close()
            backup_conn = sqlite3.connect(str(backup_path))
            backup_conn.backup(self.connection)
            backup_conn.close()
            self._connect()
            logger.info(f"Database restored from: {backup_path}")
        except sqlite3.Error as e:
            logger.error(f"Restore error: {e}")
            raise


# Global database instance
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """Get global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

