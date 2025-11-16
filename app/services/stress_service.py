"""
Stress log service for business logic.
"""

from typing import List, Optional, Dict, Any
from datetime import date
import logging

from app.data.repositories.stress_repository import StressRepository
from app.config.config import STRESS_LEVEL_MIN, STRESS_LEVEL_MAX

logger = logging.getLogger(__name__)


class StressService:
    """Service for stress log operations."""
    
    def __init__(self) -> None:
        """Initialize service."""
        self.repository = StressRepository()
    
    def create_log(self, user_id: int, stress_level: int, log_date: date,
                   notes: Optional[str] = None, sleep_hours: Optional[float] = None,
                   physical_activity: Optional[int] = None) -> Optional[int]:
        """
        Create a new stress log entry.
        
        Args:
            user_id: User ID
            stress_level: Stress level (1-10)
            log_date: Date of log entry
            notes: Optional notes
            sleep_hours: Optional sleep hours
            physical_activity: Optional physical activity minutes
            
        Returns:
            Log entry ID if successful, None otherwise
        """
        if not (STRESS_LEVEL_MIN <= stress_level <= STRESS_LEVEL_MAX):
            logger.error(f"Invalid stress level: {stress_level}")
            return None
        
        try:
            log_id = self.repository.create(
                user_id, stress_level, log_date, notes, sleep_hours, physical_activity
            )
            return log_id
        except Exception as e:
            logger.error(f"Error creating stress log: {e}")
            return None
    
    def get_log(self, log_id: int) -> Optional[Dict[str, Any]]:
        """
        Get stress log by ID.
        
        Args:
            log_id: Log entry ID
            
        Returns:
            Log data dict, or None if not found
        """
        return self.repository.get_by_id(log_id)
    
    def get_user_logs(self, user_id: int, limit: Optional[int] = None,
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Get stress logs for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            List of log data dicts
        """
        return self.repository.get_by_user(user_id, limit, start_date, end_date)
    
    def get_all_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all stress logs.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of log data dicts
        """
        return self.repository.get_all(limit)
    
    def update_log(self, log_id: int, **kwargs) -> bool:
        """
        Update stress log entry.
        
        Args:
            log_id: Log entry ID
            **kwargs: Fields to update
            
        Returns:
            True if updated successfully
        """
        if 'stress_level' in kwargs:
            level = kwargs['stress_level']
            if not (STRESS_LEVEL_MIN <= level <= STRESS_LEVEL_MAX):
                logger.error(f"Invalid stress level: {level}")
                return False
        
        return self.repository.update(log_id, **kwargs)
    
    def delete_log(self, log_id: int) -> bool:
        """
        Delete stress log entry.
        
        Args:
            log_id: Log entry ID
            
        Returns:
            True if deleted successfully
        """
        return self.repository.delete(log_id)
    
    def get_average_stress(self, user_id: int, days: int = 7) -> Optional[float]:
        """
        Get average stress level for user over specified days.
        
        Args:
            user_id: User ID
            days: Number of days to calculate average
            
        Returns:
            Average stress level, or None if no data
        """
        return self.repository.get_average_by_user(user_id, days)
    
    def get_today_stress(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get today's stress log for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Today's log entry, or None if not found
        """
        today = date.today()
        logs = self.repository.get_by_user(user_id, limit=1, start_date=today, end_date=today)
        return logs[0] if logs else None

