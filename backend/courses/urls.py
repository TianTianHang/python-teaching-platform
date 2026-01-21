# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers  # 导入 nested_routers

from .views import (
    CourseViewSet, ChapterViewSet, DiscussionReplyViewSet, DiscussionThreadViewSet, ProblemViewSet,
    SubmissionViewSet, EnrollmentViewSet, ChapterProgressViewSet, ProblemProgressViewSet, CodeDraftViewSet,
    ExamViewSet, ExamSubmissionViewSet
)

# 1. 创建父路由。这与平常的 DefaultRouter 相同。
parent_router = DefaultRouter()
parent_router.register(r"courses", CourseViewSet)
parent_router.register(r"chapters", ChapterViewSet)
parent_router.register(r"problems", ProblemViewSet)
parent_router.register(r"submissions", SubmissionViewSet, basename="submissions")
parent_router.register(r"enrollments", EnrollmentViewSet, basename="enrollments")
parent_router.register(r"chapter-progress", ChapterProgressViewSet, basename="chapter-progress")
parent_router.register(r"problem-progress", ProblemProgressViewSet, basename="problem-progress")
parent_router.register(r"drafts", CodeDraftViewSet, basename="drafts")
parent_router.register(r'threads', DiscussionThreadViewSet,basename='thread')
parent_router.register(r'replies', DiscussionReplyViewSet, basename='reply')
parent_router.register(r"exams", ExamViewSet, basename="exam")
parent_router.register(r"exam-submissions", ExamSubmissionViewSet, basename="exam-submissions")

#/courses/<pk>/
courses_router = routers.NestedDefaultRouter(
    parent_router, r"courses", lookup="course"
)
#/courses/<pk>/threads
courses_router.register(r'threads', DiscussionThreadViewSet,basename='thread')
#/courses/<pk>/threads/<pk>/
threads_courses_router = routers.NestedDefaultRouter(
    courses_router, r"threads", lookup="thread"
)
#/courses/<pk>/threads/<pk>/replies
threads_courses_router.register(r'replies', DiscussionReplyViewSet, basename='thread-replies')


#/chapters/<pk>/
chapters_router = routers.NestedDefaultRouter(
    parent_router, r"chapters", lookup="chapter"
)
#/chapters/<pk>/threads
chapters_router.register(r'threads', DiscussionThreadViewSet,basename='thread')
#/chapters/<pk>/threads/<pk>/
threads_chapters_router = routers.NestedDefaultRouter(
    chapters_router, r"threads", lookup="thread"
)
#/chapters/<pk>/threads/<pk>/replies
threads_chapters_router.register(r'replies', DiscussionReplyViewSet, basename='thread-replies')





#/courses/<pk>/chapters
courses_router.register(r"chapters", ChapterViewSet, basename="course-chapters")
#/courses/<pk>/chapters/<pk>
chapters_courses_router = routers.NestedDefaultRouter(
    courses_router, r"chapters", lookup="chapter"
)
#/courses/<pk>/chapters/<pk>/problems
chapters_courses_router.register(r"problems", ProblemViewSet, basename="chapter-problems")
#/courses/<pk>/exams
courses_router.register(r"exams", ExamViewSet, basename="course-exams")




#/problems/<pk>
problems_router = routers.NestedDefaultRouter(
    parent_router, r"problems", lookup="problem"
)
    
#/problems/<pk>/threads
problems_router.register(r'threads', DiscussionThreadViewSet,basename='thread')
#/problems/<pk>/threads/<pk>/
threads_problems_router = routers.NestedDefaultRouter(
    problems_router, r"threads", lookup="thread"
)
#/problems/<pk>/threads/<pk>/replies
threads_problems_router.register(r'replies', DiscussionReplyViewSet, basename='thread-replies')

#/problems/<pk>/submissions
problems_router.register(r"submissions",SubmissionViewSet,basename="problem-submissions")
#/problems/<pk>/drafts
problems_router.register(r"drafts", CodeDraftViewSet, basename="problem-drafts")
#/threads/<pk>
threads_router = routers.NestedDefaultRouter(
    parent_router, r"threads", lookup="thread"
)
#/threads/<pk>/replies
threads_router.register(r'replies', DiscussionReplyViewSet, basename='thread-replies')




# 合并所有urlpatterns
urlpatterns = parent_router.urls \
+ courses_router.urls + chapters_router.urls + problems_router.urls \
+ chapters_courses_router.urls  \
+ threads_router.urls + threads_courses_router.urls \
+ threads_problems_router.urls + threads_chapters_router.urls