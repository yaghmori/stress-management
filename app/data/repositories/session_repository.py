"""
Session repository for database operations.
"""

import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.data.database import get_database

logger = logging.getLogger(__name__)


class SessionRepository:
    """Repository for session data operations."""
    
    def __init__(self) -> None:
        """Initialize repository."""
        self.db = get_database()
    
    def create(self, user_id: int, exercise_id: int, duration: int,
               completion_status: str, notes: Optional[str] = None) -> int:
        """
        Create a new session.
        
        Args:
            user_id: User ID
            exercise_id: Exercise ID
            duration: Duration in minutes
            completion_status: Status (completed/incomplete/abandoned)
            notes: Optional notes
            
        Returns:
            ID of created session
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO sessions (user_id, exercise_id, duration, completion_status, notes) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, exercise_id, duration, completion_status, notes)
        )
        conn.commit()
        session_id = cursor.lastrowid
        logger.info(f"Session created: User {user_id}, Exercise {exercise_id}")
        return session_id
    
    def get_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data as dict, or None if not found
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_by_user(self, user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get sessions for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records
            
        Returns:
            List of session data dicts
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM sessions WHERE user_id = ? ORDER BY date DESC"
        if limit:
            query += " LIMIT ?"
            cursor.execute(query, (user_id, limit))
        else:
            cursor.execute(query, (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all sessions.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of session data dicts
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM sessions ORDER BY date DESC"
        if limit:
            query += " LIMIT ?"
            cursor.execute(query, (limit,))
        else:
            cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, session_id: int, **kwargs) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session ID
            **kwargs: Fields to update (duration, completion_status, notes)
            
        Returns:
            True if updated, False if not found
        """
        if not kwargs:
            return False
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        allowed_fields = {"duration", "completion_status", "notes"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [session_id]
        
        cursor.execute(f"UPDATE sessions SET {set_clause} WHERE id = ?", values)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Session updated: ID {session_id}")
            return True
        return False
    
    def delete(self, session_id: int) -> bool:
        """
        Delete session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted, False if not found
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Session deleted: ID {session_id}")
            return True
        return False
    
    def get_count_by_user(self, user_id: int) -> int:
        """
        Get total session count for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Total number of sessions
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE user_id = ?", (user_id,))
        return cursor.fetchone()[0]

