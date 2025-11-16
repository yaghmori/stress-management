"""
User service for authentication and user management.
"""

import hashlib
from typing import Optional, Dict, Any
import logging

from app.data.repositories.user_repository import UserRepository
from app.config.config import ROLE_USER, ROLE_ADMIN

logger = logging.getLogger(__name__)


class UserService:
    """Service for user operations and authentication."""
    
    def __init__(self) -> None:
        """Initialize service."""
        self.repository = UserRepository()
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using PBKDF2.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password (hex string)
        """
        salt = b'salt'  # In production, use unique salt per user
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        ).hex()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            password_hash: Stored password hash
            
        Returns:
            True if password matches
        """
        computed_hash = self.hash_password(password)
        return computed_hash == password_hash
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User data dict if authenticated, None otherwise
        """
        user = self.repository.get_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: User not found - {username}")
            return None
        
        if not user.get('is_active', 0):
            logger.warning(f"Authentication failed: User inactive - {username}")
            return None
        
        if not self.verify_password(password, user['password_hash']):
            logger.warning(f"Authentication failed: Invalid password - {username}")
            return None
        
        logger.info(f"User authenticated: {username}")
        return user
    
    def register(self, username: str, password: str, email: Optional[str] = None) -> Optional[int]:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Plain text password
            email: Email address (optional)
            
        Returns:
            User ID if successful, None if username exists
        """
        if self.repository.exists(username):
            logger.warning(f"Registration failed: Username exists - {username}")
            return None
        
        password_hash = self.hash_password(password)
        try:
            user_id = self.repository.create(username, password_hash, email, ROLE_USER)
            logger.info(f"User registered: {username} (ID: {user_id})")
            return user_id
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return None
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data dict, or None if not found
        """
        return self.repository.get_by_id(user_id)
    
    def get_all_users(self, include_inactive: bool = False) -> list[Dict[str, Any]]:
        """
        Get all users.
        
        Args:
            include_inactive: Include inactive users
            
        Returns:
            List of user data dicts
        """
        return self.repository.get_all(include_inactive)
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """
        Update user data.
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            True if updated successfully
        """
        if 'password' in kwargs:
            kwargs['password_hash'] = self.hash_password(kwargs.pop('password'))
        
        return self.repository.update(user_id, **kwargs)
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """
        Reset user password.
        
        Args:
            user_id: User ID
            new_password: New plain text password
            
        Returns:
            True if reset successfully
        """
        password_hash = self.hash_password(new_password)
        return self.repository.update(user_id, password_hash=password_hash)
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted successfully
        """
        return self.repository.delete(user_id)
    
    def enable_user(self, user_id: int) -> bool:
        """
        Enable user account.
        
        Args:
            user_id: User ID
            
        Returns:
            True if enabled successfully
        """
        return self.repository.update(user_id, is_active=1)
    
    def disable_user(self, user_id: int) -> bool:
        """
        Disable user account.
        
        Args:
            user_id: User ID
            
        Returns:
            True if disabled successfully
        """
        return self.repository.update(user_id, is_active=0)
    
    def is_admin(self, user: Dict[str, Any]) -> bool:
        """
        Check if user is admin.
        
        Args:
            user: User data dict
            
        Returns:
            True if user is admin
        """
        return user.get('role') == ROLE_ADMIN

