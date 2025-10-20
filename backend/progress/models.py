# backend/progress/models.py
from django.db import models
from django.conf import settings
from courses.models import Chapter

class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'chapter')  # One progress entry per user/chapter
        verbose_name_plural = "User progress"

    def __str__(self):
        return f"{self.user.username} - {self.chapter.title}"

'''
class Submission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    code = models.TextField()
    output = models.TextField(blank=True)  # From Pyodide or Go judge
    passed = models.BooleanField(default=False)  # For future auto-grading
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.username} on {self.chapter.title}"
'''
