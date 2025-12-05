import hashlib
from rest_framework import viewsets, permissions, filters
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
from django_redis import get_redis_connection
from courses.pagination import CustomPageNumberPagination
from .models import Course, Chapter, DiscussionReply, DiscussionThread, Problem, Submission, Enrollment, ChapterProgress, ProblemProgress
from .serializers import CourseModelSerializer, ChapterSerializer, DiscussionReplySerializer, DiscussionThreadSerializer, ProblemSerializer, SubmissionSerializer, EnrollmentSerializer, ChapterProgressSerializer, ProblemProgressSerializer
from .services import CodeExecutorService
from django.db.models import Q

class CourseViewSet(viewsets.ModelViewSet):
    """
    一个用于查看和编辑 课程 实例的视图集。
    提供了 'list', 'create', 'retrieve', 'update', 'partial_update', 'destroy' 动作。
    """
    queryset = Course.objects.all().order_by('title')
    serializer_class = CourseModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter, filters.OrderingFilter] # 示例：添加搜索和排序
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at',"updated_at"]
    
    def _clear_courses_list_cache(self):
        """清除所有以 'courses_list_' 开头的缓存键（用于 Redis）"""
        redis_conn = get_redis_connection("default")
        redis_conn.delete_pattern("courses_list_*")

    def list(self, request, *args, **kwargs):
        # 生成包含查询参数的唯一缓存键
        query_params = request.GET.urlencode()
        cache_key = f"courses_list_{hashlib.md5(query_params.encode()).hexdigest()}"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 600)  # 缓存10分钟
        return response

    def retrieve(self, request, *args, **kwargs):
        course_id = self.kwargs['pk']
        cache_key = f'course_{course_id}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, 600)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self._clear_courses_list_cache()  # 清除所有列表缓存
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # 清除单个课程缓存（如果有）
        course_id = self.kwargs['pk']
        cache.delete(f'course_{course_id}')
        # 清除所有列表缓存
        self._clear_courses_list_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        # ModelViewSet 默认调用 update，但为了保险可显式处理
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        course_id = self.kwargs['pk']
        # 先获取对象（用于后续清理，也可省略）
        response = super().destroy(request, *args, **kwargs)
        # 清除单个缓存
        cache.delete(f'course_{course_id}')
        # 清除所有列表缓存
        self._clear_courses_list_cache()
        return response

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
    filter_backends = [DjangoFilterBackend,filters.SearchFilter, filters.OrderingFilter] # 示例：添加搜索和排序
    search_fields = ['title', 'content']
    ordering_fields = ['title', 'order', 'created_at',"updated_at"]

    def get_queryset(self):
        user = self.request.user
        course_id = self.kwargs.get('course_pk')

        # 构建进度查询集：根据是否限定 course_id 来决定范围
        progress_filter = {'enrollment__user': user}
        chapter_filter = {}

        if course_id is not None:
            progress_filter['chapter__course_id'] = course_id
            chapter_filter['course_id'] = course_id

        progress_qs = ChapterProgress.objects.filter(**progress_filter)

        return Chapter.objects.filter(**chapter_filter).prefetch_related(
            Prefetch('progress_records', queryset=progress_qs, to_attr='user_progress')
        )
    
    def _clear_chapters_list_cache_for_course(self, course_pk):
        """清除该课程下所有章节列表缓存（支持带查询参数的多种缓存）"""
        if course_pk is None:
            return
        redis_conn = get_redis_connection("default")
        pattern = f"chapters_list_course_{course_pk}_*"
        redis_conn.delete_pattern(pattern)

    def list(self, request, *args, **kwargs):
        course_pk = self.kwargs.get('course_pk')
        if course_pk is None:
            # 如果没有 course_pk，可能需要特殊处理或报错 TODO 查询所有章节时的缓存
            return super().list(request, *args, **kwargs)

        # 将查询参数加入缓存键
        query_params = request.GET.urlencode()
        param_hash = hashlib.md5(query_params.encode()).hexdigest() if query_params else 'default'
        cache_key = f'chapters_list_course_{course_pk}_{param_hash}'

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 600)  # 缓存10分钟
        return response

    def retrieve(self, request, *args, **kwargs):
        chapter_id = self.kwargs['pk']
        cache_key = f'chapter_{chapter_id}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, 600)
        return response

    def create(self, request, *args, **kwargs):
        course_pk = self.kwargs.get('course_pk')
        response = super().create(request, *args, **kwargs)
        self._clear_chapters_list_cache_for_course(course_pk)
        return response

    def update(self, request, *args, **kwargs):
        chapter_id = self.kwargs['pk']
        course_pk = self.kwargs.get('course_pk')
        response = super().update(request, *args, **kwargs)
        cache.delete(f'chapter_{chapter_id}')
        self._clear_chapters_list_cache_for_course(course_pk)
        return response

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        chapter_id = self.kwargs['pk']
        course_pk = self.kwargs.get('course_pk')
        response = super().destroy(request, *args, **kwargs)
        cache.delete(f'chapter_{chapter_id}')
        self._clear_chapters_list_cache_for_course(course_pk)
        return response

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
    queryset = Problem.objects.all().order_by("type", "-created_at", "id")
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
    @action(detail=False, methods=['get'], url_path='next')
    def get_next_problem(self, request):
        problem_type = request.query_params.get('type')
        current_id = request.query_params.get('id')
        if not problem_type or not current_id:
            return Response({"error": "Missing 'type' or 'id'"}, status=400)
        try:
            current_id = int(current_id)
        except ValueError:
            return Response({"error": "'id' must be integer"}, status=400)

        # 获取当前题目（验证存在）
        get_object_or_404(Problem, id=current_id, type=problem_type)
        # 获取完整排序后的同类型题目 queryset（带 prefetch）
        same_type_qs = self.get_queryset().filter(type=problem_type)
        # 先取出当前题目的排序字段值
        try:
            current = Problem.objects.only('created_at', 'id').get(id=current_id)
        except Problem.DoesNotExist:
            return Response({"error": "Problem not found"}, status=404)
        next_obj = same_type_qs.filter(
            Q(created_at__lt=current.created_at) |
            (Q(created_at=current.created_at) & Q(id__gt=current.id))
        ).order_by("-created_at", "id").first()
        next_next_obj = same_type_qs.filter(
            Q(created_at__lt=next_obj.created_at) |
            (Q(created_at=next_obj.created_at) & Q(id__gt=next_obj.id))
        ).first()
        has_next = next_next_obj is not None


        response_data = {
            "has_next": has_next,
        }

        if next_obj:
            serializer = self.get_serializer(next_obj)
            response_data["problem"] = serializer.data
        else:
            response_data["problem"] = None
            response_data["message"] = "No next problem."
        return Response(response_data, status=200)  # 始终返回 200
    
    def _clear_global_problems_cache(self):
        """清除全局问题列表的所有缓存"""
        redis_conn = get_redis_connection("default")
        redis_conn.delete_pattern("problems_list_global_*")

    def _clear_chapter_problems_cache(self, chapter_pk):
        """清除指定章节的问题列表缓存"""
        if chapter_pk is not None:
            redis_conn = get_redis_connection("default")
            redis_conn.delete_pattern(f"problems_list_chapter_{chapter_pk}_*")

    def list(self, request, *args, **kwargs):
        chapter_pk = self.kwargs.get('chapter_pk')

        # 生成完整查询参数的哈希
        query_params = request.GET.urlencode()
        param_hash = hashlib.md5(query_params.encode()).hexdigest() if query_params else 'default'

        if chapter_pk is not None:
            cache_key = f'problems_list_chapter_{chapter_pk}_{param_hash}'
        else:
            cache_key = f'problems_list_global_{param_hash}'

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 600)
        return response

    def retrieve(self, request, *args, **kwargs):
        problem_id = self.kwargs['pk']
        cache_key = f'problem_{problem_id}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, 600)
        return response

    def create(self, request, *args, **kwargs):
        chapter_pk = self.kwargs.get('chapter_pk')
        response = super().create(request, *args, **kwargs)

        # 根据上下文清除对应缓存
        if chapter_pk is not None:
            self._clear_chapter_problems_cache(chapter_pk)
        else:
            self._clear_global_problems_cache()

        return response

    def update(self, request, *args, **kwargs):
        problem_id = self.kwargs['pk']
        chapter_pk = self.kwargs.get('chapter_pk')
        response = super().update(request, *args, **kwargs)

        cache.delete(f'problem_{problem_id}')

        if chapter_pk is not None:
            self._clear_chapter_problems_cache(chapter_pk)
        else:
            self._clear_global_problems_cache()

        return response

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        problem_id = self.kwargs['pk']
        chapter_pk = self.kwargs.get('chapter_pk')
        response = super().destroy(request, *args, **kwargs)

        cache.delete(f'problem_{problem_id}')

        if chapter_pk is not None:
            self._clear_chapter_problems_cache(chapter_pk)
        else:
            self._clear_global_problems_cache()

        return response

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']
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
    queryset = ProblemProgress.objects.all().order_by('id')
    serializer_class = ProblemProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    def get_queryset(self):
        """
        只允许用户查看自己的问题进度
        """
        qs = ProblemProgress.objects.filter(enrollment__user=self.request.user)
        status_not = self.request.query_params.get('status_not')
        if status_not:
            qs = qs.exclude(status=status_not)
        return qs

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
    
