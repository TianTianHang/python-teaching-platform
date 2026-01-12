import logging
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from common.mixins.cache_mixin import CacheListMixin, CacheRetrieveMixin, InvalidateCacheMixin
from common.decorators.logging_decorators import audit_log, log_api_call
from .permissions import IsAuthorOrReadOnly
from .models import Course, Chapter, DiscussionReply, DiscussionThread, Problem, Submission, Enrollment, ChapterProgress, ProblemProgress, CodeDraft
from .serializers import CourseModelSerializer, ChapterSerializer, DiscussionReplySerializer, DiscussionThreadSerializer, ProblemSerializer, SubmissionSerializer, EnrollmentSerializer, ChapterProgressSerializer, ProblemProgressSerializer, CodeDraftSerializer
from .services import CodeExecutorService
from django.db.models import Q

logger = logging.getLogger(__name__)

class CourseViewSet(CacheListMixin,
    CacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet):
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
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    @audit_log('course_enrollment')
    def enroll(self, request, pk=None):
        """
        用户注册课程
        """
        logger.info(f"User attempting to enroll in course {pk}", extra={
            'user_id': request.user.id,
            'course_id': pk
        })

        course = self.get_object()
        user = request.user

        # 检查用户是否已经注册了该课程
        enrollment, created = Enrollment.objects.get_or_create(
            user=user,
            course=course
        )

        if not created:
            logger.warning(f"Duplicate enrollment attempt", extra={
                'user_id': user.id,
                'course_id': pk
            })
            return Response(
                {'detail': '您已经注册了该课程'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EnrollmentSerializer(enrollment)

        logger.info(f"Course enrollment successful", extra={
            'user_id': user.id,
            'course_id': pk,
            'enrollment_id': enrollment.id
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ChapterViewSet
class ChapterViewSet(CacheListMixin,
    CacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet):
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
    
    

    @action(detail=True, methods=['post'])
    @transaction.atomic
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

        serializer = ChapterProgressSerializer(chapter_progress)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#ProblemViewset
class ProblemViewSet(CacheListMixin,
    CacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet):
    queryset = Problem.objects.all().order_by("type", "-created_at", "id")
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'difficulty']
    ordering_fields = ['difficulty', 'created_at', 'title']
    
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
        elif type_param == 'fillblank':
            prefetches.append('fillblank_info')
        else:
            # 未指定 type，预取所有类型
            prefetches.extend(['algorithm_info', 'choice_info', 'fillblank_info'])

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

        # 获取当前用户
        user = request.user if request.user.is_authenticated else None

        # 获取完整排序后的同类型题目 queryset（带 prefetch）
        same_type_qs = self.get_queryset().filter(type=problem_type)

        # 先取出当前题目的排序字段值
        try:
            current = Problem.objects.only('created_at', 'id').get(id=current_id)
        except Problem.DoesNotExist:
            return Response({"error": "Problem not found"}, status=404)

        # 查找下一个未锁定的题目
        next_obj = None
        next_qs = same_type_qs.filter(
            Q(created_at__lt=current.created_at) |
            (Q(created_at=current.created_at) & Q(id__gt=current.id))
        ).order_by("-created_at", "id")

        for problem in next_qs:
            try:
                unlock_condition = problem.unlock_condition
                if unlock_condition.is_unlocked(user):
                    next_obj = problem
                    break
            except AttributeError:
                # 如果没有解锁条件，则默认为已解锁
                next_obj = problem
                break

        # 查找下下个题目以确定是否有下一个
        has_next = False
        if next_obj:
            next_next_qs = same_type_qs.filter(
                Q(created_at__lt=next_obj.created_at) |
                (Q(created_at=next_obj.created_at) & Q(id__gt=next_obj.id))
            )

            # 检查是否存在下一个未锁定的题目
            for problem in next_next_qs:
                try:
                    unlock_condition = problem.unlock_condition
                    if unlock_condition.is_unlocked(user):
                        has_next = True
                        break
                except AttributeError:
                    has_next = True
                    break

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

    @action(detail=True, methods=['post'])
    @transaction.atomic
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

        serializer = ProblemProgressSerializer(problem_progress)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def check_fillblank(self, request, pk=None):
        """
        检查填空题答案
        接收参数: {"answers": {"blank1": "user_answer1", "blank2": "user_answer2", ...}}
        """
        problem = self.get_object()

        # 验证问题类型
        if problem.type != 'fillblank':
            return Response(
                {'error': 'This action is only for fill-in-the-blank problems'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取填空题详情
        try:
            fillblank_problem = problem.fillblank_info
        except Exception as e:
            return Response(
                {'error': f'FillBlankProblem not found: {str(e)}'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 获取用户提交的答案
        user_answers = request.data.get('answers')
        print("User answers:", user_answers)
        print("Type of user answers:", type(user_answers))
        if not user_answers or not isinstance(user_answers, dict):
            return Response(
                {'error': 'Answers must be provided as a dictionary'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取正确的答案配置
        blanks_data = fillblank_problem.blanks
        correct_blanks = {}

        # 统一转换 blanks 格式
        if all(k.startswith('blank') for k in blanks_data.keys()):
            # 格式1（详细）
            for key, config in blanks_data.items():
                correct_blanks[key] = {
                    'answers': config.get('answer', config.get('answers', [])),
                    'case_sensitive': config.get('case_sensitive', False)
                }
        elif 'blanks' in blanks_data:
            blanks_list = blanks_data['blanks']
            if blanks_list and isinstance(blanks_list[0], dict):
                # 格式3（推荐）
                for i, blank in enumerate(blanks_list):
                    correct_blanks[f'blank{i+1}'] = {
                        'answers': blank['answers'],
                        'case_sensitive': blank.get('case_sensitive', False)
                    }
            else:
                # 格式2（简单）
                case_sensitive = blanks_data.get('case_sensitive', False)
                for i, answer in enumerate(blanks_list):
                    correct_blanks[f'blank{i+1}'] = {
                        'answers': [answer] if isinstance(answer, str) else answer,
                        'case_sensitive': case_sensitive
                    }

        # 验证用户答案
        results = {}
        all_correct = True

        for blank_id, correct_config in correct_blanks.items():
            user_answer = user_answers.get(blank_id, '').strip()
            correct_answers = correct_config['answers']
            case_sensitive = correct_config['case_sensitive']

            # 检查答案是否正确
            is_correct = False
            for correct_answer in correct_answers:
                if case_sensitive:
                    if user_answer == correct_answer.strip():
                        is_correct = True
                        break
                else:
                    if user_answer.lower() == correct_answer.strip().lower():
                        is_correct = True
                        break

            results[blank_id] = {
                'user_answer': user_answer,
                'is_correct': is_correct,
                'correct_answers': correct_answers
            }

            if not is_correct:
                all_correct = False

        # 更新用户进度
        user = request.user
        chapter = problem.chapter
        course = chapter.course if chapter else None

        if course:
            enrollment, _ = Enrollment.objects.get_or_create(
                user=user,
                course=course
            )

            now = timezone.now()
            problem_progress, created = ProblemProgress.objects.get_or_create(
                enrollment=enrollment,
                problem=problem,
                defaults={
                    'status': 'solved' if all_correct else 'in_progress',
                    'attempts': 1,
                    'last_attempted_at': now,
                    'solved_at': now if all_correct else None,
                }
            )

            if not created:
                problem_progress.attempts += 1
                problem_progress.last_attempted_at = now
                if all_correct and problem_progress.status != 'solved':
                    problem_progress.status = 'solved'
                    problem_progress.solved_at = now
                problem_progress.save()

        return Response({
            'all_correct': all_correct,
            'results': results
        }, status=status.HTTP_200_OK)


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
    @transaction.atomic
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

            # 保存代码草稿（提交类型）
            CodeDraft.objects.create(
                user=request.user,
                problem=problem,
                code=code,
                language=language,
                save_type='submission',
                submission=submission
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

class CodeDraftViewSet(viewsets.ModelViewSet):
    """
    代码草稿视图集
    用于管理用户在算法题上的代码保存记录
    """
    queryset = CodeDraft.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CodeDraftSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['problem', 'save_type']

    def get_queryset(self):
        """
        只允许用户查看自己的代码草稿
        """
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)

        # Filter by problem if problem_pk is in URL (nested routing)
        problem_pk = self.kwargs.get('problem_pk')
        if problem_pk is not None:
            queryset = queryset.filter(problem_id=problem_pk)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """
        创建时自动设置用户为当前登录用户
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        获取特定问题的最新代码草稿
        查询参数: problem_id (必需)
        """
        problem_id = request.query_params.get('problem_id')
        if not problem_id:
            return Response(
                {'error': '需要提供 problem_id 查询参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        latest_draft = self.get_queryset().filter(
            problem_id=problem_id
        ).first()

        if latest_draft:
            serializer = self.get_serializer(latest_draft)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'detail': '未找到该问题的代码草稿'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def save_draft(self, request):
        """
        保存代码草稿
        请求体: {
            "problem_id": int,
            "code": str,
            "language": str (可选, 默认'python'),
            "save_type": str (可选, 默认'manual_save'),
            "submission_id": int (可选, 用于提交关联的草稿)
        }
        """
        problem_id = request.data.get('problem_id')
        code = request.data.get('code')
        save_type = request.data.get('save_type', 'manual_save')
        language = request.data.get('language', 'python')
        submission_id = request.data.get('submission_id')

        if not problem_id or not code:
            return Response(
                {'error': 'problem_id 和 code 是必需的'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证问题存在且为算法题
        try:
            problem = Problem.objects.get(id=problem_id, type='algorithm')
        except Problem.DoesNotExist:
            return Response(
                {'error': '未找到该算法题'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 验证 save_type
        valid_save_types = ['auto_save', 'manual_save', 'submission']
        if save_type not in valid_save_types:
            return Response(
                {'error': f'无效的 save_type，必须是以下之一: {valid_save_types}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取提交记录（如果提供）
        submission = None
        if submission_id:
            try:
                submission = Submission.objects.get(
                    id=submission_id,
                    user=request.user,
                    problem=problem
                )
            except Submission.DoesNotExist:
                return Response(
                    {'error': '未找到该提交记录'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # 创建新的草稿记录（始终创建新记录，不更新，以保留完整历史）
        draft = CodeDraft.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language,
            save_type=save_type,
            submission=submission
        )

        serializer = self.get_serializer(draft)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class EnrollmentViewSet(CacheListMixin,
    CacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet):
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

class ChapterProgressViewSet(CacheListMixin,
    CacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet):
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

class ProblemProgressViewSet(CacheListMixin,
    CacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet):
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

    
    @transaction.atomic
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

    @transaction.atomic
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