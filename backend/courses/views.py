from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.conf import settings
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

    def list(self, request, *args, **kwargs):
        # 生成缓存键
        cache_key = 'courses_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # 如果缓存中没有数据，执行原始的list方法
        response = super().list(request, *args, **kwargs)
        # 将数据存入缓存，缓存时间600秒（10分钟）
        cache.set(cache_key, response.data, 600)
        return response

    def retrieve(self, request, *args, **kwargs):
        # 生成基于对象ID的缓存键
        course_id = self.kwargs['pk']
        cache_key = f'course_{course_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # 如果缓存中没有数据，执行原始的retrieve方法
        response = super().retrieve(request, *args, **kwargs)
        # 将数据存入缓存，缓存时间600秒（10分钟）
        cache.set(cache_key, response.data, 600)
        return response

    def update(self, request, *args, **kwargs):
        # 当更新课程时，清除相关的缓存
        course_id = self.kwargs['pk']
        cache.delete(f'course_{course_id}')
        cache.delete('courses_list')  # 清除列表缓存
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # 当创建新课程时，清除列表缓存
        cache.delete('courses_list')
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # 当删除课程时，清除相关的缓存
        course_id = self.kwargs['pk']
        cache.delete(f'course_{course_id}')
        cache.delete('courses_list')  # 清除列表缓存
        return super().destroy(request, *args, **kwargs)

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
        course_id = self.kwargs.get('course_pk')
        user = self.request.user

        # 预取当前用户对该课程所有章节的进度
        progress_qs = ChapterProgress.objects.filter(
            enrollment__user=user,
            chapter__course_id=course_id
        )

        return Chapter.objects.filter(course_id=course_id).prefetch_related(
            Prefetch('progress_records', queryset=progress_qs, to_attr='user_progress')
        )
    
    def list(self, request, *args, **kwargs):
        course_pk = self.kwargs.get('course_pk')
        # 生成缓存键，基于课程ID
        cache_key = f'chapters_list_course_{course_pk}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # 如果缓存中没有数据，执行原始的list方法
        response = super().list(request, *args, **kwargs)
        # 将数据存入缓存，缓存时间600秒（10分钟）
        cache.set(cache_key, response.data, 600)
        return response

    def retrieve(self, request, *args, **kwargs):
        # 生成基于对象ID的缓存键
        chapter_id = self.kwargs['pk']
        cache_key = f'chapter_{chapter_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # 如果缓存中没有数据，执行原始的retrieve方法
        response = super().retrieve(request, *args, **kwargs)
        # 将数据存入缓存，缓存时间600秒（10分钟）
        cache.set(cache_key, response.data, 600)
        return response

    def update(self, request, *args, **kwargs):
        # 当更新章节时，清除相关的缓存
        chapter_id = self.kwargs['pk']
        course_pk = self.kwargs.get('course_pk')
        cache.delete(f'chapter_{chapter_id}')
        cache.delete(f'chapters_list_course_{course_pk}')  # 清除列表缓存
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # 当创建新章节时，清除课程的章节列表缓存
        course_pk = self.kwargs.get('course_pk')
        cache.delete(f'chapters_list_course_{course_pk}')
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # 当删除章节时，清除相关的缓存
        chapter_id = self.kwargs['pk']
        course_pk = self.kwargs.get('course_pk')
        cache.delete(f'chapter_{chapter_id}')
        cache.delete(f'chapters_list_course_{course_pk}')  # 清除列表缓存
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def mark_as_completed(self, request, pk=None, course_pk=None):
        """
        更新章节进度状态。
        接收参数: {"completed": true} 或 {"completed": false}
        - 若 completed=True：标记为已完成（设置 completed_at）
        - 若 completed=False：仅确保进度记录存在，但不完成（completed_at 保持 null）
        """
        chapter = self.get_object()
        user = request.user

        # 获取或创建用户的课程注册记录
        enrollment, _ = Enrollment.objects.get_or_create(
            user=user,
            course=chapter.course
        )

        # 从请求体中读取 completed 参数，默认为 True（保持向后兼容）
        completed = request.data.get('completed', True)
        if not isinstance(completed, bool):
            return Response(
                {"error": "'completed' must be a boolean (true or false)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取或创建章节进度记录
        chapter_progress, created = ChapterProgress.objects.get_or_create(
            enrollment=enrollment,
            chapter=chapter,
            defaults={'completed': completed}
        )

        # 如果已存在，更新 completed 字段
        if not created:
            if completed:
                chapter_progress.completed = completed
                chapter_progress.completed_at = timezone.now()
            chapter_progress.save()

        # 清除章节缓存，因为用户进度可能已更新
        cache.delete(f'chapter_{chapter.id}')
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            cache.delete(f'chapters_list_course_{course_pk}')
        
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
        queryset = super().get_queryset()
    
        # 按章节过滤
        if 'chapter_pk' in self.kwargs:
            queryset = queryset.filter(chapter=self.kwargs['chapter_pk'])
    
        # 获取 type 查询参数
        type_param = self.request.query_params.get("type")

        # 构建 prefetch 列表
        prefetches = []

        # 根据 type 预取对应的问题详情
        if type_param == 'algorithm':
            prefetches.append('algorithm_info')
        elif type_param == 'choice':
            prefetches.append('choice_info')
        else:
            # 未指定 type，预取两种
            prefetches.extend(['algorithm_info', 'choice_info'])

        # 预取当前用户的问题进度（关键！）
        user = self.request.user
        if user.is_authenticated:
            # 只预取当前用户的进度，通过 enrollment 关联
            progress_prefetch = Prefetch(
                'progress_records',
                queryset=ProblemProgress.objects.select_related('enrollment__user')
                                           .filter(enrollment__user=user),
                to_attr='user_progress_list'  # 自定义属性名，避免覆盖默认 related_name
            )
            prefetches.append(progress_prefetch)
        # 如果未登录，不预取进度（后续 get_status 返回默认值）

        return queryset.prefetch_related(*prefetches)

    def list(self, request, *args, **kwargs):
        chapter_pk = self.kwargs.get('chapter_pk')
        problem_type = self.request.query_params.get('type')
        
        # 生成缓存键，根据章节ID和问题类型
        cache_key = f'problems_list_chapter_{chapter_pk}_type_{problem_type or "all"}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # 如果缓存中没有数据，执行原始的list方法
        response = super().list(request, *args, **kwargs)
        # 将数据存入缓存，缓存时间600秒（10分钟）
        cache.set(cache_key, response.data, 600)
        return response

    def retrieve(self, request, *args, **kwargs):
        # 生成基于对象ID的缓存键
        problem_id = self.kwargs['pk']
        cache_key = f'problem_{problem_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # 如果缓存中没有数据，执行原始的retrieve方法
        response = super().retrieve(request, *args, **kwargs)
        # 将数据存入缓存，缓存时间600秒（10分钟）
        cache.set(cache_key, response.data, 600)
        return response

    def update(self, request, *args, **kwargs):
        # 当更新问题时，清除相关的缓存
        problem_id = self.kwargs['pk']
        chapter_pk = self.kwargs.get('chapter_pk')
        problem_type = self.request.query_params.get('type')
        cache.delete(f'problem_{problem_id}')
        cache.delete(f'problems_list_chapter_{chapter_pk}_type_{problem_type or "all"}')  # 清除列表缓存
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # 当创建新问题时，清除相关的列表缓存
        chapter_pk = self.kwargs.get('chapter_pk')
        problem_type = self.request.query_params.get('type')
        cache.delete(f'problems_list_chapter_{chapter_pk}_type_{problem_type or "all"}')
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # 当删除问题时，清除相关的缓存
        problem_id = self.kwargs['pk']
        chapter_pk = self.kwargs.get('chapter_pk')
        problem_type = self.request.query_params.get('type')
        cache.delete(f'problem_{problem_id}')
        cache.delete(f'problems_list_chapter_{chapter_pk}_type_{problem_type or "all"}')  # 清除列表缓存
        return super().destroy(request, *args, **kwargs)

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
        # 获取是否标记为已解决，默认为 True（保持原语义）
        solved = request.data.get('solved', True)
      
        now = timezone.now()
        problem_progress, created = ProblemProgress.objects.get_or_create(
            enrollment=enrollment,
            problem=problem,
            defaults={
                'status': 'solved' if solved else 'in_progress',
                'attempts': 1,
                'last_attempted_at': now,
                'solved_at': now if solved else None,
            }
    )

        if not created:
            # 已存在记录：总是增加尝试次数并更新最后尝试时间
            problem_progress.attempts += 1
            problem_progress.last_attempted_at = now

            if solved:
                problem_progress.status = 'solved'
                problem_progress.solved_at = now
            else:
                print(1111111111111111111111111)
                # 未解决：状态设为 in_progress（避免从 solved 退回去）
                if problem_progress.status != 'solved':
                    problem_progress.status = 'in_progress'
                # 如果已经是 solved，通常不应降级，可根据业务决定是否允许

        problem_progress.save()
        
        # 清除问题缓存，因为用户进度可能已更新
        cache.delete(f'problem_{problem.id}')
        chapter_pk = self.kwargs.get('chapter_pk', problem.chapter.id if problem.chapter else None)
        if chapter_pk:
            cache.delete(f'problems_list_chapter_{chapter_pk}_type_all')
            cache.delete(f'problems_list_chapter_{chapter_pk}_type_{problem.type}')
        
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