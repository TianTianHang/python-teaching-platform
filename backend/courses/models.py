from django.db import models

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