"""
Session service for business logic.
"""

from typing import List, Optional, Dict, Any
import logging

from app.data.repositories.session_repository import SessionRepository
from app.config.config import (
    SESSION_COMPLETED,
    SESSION_INCOMPLETE,
    SESSION_ABANDONED
)

logger = logging.getLogger(__name__)


class SessionService:
    """Service for session operations."""
    
    def __init__(self) -> None:
        """Initialize service."""
        self.repository = SessionRepository()
    
    VALID_STATUSES = {
        SESSION_COMPLETED,
        SESSION_INCOMPLETE,
        SESSION_ABANDONED
    }
    
    def create_session(self, user_id: int, exercise_id: int, duration: int,
                      completion_status: str, notes: Optional[str] = None) -> Optional[int]:
        """
        Create a new session.
        
        Args:
            user_id: User ID
            exercise_id: Exercise ID
            duration: Duration in minutes
            completion_status: Status (completed/incomplete/abandoned)
            notes: Optional notes
            
        Returns:
            Session ID if successful, None otherwise
        """
        if completion_status not in self.VALID_STATUSES:
            logger.error(f"Invalid completion status: {completion_status}")
            return None
        
        if duration <= 0:
            logger.error(f"Invalid duration: {duration}")
            return None
        
        try:
            session_id = self.repository.create(
                user_id, exercise_id, duration, completion_status, notes
            )
            return session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data dict, or None if not found
        """
        return self.repository.get_by_id(session_id)
    
    def get_user_sessions(self, user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get sessions for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records
            
        Returns:
            List of session data dicts
        """
        return self.repository.get_by_user(user_id, limit)
    
    def get_all_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all sessions.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of session data dicts
        """
        return self.repository.get_all(limit)
    
    def update_session(self, session_id: int, **kwargs) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session ID
            **kwargs: Fields to update
            
        Returns:
            True if updated successfully
        """
        if 'completion_status' in kwargs:
            if kwargs['completion_status'] not in self.VALID_STATUSES:
                logger.error(f"Invalid completion status: {kwargs['completion_status']}")
                return False
        
        if 'duration' in kwargs:
            if kwargs['duration'] <= 0:
                logger.error(f"Invalid duration: {kwargs['duration']}")
                return False
        
        return self.repository.update(session_id, **kwargs)
    
    def delete_session(self, session_id: int) -> bool:
        """
        Delete session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted successfully
        """
        return self.repository.delete(session_id)
    
    def get_user_session_count(self, user_id: int) -> int:
        """
        Get total session count for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Total number of sessions
        """
        return self.repository.get_count_by_user(user_id)

