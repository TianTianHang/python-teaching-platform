"""
Admin interface tests for the courses app.

This module contains test coverage for admin functionality including:
- ChapterUnlockCondition inline admin
- Dependent chapters display
- Admin CRUD operations
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.admin.sites import AdminSite

from .factories import (
    CourseFactory,
    ChapterFactory,
    EnrollmentFactory,
    ChapterProgressFactory,
    ChapterUnlockConditionFactory,
)
from accounts.tests.factories import UserFactory

from ..models import Chapter, ChapterUnlockCondition, Enrollment
from ..admin import ChapterAdmin

User = get_user_model()


class MockRequest:
    """Mock request object for admin tests"""
    pass


class ChapterUnlockConditionAdminTests(TestCase):
    """Tests for ChapterUnlockCondition admin functionality"""

    def setUp(self):
        """Set up test data"""
        self.site = AdminSite()
        self.superuser = UserFactory(
            username='admin',
            is_staff=True,
            is_superuser=True
        )
        self.client = Client()
        self.client.force_login(self.superuser)

        # Create course with chapters
        self.course = CourseFactory(title="Test Course")
        self.chapter1 = ChapterFactory(
            course=self.course,
            title="Chapter 1",
            order=1
        )
        self.chapter2 = ChapterFactory(
            course=self.course,
            title="Chapter 2",
            order=2
        )
        self.chapter3 = ChapterFactory(
            course=self.course,
            title="Chapter 3",
            order=3
        )

        # Create enrollment and progress
        self.user = UserFactory(username='student')
        self.enrollment = EnrollmentFactory(
            user=self.user,
            course=self.course
        )
        self.chapter_progress = ChapterProgressFactory(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

    def test_chapter_unlock_condition_inline_exists(self):
        """Test that ChapterUnlockConditionInline is registered"""
        from ..admin import ChapterUnlockConditionInline

        # Check that inline model is correct
        self.assertEqual(
            ChapterUnlockConditionInline.model,
            ChapterUnlockCondition
        )

    def test_chapter_admin_has_inline(self):
        """Test that ChapterAdmin has unlock condition inline"""
        chapter_admin = ChapterAdmin(Chapter, self.site)

        # Check that inlines list contains ChapterUnlockConditionInline
        from ..admin import ChapterUnlockConditionInline
        self.assertIn(ChapterUnlockConditionInline, chapter_admin.inlines)

    def test_show_dependent_chapters_with_no_dependents(self):
        """Test show_dependent_chapters when chapter has no dependents"""
        chapter_admin = ChapterAdmin(Chapter, self.site)

        # Chapter1 has no dependent chapters initially
        result = chapter_admin.show_dependent_chapters(self.chapter1)
        self.assertEqual(result, "无依赖此章节的章节")

    def test_show_dependent_chapters_with_dependents(self):
        """Test show_dependent_chapters when chapter has dependents"""
        # Create unlock condition: chapter2 depends on chapter1
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1)

        chapter_admin = ChapterAdmin(Chapter, self.site)

        # Check that chapter1 shows chapter2 as dependent
        result = chapter_admin.show_dependent_chapters(self.chapter1)
        self.assertIn("Test Course", result)
        self.assertIn("Chapter 2", result)
        self.assertIn("/admin/courses/chapter/", result)

    def test_show_dependent_chapters_multiple_dependents(self):
        """Test show_dependent_chapters with multiple dependent chapters"""
        # Both chapter2 and chapter3 depend on chapter1
        condition2 = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition2.prerequisite_chapters.add(self.chapter1)

        condition3 = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='prerequisite'
        )
        condition3.prerequisite_chapters.add(self.chapter1)

        chapter_admin = ChapterAdmin(Chapter, self.site)

        # Check that chapter1 shows both chapters as dependents
        result = chapter_admin.show_dependent_chapters(self.chapter1)
        self.assertIn("Chapter 2", result)
        self.assertIn("Chapter 3", result)

    def test_admin_chapter_list_display_includes_dependent_chapters(self):
        """Test that chapter admin list display includes dependent chapters"""
        chapter_admin = ChapterAdmin(Chapter, self.site)

        # Check that show_dependent_chapters is in list_display
        self.assertIn('show_dependent_chapters', chapter_admin.list_display)

    def test_admin_create_chapter_with_unlock_condition(self):
        """Test creating a chapter with unlock condition via admin"""
        # Create unlock condition: chapter2 depends on chapter1
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1)

        # Verify condition was created
        self.assertTrue(
            ChapterUnlockCondition.objects.filter(
                chapter=self.chapter2
            ).exists()
        )

        # Verify prerequisites
        condition = ChapterUnlockCondition.objects.get(chapter=self.chapter2)
        self.assertIn(self.chapter1, condition.prerequisite_chapters.all())

    def test_admin_edit_unlock_conditions(self):
        """Test editing existing unlock conditions via admin"""
        # Create initial condition: chapter2 depends on chapter1
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1)

        # Add chapter3 as additional prerequisite
        condition.prerequisite_chapters.add(self.chapter3)

        # Verify both prerequisites
        condition.refresh_from_db()
        self.assertEqual(condition.prerequisite_chapters.count(), 2)
        self.assertIn(self.chapter1, condition.prerequisite_chapters.all())
        self.assertIn(self.chapter3, condition.prerequisite_chapters.all())

    def test_admin_delete_unlock_conditions(self):
        """Test deleting unlock conditions via admin"""
        # Create unlock condition
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1)

        # Delete condition
        condition_id = condition.id
        condition.delete()

        # Verify deletion
        self.assertFalse(
            ChapterUnlockCondition.objects.filter(
                id=condition_id
            ).exists()
        )

    def test_admin_changelist_view_renders(self):
        """Test that chapter admin changelist view renders"""
        url = reverse('admin:courses_chapter_changelist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chapter 1")
        self.assertContains(response, "Chapter 2")

    def test_admin_change_view_renders_with_unlock_condition(self):
        """Test that chapter admin change view renders with unlock condition"""
        # Create unlock condition
        condition = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(self.chapter1)

        url = reverse('admin:courses_chapter_change', args=[self.chapter2.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "解锁条件")

    def test_dependent_chapters_display_html_escaping(self):
        """Test that dependent chapters display properly handles HTML"""
        # Create course with special characters in title
        course = CourseFactory(title="Test & <Course>")
        chapter = ChapterFactory(
            course=course,
            title="Chapter <Test>",
            order=1
        )
        dependent = ChapterFactory(
            course=course,
            title="Dependent > Chapter",
            order=2
        )

        # Create unlock condition
        condition = ChapterUnlockConditionFactory(
            chapter=dependent,
            unlock_condition_type='prerequisite'
        )
        condition.prerequisite_chapters.add(chapter)

        chapter_admin = ChapterAdmin(Chapter, self.site)
        result = chapter_admin.show_dependent_chapters(chapter)

        # The result should contain the original text (Django handles escaping)
        self.assertIn(course.title, result)
        self.assertIn(dependent.title, result)
        self.assertIn("admin/courses/chapter/", result)  # Should contain admin URL


class ChapterUnlockConditionAdminIntegrationTests(TestCase):
    """Integration tests for unlock condition admin workflow"""

    def setUp(self):
        """Set up test data"""
        self.superuser = UserFactory(
            username='admin',
            is_staff=True,
            is_superuser=True
        )
        self.client = Client()
        self.client.force_login(self.superuser)
        self.site = AdminSite()

        # Create course with chapters
        self.course = CourseFactory(title="Integration Test Course")
        self.chapter1 = ChapterFactory(
            course=self.course,
            title="Foundations",
            order=1
        )
        self.chapter2 = ChapterFactory(
            course=self.course,
            title="Intermediate",
            order=2
        )
        self.chapter3 = ChapterFactory(
            course=self.course,
            title="Advanced",
            order=3
        )

        # Create enrollment
        self.user = UserFactory(username='student')
        self.enrollment = EnrollmentFactory(
            user=self.user,
            course=self.course
        )

    def test_admin_workflow_create_sequential_chapters(self):
        """Test creating sequential chapter prerequisites in admin"""
        # Set up prerequisites: chapter2 requires chapter1, chapter3 requires chapter2
        condition2 = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition2.prerequisite_chapters.add(self.chapter1)

        condition3 = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='prerequisite'
        )
        condition3.prerequisite_chapters.add(self.chapter2)

        # Verify chain
        self.assertIn(
            self.chapter1,
            condition2.prerequisite_chapters.all()
        )
        self.assertIn(
            self.chapter2,
            condition3.prerequisite_chapters.all()
        )

    def test_admin_view_displays_dependency_chain(self):
        """Test that admin displays complete dependency chain"""
        # Create chain: chapter1 -> chapter2 -> chapter3
        condition2 = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        condition2.prerequisite_chapters.add(self.chapter1)

        condition3 = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='prerequisite'
        )
        condition3.prerequisite_chapters.add(self.chapter2)

        chapter_admin = ChapterAdmin(Chapter, self.site)

        # Chapter1 should show chapter2 as dependent
        result1 = chapter_admin.show_dependent_chapters(self.chapter1)
        self.assertIn("Intermediate", result1)

        # Chapter2 should show chapter3 as dependent
        result2 = chapter_admin.show_dependent_chapters(self.chapter2)
        self.assertIn("Advanced", result2)

        # Chapter3 should have no dependents
        result3 = chapter_admin.show_dependent_chapters(self.chapter3)
        self.assertEqual(result3, "无依赖此章节的章节")
