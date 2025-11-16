"""
Anxiety test service for business logic.
"""

from typing import List, Optional, Dict, Any
import logging
import json

from app.data.repositories.anxiety_repository import AnxietyRepository

logger = logging.getLogger(__name__)


class AnxietyTestService:
    """Service for anxiety test operations."""
    
    def __init__(self) -> None:
        """Initialize service."""
        self.repository = AnxietyRepository()
    
    # Test Definitions
    
    def get_available_tests(self) -> List[Dict[str, Any]]:
        """Get all available test definitions."""
        return self.repository.get_all_tests()
    
    def get_test_by_code(self, test_code: str) -> Optional[Dict[str, Any]]:
        """Get test definition by code."""
        return self.repository.get_test_by_code(test_code)
    
    # Test Questions
    
    def get_test_questions(self, test_id: int) -> List[Dict[str, Any]]:
        """Get questions for a test."""
        return self.repository.get_test_questions(test_id)
    
    # Score Calculation
    
    def calculate_score(self, test: Dict[str, Any], answers: List[int]) -> int:
        """
        Calculate total score from answers based on test interpretation rules.
        
        Args:
            test: Test definition
            answers: List of answer indices (0-based)
            
        Returns:
            Total score
        """
        questions = self.get_test_questions(test['id'])
        if len(answers) != len(questions):
            logger.error(f"Answer count mismatch: {len(answers)} answers for {len(questions)} questions")
            return 0
        
        # Parse interpretation rules
        rules = test.get('interpretation_rules', '')
        if not rules:
            # Default: sum of answer indices
            return sum(answers)
        
        try:
            rules_data = json.loads(rules)
            scoring_method = rules_data.get('method', 'sum')
            
            if scoring_method == 'sum':
                # Simple sum
                return sum(answers)
            elif scoring_method == 'reverse':
                # Some questions are reversed
                reverse_questions = rules_data.get('reverse_questions', [])
                score = 0
                max_option = rules_data.get('max_option_value', 3)
                for i, answer in enumerate(answers):
                    question_num = i + 1
                    if question_num in reverse_questions:
                        score += (max_option - answer)
                    else:
                        score += answer
                return score
            else:
                # Default to sum
                return sum(answers)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing interpretation rules: {e}")
            return sum(answers)
    
    def calculate_percentage(self, score: int, max_score: int) -> float:
        """Calculate percentage score."""
        if max_score == 0:
            return 0.0
        return round((score / max_score) * 100, 2)
    
    def get_interpretation(self, test: Dict[str, Any], score: int, percentage: float) -> str:
        """
        Get interpretation text based on score.
        
        Args:
            test: Test definition
            score: Calculated score
            percentage: Percentage score
            
        Returns:
            Interpretation text
        """
        rules = test.get('interpretation_rules', '')
        if not rules:
            return ""
        
        try:
            rules_data = json.loads(rules)
            thresholds = rules_data.get('thresholds', [])
            
            # Sort thresholds by score (descending)
            thresholds.sort(key=lambda x: x.get('max_score', 0), reverse=True)
            
            for threshold in thresholds:
                if score <= threshold.get('max_score', 999):
                    return threshold.get('interpretation', '')
            
            return ""
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing interpretation rules: {e}")
            return ""
    
    # Test Results
    
    def create_test_result(self, user_id: int, username: str, test_id: int,
                          answers: List[int]) -> Optional[int]:
        """
        Create a new test result.
        
        Args:
            user_id: User ID
            username: Username
            test_id: Test ID
            answers: List of answer indices
            
        Returns:
            Result ID if successful, None otherwise
        """
        test = self.repository.get_test_by_id(test_id)
        if not test:
            logger.error(f"Test not found: {test_id}")
            return None
        
        score = self.calculate_score(test, answers)
        max_score = test['max_score']
        percentage = self.calculate_percentage(score, max_score)
        interpretation = self.get_interpretation(test, score, percentage)
        
        try:
            result_id = self.repository.create_test_result(
                user_id, username, test_id, test['test_code'], test['test_name'],
                score, max_score, percentage, interpretation, answers
            )
            return result_id
        except Exception as e:
            logger.error(f"Error creating test result: {e}")
            return None
    
    def get_result(self, result_id: int) -> Optional[Dict[str, Any]]:
        """Get test result by ID."""
        return self.repository.get_result_by_id(result_id)
    
    def get_user_results(self, user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get test results for a user."""
        return self.repository.get_results_by_user(user_id, limit)
    
    def get_all_results(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all test results."""
        return self.repository.get_all_results(limit)
    
    def delete_result(self, result_id: int) -> bool:
        """Delete test result."""
        return self.repository.delete_result(result_id)
