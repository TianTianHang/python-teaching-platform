"""
Unit tests for Separated Cache Warming Tasks
"""

import unittest
from unittest.mock import patch, MagicMock, call


class TestWarmChaptersGlobal(unittest.TestCase):
    """Tests for _warm_chapters_global function"""

    @patch("courses.models.Chapter.objects")
    def test_warm_chapters_global_basic(self, mock_chapter_objects):
        """Test basic chapter warming"""
        from common.cache_warming.tasks import _warm_chapters_global

        mock_chapter = MagicMock()
        mock_chapter.pk = 1
        mock_chapter.course_id = 10

        mock_chapter_objects.select_related.return_value.filter.return_value.order_by.return_value.__iter__ = MagicMock(
            return_value=iter([])
        )

        result = _warm_chapters_global(course_limit=10)

        self.assertIsInstance(result, int)


class TestWarmProblemsGlobal(unittest.TestCase):
    """Tests for _warm_problems_global function"""

    @patch("common.utils.cache.set_cache")
    @patch("courses.serializers.ProblemGlobalSerializer")
    @patch("courses.models.Problem.objects")
    def test_warm_problems_global_basic(
        self, mock_problem_objects, mock_serializer, mock_set_cache
    ):
        """Test basic problem warming"""
        from common.cache_warming.tasks import _warm_problems_global

        mock_serializer_instance = MagicMock()
        mock_serializer.return_value = mock_serializer_instance
        mock_serializer_instance.data = [{"id": 1, "title": "Test Problem"}]

        mock_problem_objects.filter.return_value.values_list.return_value.distinct.return_value.__getitem__.return_value = [
            1
        ]

        result = _warm_problems_global(chapter_limit=10, problems_per_chapter=5)
        self.assertIsInstance(result, int)


class TestWarmChapterGlobalByPk(unittest.TestCase):
    """Tests for _warm_chapter_global_by_pk function"""

    @patch("common.utils.cache.set_cache")
    @patch("courses.serializers.ChapterGlobalSerializer")
    @patch("courses.models.Chapter.objects")
    def test_warm_chapter_by_pk_found(
        self, mock_objects, mock_serializer, mock_set_cache
    ):
        """Test warming a specific chapter"""
        from common.cache_warming.tasks import _warm_chapter_global_by_pk

        mock_chapter = MagicMock()
        mock_chapter.pk = 1
        mock_chapter.course_id = 10
        mock_objects.filter.return_value.first.return_value = mock_chapter

        mock_serializer_instance = MagicMock()
        mock_serializer.return_value = mock_serializer_instance
        mock_serializer_instance.data = {"id": 1, "title": "Test Chapter"}

        result = _warm_chapter_global_by_pk(chapter_pk=1, course_pk=10)

        self.assertTrue(result)
        mock_set_cache.assert_called_once()

    @patch("common.utils.cache.set_cache")
    @patch("courses.models.Chapter.objects")
    def test_warm_chapter_by_pk_not_found(self, mock_objects, mock_set_cache):
        """Test warming a non-existent chapter"""
        from common.cache_warming.tasks import _warm_chapter_global_by_pk

        mock_objects.filter.return_value.first.return_value = None

        result = _warm_chapter_global_by_pk(chapter_pk=999, course_pk=10)

        self.assertFalse(result)
        mock_set_cache.assert_not_called()


class TestWarmProblemsGlobalByChapter(unittest.TestCase):
    """Tests for _warm_problems_global_by_chapter function"""

    @patch("common.utils.cache.set_cache")
    @patch("courses.serializers.ProblemGlobalSerializer")
    @patch("courses.models.Problem.objects")
    def test_warm_problems_by_chapter_found(
        self, mock_objects, mock_serializer, mock_set_cache
    ):
        """Test warming problems for a specific chapter"""
        from common.cache_warming.tasks import _warm_problems_global_by_chapter

        mock_problem = MagicMock()
        mock_problem.chapter.course_id = 10
        mock_objects.filter.return_value.order_by.return_value.__getitem__.return_value = [
            mock_problem
        ]

        mock_serializer_instance = MagicMock()
        mock_serializer.return_value = mock_serializer_instance
        mock_serializer_instance.data = [{"id": 1}]

        result = _warm_problems_global_by_chapter(chapter_pk=1, course_pk=10, limit=10)

        self.assertTrue(result)


