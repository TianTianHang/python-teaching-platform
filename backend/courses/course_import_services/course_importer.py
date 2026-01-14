"""
Course importer service for importing courses from markdown repository.

This module handles the orchestration of importing courses, chapters, and problems
from a Git repository containing markdown files with YAML frontmatter.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

from django.db import transaction
from django.core.exceptions import ValidationError

from courses.models import (
    Course, Chapter, Problem, AlgorithmProblem,
    ChoiceProblem, TestCase
)
from .markdown_parser import MarkdownFrontmatterParser

logger = logging.getLogger(__name__)


class CourseImporter:
    """
    Import courses from markdown files in Git repository.

    Usage:
        importer = CourseImporter(repo_path, update_mode=True)
        stats = importer.import_all()
        print(f"Created {stats['courses_created']} courses")
    """

    def __init__(self, repo_path: Path, update_mode: bool = True):
        """
        Initialize importer.

        Args:
            repo_path: Path to cloned repository
            update_mode: If True, update existing courses; if False, skip them
        """
        self.repo_path = repo_path
        self.update_mode = update_mode
        self.stats = {
            'courses_created': 0,
            'courses_updated': 0,
            'courses_skipped': 0,
            'chapters_created': 0,
            'chapters_updated': 0,
            'problems_created': 0,
            'problems_updated': 0,
            'errors': []
        }

    def import_all(self) -> Dict[str, Any]:
        """
        Import all courses from repository.

        Returns:
            Dictionary with import statistics

        Raises:
            ValueError: If repository structure is invalid
        """
        courses_dir = self.repo_path / 'courses'

        if not courses_dir.exists():
            raise ValueError("courses/ directory not found in repository")

        logger.info(f"Starting import from {courses_dir}")

        for course_dir in sorted(courses_dir.iterdir()):
            if not course_dir.is_dir():
                continue

            try:
                self._import_course(course_dir)
            except Exception as e:
                logger.error(f"Failed to import course {course_dir.name}: {e}")
                self.stats['errors'].append({
                    'course': course_dir.name,
                    'error': str(e)
                })

        return self.stats

    @transaction.atomic
    def _import_course(self, course_dir: Path) -> None:
        """
        Import a single course.

        Args:
            course_dir: Path to course directory
        """
        course_md = course_dir / 'course.md'

        if not course_md.exists():
            raise ValueError(f"course.md not found in {course_dir.name}")

        frontmatter, content = MarkdownFrontmatterParser.parse(course_md)
        MarkdownFrontmatterParser.validate_course_frontmatter(frontmatter)

        # Get or create course
        course, created = Course.objects.get_or_create(
            title=frontmatter['title'],
            defaults={
                'description': frontmatter.get('description', ''),
            }
        )

        if created:
            self.stats['courses_created'] += 1
            logger.info(f"Created course: {course.title}")
        elif self.update_mode:
            self.stats['courses_updated'] += 1
            course.description = frontmatter.get('description', '')
            course.save()
            logger.info(f"Updated course: {course.title}")
        else:
            self.stats['courses_skipped'] += 1
            logger.info(f"Skipped existing course: {course.title}")
            return  # Skip processing children if not updating

        # Import chapters
        self._import_chapters(course, course_dir)

        # Import problems
        self._import_problems(course, course_dir)

    def _import_chapters(self, course: Course, course_dir: Path) -> None:
        """
        Import all chapters for a course.

        Args:
            course: Course instance
            course_dir: Path to course directory
        """
        chapters_dir = course_dir / 'chapters'

        if not chapters_dir.exists():
            logger.warning(f"No chapters/ directory in {course.title}")
            return

        for chapter_file in sorted(chapters_dir.glob('chapter-*.md')):
            try:
                self._import_chapter(course, chapter_file)
            except Exception as e:
                logger.error(f"Failed to import chapter {chapter_file.name}: {e}")
                self.stats['errors'].append({
                    'chapter': chapter_file.name,
                    'course': course.title,
                    'error': str(e)
                })

    def _import_chapter(self, course: Course, chapter_file: Path) -> None:
        """
        Import a single chapter.

        Args:
            course: Course instance
            chapter_file: Path to chapter markdown file
        """
        frontmatter, content = MarkdownFrontmatterParser.parse(chapter_file)
        MarkdownFrontmatterParser.validate_chapter_frontmatter(frontmatter)

        chapter, created = Chapter.objects.get_or_create(
            course=course,
            order=frontmatter['order'],
            defaults={
                'title': frontmatter['title'],
                'content': content.strip()
            }
        )

        if created:
            self.stats['chapters_created'] += 1
            logger.info(f"Created chapter: {chapter.title} (order: {chapter.order})")
        elif self.update_mode:
            self.stats['chapters_updated'] += 1
            chapter.title = frontmatter['title']
            chapter.content = content.strip()
            chapter.save()
            logger.info(f"Updated chapter: {chapter.title} (order: {chapter.order})")

    def _import_problems(self, course: Course, course_dir: Path) -> None:
        """
        Import all problems for a course.

        Args:
            course: Course instance
            course_dir: Path to course directory
        """
        problems_dir = course_dir / 'problems'

        if not problems_dir.exists():
            logger.warning(f"No problems/ directory in {course.title}")
            return

        for problem_file in problems_dir.glob('*.md'):
            if problem_file.name == 'course.md':
                continue

            try:
                self._import_problem(problem_file)
            except Exception as e:
                logger.error(f"Failed to import problem {problem_file.name}: {e}")
                self.stats['errors'].append({
                    'problem': problem_file.name,
                    'course': course.title,
                    'error': str(e)
                })

    def _import_problem(self, problem_file: Path) -> None:
        """
        Import a single problem (algorithm or choice).

        Args:
            problem_file: Path to problem markdown file
        """
        frontmatter, content = MarkdownFrontmatterParser.parse(problem_file)
        MarkdownFrontmatterParser.validate_problem_frontmatter(frontmatter)

        # Get or create problem
        problem, created = Problem.objects.get_or_create(
            title=frontmatter['title'],
            defaults={
                'type': frontmatter['type'],
                'content': content.strip(),
                'difficulty': frontmatter['difficulty'],
                'chapter': None  # Problems can be standalone initially
            }
        )

        if created:
            self.stats['problems_created'] += 1
            logger.info(f"Created problem: {problem.title}")
        elif self.update_mode:
            self.stats['problems_updated'] += 1
            problem.type = frontmatter['type']
            problem.content = content.strip()
            problem.difficulty = frontmatter['difficulty']
            problem.save()
            logger.info(f"Updated problem: {problem.title}")

        # Handle problem-specific data
        if frontmatter['type'] == 'algorithm':
            self._import_algorithm_problem(problem, frontmatter)
        elif frontmatter['type'] == 'choice':
            self._import_choice_problem(problem, frontmatter)

    def _import_algorithm_problem(self, problem: Problem, frontmatter: Dict[str, Any]) -> None:
        """
        Import algorithm problem details.

        Args:
            problem: Problem instance
            frontmatter: Validated frontmatter dictionary
        """
        algo_info, created = AlgorithmProblem.objects.get_or_create(
            problem=problem,
            defaults={
                'time_limit': frontmatter.get('time_limit', 1000),
                'memory_limit': frontmatter.get('memory_limit', 256),
                'code_template': frontmatter.get('code_template'),
                'solution_name': frontmatter['solution_name']
            }
        )

        if not created and self.update_mode:
            algo_info.time_limit = frontmatter.get('time_limit', 1000)
            algo_info.memory_limit = frontmatter.get('memory_limit', 256)
            algo_info.code_template = frontmatter.get('code_template')
            algo_info.solution_name = frontmatter['solution_name']
            algo_info.save()
            logger.info(f"Updated algorithm problem info for: {problem.title}")

        # Import test cases
        self._import_test_cases(algo_info, frontmatter.get('test_cases', []))

    def _import_test_cases(self, algo_info: AlgorithmProblem, test_cases: List[Dict]) -> None:
        """
        Import test cases for algorithm problem.

        Args:
            algo_info: AlgorithmProblem instance
            test_cases: List of test case dictionaries
        """
        for tc_data in test_cases:
            TestCase.objects.get_or_create(
                problem=algo_info,
                input_data=tc_data['input'],
                defaults={
                    'expected_output': tc_data['output'],
                    'is_sample': tc_data.get('is_sample', False)
                }
            )

        logger.info(f"Imported {len(test_cases)} test cases for {algo_info.problem.title}")

    def _import_choice_problem(self, problem: Problem, frontmatter: Dict[str, Any]) -> None:
        """
        Import choice problem details.

        Args:
            problem: Problem instance
            frontmatter: Validated frontmatter dictionary
        """
        choice_info, created = ChoiceProblem.objects.get_or_create(
            problem=problem,
            defaults={
                'options': frontmatter['options'],
                'correct_answer': frontmatter['correct_answer'],
                'is_multiple_choice': frontmatter['is_multiple_choice']
            }
        )

        if not created and self.update_mode:
            choice_info.options = frontmatter['options']
            choice_info.correct_answer = frontmatter['correct_answer']
            choice_info.is_multiple_choice = frontmatter['is_multiple_choice']
            choice_info.save()
            logger.info(f"Updated choice problem info for: {problem.title}")
