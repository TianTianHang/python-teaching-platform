from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from accounts.models import User
# Create your models here.
class Course(models.Model):
    """
    课程模型
    """
    title = models.CharField(max_length=200, verbose_name="课程标题")
    description = models.TextField(blank=True, verbose_name="课程描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    class Meta:
        verbose_name = "课程"
        verbose_name_plural = "课程"
        ordering = ['title'] # 默认按标题排序
    def __str__(self):
        return self.title
    
class Chapter(models.Model):
    """
    章节模型
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='chapters', # 通过 course.chapters 可以访问所有章节
        verbose_name="所属课程"
    )
    title = models.CharField(max_length=200, verbose_name="章节标题")
    content = models.TextField(blank=True, verbose_name="章节内容")
    order = models.PositiveIntegerField(default=0, verbose_name="章节顺序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    class Meta:
        verbose_name = "章节"
        verbose_name_plural = "章节"
        # 联合唯一索引，确保同一个课程下的章节标题和顺序是唯一的
        unique_together = ('course', 'order')
        ordering = ['course', 'order'] # 默认按课程和顺序排序
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
class Problem(models.Model):
    """
    问题模型
    """
    TYPES ={'algorithm':'算法题',"choice":"选择题","fillblank":"填空题"}
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        related_name='problems', # 通过 chapter.problems 可以访问所有问题
        verbose_name="所属章节",
        null=True, # 允许为空
        blank=True # 允许在 Admin 中为空
    )
    type = models.CharField(max_length=20, choices=TYPES, verbose_name="问题类型", db_index=True)
    title = models.CharField(max_length=200, verbose_name="问题标题")
    content = models.TextField(verbose_name="问题内容")
    difficulty = models.PositiveSmallIntegerField(verbose_name="难度等级", validators=[MinValueValidator(1),MaxValueValidator(3)]) #1-3
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    class Meta:
        verbose_name = "问题"
        verbose_name_plural = "问题列表"
    def __str__(self):
        return f"{self.type} - {self.title}"

class ProblemUnlockCondition(models.Model):
    """
    问题解锁条件模型
    支持多种解锁条件，如前置题目、解锁日期等
    """
    problem = models.OneToOneField(
        Problem,
        on_delete=models.CASCADE,
        related_name='unlock_condition',
        verbose_name="解锁条件关联的问题"
    )

    # 前置题目解锁条件
    prerequisite_problems = models.ManyToManyField(
        Problem,
        related_name='dependent_problems',
        blank=True,
        verbose_name="前置题目",
        help_text="必须完成这些前置题目才能解锁当前题目"
    )

    # 解锁日期条件
    unlock_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="解锁日期",
        help_text="在此日期之前题目将被锁定"
    )

    # 解锁条件类型
    unlock_condition_type = models.CharField(
        max_length=20,
        choices=[
            ('prerequisite', '前置题目'),
            ('date', '解锁日期'),
            ('both', '前置题目和解锁日期'),
            ('none', '无条件'),
        ],
        default='none',
        verbose_name="解锁条件类型"
    )


    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "题目解锁条件"
        verbose_name_plural = "题目解锁条件"

    def __str__(self):
        conditions = []

        # Add unlock condition type
        if self.unlock_condition_type == 'prerequisite':
            conditions.append("前置题目")
        elif self.unlock_condition_type == 'date':
            conditions.append("解锁日期")
        elif self.unlock_condition_type == 'both':
            conditions.append("前置题目和解锁日期")
        elif self.unlock_condition_type == 'none':
            conditions.append("无条件")

        # Add prerequisite count if applicable
        if self.prerequisite_problems.exists():
            prereq_count = self.prerequisite_problems.count()
            conditions.append(f"需要完成{prereq_count}个前置题目")

        # Add unlock date if applicable
        if self.unlock_date:
            conditions.append(f"解锁日期: {self.unlock_date.strftime('%Y-%m-%d %H:%M')}")


        condition_str = ", ".join(conditions) if conditions else "无条件"
        return f"解锁条件: {self.problem.title} ({condition_str})"

    def is_unlocked(self, user):
        """
        检查题目是否对用户解锁
        """
        from django.utils import timezone

        # 检查解锁日期
        if self.unlock_date and self.unlock_date > timezone.now():
            return False

        # 检查前置题目条件
        if self.prerequisite_problems.exists():
            if self.unlock_condition_type in ['prerequisite', 'both']:
                from .models import ProblemProgress, Submission

                # 获取用户已完成的前置题目
                completed_prerequisites = set()
                for prereq in self.prerequisite_problems.all():
                    # 检查用户是否已完成该前置题目
                    try:
                        progress = ProblemProgress.objects.get(
                            enrollment__user=user,
                            problem=prereq
                        )
                        if progress.status == 'solved':
                            completed_prerequisites.add(prereq.id)
                    except ProblemProgress.DoesNotExist:
                        # 检查是否有通过的提交记录
                        if Submission.objects.filter(
                            user=user,
                            problem=prereq,
                            status='accepted'
                        ).exists():
                            completed_prerequisites.add(prereq.id)

                # 检查是否完成了所有前置题目
                required_prerequisites = set(self.prerequisite_problems.values_list('id', flat=True))

               
                # 检查是否完成所有前置题目
                if completed_prerequisites != required_prerequisites:
                    return False


        return True

class AlgorithmProblem(models.Model):
    problem = models.OneToOneField(
        Problem,
        on_delete=models.CASCADE,
        related_name="algorithm_info",
        verbose_name="关联问题主表"
    )
    time_limit = models.PositiveSmallIntegerField(
        verbose_name="时间限制（毫秒）",
        default=1000,
        help_text="毫秒"
        )
    memory_limit = models.PositiveSmallIntegerField(
        verbose_name="内存限制（MB）",
        default=256,
        help_text="MB"
    )
    code_template = models.JSONField(blank=True,null=True,verbose_name="编码模板") # 格式 {"python":""}
    solution_name = models.JSONField(blank=True,null=True,verbose_name="soultion fuction name") # {"python":}
    class Meta:
        verbose_name = "算法题"
        verbose_name_plural = "算法题列表"
    def __str__(self):
        return f'{self.problem.type}-{self.problem.title}'
    
class ChoiceProblem(models.Model):
    problem = models.OneToOneField(
        Problem,
        on_delete=models.CASCADE,
        related_name="choice_info",
        verbose_name="关联问题主表"
    )
    options = models.JSONField(verbose_name="选项列表") #{'A':'','B':''}
    correct_answer = models.JSONField(verbose_name="正确答案", help_text="单选时为字符串（如 'A'），多选时为列表（如 ['A', 'C']）")
    is_multiple_choice = models.BooleanField(default=False, verbose_name="是否为多选题")

    class Meta:
        verbose_name = "选择题详情"
        verbose_name_plural = "选择题列表"

    def __str__(self):
        return f"选择题: {self.problem.title if hasattr(self.problem, 'title') else self.problem.id}"

class FillBlankProblem(models.Model):
    """
    填空题模型
    用户需要在文本中填写一个或多个空白处的答案
    """
    problem = models.OneToOneField(
        Problem,
        on_delete=models.CASCADE,
        related_name="fillblank_info",
        verbose_name="关联问题主表"
    )

    # 带空白标记的文本内容
    content_with_blanks = models.TextField(
        verbose_name="带空白的内容",
        help_text="使用 [blank1], [blank2] 等标记空白位置"
    )

    # 空白答案配置（JSON格式）
    blanks = models.JSONField(
        verbose_name="空白答案配置",
        help_text=(
            "格式1（详细）: {'blank1': {'answer': ['答案1', '备选'], 'case_sensitive': False}, "
            "'blank2': {'answer': ['答案2'], 'case_sensitive': True}}. "
            "格式2（简单）: {'blanks': ['答案1', '答案2'], 'case_sensitive': False}. "
            "格式3（推荐）: {'blanks': [{'answers': ['答案1', '备选1'], 'case_sensitive': False}, "
            "{'answers': ['答案2'], 'case_sensitive': True}]}"
        )
    )

    # 空白数量（冗余字段，便于查询）
    blank_count = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="空白数量"
    )

    class Meta:
        verbose_name = "填空题"
        verbose_name_plural = "填空题列表"

    def __str__(self):
        return f"填空题: {self.problem.title}"

    def clean(self):
        """
        验证 blanks 字段格式
        """
        from django.core.exceptions import ValidationError

        if not isinstance(self.blanks, dict):
            raise ValidationError("blanks 必须是字典格式")

        # 验证格式1（详细）
        if all(k.startswith('blank') for k in self.blanks.keys()):
            for blank_id, config in self.blanks.items():
                if not isinstance(config, dict):
                    raise ValidationError(f"{blank_id} 配置必须是字典")
                if 'answer' not in config and 'answers' not in config:
                    raise ValidationError(f"{blank_id} 缺少 answer 或 answers 字段")

        # 验证格式2（简单）
        elif 'blanks' in self.blanks:
            blanks_list = self.blanks['blanks']
            if not isinstance(blanks_list, list):
                raise ValidationError("blanks 字段必须是列表")

            # 格式3（推荐）
            if blanks_list and isinstance(blanks_list[0], dict):
                for i, blank in enumerate(blanks_list):
                    if 'answers' not in blank:
                        raise ValidationError(f"第{i+1}个空白缺少 answers 字段")
                    if not isinstance(blank['answers'], list):
                        raise ValidationError(f"第{i+1}个空白的 answers 必须是列表")

            self.blank_count = len(blanks_list)

        else:
            raise ValidationError("blanks 格式不正确，请使用支持的格式之一")

class TestCase(models.Model):
    
    problem = models.ForeignKey(AlgorithmProblem, on_delete=models.CASCADE, related_name='test_cases', verbose_name="所属问题")
    input_data = models.TextField(verbose_name="输入数据")
    expected_output = models.TextField(verbose_name="预期输出")
    is_sample = models.BooleanField(default=False, verbose_name="是否为示例测试用例")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    def __str__(self):
        return f"问题 {self.problem.problem.title} 的测试用例 {self.id}"
    class Meta:
        verbose_name = "测试用例"
        verbose_name_plural = "测试用例"


class Submission(models.Model):
    """
    用户提交记录模型
    只有算法题的提交才会创建此记录
    """
    STATUS_CHOICES = (
        ('pending', '待评测'),
        ('judging', '评测中'),
        ('accepted', '通过'),
        ('wrong_answer', '答案错误'),
        ('time_limit_exceeded', '超时'),
        ('memory_limit_exceeded', '内存超限'),
        ('runtime_error', '运行时错误'),
        ('compilation_error', '编译错误'),
        ('internal_error', '系统错误'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="提交用户"
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        verbose_name="提交的问题",
        blank=True,
        null=True,
    )
    code = models.TextField(verbose_name="提交的代码")
    language = models.CharField(max_length=50, verbose_name="编程语言", default="python")
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="评测状态"
    )
    execution_time = models.FloatField(null=True, blank=True, verbose_name="执行时间(毫秒)")
    memory_used = models.FloatField(null=True, blank=True, verbose_name="内存使用(KB)")
    output = models.TextField(blank=True, verbose_name="程序输出")
    error = models.TextField(blank=True, verbose_name="错误信息")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "提交记录"
        verbose_name_plural = "提交记录"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.status}"

class CodeDraft(models.Model):
    """
    代码草稿历史模型
    存储用户在算法题上的代码保存记录，包括自动保存、手动保存和提交记录
    """
    SAVE_TYPE_CHOICES = (
        ('auto_save', '自动保存'),
        ('manual_save', '手动保存'),
        ('submission', '提交记录'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='code_drafts',
        verbose_name="用户"
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='code_drafts',
        verbose_name="问题",
        limit_choices_to={'type': 'algorithm'}
    )
    code = models.TextField(verbose_name="代码内容")
    language = models.CharField(
        max_length=50,
        verbose_name="编程语言",
        default='python'
    )
    save_type = models.CharField(
        max_length=20,
        choices=SAVE_TYPE_CHOICES,
        default='auto_save',
        verbose_name="保存类型",
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    submission = models.ForeignKey(
        'Submission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='code_drafts',
        verbose_name="关联提交记录"
    )

    class Meta:
        verbose_name = "代码草稿"
        verbose_name_plural = "代码草稿历史"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'problem', '-created_at']),
            models.Index(fields=['user', 'problem', 'save_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.get_save_type_display()} - {self.created_at}"

class Enrollment(models.Model):
    """
    用户课程注册模型
    记录用户参与的课程及学习进度
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="参与用户"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="参与课程"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="注册时间")
    last_accessed_at = models.DateTimeField(auto_now=True, verbose_name="最后访问时间")
    
    class Meta:
        unique_together = ('user', 'course')
        verbose_name = "课程参与"
        verbose_name_plural = "课程参与记录"
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

