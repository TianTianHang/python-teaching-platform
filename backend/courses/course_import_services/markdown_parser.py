"""
Markdown frontmatter parser for course repository files.

This module provides utilities to parse markdown files with YAML frontmatter,
validate the schema, and extract metadata and content.
"""

import re
import logging
from typing import Dict, Any, Tuple, Optional
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


class MarkdownFrontmatterParser:
    """
    Parse markdown files with YAML frontmatter.

    Expected format:
        ---
        key: value
        ---
        Markdown content here...
    """

    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)$', re.DOTALL)

    @classmethod
    def parse(cls, file_path: Path) -> Tuple[Dict[str, Any], str]:
        """
        Parse markdown file and return (frontmatter, content) tuple.

        Args:
            file_path: Path to markdown file

        Returns:
            Tuple of (frontmatter dict, markdown content string)

        Raises:
            ValueError: If YAML frontmatter is invalid
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_text(encoding='utf-8')
        match = cls.FRONTMATTER_PATTERN.match(content)

        if not match:
            # No frontmatter found, return entire content as markdown
            logger.debug(f"No frontmatter found in {file_path.name}")
            return {}, content

        try:
            frontmatter = yaml.safe_load(match.group(1))
            markdown_content = match.group(2)
            return frontmatter or {}, markdown_content
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML frontmatter in {file_path}: {e}") from e

    @classmethod
    def validate_course_frontmatter(cls, frontmatter: Dict[str, Any]) -> None:
        """
        Validate course metadata.

        Required fields: title, description

        Args:
            frontmatter: Parsed frontmatter dictionary

        Raises:
            ValueError: If validation fails
        """
        required_fields = ['title', 'description']
        missing_fields = [f for f in required_fields if f not in frontmatter]

        if missing_fields:
            raise ValueError(f"Missing required fields for course: {', '.join(missing_fields)}")

        # Validate title is not empty
        if not frontmatter.get('title', '').strip():
            raise ValueError("Course title cannot be empty")

    @classmethod
    def validate_chapter_frontmatter(cls, frontmatter: Dict[str, Any]) -> None:
        """
        Validate chapter metadata.

        Required fields: title, order

        Args:
            frontmatter: Parsed frontmatter dictionary

        Raises:
            ValueError: If validation fails
        """
        if 'title' not in frontmatter:
            raise ValueError("Missing required field: title")

        if not frontmatter.get('title', '').strip():
            raise ValueError("Chapter title cannot be empty")

        if 'order' not in frontmatter:
            raise ValueError("Missing required field: order")

        # Validate order is a positive integer
        try:
            order = int(frontmatter['order'])
            if order < 0:
                raise ValueError("Chapter order must be non-negative")
        except (ValueError, TypeError):
            raise ValueError("Chapter order must be a valid integer")

    @classmethod
    def validate_problem_frontmatter(cls, frontmatter: Dict[str, Any]) -> None:
        """
        Validate problem metadata.

        Required fields: title, type, difficulty

        For algorithm problems: test_cases, solution_name
        For choice problems: options, correct_answer, is_multiple_choice

        Args:
            frontmatter: Parsed frontmatter dictionary

        Raises:
            ValueError: If validation fails
        """
        required_fields = ['title', 'type', 'difficulty']
        missing_fields = [f for f in required_fields if f not in frontmatter]

        if missing_fields:
            raise ValueError(f"Missing required fields for problem: {', '.join(missing_fields)}")

        # Validate title is not empty
        if not frontmatter.get('title', '').strip():
            raise ValueError("Problem title cannot be empty")

        # Validate problem type
        problem_type = frontmatter['type']
        if problem_type not in ['algorithm', 'choice']:
            raise ValueError(f"Invalid problem type: {problem_type}. Must be 'algorithm' or 'choice'")

        # Validate difficulty is 1-3
        try:
            difficulty = int(frontmatter['difficulty'])
            if not 1 <= difficulty <= 3:
                raise ValueError("Problem difficulty must be between 1 and 3")
        except (ValueError, TypeError):
            raise ValueError("Problem difficulty must be a valid integer (1-3)")

        # Validate optional chapter field
        if 'chapter' in frontmatter:
            try:
                chapter_order = int(frontmatter['chapter'])
                if chapter_order < 0:
                    raise ValueError("Chapter field must be a non-negative integer")
            except (ValueError, TypeError):
                raise ValueError(f"Chapter field must be a valid integer, got: {frontmatter['chapter']}")

        # Type-specific validation
        if problem_type == 'algorithm':
            cls._validate_algorithm_problem(frontmatter)
        elif problem_type == 'choice':
            cls._validate_choice_problem(frontmatter)

    @classmethod
    def _validate_algorithm_problem(cls, frontmatter: Dict[str, Any]) -> None:
        """Validate algorithm problem specific fields."""
        if 'test_cases' not in frontmatter:
            raise ValueError("Algorithm problems must have 'test_cases' field")

        if not isinstance(frontmatter['test_cases'], list) or len(frontmatter['test_cases']) == 0:
            raise ValueError("Algorithm problem 'test_cases' must be a non-empty list")

        # Validate each test case
        for i, tc in enumerate(frontmatter['test_cases']):
            if not isinstance(tc, dict):
                raise ValueError(f"Test case {i} must be a dictionary")

            if 'input' not in tc:
                raise ValueError(f"Test case {i} missing 'input' field")

            if 'output' not in tc:
                raise ValueError(f"Test case {i} missing 'output' field")

        if 'solution_name' not in frontmatter:
            raise ValueError("Algorithm problems must have 'solution_name' field")

    @classmethod
    def _validate_choice_problem(cls, frontmatter: Dict[str, Any]) -> None:
        """Validate choice problem specific fields."""
        if 'options' not in frontmatter:
            raise ValueError("Choice problems must have 'options' field")

        if not isinstance(frontmatter['options'], dict) or len(frontmatter['options']) == 0:
            raise ValueError("Choice problem 'options' must be a non-empty dictionary")

        # Validate option keys are uppercase letters
        valid_keys = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        for key in frontmatter['options'].keys():
            if key not in valid_keys:
                raise ValueError(f"Invalid option key '{key}'. Must be uppercase letter (A-Z)")

        if 'correct_answer' not in frontmatter:
            raise ValueError("Choice problems must have 'correct_answer' field")

        # Validate correct_answer format
        correct_answer = frontmatter['correct_answer']
        if isinstance(correct_answer, list):
            # Multiple choice
            for ans in correct_answer:
                if ans not in frontmatter['options']:
                    raise ValueError(f"Correct answer '{ans}' not found in options")
        elif isinstance(correct_answer, str):
            # Single choice
            if correct_answer not in frontmatter['options']:
                raise ValueError(f"Correct answer '{correct_answer}' not found in options")
        else:
            raise ValueError("'correct_answer' must be a string or list")

        if 'is_multiple_choice' not in frontmatter:
            raise ValueError("Choice problems must have 'is_multiple_choice' field")

    @classmethod
    def extract_file_order(cls, filename: str) -> Optional[int]:
        """
        Extract order number from chapter filename.

        Example: 'chapter-01-variables.md' -> 1

        Args:
            filename: Chapter filename (e.g., 'chapter-01-variables.md')

        Returns:
            Order number or None if not found
        """
        match = re.match(r'chapter-(\d+)', filename)
        if match:
            return int(match.group(1))
        return None

    @classmethod
    def validate_unlock_conditions(cls, unlock_conditions: Dict[str, Any]) -> None:
        """
        Validate unlock conditions format.

        Args:
            unlock_conditions: Unlock conditions dictionary from frontmatter

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(unlock_conditions, dict):
            raise ValueError("'unlock_conditions' must be a dictionary")

        valid_types = ['prerequisite', 'date', 'both', 'none']
        cond_type = unlock_conditions.get('type', 'none')

        if cond_type not in valid_types:
            raise ValueError(
                f"Invalid unlock_condition type: {cond_type}. "
                f"Must be one of {', '.join(valid_types)}"
            )

        # Validate prerequisite conditions
        if cond_type in ['prerequisite', 'both']:
            if 'prerequisites' not in unlock_conditions:
                raise ValueError(
                    f"unlock_conditions type '{cond_type}' requires 'prerequisites' field"
                )

            prereqs = unlock_conditions['prerequisites']
            if not isinstance(prereqs, list) or len(prereqs) == 0:
                raise ValueError("'prerequisites' must be a non-empty list")

            # Validate each prerequisite is a filename (string)
            for prereq in prereqs:
                if not isinstance(prereq, str) or not prereq.strip():
                    raise ValueError(
                        f"Each prerequisite must be a non-empty string (filename), got: {prereq}"
                    )

        # Validate date conditions
        if cond_type in ['date', 'both']:
            if 'unlock_date' not in unlock_conditions:
                raise ValueError(
                    f"unlock_conditions type '{cond_type}' requires 'unlock_date' field"
                )

            # Validate date format
            unlock_date = unlock_conditions['unlock_date']
            if not isinstance(unlock_date, str) or not unlock_date.strip():
                raise ValueError("'unlock_date' must be a non-empty string (ISO 8601 format)")

            # Try to parse the date to ensure it's valid
            try:
                from dateutil import parser as date_parser
                date_parser.parse(unlock_date)
            except Exception as e:
                raise ValueError(
                    f"Invalid date format for 'unlock_date': {unlock_date}. "
                    f"Expected ISO 8601 format (e.g., '2024-12-31T23:59:59')"
                ) from e

        # Validate minimum_percentage
        if 'minimum_percentage' in unlock_conditions:
            pct = unlock_conditions['minimum_percentage']
            if not isinstance(pct, (int, float)):
                raise ValueError(f"'minimum_percentage' must be a number, got: {type(pct).__name__}")
            if not (0 <= pct <= 100):
                raise ValueError(f"'minimum_percentage' must be between 0 and 100, got: {pct}")
