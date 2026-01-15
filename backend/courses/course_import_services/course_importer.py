"""
Course importer service for importing courses from markdown repository.

This module handles the orchestration of importing courses, chapters, and problems
from a Git repository containing markdown files with YAML frontmatter.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
from django.utils import timezone

from django.db import transaction
from django.core.exceptions import ValidationError

from courses.models import (
    Course, Chapter, Problem, AlgorithmProblem,
    ChoiceProblem, TestCase, ProblemUnlockCondition
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
        Import all problems for a course using a two-phase approach:
        1. Import all problem basic info (without unlock conditions)
        2. Process all unlock conditions after all problems exist

        Args:
            course: Course instance
            course_dir: Path to course directory
        """
        problems_dir = course_dir / 'problems'

        if not problems_dir.exists():
            logger.warning(f"No problems/ directory in {course.title}")
            return

        # Phase 1: Import all problem basic info (skip unlock conditions)
        problem_files = list(problems_dir.glob('*.md'))
        for problem_file in problem_files:
            if problem_file.name == 'course.md':
                continue

            try:
                self._import_problem_basic_info(problem_file, course, problems_dir)
            except Exception as e:
                logger.error(f"Failed to import problem {problem_file.name}: {e}")
                self.stats['errors'].append({
                    'problem': problem_file.name,
                    'course': course.title,
                    'error': str(e)
                })

        # Phase 2: Process all unlock conditions after all problems exist
        for problem_file in problem_files:
            if problem_file.name == 'course.md':
                continue

            try:
                self._import_problem_unlock_conditions(problem_file, course, problems_dir)
            except Exception as e:
                logger.error(f"Failed to import unlock conditions for {problem_file.name}: {e}")
                # Don't add to errors as this is non-critical

    def _import_problem_basic_info(self, problem_file: Path, course: Course, problems_dir: Path) -> Problem:
        """
        Import a single problem's basic information (without unlock conditions).

        This is Phase 1 of the two-phase import process.

        Args:
            problem_file: Path to problem markdown file
            course: Course instance
            problems_dir: Path to problems directory

        Returns:
            The created or updated Problem instance

        Raises:
            ValueError: If specified chapter is not found
        """
        frontmatter, content = MarkdownFrontmatterParser.parse(problem_file)
        MarkdownFrontmatterParser.validate_problem_frontmatter(frontmatter)

        # Resolve chapter if specified
        chapter = None
        if 'chapter' in frontmatter:
            chapter_order = int(frontmatter['chapter'])
            try:
                chapter = Chapter.objects.get(course=course, order=chapter_order)
                logger.info(f"Found chapter {chapter_order} for problem: {frontmatter['title']}")
            except Chapter.DoesNotExist:
                raise ValueError(
                    f"Chapter with order {chapter_order} not found in course '{course.title}'. "
                    f"Problem '{frontmatter['title']}' cannot be imported. "
                    f"Please ensure chapter order {chapter_order} exists in this course."
                )

        # Get or create problem
        problem, created = Problem.objects.get_or_create(
            title=frontmatter['title'],
            defaults={
                'type': frontmatter['type'],
                'content': content.strip(),
                'difficulty': frontmatter['difficulty'],
                'chapter': chapter  # Use resolved chapter (or None if not specified)
            }
        )

        if created:
            self.stats['problems_created'] += 1
            logger.info(f"Created problem: {problem.title} (chapter: {chapter.title if chapter else 'None'})")
        elif self.update_mode:
            self.stats['problems_updated'] += 1
            problem.type = frontmatter['type']
            problem.content = content.strip()
            problem.difficulty = frontmatter['difficulty']
            problem.chapter = chapter  # Update chapter association
            problem.save()
            logger.info(f"Updated problem: {problem.title} (chapter: {chapter.title if chapter else 'None'})")

        # Handle problem-specific data
        if frontmatter['type'] == 'algorithm':
            self._import_algorithm_problem(problem, frontmatter)
        elif frontmatter['type'] == 'choice':
            self._import_choice_problem(problem, frontmatter)

        return problem

    def _import_problem(self, problem_file: Path, course: Course, problems_dir: Path) -> None:
        """
        Import a single problem (algorithm or choice) including unlock conditions.

        Note: This method is kept for backward compatibility but is no longer used
        in the main import flow. Use _import_problem_basic_info and
        _import_problem_unlock_conditions instead.

        Args:
            problem_file: Path to problem markdown file
            course: Course instance (for unlock conditions and chapter resolution)
            problems_dir: Path to problems directory (for prerequisite file lookup)

        Raises:
            ValueError: If specified chapter is not found
        """
        frontmatter, content = MarkdownFrontmatterParser.parse(problem_file)
        MarkdownFrontmatterParser.validate_problem_frontmatter(frontmatter)

        # Resolve chapter if specified
        chapter = None
        if 'chapter' in frontmatter:
            chapter_order = int(frontmatter['chapter'])
            try:
                chapter = Chapter.objects.get(course=course, order=chapter_order)
                logger.info(f"Found chapter {chapter_order} for problem: {frontmatter['title']}")
            except Chapter.DoesNotExist:
                raise ValueError(
                    f"Chapter with order {chapter_order} not found in course '{course.title}'. "
                    f"Problem '{frontmatter['title']}' cannot be imported. "
                    f"Please ensure chapter order {chapter_order} exists in this course."
                )

        # Get or create problem
        problem, created = Problem.objects.get_or_create(
            title=frontmatter['title'],
            defaults={
                'type': frontmatter['type'],
                'content': content.strip(),
                'difficulty': frontmatter['difficulty'],
                'chapter': chapter  # Use resolved chapter (or None if not specified)
            }
        )

        if created:
            self.stats['problems_created'] += 1
            logger.info(f"Created problem: {problem.title} (chapter: {chapter.title if chapter else 'None'})")
        elif self.update_mode:
            self.stats['problems_updated'] += 1
            problem.type = frontmatter['type']
            problem.content = content.strip()
            problem.difficulty = frontmatter['difficulty']
            problem.chapter = chapter  # Update chapter association
            problem.save()
            logger.info(f"Updated problem: {problem.title} (chapter: {chapter.title if chapter else 'None'})")

        # Handle problem-specific data
        if frontmatter['type'] == 'algorithm':
            self._import_algorithm_problem(problem, frontmatter)
        elif frontmatter['type'] == 'choice':
            self._import_choice_problem(problem, frontmatter)

        # Import unlock conditions (if exists)
        if 'unlock_conditions' in frontmatter:
            MarkdownFrontmatterParser.validate_unlock_conditions(
                frontmatter['unlock_conditions']
            )
            self._import_unlock_condition(
                problem,
                frontmatter['unlock_conditions'],
                course,
                problems_dir
            )

    def _import_problem_unlock_conditions(self, problem_file: Path, course: Course, problems_dir: Path) -> None:
        """
        Import unlock conditions for a problem.

        This is Phase 2 of the two-phase import process, called after all problems
        have been created to ensure prerequisites can be found.

        Args:
            problem_file: Path to problem markdown file
            course: Course instance
            problems_dir: Path to problems directory
        """
        frontmatter, _ = MarkdownFrontmatterParser.parse(problem_file)

        # Skip if no unlock conditions
        if 'unlock_conditions' not in frontmatter:
            return

        # Find the problem by title
        title = frontmatter.get('title')
        if not title:
            logger.warning(f"Problem file {problem_file.name} has no title - skipping unlock conditions")
            return

        # Query by title (chapter may be None at this point)
        # Since we're importing within a single course context, title is sufficient
        try:
            problem = Problem.objects.get(title=title)
        except Problem.DoesNotExist:
            logger.warning(f"Problem not found for unlock conditions: {title} - skipping")
            return
        except Problem.MultipleObjectsReturned:
            # If multiple problems have the same title, try to filter by course
            # This handles the case where some problems have chapters set
            problems = Problem.objects.filter(title=title)
            if problems.filter(chapter__course=course).exists():
                problem = problems.filter(chapter__course=course).first()
            else:
                # Fallback: take the first one and log a warning
                problem = problems.first()
                logger.warning(
                    f"Multiple problems found with title '{title}', using first one. "
                    f"Consider using unique titles across problems."
                )

        # Validate and import unlock conditions
        MarkdownFrontmatterParser.validate_unlock_conditions(
            frontmatter['unlock_conditions']
        )
        self._import_unlock_condition(
            problem,
            frontmatter['unlock_conditions'],
            course,
            problems_dir
        )

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

    def _import_unlock_condition(
        self,
        problem: Problem,
        unlock_conditions: Dict[str, Any],
        course: Course,
        problems_dir: Path
    ) -> None:
        """
        Import problem unlock conditions.

        Args:
            problem: Problem instance
            unlock_conditions: Unlock conditions dictionary
            course: Course instance (for finding prerequisite problems)
            problems_dir: Path to problems directory (for prerequisite file lookup)
        """
        from dateutil import parser as date_parser

        cond_type = unlock_conditions.get('type', 'none')

        # If type is 'none', don't create unlock condition
        if cond_type == 'none':
            return

        # Parse unlock_date
        unlock_date = None
        if 'unlock_date' in unlock_conditions:
            unlock_date = date_parser.parse(unlock_conditions['unlock_date'])

        # Get or create unlock condition
        unlock_cond, created = ProblemUnlockCondition.objects.get_or_create(
            problem=problem,
            defaults={
                'unlock_condition_type': cond_type,
                'unlock_date': unlock_date,
                'minimum_percentage': unlock_conditions.get('minimum_percentage')
            }
        )

        if not created and self.update_mode:
            unlock_cond.unlock_condition_type = cond_type
            unlock_cond.unlock_date = unlock_date
            unlock_cond.minimum_percentage = unlock_conditions.get('minimum_percentage')
            unlock_cond.save()
            logger.info(f"Updated unlock condition for: {problem.title}")
        elif created:
            logger.info(f"Created unlock condition for: {problem.title}")

        # Handle prerequisite problems
        if cond_type in ['prerequisite', 'both'] and 'prerequisites' in unlock_conditions:
            self._link_prerequisite_problems(
                unlock_cond,
                unlock_conditions['prerequisites'],
                course,
                problem,  # Pass current problem to prevent self-reference
                problems_dir  # Pass problems directory for file lookup
            )

    def _link_prerequisite_problems(
        self,
        unlock_cond: ProblemUnlockCondition,
        prerequisite_filenames: List[str],
        course: Course,
        current_problem: Problem,
        problems_dir: Path
    ) -> None:
        """
        Link prerequisite problems to unlock condition.

        Args:
            unlock_cond: ProblemUnlockCondition instance
            prerequisite_filenames: List of prerequisite problem filenames
            course: Course instance
            current_problem: Current problem to prevent self-reference
            problems_dir: Path to problems directory (for prerequisite file lookup)
        """
        # Clear old prerequisite relationships
        unlock_cond.prerequisite_problems.clear()

        for filename in prerequisite_filenames:
            # Find the actual file and extract its title from frontmatter
            prereq_file = problems_dir / filename
            if not prereq_file.exists():
                logger.warning(
                    f"  Prerequisite file not found: {filename} - skipping"
                )
                continue

            try:
                # Read frontmatter to get the actual title
                frontmatter, _ = MarkdownFrontmatterParser.parse(prereq_file)
                actual_title = frontmatter.get('title')

                if not actual_title:
                    logger.warning(
                        f"  Prerequisite file {filename} has no title - skipping"
                    )
                    continue

                # Find problem with matching title in the same course
                # Since problems are imported within a course context, we can query:
                # 1. Problems with chapters in this course, OR
                # 2. Problems without chapters that were imported in the same session
                candidate_problems = Problem.objects.filter(
                    title=actual_title,
                    chapter__isnull=False,  # Has a chapter
                    chapter__course=course
                ).exclude(id=current_problem.id)  # Exclude current problem to prevent self-reference

                # If no chaptered problems found, check for standalone problems
                # This handles the case where both the current and prerequisite problems are standalone
                if not candidate_problems.exists():
                    # Get all problems with this title (could be from different courses)
                    title_matches = Problem.objects.filter(title=actual_title).exclude(id=current_problem.id)

                    # Filter to find ones that could belong to this course:
                    # - They have no chapter and were imported in this session
                    # - Or they have a chapter in this course (already covered above)
                    for problem in title_matches:
                        # Check if this could be a problem from the same import session
                        # One heuristic: problems created recently are likely from same import
                        time_diff = (timezone.now() - problem.created_at).total_seconds()
                        if problem.chapter is None and time_diff < 3600:  # Within last hour
                            candidate_problems |= Problem.objects.filter(id=problem.id)
                            break

                if candidate_problems.exists():
                    prereq_problem = candidate_problems.first()
                    unlock_cond.prerequisite_problems.add(prereq_problem)
                    logger.info(f"  Linked prerequisite: {actual_title} (from {filename})")
                else:
                    logger.warning(
                        f"  Prerequisite problem not found: {actual_title} "
                        f"(from file {filename}) - skipping"
                    )
            except Exception as e:
                logger.warning(
                    f"  Error parsing prerequisite file {filename}: {e} - skipping"
                )
