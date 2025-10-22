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
    TYPES ={'algorithm':'算法题'}
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
    code_template = models.JSONField(blank=True,null=True,verbose_name="编码模板") # 格式 {{"id":1,"template":""},{}}
    class Meta:
        verbose_name = "算法题"
        verbose_name_plural = "算法题列表"
    def __str__(self):
        return f'{self.problem.type}-{self.problem.title}'
    
class TestCase(models.Model):
    
    problem = models.ForeignKey(AlgorithmProblem, on_delete=models.CASCADE, related_name='test_cases', verbose_name="所属问题")
    input_data = models.TextField(verbose_name="输入数据")
    expected_output = models.TextField(verbose_name="预期输出")
    is_sample = models.BooleanField(default=False, verbose_name="是否为示例测试用例")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    def __str__(self):
        return f"问题 {self.problem.title} 的测试用例 {self.id}"
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
        null=True
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