"""
User repository for database operations.
"""

import sqlite3
from typing import List, Optional, Dict, Any
import logging

from app.data.database import get_database

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user data operations."""
    
    def __init__(self) -> None:
        """Initialize repository."""
        self.db = get_database()
    
    def create(self, username: str, password_hash: str, email: Optional[str] = None, role: str = "user") -> int:
        """
        Create a new user.
        
        Args:
            username: Username (must be unique)
            password_hash: Hashed password
            email: Email address (optional)
            role: User role (default: "user")
            
        Returns:
            ID of created user
            
        Raises:
            sqlite3.IntegrityError: If username already exists
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                (username, password_hash, email, role)
            )
            conn.commit()
            user_id = cursor.lastrowid
            logger.info(f"User created: {username} (ID: {user_id})")
            return user_id
        except sqlite3.IntegrityError:
            conn.rollback()
            raise
    
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data as dict, or None if not found
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User data as dict, or None if not found
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get all users.
        
        Args:
            include_inactive: Include inactive users
            
        Returns:
            List of user data dicts
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        if include_inactive:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, user_id: int, **kwargs) -> bool:
        """
        Update user data.
        
        Args:
            user_id: User ID
            **kwargs: Fields to update (username, email, role, is_active, password_hash)
            
        Returns:
            True if updated, False if user not found
        """
        if not kwargs:
            return False
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        allowed_fields = {"username", "email", "role", "is_active", "password_hash"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        
        cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"User updated: ID {user_id}")
            return True
        return False
    
    def delete(self, user_id: int) -> bool:
        """
        Delete user (cascade deletes related records).
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"User deleted: ID {user_id}")
            return True
        return False
    
    def exists(self, username: str) -> bool:
        """
        Check if username exists.
        
        Args:
            username: Username to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.get_by_username(username) is not None

