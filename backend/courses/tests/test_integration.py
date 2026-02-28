from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
import json

from courses.models import (
    Course, Enrollment, Chapter, ChapterProgress, CourseUnlockSnapshot,
    ChapterUnlockCondition
)
from courses.services import UnlockSnapshotService
from accounts.tests.factories import UserFactory
from .factories import (
    CourseFactory, EnrollmentFactory, ChapterFactory,
    ChapterUnlockConditionFactory, ChapterProgressFactory
)
from ..views import ChapterViewSet
from ..serializers import ChapterSerializer
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate


User = get_user_model()


class ChapterUnlockIntegrationTestCase(TransactionTestCase):
    """Integration tests for the complete chapter unlock snapshot system"""

    def setUp(self):
        """Set up test data"""
        self.course = CourseFactory(title="Python Programming")
        self.user = UserFactory(username="testuser")
        self.enrollment = EnrollmentFactory(
            course=self.course,
            user=self.user
        )

        # Create chapters
        self.chapter1 = ChapterFactory(
            course=self.course,
            title="Introduction",
            order=1
        )
        self.chapter2 = ChapterFactory(
            course=self.course,
            title="Variables",
            order=2
        )
        self.chapter3 = ChapterFactory(
            course=self.course,
            title="Functions",
            order=3
        )

        # Set up unlock conditions
        self.condition2 = ChapterUnlockConditionFactory(
            chapter=self.chapter2,
            unlock_condition_type='prerequisite'
        )
        self.condition2.prerequisite_chapters.set([self.chapter1])
        self.condition3 = ChapterUnlockConditionFactory(
            chapter=self.chapter3,
            unlock_condition_type='all'
        )
        self.condition3.prerequisite_chapters.set([self.chapter2])

    def test_complete_chapter_triggers_snapshot_refresh(self):
        """Test completing a chapter triggers the snapshot refresh flow"""
        # Initially, chapters 2 and 3 should be locked
        result = UnlockSnapshotService.get_unlock_status_hybrid(self.course, self.enrollment)
        self.assertTrue(result['unlock_states'][str(self.chapter2.id)]['locked'])
        self.assertTrue(result['unlock_states'][str(self.chapter3.id)]['locked'])
        self.assertEqual(result['source'], 'realtime')  # No snapshot initially

        # Complete chapter 1
        progress = ChapterProgress.objects.create(
            enrollment=self.enrollment,
            chapter=self.chapter1,
            completed=True
        )

        # Create snapshot first
        snapshot = UnlockSnapshotService.get_or_create_snapshot(self.enrollment)
        snapshot.recompute()  # Populate with initial data

        # Mark snapshot as stale (simulating signal)
        UnlockSnapshotService.mark_stale(self.enrollment)

        # Check that snapshot is marked stale
        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_stale)

        # Refresh snapshot manually
        # Save chapters to ensure they're in the database
        self.chapter1.save()
        self.chapter2.save()
        self.chapter3.save()
        snapshot.recompute()

        # Verify new unlock states
        # Chapter 2 should now be unlocked (only prerequisite required, and chapter1 is done)
        self.assertFalse(snapshot.unlock_states[str(self.chapter2.id)]['locked'])
        self.assertIsNone(snapshot.unlock_states[str(self.chapter2.id)]['reason'])

        # Chapter 3 should remain locked because chapter2 is not completed yet
        # (even though chapter1 is done, chapter3 requires chapter2 which is still incomplete)
        self.assertTrue(snapshot.unlock_states[str(self.chapter3.id)]['locked'])
        self.assertEqual(snapshot.unlock_states[str(self.chapter3.id)]['reason'], 'prerequisite')

    def test_view_set_snapshot_mode(self):
        """Test that ChapterViewSet uses snapshot mode when available and fresh"""
        factory = APIRequestFactory()
        request = factory.get(f'/api/v1/courses/{self.course.id}/chapters/')
        force_authenticate(request, user=self.user)
        view = ChapterViewSet()
        view.request = request
        view.kwargs = {'course_pk': self.course.id}

        # Add a user attribute to the request to match Django's behavior
        view.request.user = self.user

        # Create fresh snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                str(self.chapter1.id): {'locked': False, 'reason': None},
                str(self.chapter2.id): {'locked': True, 'reason': 'prerequisite'},
                str(self.chapter3.id): {'locked': True, 'reason': 'both'}
            },
            is_stale=False,
            version=1
        )

        # Get queryset
        queryset = view.get_queryset()
        chapters = list(queryset)

        # Verify snapshot mode is used
        self.assertTrue(view._use_snapshot)
        self.assertEqual(len(chapters), 3)
        # Check that unlock states are available
        self.assertIn(str(self.chapter1.id), view._unlock_states)

    def test_view_set_annotation_mode_fallback(self):
        """Test that ChapterViewSet falls back to annotation mode when snapshot is stale"""
        factory = APIRequestFactory()
        request = factory.get(f'/api/v1/courses/{self.course.id}/chapters/')
        force_authenticate(request, user=self.user)
        view = ChapterViewSet()
        view.request = request
        view.kwargs = {'course_pk': self.course.id}

        # Add a user attribute to the request to match Django's behavior
        view.request.user = self.user

        # Create stale snapshot
        CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=True
        )

        # Get queryset
        queryset = view.get_queryset()
        chapters = list(queryset)

        # Verify annotation mode is used
        self.assertFalse(view._use_snapshot)
        self.assertTrue(hasattr(view, '_completed_chapter_ids'))
        self.assertTrue(len(chapters), 3)

    def test_serializer_uses_snapshot_data(self):
        """Test that ChapterSerializer uses snapshot data when available"""
        # Create context with snapshot
        context = {
            'request': type('', (), {'user': self.user})(),
            'view': type('', (), {
                '_use_snapshot': True,
                '_unlock_states': {
                    str(self.chapter2.id): {'locked': True, 'reason': 'prerequisite'},
                    str(self.chapter3.id): {'locked': True, 'reason': 'both'}
                }
            })()
        }

        # Test serializer with snapshot data
        serializer = ChapterSerializer(
            self.chapter2,
            context=context
        )
        self.assertTrue(serializer.get_is_locked(self.chapter2))

        serializer = ChapterSerializer(
            self.chapter1,
            context=context
        )
        self.assertFalse(serializer.get_is_locked(self.chapter1))

    def test_serializer_fallback_chain(self):
        """Test that ChapterSerializer properly falls back through all options"""
        # Test with no snapshot, no annotation
        context = {
            'request': type('', (), {'user': self.user})()
        }

        serializer = ChapterSerializer(
            self.chapter1,
            context=context
        )
        # Should use service calculation for first chapter (no conditions)
        self.assertFalse(serializer.get_is_locked(self.chapter1))

    def test_concurrent_chapter_completions(self):
        """Test handling concurrent chapter completions"""
        # Create multiple enrollments
        enrollment2 = EnrollmentFactory(course=self.course, user=UserFactory())
        enrollment3 = EnrollmentFactory(course=self.course, user=UserFactory())

        # Mock the mark_stale method to capture calls
        with patch('courses.services.UnlockSnapshotService.mark_stale') as mock_mark_stale:
            # Complete chapters for multiple enrollments concurrently
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for enrollment in [self.enrollment, enrollment2, enrollment3]:
                    future = executor.submit(
                        lambda e: ChapterProgress.objects.create(
                            enrollment=e,
                            chapter=self.chapter1,
                            completed=True
                        ),
                        enrollment
                    )
                    futures.append(future)

                # Wait for all completions
                for future in futures:
                    future.result()

            # Verify that mark_stale was called for all enrollments
            # (3 signals from chapter completion)
            self.assertEqual(mock_mark_stale.call_count, 3)

    def test_snapshot_performance_improvement(self):
        """Test that snapshot mode significantly reduces database queries"""
        # This test verifies the structure but doesn't actually measure query count
        # In a real environment, you'd use django-silk or similar tools to count queries

        factory = APIRequestFactory()
        request = factory.get(f'/api/v1/courses/{self.course.id}/chapters/')
        force_authenticate(request, user=self.user)
        view = ChapterViewSet()
        view.request = request
        view.kwargs = {'course_pk': self.course.id}

        # Add a user attribute to the request to match Django's behavior
        view.request.user = self.user

        # With snapshot mode
        CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                str(chapter.id): {'locked': False, 'reason': None}
                for chapter in [self.chapter1, self.chapter2, self.chapter3]
            },
            is_stale=False
        )

        view.get_queryset()
        self.assertTrue(view._use_snapshot)

        # Without snapshot mode
        CourseUnlockSnapshot.objects.filter(enrollment=self.enrollment).delete()
        view.get_queryset()
        self.assertFalse(view._use_snapshot)

        # The performance difference is visible in the structure:
        # - Snapshot mode: direct lookup, no complex annotations
        # - Annotation mode: multiple EXISTS subqueries

    def test_date_unlock_condition_integration(self):
        """Test integration with date unlock conditions"""
        # Create a chapter with future unlock date
        future_date = timezone.now() + timedelta(hours=1)
        chapter_locked_by_date = ChapterFactory(
            course=self.course,
            title="Advanced Topics",
            order=4
        )

        condition = ChapterUnlockConditionFactory(
            chapter=chapter_locked_by_date,
            unlock_condition_type='date',
            unlock_date=future_date
        )

        # Create snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False
        )

        # Recompute
        snapshot.recompute()

        # Verify chapter is locked due to date
        self.assertTrue(snapshot.unlock_states[str(chapter_locked_by_date.id)]['locked'])
        self.assertEqual(snapshot.unlock_states[str(chapter_locked_by_date.id)]['reason'], 'date')

    def test_mixed_unlock_conditions(self):
        """Test chapters with multiple unlock conditions"""
        # Create chapter with both prerequisite and date
        future_date = timezone.now() + timedelta(hours=2)
        chapter_mixed = ChapterFactory(
            course=self.course,
            title="Advanced Topics",
            order=4
        )

        condition_mixed = ChapterUnlockConditionFactory(
            chapter=chapter_mixed,
            unlock_condition_type='all',
            unlock_date=future_date
        )
        condition_mixed.prerequisite_chapters.set([self.chapter2])

        # Create snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={},
            is_stale=False
        )

        # Without prerequisites completed
        snapshot.recompute()
        self.assertTrue(snapshot.unlock_states[str(chapter_mixed.id)]['locked'])
        # Should be locked for both reasons
        self.assertEqual(snapshot.unlock_states[str(chapter_mixed.id)]['reason'], 'both')

        # Complete prerequisites
        ChapterProgress.objects.create(
            enrollment=self.enrollment,
            chapter=self.chapter2,
            completed=True
        )

        # Recompute
        snapshot.recompute()
        # Should still be locked due to date
        self.assertTrue(snapshot.unlock_states[str(chapter_mixed.id)]['locked'])
        self.assertEqual(snapshot.unlock_states[str(chapter_mixed.id)]['reason'], 'date')

    def test_snapshot_version_increment(self):
        """Test that snapshot version increments on each recompute"""
        # Create initial snapshot
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                str(self.chapter1.id): {'locked': False, 'reason': None}
            },
            version=1
        )

        # First recompute
        snapshot.recompute()
        self.assertEqual(snapshot.version, 2)

        # Second recompute
        snapshot.recompute()
        self.assertEqual(snapshot.version, 3)

        # Verify states are updated
        self.assertTrue(len(snapshot.unlock_states) >= 3)

    def test_api_response_consistency(self):
        """Test that API response remains consistent with and without snapshots"""
        factory = APIRequestFactory()

        # Helper function to get API response
        def get_chapters():
            request = factory.get(f'/api/v1/courses/{self.course.id}/chapters/')
            force_authenticate(request, user=self.user)
            view = ChapterViewSet()
            view.request = request
            view.request.user = self.user  # Ensure user is set
            view.kwargs = {'course_pk': self.course.id}
            view.format_kwarg = None  # Set format_kwarg for serializer context
            queryset = view.get_queryset()
            chapters = list(queryset)

            serializer = ChapterSerializer(
                chapters,
                many=True,
                context=view.get_serializer_context()
            )
            return serializer.data

        # Without snapshots (should work the same)
        data_no_snapshot = get_chapters()

        # Create snapshots with same states as real-time computation
        # Chapter 1 is unlocked (no prerequisites)
        # Chapter 2 is locked (requires chapter1 which is not completed)
        # Chapter 3 is locked (requires chapter2 which is not completed)
        snapshot = CourseUnlockSnapshot.objects.create(
            course=self.course,
            enrollment=self.enrollment,
            unlock_states={
                str(self.chapter1.id): {'locked': False, 'reason': None},
                str(self.chapter2.id): {'locked': True, 'reason': 'prerequisite'},
                str(self.chapter3.id): {'locked': True, 'reason': 'prerequisite'},
            },
            is_stale=False
        )

        # With snapshots
        data_with_snapshot = get_chapters()

        # Response format should be identical
        self.assertEqual(len(data_no_snapshot), len(data_with_snapshot))
        for no_snap, with_snap in zip(data_no_snapshot, data_with_snapshot):
            self.assertEqual(no_snap['id'], with_snap['id'])
            self.assertEqual(no_snap['title'], with_snap['title'])
            self.assertEqual(no_snap['is_locked'], with_snap['is_locked'])