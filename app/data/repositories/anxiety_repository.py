"""
Anxiety test repository for database operations.
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.data.database import get_database

logger = logging.getLogger(__name__)


class AnxietyRepository:
    """Repository for anxiety test data operations."""
    
    def __init__(self) -> None:
        """Initialize repository."""
        self.db = get_database()
    
    # Test Definitions
    
    def get_all_tests(self) -> List[Dict[str, Any]]:
        """Get all test definitions."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM anxiety_tests ORDER BY test_name ASC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_test_by_code(self, test_code: str) -> Optional[Dict[str, Any]]:
        """Get test definition by code."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM anxiety_tests WHERE test_code = ?", (test_code,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_test_by_id(self, test_id: int) -> Optional[Dict[str, Any]]:
        """Get test definition by ID."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM anxiety_tests WHERE id = ?", (test_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # Test Questions
    
    def get_test_questions(self, test_id: int) -> List[Dict[str, Any]]:
        """Get all questions for a test."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM anxiety_test_questions WHERE test_id = ? ORDER BY question_number ASC",
            (test_id,)
        )
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # Parse options JSON
            if 'options' in result and result['options']:
                try:
                    result['options'] = json.loads(result['options'])
                except (json.JSONDecodeError, TypeError):
                    result['options'] = []
            results.append(result)
        return results
    
    # Test Results
    
    def create_test_result(self, user_id: int, username: str, test_id: int,
                          test_code: str, test_name: str, score: int, max_score: int,
                          percentage: float, interpretation: Optional[str],
                          answers: List[int]) -> int:
        """Create a new test result."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        answers_json = json.dumps(answers)
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute(
            """INSERT INTO anxiety_test_results 
               (user_id, username, test_id, test_code, test_name, score, max_score, 
                percentage, interpretation, answers, date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, username, test_id, test_code, test_name, score, max_score,
             percentage, interpretation, answers_json, date_str)
        )
        conn.commit()
        result_id = cursor.lastrowid
        logger.info(f"Test result created: User {user_id}, Test {test_code}, Score {score}")
        return result_id
    
    def get_result_by_id(self, result_id: int) -> Optional[Dict[str, Any]]:
        """Get test result by ID."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM anxiety_test_results WHERE id = ?", (result_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            # Parse JSON answers
            if 'answers' in result and result['answers']:
                try:
                    result['answers'] = json.loads(result['answers'])
                except (json.JSONDecodeError, TypeError):
                    result['answers'] = []
            return result
        return None
    
    def get_results_by_user(self, user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get test results for a user."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM anxiety_test_results WHERE user_id = ? ORDER BY created_at DESC"
        if limit:
            query += " LIMIT ?"
            cursor.execute(query, (user_id, limit))
        else:
            cursor.execute(query, (user_id,))
        
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # Parse JSON answers
            if 'answers' in result and result['answers']:
                try:
                    result['answers'] = json.loads(result['answers'])
                except (json.JSONDecodeError, TypeError):
                    result['answers'] = []
            results.append(result)
        return results
    
    def get_all_results(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all test results."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM anxiety_test_results ORDER BY created_at DESC"
        if limit:
            query += " LIMIT ?"
            cursor.execute(query, (limit,))
        else:
            cursor.execute(query)
        
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # Parse JSON answers
            if 'answers' in result and result['answers']:
                try:
                    result['answers'] = json.loads(result['answers'])
                except (json.JSONDecodeError, TypeError):
                    result['answers'] = []
            results.append(result)
        return results
    
    def delete_result(self, result_id: int) -> bool:
        """Delete test result."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM anxiety_test_results WHERE id = ?", (result_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Test result deleted: ID {result_id}")
            return True
        return False
