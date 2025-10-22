from django.contrib import admin
from .models import Chapter, Course,Problem,AlgorithmProblem
# Register your models here.
admin.site.register(Course)
admin.site.register(Chapter)
admin.site.register(Problem)
admin.site.register(AlgorithmProblem)