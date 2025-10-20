from rest_framework import viewsets,permissions
from .models import Course, Chapter
from .serializers import CourseModelSerializer, ChapterSerializer
class CourseViewSet(viewsets.ModelViewSet):
    """
    一个用于查看和编辑 课程 实例的视图集。
    提供了 'list', 'create', 'retrieve', 'update', 'partial_update', 'destroy' 动作。
    """
    queryset = Course.objects.all().order_by('title')
    serializer_class = CourseModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = [filters.SearchFilter, filters.OrderingFilter] # 示例：添加搜索和排序
    # search_fields = ['name', 'description']
    # ordering_fields = ['price', 'created_at']
# ChapterViewSet
class ChapterViewSet(viewsets.ModelViewSet):
    """
    一个用于查看和编辑特定课程下 Chapter 实例的视图集。
    """
    queryset = Chapter.objects.all().order_by('course__title', 'order') # 默认排序
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 如果你需要在章节ViewSet中做额外的过滤，例如只允许某个用户编辑自己的章节，
    # 可以在这里进行，但对于嵌套路由器，通常它已经通过URL参数完成了课程的过滤
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     # self.kwargs 会包含父资源的ID，例如 'course_pk'
    #     if 'course_pk' in self.kwargs:
    #         return queryset.filter(course=self.kwargs['course_pk'])
    #     return queryset