class DiscussionThreadViewSet(viewsets.ModelViewSet):
    serializer_class = DiscussionThreadSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly] #作者可改，匿名或者其他用户可读
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course','chapter','problem', 'is_pinned', 'is_resolved', 'is_archived']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'last_activity_at', 'reply_count']
    ordering = ['-last_activity_at']
    
    def get_queryset(self):
        queryset = DiscussionThread.objects.all()

        # 获取 URL 中的嵌套参数
        course_pk = self.kwargs.get('course_pk')
        chapter_pk = self.kwargs.get('chapter_pk')
        problem_pk = self.kwargs.get('problem_pk')

        # 用于 select_related 的字段列表
        select_related_fields = ['author']
 
        if course_pk:
            queryset = queryset.filter(course_id=course_pk)
            select_related_fields.append('course')
        if chapter_pk:
            
            queryset = queryset.filter(chapter_id=chapter_pk)
            select_related_fields.append('chapter')
         
        if problem_pk:
            queryset = queryset.filter(problem_id=problem_pk)
            select_related_fields.append('problem')
    

        return queryset.select_related(*select_related_fields)

    
    def perform_create(self, serializer):
        # 如果是嵌套路由创建，自动填充对应外键
        course_pk = self.kwargs.get('course_pk')
        chapter_pk = self.kwargs.get('chapter_pk')
        problem_pk = self.kwargs.get('problem_pk')

        kwargs = {'author': self.request.user}
        if course_pk:
            kwargs['course_id'] = course_pk
        if chapter_pk:
            kwargs['chapter_id'] = chapter_pk
        if problem_pk:
            kwargs['problem_id'] = problem_pk

        serializer.save(**kwargs)
        
class DiscussionReplyViewSet(viewsets.ModelViewSet):
    serializer_class = DiscussionReplySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['thread']
    ordering_fields = ['created_at']
    ordering = ['created_at']  # 按时间正序（从早到晚）

    def get_queryset(self):
        queryset = DiscussionReply.objects.select_related('author').prefetch_related('mentioned_users')
        
        # 如果是通过 /threads/{id}/replies/ 访问，自动过滤 thread
        thread_pk = self.kwargs.get('thread_pk')
        if thread_pk:
            queryset = queryset.filter(thread_id=thread_pk)
        
        return queryset

    def perform_create(self, serializer):
        # 自动从 URL 获取 thread_pk
        thread_pk = self.kwargs.get('thread_pk')
        if thread_pk:
            # 你可以选择是否验证 thread 是否存在
            thread = get_object_or_404(DiscussionThread, pk=thread_pk)
            serializer.save(author=self.request.user, thread=thread)
        else:
            # 如果不是嵌套路由（如直接 POST /replies/），则要求前端传 thread
            # 此时 serializer 必须包含 thread 字段（由 serializer 自己处理）
            serializer.save(author=self.request.user)