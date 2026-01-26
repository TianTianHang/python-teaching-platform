"""
Shared fixtures and utilities for courses app tests.

This module provides common test setup and helper functions
that can be used across multiple test modules.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.tests.conftest import AccountsTestCase

from .factories import (
    CourseFactory,
    ChapterFactory,
    ProblemFactory,
    EnrollmentFactory,
    DiscussionThreadFactory,
)
from accounts.tests.factories import UserFactory


class CoursesTestCase(TestCase):
    """
    Base test case class for courses app tests.

    Provides common setup and utility methods for testing
    courses functionality.
    """

    def setUp(self):
        """Set up common test fixtures."""
        self.client = APIClient()

    def create_course_structure(self, chapter_count=1, problems_per_chapter=1):
        """
        Create a complete course structure with chapters and problems.

        Args:
            chapter_count: Number of chapters to create
            problems_per_chapter: Number of problems per chapter

        Returns:
            Course instance with the created structure
        """
        course = CourseFactory()
        for i in range(chapter_count):
            chapter = ChapterFactory(course=course, order=i)
            for _ in range(problems_per_chapter):
                ProblemFactory(chapter=chapter)
        return course

    def create_enrolled_user(self, course=None, user=None):
        """
        Create an enrollment for a user in a course.

        Args:
            course: Optional Course instance. If None, creates a new course.
            user: Optional User instance. If None, creates a new user.

        Returns:
            Tuple of (User, Enrollment)
        """
        if course is None:
            course = CourseFactory()
        if user is None:
            user = UserFactory()
        enrollment = EnrollmentFactory(user=user, course=course)
        return user, enrollment

    def create_discussion_thread(self, course, author=None, **kwargs):
        """
        Create a discussion thread for a course.

        Args:
            course: Course instance
            author: Optional User instance. If None, creates a new user.
            **kwargs: Additional arguments for DiscussionThreadFactory

        Returns:
            DiscussionThread instance
        """
        if author is None:
            author = UserFactory()
        return DiscussionThreadFactory(course=course, author=author, **kwargs)

    def create_authenticated_client(self, user=None):
        """
        Create an authenticated API client.

        Args:
            user: Optional User instance. If None, creates a new user.

        Returns:
            Tuple of (APIClient, User) with the client authenticated as the user.
        """
        if user is None:
            user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        return client, user
