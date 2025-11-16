"""
Admin service for administrative operations.
"""

from typing import List, Dict, Any
from pathlib import Path
import logging

from app.data.database import get_database
from app.services.user_service import UserService
from app.services.exercise_service import ExerciseService
from app.services.anxiety_test_service import AnxietyTestService

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin operations."""
    
    def __init__(self) -> None:
        """Initialize service."""
        self.user_service = UserService()
        self.exercise_service = ExerciseService()
        self.anxiety_service = AnxietyTestService()
        self.db = get_database()
    
    def get_all_tables_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get data from all tables for admin viewing.
        
        Returns:
            Dictionary mapping table names to their data
        """
        from app.data.repositories.stress_repository import StressRepository
        from app.data.repositories.session_repository import SessionRepository
        from app.data.repositories.anxiety_repository import AnxietyRepository
        
        stress_repo = StressRepository()
        session_repo = SessionRepository()
        anxiety_repo = AnxietyRepository()
        
        return {
            'users': self.user_service.get_all_users(include_inactive=True),
            'stress_logs': stress_repo.get_all(),
            'exercises': self.exercise_service.get_all_exercises(include_inactive=True),
            'sessions': session_repo.get_all(),
            'anxiety_tests': self.anxiety_service.get_all_tests(),
            'anxiety_questions': self.anxiety_service.get_questions(include_inactive=True)
        }
    
    def export_database(self, export_path: Path) -> bool:
        """
        Export database to file.
        
        Args:
            export_path: Path to save exported database
            
        Returns:
            True if export successful
        """
        try:
            self.db.backup(export_path)
            logger.info(f"Database exported to: {export_path}")
            return True
        except Exception as e:
            logger.error(f"Database export error: {e}")
            return False
    
    def restore_database(self, backup_path: Path) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if restore successful
        """
        try:
            self.db.restore(backup_path)
            logger.info(f"Database restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database restore error: {e}")
            return False

