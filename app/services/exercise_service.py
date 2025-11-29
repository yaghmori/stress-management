"""
Exercise service for business logic.
"""

from typing import List, Optional, Dict, Any
import logging

from app.data.repositories.exercise_repository import ExerciseRepository
from app.config.config import (
    EXERCISE_TYPE_BREATHING,
    EXERCISE_TYPE_MEDITATION,
    EXERCISE_TYPE_GUIDED_RELAXATION,
    EXERCISE_TYPE_MUSIC_THERAPY
)

logger = logging.getLogger(__name__)


class ExerciseService:
    """Service for exercise operations."""
    
    def __init__(self) -> None:
        """Initialize service."""
        self.repository = ExerciseRepository()
    
    VALID_TYPES = {
        EXERCISE_TYPE_BREATHING,
        EXERCISE_TYPE_MEDITATION,
        EXERCISE_TYPE_GUIDED_RELAXATION,
        EXERCISE_TYPE_MUSIC_THERAPY
    }
    
    def create_exercise(self, name: str, description: Optional[str], duration: int,
                       exercise_type: str) -> Optional[int]:
        """
        Create a new exercise.
        
        Args:
            name: Exercise name
            description: Exercise description
            duration: Duration in minutes
            exercise_type: Type of exercise
            
        Returns:
            Exercise ID if successful, None otherwise
        """
        if exercise_type not in self.VALID_TYPES:
            logger.error(f"Invalid exercise type: {exercise_type}")
            return None
        
        if duration <= 0:
            logger.error(f"Invalid duration: {duration}")
            return None
        
        try:
            exercise_id = self.repository.create(name, description, duration, exercise_type)
            return exercise_id
        except Exception as e:
            logger.error(f"Error creating exercise: {e}")
            return None
    
    def get_exercise(self, exercise_id: int) -> Optional[Dict[str, Any]]:
        """
        Get exercise by ID.
        
        Args:
            exercise_id: Exercise ID
            
        Returns:
            Exercise data dict, or None if not found
        """
        return self.repository.get_by_id(exercise_id)
    
    def get_all_exercises(self, include_inactive: bool = False,
                          exercise_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all exercises.
        
        Args:
            include_inactive: Include inactive exercises
            exercise_type: Filter by exercise type
            
        Returns:
            List of exercise data dicts
        """
        return self.repository.get_all(include_inactive, exercise_type)
    
    def get_distinct_exercise_types(self, include_inactive: bool = False) -> List[str]:
        """
        Get distinct exercise types from database.
        
        Args:
            include_inactive: Include inactive exercises
            
        Returns:
            List of distinct exercise type strings
        """
        return self.repository.get_distinct_types(include_inactive)
    
    def update_exercise(self, exercise_id: int, **kwargs) -> bool:
        """
        Update exercise data.
        
        Args:
            exercise_id: Exercise ID
            **kwargs: Fields to update
            
        Returns:
            True if updated successfully
        """
        if 'exercise_type' in kwargs:
            if kwargs['exercise_type'] not in self.VALID_TYPES:
                logger.error(f"Invalid exercise type: {kwargs['exercise_type']}")
                return False
        
        if 'duration' in kwargs:
            if kwargs['duration'] <= 0:
                logger.error(f"Invalid duration: {kwargs['duration']}")
                return False
        
        return self.repository.update(exercise_id, **kwargs)
    
    def delete_exercise(self, exercise_id: int) -> bool:
        """
        Delete exercise.
        
        Args:
            exercise_id: Exercise ID
            
        Returns:
            True if deleted successfully
        """
        return self.repository.delete(exercise_id)

