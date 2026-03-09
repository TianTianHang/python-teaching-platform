## 1. Fix ChapterProgressViewSet

- [x] 1.1 在 ChapterProgressViewSet.get_queryset() 添加 select_related("chapter", "chapter__course")

## 2. Fix ProblemProgressViewSet

- [x] 2.1 在 ProblemProgressViewSet.get_queryset() 添加 select_related("problem", "problem__chapter", "problem__chapter__course")

## 3. Verify

- [x] 3.1 运行测试验证修改正确: cd /home/tiantian/project/python-teaching-platform/backend && uv run python manage.py test courses.tests.test_views.ChapterProgressViewSetTestCase courses.tests.test_views.ProblemProgressViewSetTestCase -v 2