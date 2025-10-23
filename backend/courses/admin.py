from django.contrib import admin
from .models import Chapter, Course,Problem,AlgorithmProblem, Submission, TestCase
# Register your models here.
admin.site.register(Course)
admin.site.register(Chapter)
admin.site.register(Problem)
admin.site.register(AlgorithmProblem)
admin.site.register(Submission)
admin.site.register(TestCase)