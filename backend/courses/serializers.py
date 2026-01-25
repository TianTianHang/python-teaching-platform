from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import ChoiceProblem, Course, Chapter, DiscussionReply, DiscussionThread, Problem, AlgorithmProblem, TestCase, Submission, Enrollment, ChapterProgress, ProblemProgress, CodeDraft, FillBlankProblem, Exam, ExamProblem, ExamSubmission, ExamAnswer


class CourseModelSerializer(serializers.ModelSerializer):
    recent_threads = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ["id", "title", "description","recent_threads", "created_at", "updated_at"]
        read_only_fields = ["recent_threads","created_at", "updated_at"]
    def get_recent_threads(self, obj):
        threads = obj.discussion_threads.filter(is_archived=False).order_by('-last_activity_at')[:3]
        return BriefDiscussionThreadSerializer(threads, many=True, context=self.context).data


class ChapterSerializer(serializers.ModelSerializer):
    # 这里不需要 course 或 course_id 字段来接收输入，因为它会在 ViewSet 中通过 URL 上下文设置
    # 但你可以在输出时显示所属课程的ID或名字
    course_title = serializers.ReadOnlyField(
        source="course.title"
    )  # 显示所属课程的标题
    status = serializers.SerializerMethodField()  # 新增状态字段
    class Meta:
        model = Chapter
        fields = [
            "id",
            "course",
            "course_title",
            "title",
            "content",
            "order",
            "created_at",
            "updated_at",
            "status"
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]  # course 字段在创建和更新时将通过 ViewSet 自动设置
    def get_status(self, obj):
        """
        根据当前用户的 ChapterProgress 返回章节状态
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return "not_started"  # 或者你可以返回 None，由前端处理

        # 尝试获取当前用户对该章节的进度
        try:
            progress = ChapterProgress.objects.get(
                enrollment__user=request.user,
                chapter=obj
            )
            if progress.completed:
                return "completed"
            else:
                return "in_progress"
        except ChapterProgress.DoesNotExist:
            return "not_started"

class ProblemSerializer(serializers.ModelSerializer):
    chapter_title = serializers.ReadOnlyField(source="chapter.title")
    status = serializers.SerializerMethodField()
    recent_threads = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    unlock_condition_description = serializers.SerializerMethodField()

    def get_status(self, obj):
        """
        获取当前用户对该问题的解决状态
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 'not_started'  # 未登录用户视为未开始

        try:
            progress = ProblemProgress.objects.get(
                enrollment__user=request.user,
                problem=obj
            )
            return progress.status
        except ProblemProgress.DoesNotExist:
            return 'not_started'

    def get_is_unlocked(self, obj):
        """
        获取当前用户对该问题的解锁状态
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False  # 未登录用户视为未解锁

        try:
            unlock_condition = obj.unlock_condition
            return unlock_condition.is_unlocked(request.user)
        except AttributeError:
            # 如果没有解锁条件，则默认为已解锁
            return True

    def get_unlock_condition_description(self, obj):
        """
        获取解锁条件的描述信息（结构化字典格式）
        """
        try:
            unlock_condition = obj.unlock_condition

            # 构建结构化字典
            unlock_info = {
                'type': unlock_condition.unlock_condition_type,
                'type_display': {
                    'prerequisite': '前置题目',
                    'date': '解锁日期',
                    'both': '前置题目和解锁日期',
                    'none': '无条件'
                }.get(unlock_condition.unlock_condition_type, '未知'),
                'is_prerequisite_required': unlock_condition.unlock_condition_type in ['prerequisite', 'both'],
                'is_date_required': unlock_condition.unlock_condition_type in ['date', 'both'],
                'prerequisite_problems': [],
                'unlock_date': unlock_condition.unlock_date.isoformat() if unlock_condition.unlock_date else None,
                'has_conditions': (
                    unlock_condition.prerequisite_problems.exists() or
                    unlock_condition.unlock_date is not None
                )
            }

            # 添加前置题目详细信息
            if unlock_condition.prerequisite_problems.exists():
                prereq_problems = unlock_condition.prerequisite_problems.all()
                unlock_info['prerequisite_problems'] = [
                    {
                        'id': prob.id,
                        'title': prob.title,
                        'difficulty': prob.difficulty
                    }
                    for prob in prereq_problems
                ]
                unlock_info['prerequisite_count'] = len(unlock_info['prerequisite_problems'])

            return unlock_info
        except AttributeError:
            # 如果没有解锁条件，则返回默认信息
            return {
                'type': 'none',
                'type_display': '无条件',
                'is_prerequisite_required': False,
                'is_date_required': False,
                'prerequisite_problems': [],
                'unlock_date': None,
                'has_conditions': False
            }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.type == "algorithm":
            data = {**data,**AlgorithmProblemSerializer(instance.algorithm_info).data}
        if instance.type == "choice":
            data = {**data,**ChoiceProblemSerializer(instance.choice_info).data}
        if instance.type == "fillblank":
            data = {**data,**FillBlankProblemSerializer(instance.fillblank_info).data}
        return data

    def get_recent_threads(self, obj):
        threads = obj.discussion_threads.filter(is_archived=False).order_by('-last_activity_at')[:3]
        return DiscussionThreadSerializer(threads, many=True, context=self.context).data

    class Meta:
        model = Problem
        fields = ["id", "type", "chapter_title","recent_threads", "title","content","difficulty","status","is_unlocked","unlock_condition_description","created_at","updated_at"]
        read_only_fields = ["recent_threads","created_at", "updated_at"]
        

class AlgorithmProblemSerializer(serializers.ModelSerializer):
    sample_cases = serializers.SerializerMethodField()
    def get_sample_cases(self, obj):
        sample_test_cases = obj.test_cases.filter(is_sample=True).order_by('id')
        
        return TestCaseSerializer(sample_test_cases, many=True).data
    class Meta:
        model = AlgorithmProblem
        fields = ["time_limit","memory_limit","code_template","sample_cases"]

class ChoiceProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceProblem
        fields = ['problem', 'options', 'correct_answer', 'is_multiple_choice']
        
    def validate_options(self, value):
        """验证 options 字段格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("选项必须是字典格式，例如 {'A': '内容1', 'B': '内容2'}")
        if not value:
            raise serializers.ValidationError("选项不能为空")
        keys = list(value.keys())
        # 检查键是否为连续的大写字母 A, B, C...（可选，也可只检查是否为单个大写字母）
        if not all(isinstance(k, str) and len(k) == 1 and k.isupper() for k in keys):
            raise serializers.ValidationError("选项键必须是单个大写字母，如 A、B、C...")
        # 可选：检查是否从 'A' 开始连续（更严格）
        # expected_keys = [chr(ord('A') + i) for i in range(len(keys))]
        # if keys != expected_keys:
        #     raise serializers.ValidationError("选项键应从 A 开始连续排列")
        return value

    def validate_correct_answer(self, value):
        """初步验证 correct_answer 类型（具体合法性需结合 options 和 is_multiple_choice）"""
        # 类型检查将在 validate() 中结合其他字段完成
        return value

    def validate(self, attrs):
        """跨字段验证：correct_answer 必须在 options 的键中，且类型匹配 is_multiple_choice"""
        options = attrs.get('options')
        correct_answer = attrs.get('correct_answer')
        is_multiple_choice = attrs.get('is_multiple_choice', False)

        if options is None:
            # 如果是更新操作，options 可能未提供，需从 instance 获取
            if self.instance:
                options = self.instance.options
            else:
                raise serializers.ValidationError("options 字段缺失")

        if correct_answer is None:
            if self.instance:
                correct_answer = self.instance.correct_answer
            else:
                raise serializers.ValidationError("correct_answer 字段缺失")

        if is_multiple_choice:
            if not isinstance(correct_answer, list):
                raise serializers.ValidationError("多选题的正确答案必须是列表，例如 ['A', 'C']")
            if not correct_answer:
                raise serializers.ValidationError("多选题正确答案不能为空")
            if not all(isinstance(ans, str) for ans in correct_answer):
                raise serializers.ValidationError("多选题答案中的每个选项必须是字符串")
            if not all(ans in options for ans in correct_answer):
                invalid = [ans for ans in correct_answer if ans not in options]
                raise serializers.ValidationError(f"正确答案包含无效选项: {invalid}")
        else:
            if not isinstance(correct_answer, str):
                raise serializers.ValidationError("单选题的正确答案必须是字符串，例如 'A'")
            if correct_answer not in options:
                raise serializers.ValidationError(f"正确答案 '{correct_answer}' 不在选项中")

        return attrs

