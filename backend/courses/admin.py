from django.contrib import admin
from .models import Chapter, ChoiceProblem, Course,Problem,AlgorithmProblem, ProblemProgress, Submission, TestCase
# Register your models here.
admin.site.register(Course)
admin.site.register(Chapter)
admin.site.register(Problem)
admin.site.register(AlgorithmProblem)
admin.site.register(ChoiceProblem)
admin.site.register(Submission)
admin.site.register(TestCase)
admin.site.register(ProblemProgress)