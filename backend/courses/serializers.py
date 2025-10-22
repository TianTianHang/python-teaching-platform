from rest_framework import serializers
from .models import Course, Chapter, Problem, AlgorithmProblem, TestCase, Submission


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
    chapter_title =serializers.ReadOnlyField(source="chapter.title")
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.type == "algorithm":
            data = {**data,**AlgorithmProblemSerializer(instance.algorithm_info).data}
        return data
    class Meta:
        model = Problem
        fields = ["id", "type", "chapter_title","title","content","difficulty","created_at","updated_at"]
        read_only_fields = ["created_at", "updated_at"]
        

class AlgorithmProblemSerializer(serializers.ModelSerializer):
    sample_cases = serializers.SerializerMethodField()
    def get_sample_cases(self, obj):
        sample_test_cases = obj.test_cases.filter(is_sample=True).order_by('id')
        
        return TestCaseSerializer(sample_test_cases, many=True).data
    class Meta:
        model = AlgorithmProblem
        fields = ["time_limit","memory_limit","code_template","sample_cases"]
      
      
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