class ChapterProgress(models.Model):
    """
    章节学习进度模型
    记录用户在特定章节的学习完成状态
    """
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='chapter_progress',
        verbose_name="课程参与记录"
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name="章节"
    )
    completed = models.BooleanField(default=False, verbose_name="是否完成")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    
    class Meta:
        unique_together = ('enrollment', 'chapter')
        verbose_name = "章节进度"
        verbose_name_plural = "章节进度记录"
    
    def __str__(self):
        status = "已完成" if self.completed else "未完成"
        return f"{self.enrollment.user.username} - {self.chapter.title} - {status}"

class ProblemProgress(models.Model):
    """
    问题解决进度模型
    记录用户解决问题的进度和状态
    """
    PROGRESS_STATUS = (
        ('not_started', '未开始'),
        ('in_progress', '进行中'),
        ('solved', '已解决'),
        ('failed', '失败'),
    )
    
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='problem_progress',
        verbose_name="课程参与记录"
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name="问题"
    )
    status = models.CharField(
        max_length=20,
        choices=PROGRESS_STATUS,
        default='not_started',
        verbose_name="解决状态"
    )
    attempts = models.PositiveIntegerField(default=0, verbose_name="尝试次数")
    last_attempted_at = models.DateTimeField(null=True, blank=True, verbose_name="最后尝试时间")
    solved_at = models.DateTimeField(null=True, blank=True, verbose_name="解决时间")
    
    # 对于算法题，可以记录最好成绩的提交
    best_submission = models.ForeignKey(
        Submission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="最佳提交"
    )
    
    class Meta:
        unique_together = ('enrollment', 'problem')
        verbose_name = "问题进度"
        verbose_name_plural = "问题进度记录"
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.problem.title} - {self.status}"
    
    
    
