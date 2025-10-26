# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers  # 导入 nested_routers

from .views import CourseViewSet, ChapterViewSet, ProblemViewSet, SubmissionViewSet, EnrollmentViewSet, ChapterProgressViewSet, ProblemProgressViewSet

# 1. 创建父路由。这与平常的 DefaultRouter 相同。
parent_router = DefaultRouter()
parent_router.register(r"courses", CourseViewSet)
parent_router.register(r"problems", ProblemViewSet)
parent_router.register(r"submissions", SubmissionViewSet, basename="submissions")
parent_router.register(r"enrollments", EnrollmentViewSet, basename="enrollments")
parent_router.register(r"chapter-progress", ChapterProgressViewSet, basename="chapter-progress")
parent_router.register(r"problem-progress", ProblemProgressViewSet, basename="problem-progress")

# 2. 创建嵌套路由。
#    第一个参数是父路由器实例。
#    第二个参数是父资源的 URL 前缀 (r'courses'，与父路由器注册的相匹配)。
#    第三个参数 'lookup='course'' 至关重要，它告诉嵌套路由器：
#       - 在 URL 中查找的参数名是 `course_pk` (路由会自动添加 `_pk` 后缀)。
#       - 这个参数对应的是 `Chapter` 模型中的 `course` 外键字段。
chapters_router = routers.NestedDefaultRouter(
    parent_router, r"courses", lookup="course"
)
submissions_router = routers.NestedDefaultRouter(
    parent_router, r"problems", lookup="problem"
)
# 3. 在嵌套路由器中注册子资源。
#    - r'chapters' 是子资源的 URL 段。
#    - ChapterViewSet 是处理这些子资源的 ViewSet。
#    - basename='course-chapters' 是为了生成唯一的 URL 命名空间，在逆向解析 URL 时有用。
chapters_router.register(r"chapters", ChapterViewSet, basename="course-chapters")
submissions_router.register(r"submissions",SubmissionViewSet,basename="problem-submissions")
problems_router = routers.NestedDefaultRouter(
    chapters_router, r"chapters", lookup="chapter"
)
problems_router.register(r"problems", ProblemViewSet, basename="chapter-problems")

# 添加章节标记为完成的路由
chapter_completion_router = routers.NestedDefaultRouter(
    chapters_router, r"chapters", lookup="chapter"
)
chapter_completion_router.register(r"mark-as-completed", ChapterViewSet, basename="chapter-mark-as-completed")

# 合并所有urlpatterns
urlpatterns = parent_router.urls + chapters_router.urls + problems_router.urls + submissions_router.urls + chapter_completion_router.urls