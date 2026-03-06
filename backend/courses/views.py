import logging
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import models, transaction
from django.db.models import (
    Q,
    Exists,
    OuterRef,
    Case,
    When,
    Value,
    BooleanField,
    Prefetch,
)
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from common.mixins.cache_mixin import (
    StandardCacheListMixin,
    StandardCacheRetrieveMixin,
    InvalidateCacheMixin,
)
from common.mixins.dynamic_fields_mixin import DynamicFieldsMixin
from common.decorators.logging_decorators import audit_log, log_api_call
from .permissions import IsAuthorOrReadOnly
from .models import (
    Course,
    Chapter,
    DiscussionReply,
    DiscussionThread,
    Problem,
    Submission,
    Enrollment,
    ChapterProgress,
    ProblemProgress,
    CodeDraft,
    Exam,
    ExamProblem,
    ExamSubmission,
    ExamAnswer,
    ChoiceProblem,
    FillBlankProblem,
    ChapterUnlockCondition,
    TestCase,
    CourseUnlockSnapshot,
    ProblemUnlockSnapshot,
)
from .serializers import (
    CourseModelSerializer,
    ChapterSerializer,
    DiscussionReplySerializer,
    DiscussionThreadSerializer,
    ProblemSerializer,
    SubmissionSerializer,
    EnrollmentSerializer,
    ChapterProgressSerializer,
    ProblemProgressSerializer,
    CodeDraftSerializer,
    ExamListSerializer,
    ExamDetailSerializer,
    ExamCreateSerializer,
    ExamSubmissionSerializer,
    ExamSubmissionCreateSerializer,
    ExamSubmitSerializer,
    ExamAnswerDetailSerializer,
)
from .services import CodeExecutorService
from .services import ChapterUnlockService, UnlockSnapshotService
from django.db.models import Q

from common.services import SeparatedCacheService
from common.utils.cache import get_standard_cache_key

logger = logging.getLogger(__name__)


