from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Course, Chapter, Problem, Submission
from .serializers import CourseModelSerializer, ChapterSerializer, ProblemSerializer, SubmissionSerializer
from .services import CodeExecutorService


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
    def get_queryset(self):
         queryset = super().get_queryset()
         # self.kwargs 会包含父资源的ID，例如 'course_pk'
         if 'course_pk' in self.kwargs:
             return queryset.filter(course=self.kwargs['course_pk'])
         return 
    
#ProblemViewset
class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all().order_by("created_at")
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backend = ["type"]
    def get_queryset(self):
        queryset= super().get_queryset()
        type = self.request.query_params.get("type")
        if 'chapter_pk' in self.kwargs:
            queryset =queryset.filter(chapter=self.kwargs['chapter_pk'])
        if type =='algorithm':
            return queryset.prefetch_related('algorithm_info')
        return queryset.prefetch_related('algorithm_info')


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    提交记录视图集，用于处理代码提交和执行
    """
    queryset = Submission.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissionSerializer
   
   
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 可以根据用户权限进行过滤
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset.order_by('-created_at')
    #post
    def create(self, request, *args, **kwargs):
        """
        创建新的提交记录。
        - 如果提供了 problem_id：作为算法题提交，运行所有测试用例。
        - 如果未提供 problem_id：作为自由运行（Run Code），仅执行代码并返回 stdout/stderr。
        """
        problem_id = request.data.get('problem_id')
        code = request.data.get('code')
        language = request.data.get('language', 'python')

        if not code:
            return Response(
                {'error': 'Code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 情况 1：自由运行（无 problem_id）
        if not problem_id:
            try:
                executor = CodeExecutorService()
                result = executor.run_freely(code=code, language=language)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {'error': f'Error executing code: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # 情况 2：作为算法题提交（有 problem_id）
        problem = get_object_or_404(Problem, id=problem_id)
        if problem.type != 'algorithm':
            return Response(
                {'error': 'Only algorithm problems allow code submission'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            executor = CodeExecutorService()
            submission = executor.run_all_test_cases(
                user=request.user,
                problem=problem,
                code=code,
                language=language
            )
            serializer = self.get_serializer(submission)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Error executing code: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        """
        获取特定提交的结果
        """
        submission = self.get_object()
        serializer = self.get_serializer(submission)
        return Response(serializer.data)