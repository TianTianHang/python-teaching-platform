from rest_framework import serializers
from .models import ChoiceProblem, Course, Chapter, Problem, AlgorithmProblem, TestCase, Submission, Enrollment, ChapterProgress, ProblemProgress


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
        if instance.type == "choice":
            data = {**data,**ChoiceProblemSerializer(instance.choice_info).data}
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

class ChoiceProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceProblem
        fields = ['problem', 'options', 'correct_answer', 'is_multiple_choice']
        
    def validate_options(self, value):
        """验证 options 字段格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("选项必须是字典格式，例如 {'A': '内容1', 'B': '内容2'}")
        if not value:
            raise serializers.ValidationError("选项不能为空")
        keys = list(value.keys())
        # 检查键是否为连续的大写字母 A, B, C...（可选，也可只检查是否为单个大写字母）
        if not all(isinstance(k, str) and len(k) == 1 and k.isupper() for k in keys):
            raise serializers.ValidationError("选项键必须是单个大写字母，如 A、B、C...")
        # 可选：检查是否从 'A' 开始连续（更严格）
        # expected_keys = [chr(ord('A') + i) for i in range(len(keys))]
        # if keys != expected_keys:
        #     raise serializers.ValidationError("选项键应从 A 开始连续排列")
        return value

    def validate_correct_answer(self, value):
        """初步验证 correct_answer 类型（具体合法性需结合 options 和 is_multiple_choice）"""
        # 类型检查将在 validate() 中结合其他字段完成
        return value

    def validate(self, attrs):
        """跨字段验证：correct_answer 必须在 options 的键中，且类型匹配 is_multiple_choice"""
        options = attrs.get('options')
        correct_answer = attrs.get('correct_answer')
        is_multiple_choice = attrs.get('is_multiple_choice', False)

        if options is None:
            # 如果是更新操作，options 可能未提供，需从 instance 获取
            if self.instance:
                options = self.instance.options
            else:
                raise serializers.ValidationError("options 字段缺失")

        if correct_answer is None:
            if self.instance:
                correct_answer = self.instance.correct_answer
            else:
                raise serializers.ValidationError("correct_answer 字段缺失")

        if is_multiple_choice:
            if not isinstance(correct_answer, list):
                raise serializers.ValidationError("多选题的正确答案必须是列表，例如 ['A', 'C']")
            if not correct_answer:
                raise serializers.ValidationError("多选题正确答案不能为空")
            if not all(isinstance(ans, str) for ans in correct_answer):
                raise serializers.ValidationError("多选题答案中的每个选项必须是字符串")
            if not all(ans in options for ans in correct_answer):
                invalid = [ans for ans in correct_answer if ans not in options]
                raise serializers.ValidationError(f"正确答案包含无效选项: {invalid}")
        else:
            if not isinstance(correct_answer, str):
                raise serializers.ValidationError("单选题的正确答案必须是字符串，例如 'A'")
            if correct_answer not in options:
                raise serializers.ValidationError(f"正确答案 '{correct_answer}' 不在选项中")

        return attrs
      
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


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    课程参与序列化器
    """
    user_username = serializers.ReadOnlyField(source='user.username')
    course_title = serializers.ReadOnlyField(source='course.title')
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'user_username', 'course', 'course_title', 
            'enrolled_at', 'last_accessed_at', 'progress_percentage'
        ]
        read_only_fields = ['user', 'enrolled_at', 'last_accessed_at', 'progress_percentage']
    
    def get_progress_percentage(self, obj):
        """
        计算课程完成进度百分比
        """
        total_chapters = obj.course.chapters.count()
        if total_chapters == 0:
            return 0
        
        completed_chapters = obj.chapter_progress.filter(completed=True).count()
        return round((completed_chapters / total_chapters) * 100, 2)


class ChapterProgressSerializer(serializers.ModelSerializer):
    """
    章节进度序列化器
    """
    chapter_title = serializers.ReadOnlyField(source='chapter.title')
    course_title = serializers.ReadOnlyField(source='chapter.course.title')
    
    class Meta:
        model = ChapterProgress
        fields = [
            'id', 'enrollment', 'chapter', 'chapter_title', 'course_title',
            'completed', 'completed_at'
        ]
        read_only_fields = ['completed_at']


class ProblemProgressSerializer(serializers.ModelSerializer):
    """
    问题进度序列化器
    """
    problem_title = serializers.ReadOnlyField(source='problem.title')
    chapter_title = serializers.ReadOnlyField(source='problem.chapter.title')
    course_title = serializers.ReadOnlyField(source='problem.chapter.course.title')
    
    class Meta:
        model = ProblemProgress
        fields = [
            'id', 'enrollment', 'problem', 'problem_title', 'chapter_title', 'course_title',
            'status', 'attempts', 'last_attempted_at', 'solved_at', 'best_submission'
        ]
        read_only_fields = ['attempts', 'last_attempted_at', 'solved_at', 'best_submission']