class FillBlankProblemSerializer(serializers.ModelSerializer):
    """
    填空题序列化器
    """
    blanks_list = serializers.SerializerMethodField()

    def get_blanks_list(self, obj):
        """
        将不同格式的 blanks 转换为统一的前端友好格式
        """
        blanks_data = obj.blanks

        # 格式1（详细）：{'blank1': {'answer': [...], 'case_sensitive': False}, ...}
        if all(k.startswith('blank') and k[5:].isdigit() for k in blanks_data.keys()):
            result = []
            for key in sorted(blanks_data.keys(), key=lambda x: int(x.replace('blank', ''))):
                config = blanks_data[key]
                result.append({
                    'id': key,
                    'answers': config.get('answer', config.get('answers', [])),
                    'case_sensitive': config.get('case_sensitive', False)
                })
            return result

        # 格式2（简单）：{'blanks': ['答案1', '答案2'], 'case_sensitive': False}
        elif 'blanks' in blanks_data:
            blanks_list = blanks_data['blanks']
            case_sensitive = blanks_data.get('case_sensitive', False)

            # 格式3（推荐）：已经是列表格式
            if blanks_list and isinstance(blanks_list[0], dict):
                return [
                    {
                        'id': f'blank{i+1}',
                        'answers': blank['answers'],
                        'case_sensitive': blank.get('case_sensitive', False)
                    }
                    for i, blank in enumerate(blanks_list)
                ]

            # 格式2（简单）：简单字符串列表
            return [
                {
                    'id': f'blank{i+1}',
                    'answers': [answer],
                    'case_sensitive': case_sensitive
                }
                for i, answer in enumerate(blanks_list)
            ]

        return []

    class Meta:
        model = FillBlankProblem
        fields = [
            'content_with_blanks',
            'blanks',
            'blanks_list',
            'blank_count'
        ]

    def validate_blanks(self, value):
        """验证 blanks 字段格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("blanks 必须是字典格式")

        # 至少需要包含有效数据
        if not value:
            raise serializers.ValidationError("blanks 不能为空")

        return value

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ["id", "input_data", "expected_output", "is_sample"] # 不包含 problem 字段，避免循环引用  

class SubmissionSerializer(serializers.ModelSerializer):
    """
    提交记录序列化器
    """
    username = serializers.ReadOnlyField(source='user.username')
    problem_title = serializers.ReadOnlyField(source='problem.title')
   
    class Meta:
        model = Submission
        fields = [
            'id', 'user', 'username', 'problem', 'problem_title', 'code',
            'language', 'status', 'execution_time', 'memory_used',
            'output', 'error', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status', 'execution_time', 'memory_used', 
                           'output', 'error', 'created_at', 'updated_at']

    def create(self, validated_data):
        # The actual creation happens in the view, not here
        # This is just to prevent direct creation if someone tries to bypass the logic
        raise serializers.ValidationError("Submissions must be created through the submission endpoint")


class CodeDraftSerializer(serializers.ModelSerializer):
    """
    代码草稿序列化器
    """
    username = serializers.ReadOnlyField(source='user.username')
    problem_title = serializers.ReadOnlyField(source='problem.title')
    submission_id = serializers.ReadOnlyField(source='submission.id')

    class Meta:
        model = CodeDraft
        fields = [
            'id', 'user', 'username', 'problem', 'problem_title',
            'code', 'language', 'save_type', 'submission_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        验证问题是否为算法题
        """
        problem = attrs.get('problem')
        if problem and problem.type != 'algorithm':
            raise serializers.ValidationError(
                {"problem": "代码草稿只能为算法题创建"}
            )
        return attrs


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    课程参与序列化器
    """
    user_username = serializers.ReadOnlyField(source='user.username')
    course_title = serializers.ReadOnlyField(source='course.title')
    progress_percentage = serializers.SerializerMethodField()
    next_chapter = serializers.SerializerMethodField()
    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'user_username', 'course', 'course_title', 
            'enrolled_at', 'last_accessed_at', 'progress_percentage','next_chapter'
        ]
        read_only_fields = ['user','next_chapter', 'enrolled_at', 'last_accessed_at', 'progress_percentage']
    
    def get_progress_percentage(self, obj):
        """
        计算课程完成进度百分比
        """
        total_chapters = obj.course.chapters.count()
        if total_chapters == 0:
            return 0
        
        completed_chapters = obj.chapter_progress.filter(completed=True).count()
        return round((completed_chapters / total_chapters) * 100, 2)
    def get_next_chapter(self, obj):
        course = obj.course
       # 获取用户在该课程中已完成的章节 IDs
        completed_chapter_ids = ChapterProgress.objects.filter(
            enrollment=obj,
            completed=True
        ).values_list('chapter_id', flat=True)

        # 找第一个未完成的章节（按 order）
        next_chapter = Chapter.objects.filter(
            course=course
        ).exclude(id__in=completed_chapter_ids).order_by('order').first()

        if next_chapter:
            return ChapterSerializer(next_chapter).data
        return None

class ChapterProgressSerializer(serializers.ModelSerializer):
    """
    章节进度序列化器
    """
    chapter_title = serializers.ReadOnlyField(source='chapter.title')
    course_title = serializers.ReadOnlyField(source='chapter.course.title')
    
    class Meta:
        model = ChapterProgress
        fields = [
            'id', 'enrollment', 'chapter', 'chapter_title', 'course_title',
            'completed', 'completed_at'
        ]
        read_only_fields = ['completed_at']


class ProblemProgressSerializer(serializers.ModelSerializer):
    """
    问题进度序列化器
    """
    problem_title = serializers.ReadOnlyField(source='problem.title')
    problem_type = serializers.ReadOnlyField(source='problem.type')
    problem_difficulty = serializers.ReadOnlyField(source='problem.difficulty')
    chapter_title = serializers.ReadOnlyField(source='problem.chapter.title')
    course_title = serializers.ReadOnlyField(source='problem.chapter.course.title')
    
    class Meta:
        model = ProblemProgress
        fields = [
            'id', 'enrollment', 'problem', 'problem_title', 'chapter_title', 'course_title',
            'status', 'attempts', 'last_attempted_at', 'solved_at', 'best_submission','problem_type',"problem_difficulty"
        ]
        read_only_fields = ['attempts', 'last_attempted_at', 'solved_at', 'best_submission']

class BriefDiscussionThreadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = DiscussionThread
        fields = [
            'id', 'course','chapter','problem', 'author', 'title', 'content',
            'is_pinned', 'is_resolved', 'is_archived',
            'reply_count', 'last_activity_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'reply_count', 'last_activity_at',
            'created_at', 'updated_at'
        ]       
class DiscussionThreadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField() # 显示部分回复，有需要再访问api获取全部回复
    

    class Meta:
        model = DiscussionThread
        fields = [
            'id', 'course','chapter','problem', 'author', 'title', 'content',
            'is_pinned', 'is_resolved', 'is_archived',
            'reply_count', 'last_activity_at',
            'created_at', 'updated_at', 'replies'
        ]
        read_only_fields = [
            'id', 'author', 'reply_count', 'last_activity_at',
            'created_at', 'updated_at'
        ]

    def get_replies(self, obj):
        # 仅返回顶级回复（parent=None），子回复由 DiscussionReplySerializer 的 children 处理
        # top_replies = obj.replies.filter(parent__isnull=True).select_related('author').prefetch_related(
        #     'children__author', 'mentioned_users'
        # ).order_by('created_at')[:20]  # 限制初始加载数量
        top_replies = obj.replies.select_related('author').prefetch_related(
            'mentioned_users'
        ).order_by('created_at')[:20] 
        return DiscussionReplySerializer(top_replies, many=True, context=self.context).data
    
class DiscussionReplySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    #children = serializers.SerializerMethodField()
    mentioned_users = UserSerializer(many=True, read_only=True)
    thread = serializers.PrimaryKeyRelatedField(
        queryset=DiscussionThread.objects.all(),
        required=False,
        write_only=True
    )

    class Meta:
        model = DiscussionReply
        fields = [
            'id', 'author', 'content', 'thread',
            'mentioned_users', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def validate(self, attrs):
        # 如果上下文中有 view，并且是嵌套路由（有 thread_pk），则忽略 thread 字段
        view = self.context.get('view')
        if view and hasattr(view, 'kwargs') and 'thread_pk' in view.kwargs:
            # 嵌套路由：不依赖前端传 thread
            pass
        elif 'pk' in view.kwargs: # reply 自身的pk有的话也不需要绑定thread，此时已有该回复可以反插
            pass
        else:
            # 非嵌套路由：必须提供 thread
            if 'thread' not in attrs:
                raise serializers.ValidationError({
                    'thread': 'This field is required when not using nested route.'
                })
        return attrs
    # def get_children(self, obj):
    #     # 只在顶级回复（parent=None）时展开一层子回复，避免无限递归
    #     if obj.parent is None:
    #         children = obj.children.all()[:10]  # 限制子回复数量，防性能问题
    #         return DiscussionReplySerializer(children, many=True, context=self.context).data
    #     return []


# ============================================================================
# 测验功能相关序列化器
# ============================================================================

class ExamListSerializer(serializers.ModelSerializer):
    """测验列表序列化器"""
    course_title = serializers.ReadOnlyField(source='course.title')
    is_active = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    user_submission_status = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            'id', 'course', 'course_title', 'title', 'description',
            'start_time', 'end_time', 'duration_minutes',
            'total_score', 'passing_score', 'status',
            'is_active', 'question_count', 'user_submission_status', 'remaining_time',
            'show_results_after_submit'
        ]

    def get_is_active(self, obj):
        """检查测验是否激活"""
        return obj.is_active()

    def get_question_count(self, obj):
        """获取题目数量"""
        return obj.exam_problems.count()

    def get_user_submission_status(self, obj):
        """获取用户的提交状态（使用预取的数据）"""
        # 首先尝试使用预取的user_submissions
        if hasattr(obj, 'user_submissions'):
            user_submissions = obj.user_submissions
            if user_submissions:
                submission = user_submissions[0]  # 只有一个提交记录
                return {
                    'status': submission.status,
                    'submitted_at': submission.submitted_at,
                    'total_score': submission.total_score,
                    'is_passed': submission.is_passed
                }
            return None

        # 降级处理：如果没有预取数据，使用原有逻辑
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        submission = obj.submissions.filter(user=request.user).first()
        if submission:
            return {
                'status': submission.status,
                'submitted_at': submission.submitted_at,
                'total_score': submission.total_score,
                'is_passed': submission.is_passed
            }
        return None

    def get_remaining_time(self, obj):
        """获取剩余时间（使用预取的数据）"""
        # 首先尝试使用预取的user_submissions
        submission = None
        if hasattr(obj, 'user_submissions'):
            in_progress_submissions = [s for s in obj.user_submissions if s.status == 'in_progress']
            if in_progress_submissions:
                submission = in_progress_submissions[0]

        # 降级处理：如果没有预取数据
        if not submission:
            request = self.context.get('request')
            if not request or not request.user.is_authenticated:
                return None
            submission = obj.submissions.filter(
                user=request.user,
                status='in_progress'
            ).first()

        if not submission:
            return None

        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()

        # 计算时间限制
        if obj.duration_minutes > 0:
            deadline = submission.started_at + timedelta(minutes=obj.duration_minutes)
            time_limit_deadline = deadline
        else:
            time_limit_deadline = obj.end_time

        # 取两者中较早的时间
        actual_deadline = min(time_limit_deadline, obj.end_time)
        remaining_seconds = max(0, int((actual_deadline - now).total_seconds()))

        return {
            'remaining_seconds': remaining_seconds,
        }


class ExamDetailSerializer(serializers.ModelSerializer):
    """测验详情序列化器"""
    course_title = serializers.ReadOnlyField(source='course.title')
    exam_problems = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    can_start = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    class Meta:
        model = Exam
        fields = [
            'id', 'course', 'course_title', 'title', 'description',
            'start_time', 'end_time', 'duration_minutes',
            'total_score', 'passing_score', 'status',
            'shuffle_questions', 'show_results_after_submit','question_count',
            'is_active', 'can_start', 'remaining_time', 'exam_problems'
        ]
        read_only_fields = ['total_score', 'created_at', 'updated_at']
    def get_question_count(self, obj):
        """获取题目数量"""
        return obj.exam_problems.count()
    def get_exam_problems(self, obj):
        """获取测验题目列表（不包含答案）"""
        exam_problems = obj.exam_problems.select_related('problem').order_by('order')
        problems_data = []

        for ep in exam_problems:
            problem_data = {
                'exam_problem_id': ep.id,
                'problem_id': ep.problem.id,
                'title': ep.problem.title,
                'content': ep.problem.content,
                'type': ep.problem.type,
                'difficulty': ep.problem.difficulty,
                'score': ep.score,
                'order': ep.order
            }

            # 根据题目类型添加额外信息
            if ep.problem.type == 'choice':
                choice_info = ep.problem.choice_info
                problem_data.update({
                    'options': choice_info.options,
                    'is_multiple_choice': choice_info.is_multiple_choice,
                })
            elif ep.problem.type == 'fillblank':
                fillblank_info = ep.problem.fillblank_info
                problem_data.update({
                    'content_with_blanks': fillblank_info.content_with_blanks,
                    'blanks_list': fillblank_info.blanks_list,
                    'blank_count': fillblank_info.blank_count,
                })

            problems_data.append(problem_data)

        return problems_data

    def get_is_active(self, obj):
        return obj.is_active()

    def get_can_start(self, obj):
        """检查当前用户是否可以开始测验"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        # 检查是否已注册课程
        if not obj.is_available_for_user(request.user):
            return False

        # 检查是否已经提交过
        if obj.submissions.filter(user=request.user).exists():
            return False

        # 检查是否在时间范围内
        from django.utils import timezone
        now = timezone.now()
        return obj.status == 'published' and obj.start_time <= now <= obj.end_time

    def get_remaining_time(self, obj):
        """获取剩余时间"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        submission = obj.submissions.filter(
            user=request.user,
            status='in_progress'
        ).first()

        if submission:
            from django.utils import timezone
            from datetime import timedelta

            now = timezone.now()

            # 计算时间限制
            if obj.duration_minutes > 0:
                deadline = submission.started_at + timedelta(minutes=obj.duration_minutes)
                time_limit_deadline = deadline
            else:
                time_limit_deadline = obj.end_time

            # 取两者中较早的时间
            actual_deadline = min(time_limit_deadline, obj.end_time)
            remaining_seconds = max(0, int((actual_deadline - now).total_seconds()))

            return {
                'remaining_seconds': remaining_seconds,
                'deadline': actual_deadline.isoformat()
            }

        return None


class ExamCreateSerializer(serializers.ModelSerializer):
    """测验创建序列化器"""
    exam_problems = serializers.ListField(
        write_only=True,
        child=serializers.DictField(),
        required=False
    )

    class Meta:
        model = Exam
        fields = [
            'course', 'title', 'description', 'start_time', 'end_time',
            'duration_minutes', 'passing_score', 'status',
            'shuffle_questions', 'show_results_after_submit', 'exam_problems'
        ]

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("结束时间必须晚于开始时间")

        return attrs

    def create(self, validated_data):
        exam_problems_data = validated_data.pop('exam_problems', [])
        exam = Exam.objects.create(**validated_data)

        # 设置标志：阻止 Exam 创建时的信号触发
        exam._skip_exam_problem_signals = True

        # 创建关联题目
        total_score = 0
        for ep_data in exam_problems_data:
            problem_id = ep_data.get('problem_id')
            score = ep_data.get('score', 10)
            order = ep_data.get('order', 0)

            try:
                problem = Problem.objects.get(id=problem_id)
                ExamProblem.objects.create(
                    exam=exam,
                    problem=problem,
                    score=score,
                    order=order
                )
                total_score += score
            except Problem.DoesNotExist:
                continue

        # 更新总分
        exam.total_score = total_score
        exam.save()

        # 重置标志：允许后续添加题目时触发信号
        exam._skip_exam_problem_signals = None

        return exam


class ExamAnswerDetailSerializer(serializers.ModelSerializer):
    """测验答案详情序列化器"""
    problem_title = serializers.ReadOnlyField(source='problem.title')
    problem_type = serializers.ReadOnlyField(source='problem.type')
    correct_answer = serializers.SerializerMethodField()
    problem_data = serializers.SerializerMethodField()

    class Meta:
        model = ExamAnswer
        fields = [
            'id', 'problem', 'problem_title', 'problem_type',
            'choice_answers', 'fillblank_answers',
            'score', 'is_correct', 'correct_percentage',
            'correct_answer', 'problem_data',
            'created_at'
        ]

    def get_correct_answer(self, obj):
        """Return correct answer based on problem type"""
        if obj.problem.type == 'choice':
            choice_info = obj.problem.choice_info
            return {
                'correct_answer': choice_info.correct_answer,
                'is_multiple': choice_info.is_multiple_choice,
                'all_options': choice_info.options
            }
        elif obj.problem.type == 'fillblank':
            fillblank_info = obj.problem.fillblank_info
            return {
                'blanks_list': fillblank_info.blanks_list,
                'case_sensitive': fillblank_info.case_sensitive
            }
        return None

    def get_problem_data(self, obj):
        """Return additional problem data for display"""
        return {
            'content': obj.problem.content,
            'difficulty': obj.problem.difficulty,
            'score': obj.submission.exam.exam_problems.get(problem=obj.problem).score
        }


class ExamSubmissionSerializer(serializers.ModelSerializer):
    """测验提交序列化器"""
    username = serializers.ReadOnlyField(source='user.username')
    exam_title = serializers.ReadOnlyField(source='exam.title')
    exam_passing_score = serializers.ReadOnlyField(source='exam.passing_score')
    exam_total_score = serializers.ReadOnlyField(source='exam.total_score')
    answers = ExamAnswerDetailSerializer(many=True, read_only=True)

    class Meta:
        model = ExamSubmission
        fields = [
            'id', 'exam', 'exam_title', 'user', 'username',
            'started_at', 'submitted_at', 'status',
            'total_score', 'is_passed', 'time_spent_seconds',
            'exam_passing_score', 'exam_total_score',
            'answers'
        ]
        read_only_fields = [
            'started_at', 'submitted_at', 'total_score',
            'is_passed', 'time_spent_seconds'
        ]


class ExamSubmissionCreateSerializer(serializers.Serializer):
    """开始测验序列化器"""
    def validate(self, attrs):
        request = self.context.get('request')
        exam_id = self.context.get('exam_id')

        # 获取测验
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            raise serializers.ValidationError("测验不存在")

        # 检查用户是否注册了课程
        if not exam.is_available_for_user(request.user):
            raise serializers.ValidationError("您尚未注册该课程")

        # 检查是否已经提交过（不包括 in_progress 状态）
        completed_statuses = ['submitted', 'auto_submitted', 'graded']
        if exam.submissions.filter(
            user=request.user,
            status__in=completed_statuses
        ).exists():
            raise serializers.ValidationError("您已经参加过该测验")

        # 检查测验是否在时间范围内
        from django.utils import timezone
        now = timezone.now()
        if not (exam.start_time <= now <= exam.end_time):
            raise serializers.ValidationError("测验不在开放时间内")

        return attrs


class ExamSubmitSerializer(serializers.Serializer):
    """提交答案序列化器"""
    answers = serializers.ListField(
        child=serializers.DictField(),
        required=True
    )

    def validate_answers(self, value):
        """验证答案格式"""
        if not value:
            raise serializers.ValidationError("答案不能为空")

        for answer in value:
            if 'problem_id' not in answer:
                raise serializers.ValidationError("答案必须包含 problem_id")

            problem_type = answer.get('problem_type')
            if problem_type == 'choice':
                if 'choice_answers' not in answer:
                    raise serializers.ValidationError("选择题必须包含 choice_answers")
            elif problem_type == 'fillblank':
                if 'fillblank_answers' not in answer:
                    raise serializers.ValidationError("填空题必须包含 fillblank_answers")

        return value