class CourseViewSet(
    StandardCacheListMixin,
    StandardCacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet,
):
    """
    一个用于查看和编辑 课程 实例的视图集。
    提供了 'list', 'create', 'retrieve', 'update', 'partial_update', 'destroy' 动作。

    缓存: 使用 StandardCacheMixin 统一缓存key生成（已迁移）

    TODO: 已从 CacheListMixin, CacheRetrieveMixin 迁移到 StandardCacheListMixin, StandardCacheRetrieveMixin
    使用 get_standard_cache_key() 替代 get_cache_key()
    """

    """
    一个用于查看和编辑 课程 实例的视图集。
    提供了 'list', 'create', 'retrieve', 'update', 'partial_update', 'destroy' 动作。
    """

    queryset = Course.objects.all().order_by("title")
    serializer_class = CourseModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]  # 示例：添加搜索和排序
    search_fields = ["title", "description"]
    ordering_fields = ["title", "created_at", "updated_at"]

    @action(detail=True, methods=["post"])
    @transaction.atomic
    @audit_log("course_enrollment")
    def enroll(self, request, pk=None):
        """
        用户注册课程
        """
        logger.info(
            f"User attempting to enroll in course {pk}",
            extra={"user_id": request.user.id, "course_id": pk},
        )

        course = self.get_object()
        user = request.user

        # 检查用户是否已经注册了该课程
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)

        if not created:
            logger.warning(
                f"Duplicate enrollment attempt",
                extra={"user_id": user.id, "course_id": pk},
            )
            return Response(
                {"detail": "您已经注册了该课程"}, status=status.HTTP_400_BAD_REQUEST
            )

        from .tasks import refresh_unlock_snapshot, refresh_problem_unlock_snapshot

        refresh_unlock_snapshot.delay(enrollment.id)
        refresh_problem_unlock_snapshot.delay(enrollment.id)

        serializer = EnrollmentSerializer(enrollment)

        logger.info(
            f"Course enrollment successful",
            extra={"user_id": user.id, "course_id": pk, "enrollment_id": enrollment.id},
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ChapterViewSet
class ChapterViewSet(
    DynamicFieldsMixin,
    viewsets.ModelViewSet,
):
    """
    一个用于查看和编辑特定课程下 Chapter 实例的视图集。

    缓存策略：使用分离缓存（Separated Cache）
    - 全局数据缓存：chapter:global:{id}, chapter:global:list:{course_id}
    - 用户状态缓存：chapter:status:{course_id}:{user_id}
    - 缓存失效由 signals.py 中的 on_chapter_progress_change 和 on_chapter_content_change 处理

    Query Parameters:
        exclude: 可选参数，用于排除响应中的特定字段，以减少数据传输量
            - 可排除字段: content, status, is_locked, prerequisite_progress
            - 示例: ?exclude=content,status
            - 多个字段用逗号分隔
    """

    queryset = Chapter.objects.all().order_by("course__title", "order")  # 默认排序
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]  # 示例：添加搜索和排序
    search_fields = ["title", "content"]
    ordering_fields = ["title", "order", "created_at", "updated_at"]

    def get_queryset(self):
        if getattr(self, "action", None) in ("mark_as_completed",):
            return Chapter.objects.all()

        user = self.request.user
        course_id = self.kwargs.get("course_pk")
        enrollment = None
        self._completed_chapter_ids = set()
        progress_qs = ChapterProgress.objects.none()

        # 学生用户：添加 is_locked_db 数据库注解而不是过滤掉锁定章节
        # 这样序列化器可以直接使用注解值，避免 N+1 查询
        if course_id:
            try:
                enrollment = Enrollment.objects.select_related("user", "course").get(
                    user=user, course_id=course_id
                )
                # 缓存 enrollment 以便在 get_serializer_context 中复用
                self._enrollment = enrollment

                # 尝试使用快照
                try:
                    snapshot = CourseUnlockSnapshot.objects.get(enrollment=enrollment)

                    if not snapshot.is_stale:
                        # 快照新鲜，使用简化查询
                        self._unlock_states = snapshot.unlock_states
                        self._use_snapshot = True

                        # 快照模式下不需要复杂的注解和预取
                        queryset = Chapter.objects.filter(course_id=course_id).order_by(
                            "course__title", "order"
                        )
                        return queryset
                    else:
                        # 快照过期，标记为降级模式
                        self._use_snapshot = False

                except CourseUnlockSnapshot.DoesNotExist:
                    # 快照不存在，降级到原有逻辑
                    self._use_snapshot = False

                # 原有逻辑（预取已完成的章节 ID）
                progress_qs = ChapterProgress.objects.filter(enrollment=enrollment)
                self._completed_chapter_ids = set(
                    progress_qs.filter(completed=True).values_list(
                        "chapter_id", flat=True
                    )
                )

            except Enrollment.DoesNotExist:
                # 如果没有注册课程，无法查看任何章节
                return Chapter.objects.none()

        # 构建查询集 - 一次性完成所有预取，避免 prefetch_related 被覆盖
        # 使用 to_attr 存储 prerequisite_chapters，避免序列化器中的 N+1 查询
        queryset = (
            Chapter.objects.select_related("course")
            .prefetch_related(
                Prefetch(
                    "unlock_condition__prerequisite_chapters",
                    queryset=Chapter.objects.select_related("course"),
                    to_attr="prerequisite_chapters_all",
                ),
                Prefetch(
                    "progress_records", queryset=progress_qs, to_attr="user_progress"
                ),
            )
            .all()
        )

        if enrollment:
            # 只有在非快照模式下才使用复杂注解
            if not self._use_snapshot:
                queryset = self._annotate_is_locked(queryset, enrollment)

        # 应用课程过滤
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset

    def get_serializer_context(self):
        """
        向序列化器传递额外的上下文
        """
        context = super().get_serializer_context()

        # 使用预先缓存的 completed_chapter_ids（在 get_queryset 中设置）
        if hasattr(self, "_completed_chapter_ids"):
            context["completed_chapter_ids"] = self._completed_chapter_ids

        # 传递缓存的 enrollment 到 serializer context
        # 这样 serializer 的回退逻辑不需要再次查询 enrollment
        if hasattr(self, "_enrollment"):
            context["enrollment"] = self._enrollment

        # 传递快照相关变量
        if hasattr(self, "_use_snapshot"):
            context["use_snapshot"] = self._use_snapshot
        if hasattr(self, "_unlock_states"):
            context["unlock_states"] = self._unlock_states

        return context

    def _annotate_is_locked(self, queryset, enrollment):
        """
        为学生用户的章节查询集添加 is_locked_db 数据库注解
        这样序列化器可以直接使用注解值，避免 N+1 查询

        根据 unlock_condition_type 应用不同的解锁逻辑：
        - 'prerequisite': 仅检查前置章节是否完成
        - 'date': 仅检查解锁日期是否到达
        - 'all': 同时检查前置章节和解锁日期
        - 无解锁条件：章节默认解锁
        """
        from django.utils import timezone

        # 优先使用缓存的 completed_chapter_ids，避免重复查询
        if hasattr(self, "_completed_chapter_ids"):
            completed_chapter_ids = self._completed_chapter_ids
        else:
            # 回退逻辑：如果缓存不存在，使用原查询方式
            completed_chapter_ids = set(
                ChapterProgress.objects.filter(
                    enrollment=enrollment, completed=True
                ).values_list("chapter_id", flat=True)
            )

        has_unmet_prerequisites = Exists(
            ChapterUnlockCondition.objects.filter(
                chapter=OuterRef("pk"),
                unlock_condition_type__in=["prerequisite", "all"],
            )
            .filter(prerequisite_chapters__isnull=False)
            .exclude(prerequisite_chapters__id__in=completed_chapter_ids)
        )

        # 检查是否未到解锁日期
        is_before_unlock_date = Exists(
            ChapterUnlockCondition.objects.filter(
                chapter=OuterRef("pk"),
                unlock_condition_type__in=["date", "all"],
                unlock_date__gt=timezone.now(),
            )
        )

        # 使用 Case 语句计算 is_locked_db
        # 如果有任何锁定条件满足，则 is_locked_db=True，否则 False
        queryset = queryset.annotate(
            is_locked_db=Case(
                # 有未满足的前置章节 → 锁定
                When(has_unmet_prerequisites, then=Value(True)),
                # 未到解锁日期 → 锁定
                When(is_before_unlock_date, then=Value(True)),
                # 默认情况 → 未锁定
                default=Value(False),
                output_field=BooleanField(),
            )
        )

        return queryset

    # TODO: Phase 3 - 迁移用户状态缓存到 BusinessCacheService
    # 当前用户状态仍使用直接缓存访问，需要在 Phase 3 迁移到 BusinessCacheService
    # TODO: Phase 3 - 迁移用户状态缓存到 BusinessCacheService
    # 当前用户状态缓存仍使用直接 cache.get/set，需要在 Phase 3 迁移
    def _get_user_status_batch(self, chapter_ids, user_id, course_id):
        """
        批量获取用户状态

        Args:
            chapter_ids: 章节ID列表
            user_id: 用户ID
            course_id: 课程ID

        Returns:
            dict: 章节ID到用户状态的映射
        """
        from .services import get_chapter_user_status

        return get_chapter_user_status(chapter_ids, user_id, course_id)

    def _merge_global_and_user_status(
        self, global_data, user_status, exclude_fields=None
    ):
        """
        合并全局数据和用户状态

        Args:
            global_data: 全局数据列表（来自 ChapterGlobalSerializer）
            user_status: 用户状态映射 {chapter_id: {status, is_locked}, "_meta": {completed_chapter_ids}}
            exclude_fields: 需要排除的字段集合

        Returns:
            list: 合并后的数据列表
        """
        result = []

        # 提取已完成的章节ID列表
        completed_chapter_ids = set(
            user_status.get("_meta", {}).get("completed_chapter_ids", [])
        )

        for item in global_data:
            chapter_id = str(item["id"])
            status_info = user_status.get(chapter_id, {})

            # 合并数据
            merged_item = dict(item)
            merged_item["status"] = status_info.get("status", "not_started")
            merged_item["is_locked"] = status_info.get("is_locked", True)

            # 计算 prerequisite_progress
            prerequisite_chapters = item.get("prerequisite_chapters", [])
            if prerequisite_chapters:
                prerequisite_ids = {ch["id"] for ch in prerequisite_chapters}
                completed_prereqs = prerequisite_ids & completed_chapter_ids
                remaining_prereqs = [
                    ch
                    for ch in prerequisite_chapters
                    if ch["id"] not in completed_prereqs
                ]
                merged_item["prerequisite_progress"] = {
                    "total": len(prerequisite_ids),
                    "completed": len(completed_prereqs),
                    "remaining": remaining_prereqs,
                }
            else:
                merged_item["prerequisite_progress"] = None

            # 从响应中移除 prerequisite_chapters（仅用于计算）
            merged_item.pop("prerequisite_chapters", None)

            # 排除指定字段
            if exclude_fields:
                for field in exclude_fields:
                    merged_item.pop(field, None)

            result.append(merged_item)

        return result

    def list(self, request, *args, **kwargs):
        """
        重写 list 方法以实现分离缓存逻辑

        仅在通过课程路由访问时（course_pk 存在）且无过滤/排序参数时使用分离缓存逻辑，
        否则使用父类的默认实现以支持完整功能。

        缓存策略：
        1. 全局数据缓存：使用标准缓存 key 格式（不含 user_id，跨用户共享）
        2. 用户状态缓存：使用标准缓存 key 格式（含 user_id，按用户隔离）
        3. 合并两层缓存数据后返回
        """
        course_id = self.kwargs.get("course_pk")

        # 如果不是通过课程路由访问，使用父类的默认实现
        if course_id is None:
            return super().list(request, *args, **kwargs)

        # 获取需要排除的字段，检查是否需要 prerequisite_progress
        from rest_framework.serializers import ValidationError

        try:
            exclude_fields = self.get_exclude_fields()
        except ValidationError:
            # 让验证错误传播，返回400响应
            raise
        except Exception:
            exclude_fields = set()

        # 检查是否有过滤、搜索或排序参数（除了分页参数）
        # 如果有这些参数，使用父类实现以支持完整功能
        query_params = set(request.query_params.keys())
        cache_bypass_params = {"search", "ordering"}
        # 分页和排除参数不影响缓存逻辑
        allowed_params = {"page", "page_size", "exclude", "offset", "limit"}

        if query_params - allowed_params:
            # 有过滤或排序参数，检查是否是缓存绕过参数
            if cache_bypass_params & query_params:
                # 有 search 或 ordering 参数，使用父类实现
                return super().list(request, *args, **kwargs)

        from django.core.cache import cache
        from .serializers import ChapterGlobalSerializer

        user_id = request.user.id

        # 1. 获取全局数据缓存（使用 SeparatedCacheService）
        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            parent_pks={"course_pk": course_id},
            is_separated=True,
            separated_type="GLOBAL",
        )
        global_data, is_hit = SeparatedCacheService.get_global_data(
            cache_key=cache_key,
            data_fetcher=lambda: ChapterGlobalSerializer(
                Chapter.objects.filter(course_id=course_id)
                .select_related("course")
                .order_by("order"),
                many=True,
            ).data,
            ttl=1800,
        )

        # 添加 cache hit/miss 日志
        if is_hit:
            logger.debug(f"Global cache HIT for course {course_id}")
        else:
            logger.debug(
                f"Global cache MISS for course {course_id}, data fetched from DB"
            )

        # 2. 获取用户状态缓存
        if request.user.is_authenticated:
            chapter_ids = [item["id"] for item in global_data]
            user_status = self._get_user_status_batch(chapter_ids, user_id, course_id)
        else:
            # 未登录用户，使用默认状态
            user_status = {}

        # 3. 合并数据，并排除指定字段
        merged_data = self._merge_global_and_user_status(
            global_data, user_status, exclude_fields
        )

        # 4. 返回分页响应
        from rest_framework.pagination import PageNumberPagination

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(merged_data, request, view=self)

        if page is not None:
            return paginator.get_paginated_response(page)

        return Response(merged_data)

    def retrieve(self, request, *args, **kwargs):
        """
        重写 retrieve 方法以实现分离缓存逻辑

        缓存策略：
        1. 全局数据缓存：使用标准缓存 key 格式（不含 user_id，跨用户共享）
        2. 用户状态缓存：使用标准缓存 key 格式（含 user_id，按用户隔离）
        3. 合并两层缓存数据后返回
        """
        from django.core.cache import cache
        from .serializers import ChapterGlobalSerializer

        chapter = self.get_object()
        course_id = chapter.course_id
        chapter_id = chapter.id
        user_id = request.user.id

        # 获取需要排除的字段
        exclude_fields = self.get_exclude_fields()

        # 1. 获取全局数据缓存（使用 SeparatedCacheService）
        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ChapterViewSet",
            pk=chapter_id,
            parent_pks={"course_pk": course_id},
            is_separated=True,
            separated_type="GLOBAL",
        )
        global_data, is_hit = SeparatedCacheService.get_global_data(
            cache_key=cache_key,
            data_fetcher=lambda: ChapterGlobalSerializer(chapter).data,
            ttl=1800,
        )

        # 添加 cache hit/miss 日志
        if is_hit:
            logger.debug(f"Global cache HIT for chapter {chapter_id}")
        else:
            logger.debug(
                f"Global cache MISS for chapter {chapter_id}, data fetched from DB"
            )

        # 2. 获取用户状态缓存
        if request.user.is_authenticated:
            user_status = self._get_user_status_batch([chapter_id], user_id, course_id)
        else:
            # 未登录用户，使用默认状态
            user_status = {}

        # 3. 合并数据，并排除指定字段
        merged_data = self._merge_global_and_user_status(
            [global_data], user_status, exclude_fields
        )[0]

        return Response(merged_data)

    @action(detail=True, methods=["post"])
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
            user=user, course=chapter.course
        )

        # 从请求体中读取 completed 参数，默认为 True（保持向后兼容）
        completed = request.data.get("completed", True)
        # 处理字符串形式的布尔值（form-data中的'true'/'false'）
        if isinstance(completed, str):
            if completed.lower() in ("true", "1", "yes"):
                completed = True
            elif completed.lower() in ("false", "0", "no"):
                completed = False
            else:
                return Response(
                    {"error": "'completed' must be a boolean (true or false)."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif not isinstance(completed, bool):
            return Response(
                {"error": "'completed' must be a boolean (true or false)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 获取或创建章节进度记录
        chapter_progress, created = ChapterProgress.objects.get_or_create(
            enrollment=enrollment, chapter=chapter, defaults={"completed": completed}
        )

        # 如果是新创建或需要更新状态
        if not created:
            # 已存在的记录，根据 completed 参数更新
            if completed:
                chapter_progress.completed = completed
                chapter_progress.completed_at = timezone.now()
            chapter_progress.save()
        elif completed:
            # 新创建的记录且 completed=True，设置 completed_at
            chapter_progress.completed_at = timezone.now()
            chapter_progress.save()

        serializer = ChapterProgressSerializer(chapter_progress)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def unlock_status(self, request, pk=None, course_pk=None):
        """
        获取章节解锁状态详情
        使用快照优化查询，返回前置章节完成进度、解锁时间等信息
        """
        from django.utils import timezone

        chapter = self.get_object()
        user = request.user

        try:
            enrollment = Enrollment.objects.get(user=user, course=chapter.course)
        except Enrollment.DoesNotExist:
            return Response(
                {"detail": "您尚未注册该课程"}, status=status.HTTP_403_FORBIDDEN
            )

        hybrid_result = UnlockSnapshotService.get_unlock_status_hybrid(
            chapter.course, enrollment
        )
        unlock_states = hybrid_result["unlock_states"]
        chapter_state = unlock_states.get(str(chapter.id))

        if chapter_state:
            prerequisite_progress = chapter_state.get("prerequisite_progress")
            reason = chapter_state.get("reason")

            if reason in ("prerequisite", "both") and prerequisite_progress is None:
                from .models import CourseUnlockSnapshot
                from .tasks import refresh_unlock_snapshot

                try:
                    snapshot = CourseUnlockSnapshot.objects.get(enrollment=enrollment)
                    snapshot.is_stale = True
                    snapshot.save(update_fields=["is_stale"])
                    refresh_unlock_snapshot.delay(enrollment.id)
                except CourseUnlockSnapshot.DoesNotExist:
                    pass

                status_info = ChapterUnlockService.get_unlock_status(
                    chapter, enrollment
                )
                return Response(status_info)

            result = {
                "is_locked": chapter_state.get("locked", False),
                "reason": reason,
                "prerequisite_progress": prerequisite_progress,
                "unlock_date": None,
                "time_until_unlock": None,
                "chapter": {
                    "id": chapter.id,
                    "title": chapter.title,
                    "order": chapter.order,
                    "course_title": chapter.course.title,
                },
            }

            if hasattr(chapter, "unlock_condition") and chapter.unlock_condition:
                condition = chapter.unlock_condition
                result["unlock_date"] = condition.unlock_date

                if condition.unlock_date and result["is_locked"]:
                    if condition.unlock_condition_type in ("date", "all"):
                        now = timezone.now()
                        if now < condition.unlock_date:
                            delta = condition.unlock_date - now
                            result["time_until_unlock"] = {
                                "days": delta.days,
                                "hours": delta.seconds // 3600,
                                "minutes": (delta.seconds % 3600) // 60,
                            }

            return Response(result)

        status_info = ChapterUnlockService.get_unlock_status(chapter, enrollment)
        return Response(status_info)

    def retrieve(self, request, *args, **kwargs):
        """
        获取章节详情，检查解锁状态
        使用快照缓存避免重复查询
        """
        chapter = self.get_object()

        enrollment = getattr(self, "_enrollment", None)
        if not enrollment:
            try:
                enrollment = Enrollment.objects.get(
                    user=request.user, course=chapter.course
                )
            except Enrollment.DoesNotExist:
                return Response(
                    {"detail": "您尚未注册该课程"}, status=status.HTTP_403_FORBIDDEN
                )

        unlock_states = getattr(self, "_unlock_states", None)
        if unlock_states:
            chapter_state = unlock_states.get(str(chapter.id))
            if chapter_state and chapter_state.get("locked"):
                return self._build_locked_response(chapter_state, chapter)

        if hasattr(self, "_use_snapshot") and self._use_snapshot:
            return super().retrieve(request, *args, **kwargs)

        if not ChapterUnlockService.is_unlocked(chapter, enrollment):
            status_info = ChapterUnlockService.get_unlock_status(chapter, enrollment)
            return self._build_locked_response(status_info, chapter)

        return super().retrieve(request, *args, **kwargs)

    def _build_locked_response(self, status_info, chapter):
        """
        构建锁定章节的响应
        """
        if status_info.get("reason") == "prerequisite":
            remaining = status_info.get("prerequisite_progress", {}).get(
                "remaining", []
            )
            if remaining:
                chapter_titles = [c["title"] for c in remaining]
                error_msg = f"请先完成以下章节：{', '.join(chapter_titles)}"
            else:
                error_msg = "该章节尚未解锁，需要完成前置章节"
        elif status_info.get("reason") == "date":
            unlock_date = status_info.get("unlock_date")
            if unlock_date:
                error_msg = f"该章节将于 {unlock_date.strftime('%Y-%m-%d %H:%M')} 解锁"
            else:
                error_msg = "该章节尚未到解锁时间"
        else:
            error_msg = "该章节尚未解锁，需要满足前置章节并到达解锁时间"

        return Response(
            {"detail": error_msg, "lock_status": status_info},
            status=status.HTTP_403_FORBIDDEN,
        )


# ProblemViewset
class ProblemViewSet(
    DynamicFieldsMixin,
    viewsets.ModelViewSet,
):
    """
    API endpoint for Problem model with dynamic field exclusion support.

    缓存策略：使用分离缓存（Separated Cache）
    - 全局数据缓存：使用标准缓存 key 格式
    - 用户状态缓存：使用标准缓存 key 格式
    - 缓存失效由 signals.py 中的 on_problem_progress_change 和 on_problem_content_change 处理

    This ViewSet uses the generic `DynamicFieldsMixin` to provide field exclusion
    functionality, which can be reused across other ViewSets.

    ## Query Parameters

    ### Filtering
    - `type`: Filter by problem type (algorithm, choice, fillblank)
    - `difficulty`: Filter by difficulty level (1-5)

    ### Ordering
    - `ordering`: Sort results (e.g., `-difficulty`, `created_at`, `title`)
      Supported fields: difficulty, created_at, title

    ### Field Exclusion (Optimization)
    - `exclude`: Comma-separated list of fields to exclude from response

      **Available fields:** content, recent_threads, status, chapter_title, updated_at,
      is_unlocked, unlock_condition_description, type, difficulty, title, id, created_at

      **Example usage:**
      - `?exclude=content,recent_threads` - Exclude large fields for list view
      - `?exclude=content,recent_threads,status,chapter_title,updated_at` - Maximum optimization

      **Benefits:**
      - Reduces response size by ~70-80% (from ~300KB to ~50-60KB per page)
      - Skips database queries when excluding `recent_threads`
      - Improves page load performance, especially on mobile/low-bandwidth connections

      **Validation:**
      - Invalid field names return 400 Bad Request with error details
      - Empty or missing parameter returns all fields (backward compatible)

    ## Pagination
    - Page-based pagination with customizable `page_size` (default: 10)

    ## Example Requests
    ```
    GET /problems/                                    # All fields (backward compatible)
    GET /problems/?exclude=content                   # Single field exclusion
    GET /problems/?exclude=content,recent_threads    # Multiple field exclusion
    GET /problems/?exclude=content&type=algorithm    # Combine with filtering
    GET /problems/123/?exclude=recent_threads        # Detail endpoint support
    ```
    """

    queryset = Problem.objects.all().order_by("type", "-created_at", "id")
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["type", "difficulty"]
    ordering_fields = ["difficulty", "created_at", "title"]

    def get_queryset(self):
        user = self.request.user
        course_id = self.kwargs.get("course_pk")
        enrollment = None

        # 获取排除字段（用于优化查询）
        try:
            exclude_fields = self.get_exclude_fields()
        except Exception:
            # 如果验证失败，在 list/retrieve 方法中会处理错误
            exclude_fields = set()

        # 尝试获取 enrollment（如果通过 course_pk 访问）
        if course_id and user.is_authenticated:
            try:
                enrollment = Enrollment.objects.select_related("user", "course").get(
                    user=user, course_id=course_id
                )
                # 缓存 enrollment 以便在 get_serializer_context 中复用
                self._enrollment = enrollment

                # 尝试使用快照
                try:
                    snapshot = ProblemUnlockSnapshot.objects.get(enrollment=enrollment)

                    if not snapshot.is_stale:
                        # 快照新鲜，使用简化查询
                        self._unlock_states = snapshot.unlock_states
                        self._use_snapshot = True

                        # 快照模式下跳过复杂的进度预取
                        queryset = super().get_queryset()

                        # 优化：使用 select_related 预取 unlock_condition 和 chapter（ForeignKey）
                        queryset = queryset.select_related(
                            "unlock_condition", "chapter"
                        )

                        # 按课程过滤（如果通过 course_pk 访问）
                        if course_id:
                            queryset = queryset.filter(chapter__course_id=course_id)

                        # 按章节过滤
                        if "chapter_pk" in self.kwargs:
                            queryset = queryset.filter(
                                chapter=self.kwargs["chapter_pk"]
                            )

                        # 获取 type 查询参数
                        type_param = self.request.query_params.get("type")

                        # 构建 prefetch 列表（不包括用户进度，因为快照已包含）
                        prefetches = []

                        # 根据 type 预取对应的问题详情
                        if type_param == "algorithm":
                            prefetches.append("algorithm_info")
                            # 算法题：预取测试用例（嵌套 prefetch）
                            prefetches.append(
                                Prefetch(
                                    "algorithm_info__test_cases",
                                    queryset=TestCase.objects.filter(
                                        is_sample=True
                                    ).order_by("id"),
                                    to_attr="sample_test_cases",
                                )
                            )
                        elif type_param == "choice":
                            prefetches.append("choice_info")
                        elif type_param == "fillblank":
                            prefetches.append("fillblank_info")
                        else:
                            # 未指定 type，预取所有类型（包括 test_cases）
                            prefetches.extend(
                                ["algorithm_info", "choice_info", "fillblank_info"]
                            )
                            prefetches.append(
                                Prefetch(
                                    "algorithm_info__test_cases",
                                    queryset=TestCase.objects.filter(
                                        is_sample=True
                                    ).order_by("id"),
                                    to_attr="sample_test_cases",
                                )
                            )

                        # 优化：仅在 recent_threads 未被排除时预取 discussion_threads
                        if "recent_threads" not in exclude_fields:
                            prefetches.append(
                                Prefetch(
                                    "discussion_threads",
                                    queryset=DiscussionThread.objects.filter(
                                        is_archived=False
                                    ).order_by("-last_activity_at")[:3],
                                    to_attr="recent_threads_list",
                                )
                            )

                        # 优化：仅在 unlock_condition_description 未被排除时预取 prerequisite_problems
                        if "unlock_condition_description" not in exclude_fields:
                            prefetches.append(
                                Prefetch(
                                    "unlock_condition__prerequisite_problems",
                                    to_attr="prerequisite_problems_all",
                                )
                            )

                        return queryset.prefetch_related(*prefetches)
                    else:
                        # 快照过期，标记需要刷新，继续使用原有逻辑
                        from .tasks import refresh_problem_unlock_snapshot

                        refresh_problem_unlock_snapshot.delay(enrollment.id)
                        self._use_snapshot = False
                except ProblemUnlockSnapshot.DoesNotExist:
                    # 快照不存在，继续使用原有逻辑
                    self._use_snapshot = False
            except Enrollment.DoesNotExist:
                # 没有 enrollment，继续使用原有逻辑
                self._use_snapshot = False
        else:
            # 没有 course_pk 或未登录，使用原有逻辑
            self._use_snapshot = False

        # 原有逻辑：完整查询（降级模式）
        queryset = super().get_queryset()

        # 优化：使用 select_related 预取 unlock_condition 和 chapter（ForeignKey）
        queryset = queryset.select_related("unlock_condition", "chapter")

        # 按课程过滤（如果通过 course_pk 访问）
        if course_id:
            queryset = queryset.filter(chapter__course_id=course_id)

        # 按章节过滤
        if "chapter_pk" in self.kwargs:
            queryset = queryset.filter(chapter=self.kwargs["chapter_pk"])

        # 获取 type 查询参数
        type_param = self.request.query_params.get("type")

        # 构建 prefetch 列表
        prefetches = []

        # 根据 type 预取对应的问题详情
        if type_param == "algorithm":
            prefetches.append("algorithm_info")
            # 算法题：预取测试用例（嵌套 prefetch）
            prefetches.append(
                Prefetch(
                    "algorithm_info__test_cases",
                    queryset=TestCase.objects.filter(is_sample=True).order_by("id"),
                    to_attr="sample_test_cases",
                )
            )
        elif type_param == "choice":
            prefetches.append("choice_info")
        elif type_param == "fillblank":
            prefetches.append("fillblank_info")
        else:
            # 未指定 type，预取所有类型（包括 test_cases）
            prefetches.extend(["algorithm_info", "choice_info", "fillblank_info"])
            prefetches.append(
                Prefetch(
                    "algorithm_info__test_cases",
                    queryset=TestCase.objects.filter(is_sample=True).order_by("id"),
                    to_attr="sample_test_cases",
                )
            )

        # 优化：仅在 recent_threads 未被排除时预取 discussion_threads
        if "recent_threads" not in exclude_fields:
            prefetches.append(
                Prefetch(
                    "discussion_threads",
                    queryset=DiscussionThread.objects.filter(
                        is_archived=False
                    ).order_by("-last_activity_at")[:3],
                    to_attr="recent_threads_list",
                )
            )

        # 优化：仅在 unlock_condition_description 未被排除时预取 prerequisite_problems
        if "unlock_condition_description" not in exclude_fields:
            prefetches.append(
                Prefetch(
                    "unlock_condition__prerequisite_problems",
                    to_attr="prerequisite_problems_all",
                )
            )

        # 优化：仅在 status 未被排除时预取用户进度
        user = self.request.user
        if user.is_authenticated and "status" not in exclude_fields:
            # 只预取当前用户的进度，通过 enrollment 关联
            progress_prefetch = Prefetch(
                "progress_records",
                queryset=ProblemProgress.objects.select_related(
                    "enrollment__user"
                ).filter(enrollment__user=user),
                to_attr="user_progress_list",  # 自定义属性名，避免覆盖默认 related_name
            )
            prefetches.append(progress_prefetch)
        # 如果未登录或 status 被排除，不预取进度（后续 get_status 返回默认值）

        return queryset.prefetch_related(*prefetches)

    def get_serializer_context(self):
        """
        向序列化器传递额外的上下文
        """
        context = super().get_serializer_context()

        # 传递缓存的 enrollment 到 serializer context
        # 这样 serializer 的回退逻辑不需要再次查询 enrollment
        if hasattr(self, "_enrollment"):
            context["enrollment"] = self._enrollment

        # 传递快照相关变量
        if hasattr(self, "_use_snapshot"):
            context["use_snapshot"] = self._use_snapshot
        if hasattr(self, "_unlock_states"):
            context["unlock_states"] = self._unlock_states

        return context

    # TODO: Phase 3 - 迁移用户状态缓存到 BusinessCacheService
    # 当前用户状态缓存仍使用直接 cache.get/set，需要在 Phase 3 迁移
    def _get_problem_user_status_batch(self, problem_ids, user_id, chapter_id):
        """
        批量获取问题用户状态

        Args:
            problem_ids: 问题ID列表
            user_id: 用户ID
            chapter_id: 章节ID

        Returns:
            dict: 问题ID到用户状态的映射
        """
        from .services import get_problem_user_status

        return get_problem_user_status(problem_ids, user_id, chapter_id)

    def _merge_problem_global_and_user_status(
        self, global_data, user_status, exclude_fields=None
    ):
        """
        合并问题全局数据和用户状态

        Args:
            global_data: 全局数据列表（来自 ProblemGlobalSerializer）
            user_status: 用户状态映射 {problem_id: {status, is_unlocked}}
            exclude_fields: 需要排除的字段集合

        Returns:
            list: 合并后的数据列表
        """
        result = []

        for item in global_data:
            problem_id = str(item["id"])
            status_info = user_status.get(problem_id, {})

            # 合并数据
            merged_item = dict(item)
            merged_item["status"] = status_info.get("status", "not_started")
            merged_item["is_unlocked"] = status_info.get("is_unlocked", False)

            # 排除指定字段
            if exclude_fields:
                for field in exclude_fields:
                    merged_item.pop(field, None)

            result.append(merged_item)

        return result

    def list(self, request, *args, **kwargs):
        """
        重写 list 方法以实现分离缓存逻辑

        仅在通过章节路由访问时（chapter_pk 存在）且无过滤/排序参数时使用分离缓存逻辑，
        否则使用父类的默认实现以支持完整功能。

        缓存策略：
        1. 全局数据缓存：使用标准缓存 key 格式（不含 user_id，跨用户共享）
        2. 用户状态缓存：使用标准缓存 key 格式（含 user_id，按用户隔离）
        3. 合并两层缓存数据后返回
        """
        chapter_id = self.kwargs.get("chapter_pk")

        # 如果不是通过章节路由访问，使用父类的默认实现
        if chapter_id is None:
            return super().list(request, *args, **kwargs)

        # 检查是否有过滤、搜索或排序参数（除了分页参数）
        # 如果有这些参数，使用父类实现以支持完整功能
        query_params = set(request.query_params.keys())
        cache_bypass_params = {"search", "ordering", "type", "difficulty"}
        # 分页和排除参数不影响缓存逻辑
        allowed_params = {"page", "page_size", "exclude", "offset", "limit"}

        if query_params - allowed_params:
            # 有过滤或排序参数，检查是否是缓存绕过参数
            if cache_bypass_params & query_params:
                # 有 search, ordering, type 或 difficulty 参数，使用父类实现
                return super().list(request, *args, **kwargs)

        from django.core.cache import cache
        from .serializers import ProblemGlobalSerializer

        user_id = request.user.id

        # 获取需要排除的字段
        exclude_fields = self.get_exclude_fields()

        # 1. 获取全局数据缓存（使用 SeparatedCacheService）
        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ProblemViewSet",
            parent_pks={"chapter_pk": chapter_id},
            is_separated=True,
            separated_type="GLOBAL",
        )
        global_data, is_hit = SeparatedCacheService.get_global_data(
            cache_key=cache_key,
            data_fetcher=lambda: ProblemGlobalSerializer(
                Problem.objects.filter(chapter_id=chapter_id)
                .select_related("chapter")
                .order_by("id"),
                many=True,
            ).data,
            ttl=1800,
        )

        # 添加 cache hit/miss 日志
        if is_hit:
            logger.debug(f"Global cache HIT for chapter {chapter_id}")
        else:
            logger.debug(
                f"Global cache MISS for chapter {chapter_id}, data fetched from DB"
            )

        # 2. 获取用户状态缓存
        if request.user.is_authenticated:
            problem_ids = [item["id"] for item in global_data]
            user_status = self._get_problem_user_status_batch(
                problem_ids, user_id, chapter_id
            )
        else:
            # 未登录用户，使用默认状态
            user_status = {}

        # 3. 合并数据，并排除指定字段
        merged_data = self._merge_problem_global_and_user_status(
            global_data, user_status, exclude_fields
        )

        # 4. 返回分页响应
        from rest_framework.pagination import PageNumberPagination

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(merged_data, request, view=self)

        if page is not None:
            return paginator.get_paginated_response(page)

        return Response(merged_data)

    def retrieve(self, request, *args, **kwargs):
        """
        重写 retrieve 方法以实现分离缓存逻辑

        仅在通过章节路由访问时（chapter_pk 存在）使用分离缓存逻辑，
        否则使用父类的默认实现。

        缓存策略：
        1. 全局数据缓存：使用标准缓存 key 格式（不含 user_id，跨用户共享）
        2. 用户状态缓存：使用标准缓存 key 格式（含 user_id，按用户隔离）
        3. 合并两层缓存数据后返回
        """
        # 如果不是通过章节路由访问，使用父类的默认实现
        chapter_id = self.kwargs.get("chapter_pk")
        if chapter_id is None:
            return super().retrieve(request, *args, **kwargs)

        from django.core.cache import cache
        from .serializers import ProblemGlobalSerializer

        problem = self.get_object()
        chapter_id = problem.chapter_id
        problem_id = problem.id
        user_id = request.user.id

        # 获取需要排除的字段
        exclude_fields = self.get_exclude_fields()

        # 1. 获取全局数据缓存（使用 SeparatedCacheService）
        cache_key = get_standard_cache_key(
            prefix="courses",
            view_name="ProblemViewSet",
            pk=problem_id,
            parent_pks={"chapter_pk": chapter_id},
            is_separated=True,
            separated_type="GLOBAL",
        )
        global_data, is_hit = SeparatedCacheService.get_global_data(
            cache_key=cache_key,
            data_fetcher=lambda: ProblemGlobalSerializer(problem).data,
            ttl=1800,
        )

        # 添加 cache hit/miss 日志
        if is_hit:
            logger.debug(f"Global cache HIT for problem {problem_id}")
        else:
            logger.debug(
                f"Global cache MISS for problem {problem_id}, data fetched from DB"
            )

        # 2. 获取用户状态缓存
        if request.user.is_authenticated and chapter_id:
            user_status = self._get_problem_user_status_batch(
                [problem_id], user_id, chapter_id
            )
        else:
            # 未登录用户或孤儿问题，使用默认状态
            user_status = {}

        # 3. 合并数据，并排除指定字段
        merged_data = self._merge_problem_global_and_user_status(
            [global_data], user_status, exclude_fields
        )[0]

        return Response(merged_data)

    @action(detail=False, methods=["get"], url_path="next")
    def get_next_problem(self, request):
        problem_type = request.query_params.get("type")
        current_id = request.query_params.get("id")
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
            current = Problem.objects.only("created_at", "id").get(id=current_id)
        except Problem.DoesNotExist:
            return Response({"error": "Problem not found"}, status=404)

        # 获取快照数据（如果可用）
        unlock_states = getattr(self, "_unlock_states", {})
        use_snapshot = getattr(self, "_use_snapshot", False)

        # 查找下一个未锁定的题目
        next_obj = None
        next_qs = same_type_qs.filter(
            Q(created_at__lt=current.created_at)
            | (Q(created_at=current.created_at) & Q(id__gt=current.id))
        ).order_by("-created_at", "id")

        for problem in next_qs:
            if use_snapshot:
                # 优先使用快照数据（完全避免数据库查询）
                problem_state = unlock_states.get(str(problem.id))
                if problem_state and problem_state["unlocked"]:
                    next_obj = problem
                    break
                elif not problem_state:
                    # 快照中没有该题目，默认解锁（向后兼容）
                    next_obj = problem
                    break
            else:
                # 降级：实时计算解锁状态
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
                Q(created_at__lt=next_obj.created_at)
                | (Q(created_at=next_obj.created_at) & Q(id__gt=next_obj.id))
            )

            # 检查是否存在下一个未锁定的题目
            for problem in next_next_qs:
                if use_snapshot:
                    # 优先使用快照数据
                    problem_state = unlock_states.get(str(problem.id))
                    if problem_state and problem_state["unlocked"]:
                        has_next = True
                        break
                    elif not problem_state:
                        # 快照中没有该题目，默认解锁
                        has_next = True
                        break
                else:
                    # 降级：实时计算
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

    @action(detail=True, methods=["post"])
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
                {"detail": "问题未关联到课程"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 获取或创建用户的课程注册记录
        enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)
        # 获取是否标记为已解决，默认为 True（保持原语义）
        solved = request.data.get("solved", True)

        now = timezone.now()
        problem_progress, created = ProblemProgress.objects.get_or_create(
            enrollment=enrollment,
            problem=problem,
            defaults={
                "status": "solved" if solved else "in_progress",
                "attempts": 1,
                "last_attempted_at": now,
                "solved_at": now if solved else None,
            },
        )

        if not created:
            # 已存在记录：总是增加尝试次数并更新最后尝试时间
            problem_progress.attempts += 1
            problem_progress.last_attempted_at = now

            if solved:
                problem_progress.status = "solved"
                problem_progress.solved_at = now
            else:
                # 未解决：状态设为 in_progress（避免从 solved 退回去）
                if problem_progress.status != "solved":
                    problem_progress.status = "in_progress"
                # 如果已经是 solved，通常不应降级，可根据业务决定是否允许

        problem_progress.save()

        serializer = ProblemProgressSerializer(problem_progress)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def check_fillblank(self, request, pk=None):
        """
        检查填空题答案
        接收参数: {"answers": {"blank1": "user_answer1", "blank2": "user_answer2", ...}}
        """
        problem = self.get_object()

        # 验证问题类型
        if problem.type != "fillblank":
            return Response(
                {"error": "This action is only for fill-in-the-blank problems"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 获取填空题详情
        try:
            fillblank_problem = problem.fillblank_info
        except Exception as e:
            return Response(
                {"error": f"FillBlankProblem not found: {str(e)}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 获取用户提交的答案
        user_answers = request.data.get("answers")
        if not user_answers or not isinstance(user_answers, dict):
            return Response(
                {"error": "Answers must be provided as a dictionary"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 获取正确的答案配置
        blanks_data = fillblank_problem.blanks
        correct_blanks = {}

        # 统一转换 blanks 格式
        if all(k.startswith("blank") and k[5:].isdigit() for k in blanks_data.keys()):
            # 格式1（详细）
            for key, config in blanks_data.items():
                correct_blanks[key] = {
                    "answers": config.get("answer", config.get("answers", [])),
                    "case_sensitive": config.get("case_sensitive", False),
                }
        elif "blanks" in blanks_data:
            blanks_list = blanks_data["blanks"]
            if blanks_list and isinstance(blanks_list[0], dict):
                # 格式3（推荐）
                for i, blank in enumerate(blanks_list):
                    correct_blanks[f"blank{i + 1}"] = {
                        "answers": blank["answers"],
                        "case_sensitive": blank.get("case_sensitive", False),
                    }
            else:
                # 格式2（简单）
                case_sensitive = blanks_data.get("case_sensitive", False)
                for i, answer in enumerate(blanks_list):
                    correct_blanks[f"blank{i + 1}"] = {
                        "answers": [answer] if isinstance(answer, str) else answer,
                        "case_sensitive": case_sensitive,
                    }

        # 验证用户答案
        results = {}
        all_correct = True

        for blank_id, correct_config in correct_blanks.items():
            user_answer = user_answers.get(blank_id, "").strip()
            correct_answers = correct_config["answers"]
            case_sensitive = correct_config["case_sensitive"]

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
                "user_answer": user_answer,
                "is_correct": is_correct,
                "correct_answers": correct_answers,
            }

            if not is_correct:
                all_correct = False

        # 更新用户进度
        user = request.user
        chapter = problem.chapter
        course = chapter.course if chapter else None

        if course:
            enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)

            now = timezone.now()
            problem_progress, created = ProblemProgress.objects.get_or_create(
                enrollment=enrollment,
                problem=problem,
                defaults={
                    "status": "solved" if all_correct else "in_progress",
                    "attempts": 1,
                    "last_attempted_at": now,
                    "solved_at": now if all_correct else None,
                },
            )

            if not created:
                problem_progress.attempts += 1
                problem_progress.last_attempted_at = now
                if all_correct and problem_progress.status != "solved":
                    problem_progress.status = "solved"
                    problem_progress.solved_at = now
                problem_progress.save()

        return Response(
            {"all_correct": all_correct, "results": results}, status=status.HTTP_200_OK
        )


class SubmissionViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """
    提交记录视图集，用于处理代码提交和执行

    Query Parameters:
        exclude: 可选参数，用于排除响应中的特定字段，以减少数据传输量
            - 可排除字段: code, output, error, execution_time, memory_used
            - 示例: ?exclude=code,output,error
            - 多个字段用逗号分隔
    """

    queryset = Submission.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        problem_pk = self.kwargs.get("problem_pk")
        if problem_pk is not None:
            # 只返回属于该 problem 的 submissions
            queryset = queryset.filter(problem_id=problem_pk, problem__type="algorithm")
        # 可以根据用户权限进行过滤
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset.order_by("-created_at")

    # post
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        创建新的提交记录。
        - 如果提供了 problem_id：作为算法题提交，运行所有测试用例。
        - 如果未提供 problem_id：作为自由运行（Run Code），仅执行代码并返回 stdout/stderr。
        """
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language", "python")

        if not code:
            return Response(
                {"error": "Code is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        # 情况 1：自由运行（无 problem_id）
        if not problem_id:
            try:
                executor = CodeExecutorService()
                result = executor.run_freely(code=code, language=language)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"error": f"Error executing code: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # 情况 2：作为算法题提交（有 problem_id）
        problem = get_object_or_404(Problem, id=problem_id)
        if problem.type != "algorithm":
            return Response(
                {"error": "Only algorithm problems allow code submission"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            executor = CodeExecutorService()
            submission = executor.run_all_test_cases(
                user=request.user, problem=problem, code=code, language=language
            )

            # 保存代码草稿（提交类型）
            CodeDraft.objects.create(
                user=request.user,
                problem=problem,
                code=code,
                language=language,
                save_type="submission",
                submission=submission,
            )

            # 如果提交成功，更新问题进度
            if submission.status == "accepted":
                # 获取或创建用户的课程注册记录
                chapter = problem.chapter
                course = chapter.course if chapter else None

                if course:
                    enrollment, _ = Enrollment.objects.get_or_create(
                        user=request.user, course=course
                    )

                    # 更新或创建问题进度记录
                    problem_progress, created = ProblemProgress.objects.get_or_create(
                        enrollment=enrollment,
                        problem=problem,
                        defaults={
                            "status": "solved",
                            "attempts": 1,
                            "best_submission": submission,
                        },
                    )

                    if not created:
                        problem_progress.status = "solved"
                        problem_progress.attempts = problem_progress.attempts + 1
                        # 如果是更好的提交（通过且执行时间更短），则更新最佳提交
                        if (
                            not problem_progress.best_submission
                            or submission.execution_time
                            < problem_progress.best_submission.execution_time
                        ):
                            problem_progress.best_submission = submission
                        problem_progress.save()

            serializer = self.get_serializer(submission)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": f"Error executing code: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
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
    filterset_fields = ["problem", "save_type"]

    def get_queryset(self):
        """
        只允许用户查看自己的代码草稿
        """
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)

        # Filter by problem if problem_pk is in URL (nested routing)
        problem_pk = self.kwargs.get("problem_pk")
        if problem_pk is not None:
            queryset = queryset.filter(problem_id=problem_pk)

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        """
        创建时自动设置用户为当前登录用户
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """
        获取特定问题的最新代码草稿
        查询参数: problem_id (必需)
        """
        problem_id = request.query_params.get("problem_id")
        if not problem_id:
            return Response(
                {"error": "需要提供 problem_id 查询参数"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        latest_draft = self.get_queryset().filter(problem_id=problem_id).first()

        if latest_draft:
            serializer = self.get_serializer(latest_draft)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "未找到该问题的代码草稿"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"])
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
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        save_type = request.data.get("save_type", "manual_save")
        language = request.data.get("language", "python")
        submission_id = request.data.get("submission_id")

        if not problem_id or not code:
            return Response(
                {"error": "problem_id 和 code 是必需的"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 验证问题存在且为算法题
        try:
            problem = Problem.objects.get(id=problem_id, type="algorithm")
        except Problem.DoesNotExist:
            return Response(
                {"error": "未找到该算法题"}, status=status.HTTP_404_NOT_FOUND
            )

        # 验证 save_type
        valid_save_types = ["auto_save", "manual_save", "submission"]
        if save_type not in valid_save_types:
            return Response(
                {"error": f"无效的 save_type，必须是以下之一: {valid_save_types}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 获取提交记录（如果提供）
        submission = None
        if submission_id:
            try:
                submission = Submission.objects.get(
                    id=submission_id, user=request.user, problem=problem
                )
            except Submission.DoesNotExist:
                return Response(
                    {"error": "未找到该提交记录"}, status=status.HTTP_404_NOT_FOUND
                )

        # 创建新的草稿记录（始终创建新记录，不更新，以保留完整历史）
        draft = CodeDraft.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language,
            save_type=save_type,
            submission=submission,
        )

        serializer = self.get_serializer(draft)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EnrollmentViewSet(
    StandardCacheListMixin,
    StandardCacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet,
):
    """
    课程参与视图集

    缓存: 使用 StandardCacheMixin 统一缓存key生成（已迁移）
    注意: 此ViewSet使用用户隔离缓存（user_id自动注入）

    TODO: 已从 CacheListMixin, CacheRetrieveMixin 迁移到 StandardCacheListMixin, StandardCacheRetrieveMixin
    使用 get_standard_cache_key() 替代 get_cache_key()
    signals.py 中的缓存失效逻辑已使用 CacheInvalidator
    """

    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["course"]

    def get_queryset(self):
        """
        只允许用户查看自己的课程参与记录

        优化查询：
        - select_related: user, course (FK关系，使用JOIN优化)
        - prefetch_related: chapter_progress (反向关系，预取避免N+1)
        - Prefetch course__chapters with to_attr: 预取章节用于进度计算
        - Prefetch chapters with unlock_condition: 避免 next_chapter 序列化时的 N+1
        - Nested prefetch for prerequisite_chapters: 避免 ChapterUnlockCondition 的 N+1
        """
        # 预取前置章节及其课程，避免 ChapterUnlockCondition 序列化时额外查询
        prereq_chapters_qs = Chapter.objects.select_related("course")
        # 预取解锁条件的前置章节，并预取解锁条件本身
        unlock_condition_qs = ChapterUnlockCondition.objects.prefetch_related(
            Prefetch(
                "prerequisite_chapters",
                queryset=prereq_chapters_qs,
                to_attr="prerequisite_chapters_all",
            )
        )
        # 预取章节及其课程和解锁条件
        chapters_qs = Chapter.objects.select_related("course").prefetch_related(
            Prefetch("unlock_condition", queryset=unlock_condition_qs)
        )
        queryset = self.queryset.filter(user=self.request.user)
        queryset = queryset.select_related("user", "course")
        queryset = queryset.prefetch_related(
            "chapter_progress",
            Prefetch("course__chapters", queryset=chapters_qs, to_attr="all_chapters"),
        )
        return queryset

    def create(self, request, *args, **kwargs):
        """
        创建课程参与，并处理重复
        """
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            # 检查是否是数据库唯一性约束错误
            if (
                "unique" in str(e).lower()
                or "duplicate" in str(e).lower()
                or "7c8ca1bf_uniq" in str(e)
            ):
                return Response(
                    {"detail": "您已经注册了该课程"}, status=status.HTTP_400_BAD_REQUEST
                )
            raise e

    def perform_create(self, serializer):
        """
        创建时自动设置用户为当前登录用户
        """
        serializer.save(user=self.request.user)


class ChapterProgressViewSet(
    StandardCacheListMixin,
    StandardCacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet,
):
    """
    章节进度视图集（只读）

    缓存: 使用 StandardCacheMixin 统一缓存key生成（已迁移）
    注意: 此ViewSet使用用户隔离缓存（user_id自动注入）

    TODO: 已从 CacheListMixin, CacheRetrieveMixin 迁移到 StandardCacheListMixin, StandardCacheRetrieveMixin
    使用 get_standard_cache_key() 替代 get_cache_key()
    """

    queryset = ChapterProgress.objects.all()
    serializer_class = ChapterProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        只允许用户查看自己的章节进度
        """
        return self.queryset.filter(enrollment__user=self.request.user)


class ProblemProgressViewSet(
    StandardCacheListMixin,
    StandardCacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet,
):
    """
    问题进度视图集（只读）

    缓存: 使用 StandardCacheMixin 统一缓存key生成（已迁移）
    注意: 此ViewSet使用用户隔离缓存（user_id自动注入）

    TODO: 已从 CacheListMixin, CacheRetrieveMixin 迁移到 StandardCacheListMixin, StandardCacheRetrieveMixin
    使用 get_standard_cache_key() 替代 get_cache_key()
    """

    queryset = ProblemProgress.objects.all().order_by("id")
    serializer_class = ProblemProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        """
        只允许用户查看自己的问题进度
        """
        qs = ProblemProgress.objects.filter(enrollment__user=self.request.user)
        status_not = self.request.query_params.get("status_not")
        if status_not:
            qs = qs.exclude(status=status_not)
        return qs


class DiscussionThreadViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    """
    讨论主题视图集，用于管理课程讨论

    Query Parameters:
        exclude: 可选参数，用于排除响应中的特定字段，以减少数据传输量
            - 可排除字段: content, replies
            - 示例: ?exclude=content,replies
            - 多个字段用逗号分隔
    """

    serializer_class = DiscussionThreadSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]  # 作者可改，匿名或者其他用户可读
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "course",
        "chapter",
        "problem",
        "is_pinned",
        "is_resolved",
        "is_archived",
    ]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "last_activity_at", "reply_count"]
    ordering = ["-last_activity_at"]

    def get_queryset(self):
        queryset = DiscussionThread.objects.all()

        # 获取 URL 中的嵌套参数
        course_pk = self.kwargs.get("course_pk")
        chapter_pk = self.kwargs.get("chapter_pk")
        problem_pk = self.kwargs.get("problem_pk")

        # 用于 select_related 的字段列表
        select_related_fields = ["author"]

        if course_pk:
            queryset = queryset.filter(course_id=course_pk)
            select_related_fields.append("course")
        if chapter_pk:
            queryset = queryset.filter(chapter_id=chapter_pk)
            select_related_fields.append("chapter")

        if problem_pk:
            queryset = queryset.filter(problem_id=problem_pk)
            select_related_fields.append("problem")

        return queryset.select_related(*select_related_fields)

    @transaction.atomic
    def perform_create(self, serializer):
        # 如果是嵌套路由创建，自动填充对应外键
        course_pk = self.kwargs.get("course_pk")
        chapter_pk = self.kwargs.get("chapter_pk")
        problem_pk = self.kwargs.get("problem_pk")

        kwargs = {"author": self.request.user}
        if course_pk:
            kwargs["course_id"] = course_pk
        if chapter_pk:
            kwargs["chapter_id"] = chapter_pk
        if problem_pk:
            kwargs["problem_id"] = problem_pk

        serializer.save(**kwargs)


class DiscussionReplyViewSet(viewsets.ModelViewSet):
    serializer_class = DiscussionReplySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["thread"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]  # 按时间正序（从早到晚）

    def get_queryset(self):
        queryset = DiscussionReply.objects.select_related("author").prefetch_related(
            "mentioned_users"
        )

        # 如果是通过 /threads/{id}/replies/ 访问，自动过滤 thread
        thread_pk = self.kwargs.get("thread_pk")
        if thread_pk:
            queryset = queryset.filter(thread_id=thread_pk)

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        # 自动从 URL 获取 thread_pk
        thread_pk = self.kwargs.get("thread_pk")
        if thread_pk:
            # 你可以选择是否验证 thread 是否存在
            thread = get_object_or_404(DiscussionThread, pk=thread_pk)
            serializer.save(author=self.request.user, thread=thread)
        else:
            # 如果不是嵌套路由（如直接 POST /replies/），则要求前端传 thread
            # 此时 serializer 必须包含 thread 字段（由 serializer 自己处理）
            serializer.save(author=self.request.user)


# ============================================================================
# 测验功能相关视图
# ============================================================================


class ExamViewSet(
    StandardCacheListMixin,
    StandardCacheRetrieveMixin,
    InvalidateCacheMixin,
    viewsets.ModelViewSet,
):
    """
    测验视图集

    缓存: 使用 StandardCacheMixin 统一缓存key生成（已迁移）

    TODO: 已从 CacheListMixin, CacheRetrieveMixin 迁移到 StandardCacheListMixin, StandardCacheRetrieveMixin
    使用 get_standard_cache_key() 替代 get_cache_key()
    signals.py 中的缓存失效逻辑已使用 CacheInvalidator
    """

    queryset = (
        Exam.objects.all()
        .select_related("course")
        .prefetch_related("exam_problems__problem")
    )
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["course", "status"]
    search_fields = ["title", "description"]
    ordering_fields = ["start_time", "end_time", "created_at"]
    ordering = ["-start_time"]

    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == "list":
            return ExamListSerializer
        elif self.action == "create":
            return ExamCreateSerializer
        return ExamDetailSerializer

    def get_queryset(self):
        """根据用户角色过滤查询集"""
        queryset = super().get_queryset()
        user = self.request.user

        # 学生只能看到已发布的测验
        if not user.is_staff:
            queryset = queryset.filter(status="published")

        # 如果通过课程路由访问，只返回该课程的测验
        course_pk = self.kwargs.get("course_pk")
        if course_pk:
            queryset = queryset.filter(course_id=course_pk)

        return queryset

    def list(self, request, *args, **kwargs):
        """重写list方法以优化查询，预取用户提交记录避免N+1查询"""
        queryset = self.filter_queryset(self.get_queryset())

        # 预取当前用户的提交记录，避免N+1查询
        queryset = queryset.prefetch_related(
            Prefetch(
                "submissions",
                queryset=ExamSubmission.objects.filter(user=request.user),
                to_attr="user_submissions",
            )
        )

        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="start")
    @transaction.atomic
    def start(self, request, pk=None, course_pk=None):
        """
        开始测验
        - 如果已有 in_progress 的 submission，返回它
        - 否则创建新的 in_progress submission
        """
        exam = self.get_object()
        # 获取或创建注册记录
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=exam.course)
        except Enrollment.DoesNotExist:
            return Response(
                {"error": "您未注册该课程，无法参加测验"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 查找已有的 in_progress submission
        submission = ExamSubmission.objects.filter(
            exam=exam, user=request.user, status="in_progress"
        ).first()

        # 如果没有 in_progress 的 submission，创建新的
        if not submission:
            # 使用序列化器进行验证
            serializer = ExamSubmissionCreateSerializer(
                data={}, context={"request": request, "exam_id": exam.id}
            )
            serializer.is_valid(raise_exception=True)

            # 创建提交记录
            submission = ExamSubmission.objects.create(
                exam=exam,
                enrollment=enrollment,
                user=request.user,
                status="in_progress",
            )

            # 为所有题目创建答案记录
            exam_problems = exam.exam_problems.select_related("problem").all()
            for exam_problem in exam_problems:
                ExamAnswer.objects.create(
                    submission=submission, problem=exam_problem.problem
                )

            return Response(
                {
                    "submission_id": submission.id,
                    "started_at": submission.started_at,
                    "duration_minutes": exam.duration_minutes,
                    "end_time": exam.end_time,
                },
                status=status.HTTP_201_CREATED,
            )
        # 返回已有的 submission
        return Response(
            {
                "submission_id": submission.id,
                "started_at": submission.started_at,
                "duration_minutes": exam.duration_minutes,
                "end_time": exam.end_time,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="submit")
    @transaction.atomic
    def submit(self, request, pk=None, course_pk=None):
        """
        提交答案并自动评分
        """
        exam = self.get_object()

        # 获取用户的进行中提交
        submission = get_object_or_404(
            ExamSubmission, exam=exam, user=request.user, status="in_progress"
        )

        # 验证并解析答案
        serializer = ExamSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers_data = serializer.validated_data["answers"]

        # 更新答案记录
        for answer_data in answers_data:
            problem_id = answer_data.get("problem_id")
            problem_type = answer_data.get("problem_type")

            answer = get_object_or_404(
                ExamAnswer, submission=submission, problem_id=problem_id
            )

            if problem_type == "choice":
                answer.choice_answers = answer_data.get("choice_answers")
            elif problem_type == "fillblank":
                answer.fillblank_answers = answer_data.get("fillblank_answers")

            answer.save()

        # 计算时间花费
        now = timezone.now()
        time_spent = int((now - submission.started_at).total_seconds())

        # 检查是否超时
        if exam.duration_minutes > 0:
            deadline = submission.started_at + timezone.timedelta(
                minutes=exam.duration_minutes
            )
            if now > deadline:
                submission.status = "auto_submitted"
            else:
                submission.status = "submitted"
        else:
            submission.status = "submitted"

        submission.submitted_at = now
        submission.time_spent_seconds = time_spent

        # 评分
        self._grade_submission(submission)

        submission.save()
        # if exam.show_results_after_submit:
        #     submission.status = 'graded'
        # 返回结果
        result_serializer = ExamSubmissionSerializer(submission)
        return Response(result_serializer.data, status=status.HTTP_200_OK)

    def _grade_submission(self, submission):
        """
        评分提交
        支持选择题和填空题
        """
        answers = submission.answers.all()
        total_score = 0

        for answer in answers:
            # 获取该题在测验中的分值
            exam_problem = ExamProblem.objects.get(
                exam=submission.exam, problem=answer.problem
            )
            max_score = exam_problem.score

            if answer.problem.type == "choice":
                result = self._grade_choice_problem(answer, max_score)
            elif answer.problem.type == "fillblank":
                result = self._grade_fillblank_problem(answer, max_score)
            else:
                # 不应该发生，因为测验只包含选择题和填空题
                result = {"score": 0, "is_correct": False}

            answer.score = result["score"]
            answer.is_correct = result.get("is_correct", False)
            answer.correct_percentage = result.get("correct_percentage")
            answer.save()

            total_score += result["score"]

        # 更新提交记录
        submission.total_score = total_score
        submission.is_passed = total_score >= submission.exam.passing_score

    def _grade_choice_problem(self, answer, max_score):
        """评分选择题"""
        try:
            choice_info = answer.problem.choice_info
        except ChoiceProblem.DoesNotExist:
            return {"score": 0, "is_correct": False}

        user_answer = answer.choice_answers
        correct_answer = choice_info.correct_answer

        # 判断是否正确
        if isinstance(correct_answer, list):
            # 多选题
            is_correct = isinstance(user_answer, list) and set(user_answer) == set(
                correct_answer
            )
        else:
            # 单选题
            is_correct = user_answer == correct_answer

        return {"score": max_score if is_correct else 0, "is_correct": is_correct}

    def _grade_fillblank_problem(self, answer, max_score):
        """
        评分填空题
        基于正确比例计分（如3个空白答对2个，得分为题目分数的2/3）
        """
        try:
            fillblank_problem = answer.problem.fillblank_info
        except FillBlankProblem.DoesNotExist:
            return {"score": 0, "is_correct": False, "correct_percentage": 0}

        user_answers = answer.fillblank_answers or {}

        # 获取正确的答案配置（复用现有逻辑）
        blanks_data = fillblank_problem.blanks
        correct_blanks = {}

        # 统一转换 blanks 格式（与 check_fillblank API 相同）
        if all(k.startswith("blank") for k in blanks_data.keys()):
            # 格式1（详细）
            for key, config in blanks_data.items():
                correct_blanks[key] = {
                    "answers": config.get("answer", config.get("answers", [])),
                    "case_sensitive": config.get("case_sensitive", False),
                }
        elif "blanks" in blanks_data:
            blanks_list = blanks_data["blanks"]
            if blanks_list and isinstance(blanks_list[0], dict):
                # 格式3（推荐）
                for i, blank in enumerate(blanks_list):
                    correct_blanks[f"blank{i + 1}"] = {
                        "answers": blank["answers"],
                        "case_sensitive": blank.get("case_sensitive", False),
                    }
            else:
                # 格式2（简单）
                case_sensitive = blanks_data.get("case_sensitive", False)
                for i, blank_answer in enumerate(blanks_list):
                    correct_blanks[f"blank{i + 1}"] = {
                        "answers": [blank_answer]
                        if isinstance(blank_answer, str)
                        else blank_answer,
                        "case_sensitive": case_sensitive,
                    }

        # 计算正确的空白比例
        correct_count = 0
        total_count = len(correct_blanks)

        for blank_id, correct_config in correct_blanks.items():
            user_answer = user_answers.get(blank_id, "").strip()
            correct_answers_list = correct_config["answers"]
            case_sensitive = correct_config["case_sensitive"]

            # 检查答案是否正确
            is_correct = False
            for correct_answer in correct_answers_list:
                if case_sensitive:
                    if user_answer == correct_answer.strip():
                        is_correct = True
                        break
                else:
                    if user_answer.lower() == correct_answer.strip().lower():
                        is_correct = True
                        break

            if is_correct:
                correct_count += 1

        # 计算得分（按正确比例）
        correct_percentage = correct_count / total_count if total_count > 0 else 0
        score = max_score * correct_percentage

        return {
            "score": round(score, 2),
            "is_correct": correct_count == total_count,
            "correct_percentage": round(correct_percentage, 2),
            "correct_count": correct_count,
            "total_count": total_count,
        }

    @action(detail=True, methods=["get"], url_path="results")
    def results(self, request, pk=None, course_pk=None):
        """
        查看测验结果
        """
        exam = self.get_object()

        # 获取用户的提交记录
        submission = exam.submissions.filter(user=request.user).first()

        if not submission:
            return Response(
                {"detail": "您还没有参加该测验"}, status=status.HTTP_404_NOT_FOUND
            )

        # 如果测验不显示结果且未提交，则返回提示
        if not exam.show_results_after_submit and submission.status == "in_progress":
            return Response(
                {"detail": "提交后才能查看结果"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = ExamSubmissionSerializer(submission)
        return Response(serializer.data)


class ExamSubmissionViewSet(
    StandardCacheListMixin, StandardCacheRetrieveMixin, viewsets.ReadOnlyModelViewSet
):
    """
    测验提交记录视图集（只读）
    用户只能查看自己的提交记录

    缓存: 使用 StandardCacheMixin 统一缓存key生成（已迁移）
    注意: 此ViewSet使用用户隔离缓存（user_id自动注入）

    TODO: 已从 CacheListMixin, CacheRetrieveMixin 迁移到 StandardCacheListMixin, StandardCacheRetrieveMixin
    使用 get_standard_cache_key() 替代 get_cache_key()
    """

    queryset = (
        ExamSubmission.objects.all()
        .select_related("exam", "user")
        .prefetch_related("answers__problem")
    )
    serializer_class = ExamSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["exam", "status"]
    ordering = ["-started_at"]

    def get_queryset(self):
        """只返回当前用户的提交记录"""
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=["get"])
    def detail(self, request, pk=None):
        """
        获取提交详情（包含答案详情）
        """
        submission = self.get_object()

        # 检查权限
        if submission.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "您没有权限查看此提交"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = ExamSubmissionSerializer(submission)
        return Response(serializer.data)