class DiscussionThread(models.Model):
    """讨论主题（主帖）"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussion_threads', 
                                null=True, 
                                blank=True 
            )
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='discussion_threads',
                                null=True,
                                blank=True
                                )
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='discussion_threads',
                                null=True,
                                blank=True
                                )
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='started_threads')
    title = models.CharField(max_length=200)
    content = models.TextField()  # Markdown
    
    # 状态字段
    is_pinned = models.BooleanField(default=False, help_text="是否置顶")
    is_resolved = models.BooleanField(default=False, help_text="是否已解决（问答场景）")
    is_archived = models.BooleanField(default=False, help_text="是否归档")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 统计字段（可选，避免频繁 COUNT）
    reply_count = models.PositiveIntegerField(default=0)
    last_activity_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-last_activity_at']
        indexes = [
            models.Index(fields=['course', '-last_activity_at']),
        ]
        verbose_name = "主题贴"
        verbose_name_plural = "主题贴"
    def __str__(self):
        return f"{self.title} ({self.course})"


class DiscussionReply(models.Model):
    """回复（包括对主题的回复，或对回复的回复）"""
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_replies')
    content = models.TextField()
    
    # # 支持“回复某条回复”（可选）
    # parent = models.ForeignKey(
    #     'self',
    #     null=True,
    #     blank=True,
    #     on_delete=models.CASCADE,
    #     related_name='children'
    # )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 用于通知
    mentioned_users = models.ManyToManyField(User, blank=True, related_name='mentioned_in_replies')

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['thread', 'created_at']),
        ]

    def __str__(self):
        return f"Reply by {self.author} on {self.thread.title}"


# ============================================================================
# 测验功能相关模型
# ============================================================================

class Exam(models.Model):
    """
    测验模型 - 关联到课程
    """
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='exams',
        verbose_name="所属课程"
    )
    title = models.CharField(max_length=200, verbose_name="测验标题")
    description = models.TextField(blank=True, verbose_name="测验描述")

    # 时间限制
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="结束时间")
    duration_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="答题时长(分钟)",
        help_text="0表示不限制，以结束时间为准"
    )

    # 分数设置
    total_score = models.PositiveIntegerField(
        default=100,
        verbose_name="总分",
        help_text="由系统根据题目分数自动计算"
    )
    passing_score = models.PositiveIntegerField(
        default=60,
        verbose_name="及格分数"
    )

    # 状态控制
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="状态"
    )

    # 显示设置
    shuffle_questions = models.BooleanField(
        default=False,
        verbose_name="是否随机排序题目"
    )
    show_results_after_submit = models.BooleanField(
        default=True,
        verbose_name="提交后立即显示结果"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "测验"
        verbose_name_plural = "测验列表"
        ordering = ['course', '-start_time']
        indexes = [
            models.Index(fields=['course', 'status']),
            models.Index(fields=['start_time', 'end_time']),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def is_active(self):
        """检查测验是否正在进行中"""
        from django.utils import timezone
        now = timezone.now()
        return self.status == 'published' and self.start_time <= now <= self.end_time

    def is_available_for_user(self, user):
        """检查用户是否有权参加测验(必须已注册课程)"""
        return Enrollment.objects.filter(
            user=user,
            course=self.course
        ).exists()


class ExamProblem(models.Model):
    """
    测验-题目关联表(中间表)
    定义题目在测验中的属性
    """
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='exam_problems',
        verbose_name="所属测验"
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='exam_problems',
        verbose_name="关联题目"
    )

    # 题目在测验中的属性
    score = models.PositiveIntegerField(
        default=10,
        verbose_name="题目分值",
        validators=[MinValueValidator(1)]
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="题目顺序"
    )

    # 可选:题目是否必答(未来扩展)
    is_required = models.BooleanField(
        default=True,
        verbose_name="是否必答"
    )

    class Meta:
        verbose_name = "测验题目"
        verbose_name_plural = "测验题目列表"
        unique_together = ('exam', 'problem')  # 同一题目在同一测验中只能出现一次
        ordering = ['exam', 'order', 'id']

    def __str__(self):
        return f"{self.exam.title} - {self.problem.title} ({self.score}分)"

    def clean(self):
        """
        验证只能添加选择题和填空题
        """
        from django.core.exceptions import ValidationError
        valid_types = ['choice', 'fillblank']
        if self.problem.type not in valid_types:
            raise ValidationError(f'测验只能包含选择题和填空题，不能包含{self.problem.type}类型的题目')


class ExamSubmission(models.Model):
    """
    用户测验提交记录
    记录用户对某次测验的提交状态
    """
    STATUS_CHOICES = (
        ('in_progress', '进行中'),
        ('submitted', '已提交'),
        ('auto_submitted', '自动提交(超时)'),
        ('graded', '已评分'),
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name="所属测验"
    )
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='exam_submissions',
        verbose_name="课程注册记录"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exam_submissions',
        verbose_name="提交用户"
    )

    # 时间记录
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="开始时间"
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="提交时间"
    )

    # 评分结果
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name="状态"
    )
    total_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="总分"
    )
    is_passed = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="是否及格"
    )

    # 时间统计
    time_spent_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="用时(秒)"
    )

    class Meta:
        verbose_name = "测验提交"
        verbose_name_plural = "测验提交记录"
        unique_together = ('exam', 'user')  # 每个用户对同一测验只能提交一次
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['exam', 'user']),
            models.Index(fields=['status', '-started_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} ({self.get_status_display()})"

    def calculate_total_score(self):
        """计算总分"""
        return sum(
            answer.score for answer in self.answers.all()
            if answer.score is not None
        )

    def check_is_passed(self):
        """检查是否及格"""
        if self.total_score is None:
            return None
        return self.total_score >= self.exam.passing_score


class ExamAnswer(models.Model):
    """
    测验答案详情
    记录用户对测验中每个题目的答案
    """
    submission = models.ForeignKey(
        ExamSubmission,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="所属提交"
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='exam_answers',
        verbose_name="题目"
    )

    # 用户答案
    # 选择题答案
    choice_answers = models.JSONField(
        blank=True,
        null=True,
        verbose_name="选择题答案"
    )
    # 填空题答案
    fillblank_answers = models.JSONField(
        blank=True,
        null=True,
        verbose_name="填空题答案"
    )

    # 评分结果
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="得分"
    )
    is_correct = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="是否正确"
    )
    correct_percentage = models.FloatField(
        null=True,
        blank=True,
        verbose_name="正确比例（用于填空题）"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "测验答案"
        verbose_name_plural = "测验答案详情"
        unique_together = ('submission', 'problem')  # 每个提交中每题只有一个答案
        ordering = ['submission', 'problem__id']

    def __str__(self):
        return f"{self.submission.user.username} - {self.problem.title}"