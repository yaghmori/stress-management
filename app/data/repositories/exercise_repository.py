"""
Exercise repository for database operations.
"""

import sqlite3
from typing import List, Optional, Dict, Any
import logging

from app.data.database import get_database

logger = logging.getLogger(__name__)


class ExerciseRepository:
    """Repository for exercise data operations."""
    
    def __init__(self) -> None:
        """Initialize repository."""
        self.db = get_database()
    
    def create(self, name: str, description: Optional[str], duration: int, 
               exercise_type: str) -> int:
        """
        Create a new exercise.
        
        Args:
            name: Exercise name
            description: Exercise description
            duration: Duration in minutes
            exercise_type: Type of exercise
            
        Returns:
            ID of created exercise
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO exercises (name, description, duration, type) 
               VALUES (?, ?, ?, ?)""",
            (name, description, duration, exercise_type)
        )
        conn.commit()
        exercise_id = cursor.lastrowid
        logger.info(f"Exercise created: {name} (ID: {exercise_id})")
        return exercise_id
    
    def get_by_id(self, exercise_id: int) -> Optional[Dict[str, Any]]:
        """
        Get exercise by ID.
        
        Args:
            exercise_id: Exercise ID
            
        Returns:
            Exercise data as dict, or None if not found
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all(self, include_inactive: bool = False, 
                exercise_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all exercises.
        
        Args:
            include_inactive: Include inactive exercises
            exercise_type: Filter by exercise type
            
        Returns:
            List of exercise data dicts
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM exercises WHERE 1=1"
        params = []
        
        if not include_inactive:
            query += " AND is_active = 1"
        
        if exercise_type:
            # Map 'guided_relaxation' to also match 'relaxation' in database
            # This handles legacy data where exercises were stored as 'relaxation'
            if exercise_type == "guided_relaxation":
                query += " AND (type = ? OR type = ?)"
                params.extend(["guided_relaxation", "relaxation"])
            else:
                query += " AND type = ?"
                params.append(exercise_type)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, exercise_id: int, **kwargs) -> bool:
        """
        Update exercise data.
        
        Args:
            exercise_id: Exercise ID
            **kwargs: Fields to update (name, description, duration, type, is_active)
            
        Returns:
            True if updated, False if not found
        """
        if not kwargs:
            return False
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        allowed_fields = {"name", "description", "duration", "type", "is_active"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [exercise_id]
        
        cursor.execute(f"UPDATE exercises SET {set_clause} WHERE id = ?", values)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Exercise updated: ID {exercise_id}")
            return True
        return False
    
    def delete(self, exercise_id: int) -> bool:
        """
        Delete exercise.
        
        Args:
            exercise_id: Exercise ID
            
        Returns:
            True if deleted, False if not found
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM exercises WHERE id = ?", (exercise_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Exercise deleted: ID {exercise_id}")
            return True
        return False