class TestCeleryTasksExist(unittest.TestCase):
    """Test that Celery tasks are properly defined"""

    def test_warm_separated_global_startup_exists(self):
        """Test startup task exists"""
        from common.cache_warming.tasks import warm_separated_global_startup

        self.assertTrue(callable(warm_separated_global_startup))

    def test_warm_separated_global_scheduled_exists(self):
        """Test scheduled task exists"""
        from common.cache_warming.tasks import warm_separated_global_scheduled

        self.assertTrue(callable(warm_separated_global_scheduled))

    def test_warm_separated_global_on_demand_exists(self):
        """Test on-demand task exists"""
        from common.cache_warming.tasks import warm_separated_global_on_demand

        self.assertTrue(callable(warm_separated_global_on_demand))

    def test_cache_performance_summary_exists(self):
        """Test performance summary task exists"""
        from common.cache_warming.tasks import cache_performance_summary

        self.assertTrue(callable(cache_performance_summary))


class TestHelperFunctionsExist(unittest.TestCase):
    """Test helper functions exist"""

    def test_warming_priority_exists(self):
        from common.cache_warming.tasks import WarmingPriority

        self.assertTrue(hasattr(WarmingPriority, "HIGH"))
        self.assertTrue(hasattr(WarmingPriority, "MEDIUM"))
        self.assertTrue(hasattr(WarmingPriority, "LOW"))

    def test_lock_functions_exist(self):
        from common.cache_warming.tasks import (
            get_warming_lock_key,
            get_warming_stats_key,
            acquire_warming_lock,
            release_warming_lock,
            record_warming_stats,
        )

        self.assertTrue(callable(get_warming_lock_key))
        self.assertTrue(callable(get_warming_stats_key))
        self.assertTrue(callable(acquire_warming_lock))
        self.assertTrue(callable(release_warming_lock))
        self.assertTrue(callable(record_warming_stats))


class TestOnDemandTask(unittest.TestCase):
    """Test on-demand warming task"""

    @patch("common.cache_warming.tasks.release_warming_lock")
    @patch("common.cache_warming.tasks.acquire_warming_lock")
    @patch("common.cache_warming.tasks._warm_chapter_global_by_pk")
    @patch("common.cache_warming.tasks.record_warming_stats")
    def test_on_demand_chapter(
        self, mock_stats, mock_warm_chapter, mock_acquire, mock_release
    ):
        """Test on-demand warming for ChapterViewSet"""
        from common.cache_warming.tasks import warm_separated_global_on_demand

        mock_acquire.return_value = True
        mock_warm_chapter.return_value = True

        result = warm_separated_global_on_demand(
            cache_key="test:key",
            view_name="ChapterViewSet",
            pk=1,
            parent_pks={"course_pk": 10},
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["warmed"])
        mock_warm_chapter.assert_called_once_with(1, 10)

    @patch("common.cache_warming.tasks.release_warming_lock")
    @patch("common.cache_warming.tasks.acquire_warming_lock")
    @patch("common.cache_warming.tasks._warm_problems_global_by_chapter")
    @patch("common.cache_warming.tasks.record_warming_stats")
    def test_on_demand_problem(
        self, mock_stats, mock_warm_problems, mock_acquire, mock_release
    ):
        """Test on-demand warming for ProblemViewSet"""
        from common.cache_warming.tasks import warm_separated_global_on_demand

        mock_acquire.return_value = True
        mock_warm_problems.return_value = True

        result = warm_separated_global_on_demand(
            cache_key="test:key",
            view_name="ProblemViewSet",
            pk=1,
            parent_pks={"chapter_pk": 5, "course_pk": 10},
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["warmed"])


if __name__ == "__main__":
    unittest.main()
