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
        if problem_type not in ['algorithm', 'choice', 'fillblank']:
            raise ValueError(f"Invalid problem type: {problem_type}. Must be 'algorithm', 'choice', or 'fillblank'")

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
        elif problem_type == 'fillblank':
            cls._validate_fillblank_problem(frontmatter)

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

    @classmethod
    def _validate_fillblank_problem(cls, frontmatter: Dict[str, Any]) -> None:
        """Validate fill-in-blank problem specific fields."""
        if 'content_with_blanks' not in frontmatter:
            raise ValueError("Fill-in-blank problems must have 'content_with_blanks' field")

        if not isinstance(frontmatter['content_with_blanks'], str) or not frontmatter['content_with_blanks'].strip():
            raise ValueError("'content_with_blanks' must be a non-empty string")

        if 'blanks' not in frontmatter:
            raise ValueError("Fill-in-blank problems must have 'blanks' field")

        blanks = frontmatter['blanks']

        # Extract blank markers from content
        blank_numbers = cls._extract_blank_markers(frontmatter['content_with_blanks'])

        if not blank_numbers:
            raise ValueError("'content_with_blanks' must contain at least one blank marker (e.g., [blank1])")

        # Validate the blanks format
        cls._validate_blanks_format(blanks, blank_numbers)

        # Validate blank_count if provided
        if 'blank_count' in frontmatter:
            blank_count = frontmatter['blank_count']
            if not isinstance(blank_count, int) or blank_count < 0:
                raise ValueError("'blank_count' must be a non-negative integer")
            if blank_count != len(blank_numbers):
                raise ValueError(
                    f"'blank_count' ({blank_count}) does not match the number of "
                    f"blank markers found ({len(blank_numbers)}) in content_with_blanks"
                )

    @classmethod
    def _extract_blank_markers(cls, content: str) -> set:
        """Extract all blank marker numbers from content.

        Example: "Python is [blank1] language" -> {1}

        Args:
            content: Text with [blankN] markers

        Returns:
            Set of blank numbers found (e.g., {1, 2, 3})
        """
        import re
        # Match [blankN] patterns where N is at least 1
        pattern = re.compile(r'\[blank(\d+)\]')
        matches = pattern.findall(content)
        numbers = set()

        for match in matches:
            try:
                num = int(match)
                if num < 1:
                    raise ValueError(f"Blank number must be >= 1, got {num}")
                numbers.add(num)
            except ValueError:
                raise ValueError(f"Invalid blank marker format: [blank{match}]. Must be [blankN] where N >= 1")

        # Validate numbering is sequential starting from 1
        if numbers and sorted(numbers) != list(range(1, len(numbers) + 1)):
            missing = sorted(numbers)
            raise ValueError(
                f"Blank markers must be numbered sequentially starting from 1. "
                f"Found: {sorted(numbers)}"
            )

        return numbers

    @classmethod
    def _validate_blanks_format(cls, blanks: Any, blank_numbers: set) -> None:
        """Validate blanks field format. Supports three formats:

        Format 1 (detailed):
          {
            "blank1": {"answers": [...], "case_sensitive": false},
            "blank2": {"answers": [...], "case_sensitive": true}
          }

        Format 2 (simple):
          {
            "blanks": [...],
            "case_sensitive": false
          }

        Format 3 (recommended list):
          {
            "blanks": [
              {"answers": [...], "case_sensitive": false},
              {"answers": [...], "case_sensitive": true}
            ]
          }
        """
        if not isinstance(blanks, dict):
            raise ValueError("'blanks' must be a dictionary")

        # Check for format 2 (simple)
        if 'blanks' in blanks and len(blanks) == 2 and 'case_sensitive' in blanks:
            cls._validate_simple_blanks_format(blanks, blank_numbers)
        # Check for format 3 (list)
        elif 'blanks' in blanks and isinstance(blanks['blanks'], list) and len(blanks) == 1:
            cls._validate_list_blanks_format(blanks, blank_numbers)
        # Check for format 1 (detailed)
        elif all(isinstance(v, dict) and 'answers' in v for v in blanks.values()):
            cls._validate_detailed_blanks_format(blanks, blank_numbers)
        else:
            raise ValueError(
                "'blanks' must be one of these formats:\n"
                "1. Detailed: {blank1: {answers: [...], case_sensitive: false}}\n"
                "2. Simple: {blanks: [...], case_sensitive: false}\n"
                "3. List: {blanks: [{answers: [...], case_sensitive: false}]}"
            )

    @classmethod
    def _validate_detailed_blanks_format(cls, blanks: Dict, blank_numbers: set) -> None:
        """Validate detailed blanks format: {blank1: {...}, blank2: {...}}"""
        # Extract defined blank numbers from keys
        defined_blank_numbers = set()
        for key in blanks.keys():
            if not key.startswith('blank') or not key[5:].isdigit():
                raise ValueError(f"Invalid blank key '{key}'. Must be 'blankN' where N is a number")

            blank_num = int(key[5:])
            defined_blank_numbers.add(blank_num)

            blank_config = blanks[key]
            cls._validate_blank_config(blank_config, key)

        # Check for orphaned definitions (defined but not used)
        for blank_num in defined_blank_numbers:
            if blank_num not in blank_numbers:
                key = f'blank{blank_num}'
                raise ValueError(f"Blank key '{key}' defined but not referenced in content_with_blanks")

        # Check for missing definitions (used but not defined)
        for blank_num in blank_numbers:
            if blank_num not in defined_blank_numbers:
                key = f'blank{blank_num}'
                raise ValueError(f"Blank '{key}' is referenced in content_with_blanks but has no definition")

    @classmethod
    def _validate_simple_blanks_format(cls, blanks: Dict, blank_numbers: set) -> None:
        """Validate simple blanks format: {blanks: [...], case_sensitive: boolean}"""
        if not isinstance(blanks['blanks'], list):
            raise ValueError("'blanks' must be a list in simple format")

        if not isinstance(blanks['case_sensitive'], bool):
            raise ValueError("'case_sensitive' must be a boolean in simple format")

        if len(blanks['blanks']) != len(blank_numbers):
            raise ValueError(
                f"Number of answers in simple format ({len(blanks['blanks'])}) "
                f"does not match number of blank markers ({len(blank_numbers)})"
            )

        for i, answer in enumerate(blanks['blanks']):
            blank_key = f'blank{i+1}'
            cls._validate_blank_content(answer, blank_key)

    @classmethod
    def _validate_list_blanks_format(cls, blanks: Dict, blank_numbers: set) -> None:
        """Validate list blanks format: {blanks: [{answers: [...], case_sensitive: ...}]}"""
        blanks_list = blanks['blanks']
        if len(blanks_list) != len(blank_numbers):
            raise ValueError(
                f"Number of blank configurations in list format ({len(blanks_list)}) "
                f"does not match number of blank markers ({len(blank_numbers)})"
            )

        for i, blank_config in enumerate(blanks_list):
            blank_key = f'blank{i+1}'
            if not isinstance(blank_config, dict):
                raise ValueError(f"Blank configuration for {blank_key} must be a dictionary")
            cls._validate_blank_config(blank_config, blank_key)

    @classmethod
    def _validate_blank_config(cls, config: Dict, blank_key: str) -> None:
        """Validate a single blank configuration."""
        if 'answers' not in config:
            raise ValueError(f"'answers' required for {blank_key}")

        answers = config['answers']
        if not isinstance(answers, list) or len(answers) == 0:
            raise ValueError(f"'answers' for {blank_key} must be a non-empty list")

        for answer in answers:
            cls._validate_blank_content(answer, blank_key)

        # Validate case_sensitive if present
        if 'case_sensitive' in config and not isinstance(config['case_sensitive'], bool):
            raise ValueError(f"'case_sensitive' for {blank_key} must be a boolean")

    @classmethod
    def _validate_blank_content(cls, content: Any, blank_key: str) -> None:
        """Validate blank answer content."""
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"Answer for {blank_key} must be a non-empty string")

    @classmethod
    def validate_chapter_unlock_conditions(cls, unlock_conditions: Dict[str, Any]) -> None:
        """
        Validate chapter unlock conditions.

        Args:
            unlock_conditions: Unlock conditions dictionary from frontmatter

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(unlock_conditions, dict):
            raise ValueError("'unlock_conditions' must be a dictionary")

        valid_types = ['prerequisite', 'date', 'all', 'none']
        cond_type = unlock_conditions.get('type', 'none')

        if cond_type not in valid_types:
            raise ValueError(
                f"Invalid unlock_condition type: {cond_type}. "
                f"Must be one of {', '.join(valid_types)}"
            )

        # Validate required fields based on type
        if cond_type == 'prerequisite':
            if 'prerequisites' not in unlock_conditions:
                raise ValueError("unlock_conditions type 'prerequisite' requires 'prerequisites' field")
            cls.validate_chapter_prerequisites(unlock_conditions['prerequisites'])
        elif cond_type == 'date':
            if 'unlock_date' not in unlock_conditions:
                raise ValueError("unlock_conditions type 'date' requires 'unlock_date' field")
            cls.validate_chapter_unlock_date(unlock_conditions['unlock_date'])
        elif cond_type == 'all':
            if 'prerequisites' not in unlock_conditions:
                raise ValueError("unlock_conditions type 'all' requires 'prerequisites' field")
            if 'unlock_date' not in unlock_conditions:
                raise ValueError("unlock_conditions type 'all' requires 'unlock_date' field")
            cls.validate_chapter_prerequisites(unlock_conditions['prerequisites'])
            cls.validate_chapter_unlock_date(unlock_conditions['unlock_date'])
        # 'none' type requires no additional validation

    @classmethod
    def validate_chapter_prerequisites(cls, prerequisites: Any) -> None:
        """
        Validate chapter prerequisites field.

        Args:
            prerequisites: Prerequisites value from frontmatter

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(prerequisites, list):
            raise ValueError("'prerequisites' must be a list")

        for prereq in prerequisites:
            if not isinstance(prereq, int):
                raise ValueError(f"Each prerequisite must be an integer, got: {prereq}")
            if prereq < 0:
                raise ValueError(f"Prerequisite order cannot be negative, got: {prereq}")

    @classmethod
    def validate_chapter_unlock_date(cls, unlock_date: Any) -> None:
        """
        Validate chapter unlock_date field.

        Args:
            unlock_date: Unlock date value from frontmatter

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(unlock_date, str) or not unlock_date.strip():
            raise ValueError("'unlock_date' must be a non-empty string")

        # Try to parse the date to ensure it's valid ISO 8601
        try:
            from dateutil import parser as date_parser
            # Use isoparse for stricter ISO 8601 validation
            date_parser.isoparse(unlock_date)
        except Exception as e:
            raise ValueError(
                f"Invalid ISO 8601 format for 'unlock_date': {unlock_date}. "
                f"Expected format: '2025-03-01T00:00:00Z'"
            ) from e
