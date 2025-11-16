"""
Stress log repository for database operations.
"""

import sqlite3
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import logging

from app.data.database import get_database

logger = logging.getLogger(__name__)


class StressRepository:
    """Repository for stress log data operations."""
    
    def __init__(self) -> None:
        """Initialize repository."""
        self.db = get_database()
    
    def create(self, user_id: int, stress_level: int, log_date: date, 
               notes: Optional[str] = None, sleep_hours: Optional[float] = None,
               physical_activity: Optional[int] = None) -> int:
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
            ID of created log entry
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO stress_logs 
               (user_id, stress_level, date, notes, sleep_hours, physical_activity) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, stress_level, log_date, notes, sleep_hours, physical_activity)
        )
        conn.commit()
        log_id = cursor.lastrowid
        logger.info(f"Stress log created: User {user_id}, Level {stress_level}")
        return log_id
    
    def get_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        """
        Get stress log by ID.
        
        Args:
            log_id: Log entry ID
            
        Returns:
            Log data as dict, or None if not found
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stress_logs WHERE id = ?", (log_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_by_user(self, user_id: int, limit: Optional[int] = None, 
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
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM stress_logs WHERE user_id = ?"
        params = [user_id]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC, created_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all stress logs.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of log data dicts
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM stress_logs ORDER BY date DESC, created_at DESC"
        if limit:
            query += " LIMIT ?"
            cursor.execute(query, (limit,))
        else:
            cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, log_id: int, **kwargs) -> bool:
        """
        Update stress log entry.
        
        Args:
            log_id: Log entry ID
            **kwargs: Fields to update
            
        Returns:
            True if updated, False if not found
        """
        if not kwargs:
            return False
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        allowed_fields = {"stress_level", "date", "notes", "sleep_hours", "physical_activity"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [log_id]
        
        cursor.execute(f"UPDATE stress_logs SET {set_clause} WHERE id = ?", values)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Stress log updated: ID {log_id}")
            return True
        return False
    
    def delete(self, log_id: int) -> bool:
        """
        Delete stress log entry.
        
        Args:
            log_id: Log entry ID
            
        Returns:
            True if deleted, False if not found
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stress_logs WHERE id = ?", (log_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Stress log deleted: ID {log_id}")
            return True
        return False
    
    def get_average_by_user(self, user_id: int, days: int = 7) -> Optional[float]:
        """
        Get average stress level for user over specified days.
        
        Args:
            user_id: User ID
            days: Number of days to calculate average
            
        Returns:
            Average stress level, or None if no data
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT AVG(stress_level) FROM stress_logs 
               WHERE user_id = ? AND date >= date('now', '-' || ? || ' days')""",
            (user_id, days)
        )
        result = cursor.fetchone()[0]
        return float(result) if result is not None else None

