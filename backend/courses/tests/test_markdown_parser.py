"""
Tests for MarkdownFrontmatterParser.
"""

import tempfile
import yaml
from pathlib import Path

from django.test import TestCase

from courses.course_import_services.markdown_parser import MarkdownFrontmatterParser


class TestMarkdownFrontmatterParser(TestCase):
    """Test markdown frontmatter parsing and validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_test_file(self, content: str) -> Path:
        """Create a test markdown file with given content."""
        file_path = self.temp_path / "test.md"
        file_path.write_text(content, encoding='utf-8')
        return file_path

    def test_parse_no_frontmatter(self):
        """Test parsing markdown without frontmatter."""
        file_path = self.create_test_file("# Title\n\nContent here...")

        frontmatter, content = MarkdownFrontmatterParser.parse(file_path)

        self.assertEqual(frontmatter, {})
        self.assertEqual(content, "# Title\n\nContent here...")

    def test_parse_with_frontmatter(self):
        """Test parsing markdown with frontmatter."""
        frontmatter_data = {
            'title': 'Test Course',
            'description': 'A test course'
        }
        content = "# Title\n\nContent here..."
        yaml_content = yaml.dump(frontmatter_data)
        file_content = f"---\n{yaml_content}\n---\n{content}"

        file_path = self.create_test_file(file_content)
        frontmatter, parsed_content = MarkdownFrontmatterParser.parse(file_path)

        self.assertEqual(frontmatter, frontmatter_data)
        self.assertEqual(parsed_content, content)

    # Course frontmatter validation tests
    def test_validate_course_frontmatter_valid(self):
        """Test validation of valid course frontmatter."""
        frontmatter = {
            'title': 'Test Course',
            'description': 'A test course'
        }

        # Should not raise exception
        MarkdownFrontmatterParser.validate_course_frontmatter(frontmatter)

    def test_validate_course_frontmatter_missing_title(self):
        """Test validation fails when title is missing."""
        frontmatter = {
            'description': 'A test course'
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_course_frontmatter(frontmatter)
        self.assertIn("Missing required fields for course: title", str(context.exception))

    def test_validate_course_frontmatter_empty_title(self):
        """Test validation fails when title is empty."""
        frontmatter = {
            'title': '',
            'description': 'A test course'
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_course_frontmatter(frontmatter)
        self.assertIn("Course title cannot be empty", str(context.exception))

    # Chapter frontmatter validation tests
    def test_validate_chapter_frontmatter_valid(self):
        """Test validation of valid chapter frontmatter."""
        frontmatter = {
            'title': 'Chapter 1',
            'order': 1
        }

        # Should not raise exception
        MarkdownFrontmatterParser.validate_chapter_frontmatter(frontmatter)

    def test_validate_chapter_frontmatter_missing_title(self):
        """Test validation fails when title is missing."""
        frontmatter = {
            'order': 1
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_frontmatter(frontmatter)
        self.assertIn("Missing required field: title", str(context.exception))

    def test_validate_chapter_frontmatter_missing_order(self):
        """Test validation fails when order is missing."""
        frontmatter = {
            'title': 'Chapter 1'
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_frontmatter(frontmatter)
        self.assertIn("Missing required field: order", str(context.exception))

    # Chapter unlock condition validation tests
    def test_validate_chapter_unlock_conditions_prerequisite_valid(self):
        """Test validation of valid prerequisite unlock conditions."""
        unlock_conditions = {
            'type': 'prerequisite',
            'prerequisites': [1, 2, 3]
        }

        # Should not raise exception
        MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)

    def test_validate_chapter_unlock_conditions_date_valid(self):
        """Test validation of valid date unlock conditions."""
        unlock_conditions = {
            'type': 'date',
            'unlock_date': '2025-03-01T00:00:00Z'
        }

        # Should not raise exception
        MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)

    def test_validate_chapter_unlock_conditions_all_valid(self):
        """Test validation of valid all-type unlock conditions."""
        unlock_conditions = {
            'type': 'all',
            'prerequisites': [1, 2],
            'unlock_date': '2025-03-01T00:00:00Z'
        }

        # Should not raise exception
        MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)

    def test_validate_chapter_unlock_conditions_none_valid(self):
        """Test validation of none-type unlock conditions."""
        unlock_conditions = {
            'type': 'none'
        }

        # Should not raise exception
        MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)

    def test_validate_chapter_unlock_conditions_missing_type(self):
        """Test validation accepts missing type (defaults to none)."""
        unlock_conditions = {}

        # Should not raise exception (defaults to 'none')
        MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)

    def test_validate_chapter_unlock_conditions_invalid_type(self):
        """Test validation fails for invalid unlock condition type."""
        unlock_conditions = {
            'type': 'invalid_type'
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)
        self.assertIn("Invalid unlock_condition type: invalid_type", str(context.exception))

    def test_validate_chapter_unlock_conditions_prerequisites_missing(self):
        """Test validation fails when prerequisites are missing for prerequisite type."""
        unlock_conditions = {
            'type': 'prerequisite'
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)
        self.assertIn("unlock_conditions type 'prerequisite' requires 'prerequisites' field", str(context.exception))

    def test_validate_chapter_unlock_conditions_date_missing(self):
        """Test validation fails when unlock_date is missing for date type."""
        unlock_conditions = {
            'type': 'date'
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)
        self.assertIn("unlock_conditions type 'date' requires 'unlock_date' field", str(context.exception))

    def test_validate_chapter_unlock_conditions_prerequisites_invalid_type(self):
        """Test validation fails when prerequisites is not a list."""
        unlock_conditions = {
            'type': 'prerequisite',
            'prerequisites': 'not_a_list'
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)
        self.assertIn("'prerequisites' must be a list", str(context.exception))

    def test_validate_chapter_unlock_conditions_prerequisites_non_int(self):
        """Test validation fails when prerequisites contains non-integer."""
        unlock_conditions = {
            'type': 'prerequisite',
            'prerequisites': [1, 2, 'not_an_int']
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)
        self.assertIn("Each prerequisite must be an integer, got: not_an_int", str(context.exception))

    def test_validate_chapter_unlock_conditions_prerequisites_negative(self):
        """Test validation fails when prerequisites contains negative number."""
        unlock_conditions = {
            'type': 'prerequisite',
            'prerequisites': [1, -1, 2]
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)
        self.assertIn("Prerequisite order cannot be negative, got: -1", str(context.exception))

    def test_validate_chapter_unlock_date_invalid_format(self):
        """Test validation fails for invalid unlock date format."""
        unlock_conditions = {
            'type': 'date',
            'unlock_date': 'not_a_date'
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)
        self.assertIn("Invalid ISO 8601 format for 'unlock_date'", str(context.exception))

    def test_validate_chapter_unlock_date_empty(self):
        """Test validation fails for empty unlock date."""
        unlock_conditions = {
            'type': 'date',
            'unlock_date': ''
        }

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_conditions(unlock_conditions)
        self.assertIn("'unlock_date' must be a non-empty string", str(context.exception))

    def test_validate_chapter_prerequisites_valid(self):
        """Test validation of valid prerequisites."""
        prerequisites = [1, 2, 3]

        # Should not raise exception
        MarkdownFrontmatterParser.validate_chapter_prerequisites(prerequisites)

    def test_validate_chapter_prerequisites_not_list(self):
        """Test validation fails when prerequisites is not a list."""
        prerequisites = "not_a_list"

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_prerequisites(prerequisites)
        self.assertIn("'prerequisites' must be a list", str(context.exception))

    def test_validate_chapter_prerequisites_with_string(self):
        """Test validation fails when prerequisites contains string."""
        prerequisites = [1, "2", 3]

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_prerequisites(prerequisites)
        self.assertIn("Each prerequisite must be an integer, got: 2", str(context.exception))

    def test_validate_chapter_prerequisites_with_negative(self):
        """Test validation fails when prerequisites contains negative number."""
        prerequisites = [1, -1, 2]

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_prerequisites(prerequisites)
        self.assertIn("Prerequisite order cannot be negative, got: -1", str(context.exception))

    def test_validate_chapter_unlock_date_valid(self):
        """Test validation of valid unlock date."""
        unlock_date = '2025-03-01T00:00:00Z'

        # Should not raise exception
        MarkdownFrontmatterParser.validate_chapter_unlock_date(unlock_date)

    def test_validate_chapter_unlock_date_not_string(self):
        """Test validation fails when unlock_date is not a string."""
        unlock_date = 123

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_date(unlock_date)
        self.assertIn("'unlock_date' must be a non-empty string", str(context.exception))

    def test_validate_chapter_unlock_date_empty_string(self):
        """Test validation fails for empty unlock date."""
        unlock_date = ''

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_date(unlock_date)
        self.assertIn("'unlock_date' must be a non-empty string", str(context.exception))

    def test_validate_chapter_unlock_date_invalid_iso(self):
        """Test validation fails for invalid ISO date."""
        unlock_date = 'not_a_date'

        with self.assertRaises(ValueError) as context:
            MarkdownFrontmatterParser.validate_chapter_unlock_date(unlock_date)
        self.assertIn("Invalid ISO 8601 format for 'unlock_date'", str(context.exception))

    def test_validate_chapter_unlock_date_valid_with_timezone(self):
        """Test validation accepts valid ISO date with timezone."""
        unlock_date = '2025-03-01T08:00:00+08:00'

        # Should not raise exception
        MarkdownFrontmatterParser.validate_chapter_unlock_date(unlock_date)