from rest_framework import serializers
from .models import Course, Chapter, Problem


class CourseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class ChapterSerializer(serializers.ModelSerializer):
    # 这里不需要 course 或 course_id 字段来接收输入，因为它会在 ViewSet 中通过 URL 上下文设置
    # 但你可以在输出时显示所属课程的ID或名字
    course_title = serializers.ReadOnlyField(
        source="course.title"
    )  # 显示所属课程的标题

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
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
        ]  # course 字段在创建和更新时将通过 ViewSet 自动设置


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["id", "type", "title", "content", "correct_answer"]
        read_only_fields = ["created_at", "updated_at"]
