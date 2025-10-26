from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Chapter, Problem, Submission, Enrollment, ChapterProgress, ProblemProgress
from .serializers import CourseModelSerializer, ChapterSerializer, ProblemSerializer, SubmissionSerializer, EnrollmentSerializer, ChapterProgressSerializer, ProblemProgressSerializer
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

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """
        用户注册课程
        """
        course = self.get_object()
        user = request.user
        
        # 检查用户是否已经注册了该课程
        enrollment, created = Enrollment.objects.get_or_create(
            user=user,
            course=course
        )
        
        if not created:
            return Response(
                {'detail': '您已经注册了该课程'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
    
    @action(detail=True, methods=['post'])
    def mark_as_completed(self, request, pk=None, course_pk=None):
        """
        标记章节为已完成
        """
        chapter = self.get_object()
        user = request.user
        
        # 获取或创建用户的课程注册记录
        enrollment, _ = Enrollment.objects.get_or_create(
            user=user,
            course=chapter.course
        )
        
        # 更新或创建章节进度记录
        chapter_progress, created = ChapterProgress.objects.get_or_create(
            enrollment=enrollment,
            chapter=chapter,
            defaults={'completed': True}
        )
        
        if not created:
            chapter_progress.completed = True
            chapter_progress.save()
        
        serializer = ChapterProgressSerializer(chapter_progress)
        return Response(serializer.data, status=status.HTTP_200_OK)

#ProblemViewset
class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all().order_by("type").order_by("-created_at")
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']
    def get_queryset(self):
        queryset= super().get_queryset()
        type = self.request.query_params.get("type")
        if 'chapter_pk' in self.kwargs:
            queryset =queryset.filter(chapter=self.kwargs['chapter_pk'])
        if type =='algorithm':
            return queryset.prefetch_related('algorithm_info')
        elif type == 'choice':
            return queryset.prefetch_related('choice_info')
        return queryset.prefetch_related('algorithm_info')

    @action(detail=True, methods=['post'])
    def mark_as_solved(self, request, pk=None):
        """
        标记问题为已解决
        """
        problem = self.get_object()
        user = request.user
        
        # 获取问题所属的章节和课程
        chapter = problem.chapter
        course = chapter.course if chapter else None
        
        if not course:
            return Response(
                {'detail': '问题未关联到课程'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取或创建用户的课程注册记录
        enrollment, _ = Enrollment.objects.get_or_create(
            user=user,
            course=course
        )
        
        # 更新或创建问题进度记录
        problem_progress, created = ProblemProgress.objects.get_or_create(
            enrollment=enrollment,
            problem=problem,
            defaults={
                'status': 'solved',
                'attempts': 1,
            }
        )
        
        if not created:
            problem_progress.status = 'solved'
            problem_progress.attempts = problem_progress.attempts + 1
            problem_progress.save()
        
        serializer = ProblemProgressSerializer(problem_progress)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    提交记录视图集，用于处理代码提交和执行
    """
    queryset = Submission.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissionSerializer

    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        problem_pk = self.kwargs.get('problem_pk')
        if problem_pk is not None:
            # 只返回属于该 problem 的 submissions
            queryset =  queryset.filter(
                problem_id=problem_pk,
                problem__type="algorithm"
                )
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
            
            # 如果提交成功，更新问题进度
            if submission.status == 'accepted':
                # 获取或创建用户的课程注册记录
                chapter = problem.chapter
                course = chapter.course if chapter else None
                
                if course:
                    enrollment, _ = Enrollment.objects.get_or_create(
                        user=request.user,
                        course=course
                    )
                    
                    # 更新或创建问题进度记录
                    problem_progress, created = ProblemProgress.objects.get_or_create(
                        enrollment=enrollment,
                        problem=problem,
                        defaults={
                            'status': 'solved',
                            'attempts': 1,
                            'best_submission': submission
                        }
                    )
                    
                    if not created:
                        problem_progress.status = 'solved'
                        problem_progress.attempts = problem_progress.attempts + 1
                        # 如果是更好的提交（通过且执行时间更短），则更新最佳提交
                        if (not problem_progress.best_submission or 
                            submission.execution_time < problem_progress.best_submission.execution_time):
                            problem_progress.best_submission = submission
                        problem_progress.save()
            
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

class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    课程参与视图集
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        只允许用户查看自己的课程参与记录
        """
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        创建时自动设置用户为当前登录用户
        """
        serializer.save(user=self.request.user)

class ChapterProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    章节进度视图集（只读）
    """
    queryset = ChapterProgress.objects.all()
    serializer_class = ChapterProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        只允许用户查看自己的章节进度
        """
        return self.queryset.filter(enrollment__user=self.request.user)

class ProblemProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    问题进度视图集（只读）
    """
    queryset = ProblemProgress.objects.all()
    serializer_class = ProblemProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        只允许用户查看自己的问题进度
        """
        return self.queryset.filter(enrollment__user=self.request.user)