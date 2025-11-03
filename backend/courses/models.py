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
    TYPES ={'algorithm':'算法题',"choice":"选择题"}
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