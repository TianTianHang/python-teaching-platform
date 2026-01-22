from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course, Chapter, Problem, AlgorithmProblem, ChoiceProblem, Enrollment, ChapterProgress, ProblemProgress

User = get_user_model()

class ProgressTrackingTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            st_number='123456'
        )
        
        # 创建测试课程
        self.course = Course.objects.create(
            title='Test Course',
            description='A test course for progress tracking'
        )
        
        # 创建测试章节
        self.chapter = Chapter.objects.create(
            course=self.course,
            title='Test Chapter',
            content='A test chapter',
            order=1
        )
        
        # 创建测试问题
        self.problem = Problem.objects.create(
            chapter=self.chapter,
            type='algorithm',
            title='Test Problem',
            content='A test algorithm problem',
            difficulty=2
        )
        
        # 创建算法题详情
        self.algorithm_problem = AlgorithmProblem.objects.create(
            problem=self.problem,
            time_limit=1000,
            memory_limit=256
        )
        
        # 创建选择题
        self.choice_problem = Problem.objects.create(
            chapter=self.chapter,
            type='choice',
            title='Test Choice Problem',
            content='A test choice problem',
            difficulty=1
        )
        
        self.choice_problem_detail = ChoiceProblem.objects.create(
            problem=self.choice_problem,
            options={'A': 'Option A', 'B': 'Option B', 'C': 'Option C'},
            correct_answer='A'
        )

    def test_enrollment_creation(self):
        """测试课程参与记录创建"""
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course
        )
        
        self.assertEqual(enrollment.user, self.user)
        self.assertEqual(enrollment.course, self.course)
        self.assertIsNotNone(enrollment.enrolled_at)
        self.assertIsNotNone(enrollment.last_accessed_at)
        
        # 测试唯一约束
        with self.assertRaises(Exception):
            Enrollment.objects.create(
                user=self.user,
                course=self.course
            )

    def test_chapter_progress(self):
        """测试章节进度记录"""
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course
        )
        
        chapter_progress = ChapterProgress.objects.create(
            enrollment=enrollment,
            chapter=self.chapter,
            completed=True
        )
        
        self.assertTrue(chapter_progress.completed)
        # self.assertIsNotNone(chapter_progress.completed_at)
        self.assertEqual(str(chapter_progress), f"{self.user.username} - {self.chapter.title} - 已完成")

    def test_problem_progress(self):
        """测试问题进度记录"""
        enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course
        )
        
        problem_progress = ProblemProgress.objects.create(
            enrollment=enrollment,
            problem=self.problem,
            status='solved'
        )
        
        self.assertEqual(problem_progress.status, 'solved')
        self.assertEqual(problem_progress.attempts, 0)
        self.assertIsNone(problem_progress.solved_at)
        
        # 更新尝试次数
        problem_progress.attempts = 1
        problem_progress.save()


class FillBlankImportTestCase(TestCase):
    """测试填空题导入功能"""

    def setUp(self):
        """设置测试数据"""
        from courses.models import FillBlankProblem

        self.valid_detailed_format = {
            'title': 'Python 基础填空题',
            'type': 'fillblank',
            'difficulty': 1,
            'content_with_blanks': 'Python 是一种 [blank1] 编程语言。',
            'blanks': {
                'blank1': {
                    'answers': ['解释型', '脚本'],
                    'case_sensitive': False
                }
            }
        }

        self.valid_simple_format = {
            'title': '简单填空题',
            'type': 'fillblank',
            'difficulty': 2,
            'content_with_blanks': 'Python 是 [blank1] 语言，作者是 [blank2]。',
            'blanks': {
                'blanks': ['解释型', 'Guido van Rossum'],
                'case_sensitive': False
            }
        }

        self.valid_list_format = {
            'title': '列表格式填空题',
            'type': 'fillblank',
            'difficulty': 3,
            'content_with_blanks': 'Python 使用 [blank1]。',
            'blanks': {
                'blanks': [
                    {'answers': ['pip'], 'case_sensitive': False}
                ]
            }
        }

    def test_validate_detailed_format(self):
        """测试详细格式验证"""
        from courses.course_import_services.markdown_parser import MarkdownFrontmatterParser

        # 应该通过验证
        try:
            MarkdownFrontmatterParser.validate_problem_frontmatter(self.valid_detailed_format)
        except Exception as e:
            self.fail(f"验证失败: {e}")

    def test_validate_simple_format(self):
        """测试简单格式验证"""
        from courses.course_import_services.markdown_parser import MarkdownFrontmatterParser

        # 应该通过验证
        try:
            MarkdownFrontmatterParser.validate_problem_frontmatter(self.valid_simple_format)
        except Exception as e:
            self.fail(f"验证失败: {e}")

    def test_validate_list_format(self):
        """测试列表格式验证"""
        from courses.course_import_services.markdown_parser import MarkdownFrontmatterParser

        # 应该通过验证
        try:
            MarkdownFrontmatterParser.validate_problem_frontmatter(self.valid_list_format)
        except Exception as e:
            self.fail(f"验证失败: {e}")

    def test_invalid_blank_key(self):
        """测试无效的 blank key"""
        from courses.course_import_services.markdown_parser import MarkdownFrontmatterParser

        invalid_format = self.valid_detailed_format.copy()
        invalid_format['blanks'] = {
            'blank2': {
                'answers': ['解释型'],
                'case_sensitive': False
            }
        }

        with self.assertRaises(ValueError):
            MarkdownFrontmatterParser.validate_problem_frontmatter(invalid_format)

    def test_missing_blank_definition(self):
        """测试缺失的 blank 定义"""
        from courses.course_import_services.markdown_parser import MarkdownFrontmatterParser

        invalid_format = self.valid_detailed_format.copy()
        invalid_format['content_with_blanks'] = 'Python 是 [blank1] 和 [blank2] 语言。'

        with self.assertRaises(ValueError):
            MarkdownFrontmatterParser.validate_problem_frontmatter(invalid_format)

    def test_blank_count_mismatch(self):
        """测试 blank count 不匹配"""
        from courses.course_import_services.markdown_parser import MarkdownFrontmatterParser

        invalid_format = self.valid_detailed_format.copy()
        invalid_format['blank_count'] = 5  # 实际只有 1 个 blank

        with self.assertRaises(ValueError) as cm:
            MarkdownFrontmatterParser.validate_problem_frontmatter(invalid_format)

        self.assertIn('blank_count', str(cm.exception))

    def test_extract_blank_markers(self):
        """测试提取 blank 标记"""
        from courses.course_import_services.markdown_parser import MarkdownFrontmatterParser

        content1 = 'Python 是 [blank1] 语言，作者是 [blank2]。'
        markers = MarkdownFrontmatterParser._extract_blank_markers(content1)
        self.assertEqual(markers, {1, 2})

        content2 = '只有 [blank1] 一个标记。'
        markers2 = MarkdownFrontmatterParser._extract_blank_markers(content2)
        self.assertEqual(markers2, {1})

        content3 = '没有标记。'
        markers3 = MarkdownFrontmatterParser._extract_blank_markers(content3)
        self.assertEqual(markers3, set())

    def test_validate_problem_frontmatter_with_fillblank(self):
        """测试 validate_problem_frontmatter 支持 fillblank 类型"""
        from courses.course_import_services.markdown_parser import MarkdownFrontmatterParser

        # 应该通过验证
        try:
            MarkdownFrontmatterParser.validate_problem_frontmatter(self.valid_detailed_format)
        except Exception as e:
            self.fail(f"验证失败: {e}")

    def test_problem_type_not_allowed(self):
        """测试不允许的问题类型"""
        from courses.course_import_services.markdown_parser import MarkdownFrontmatterParser
        
        invalid_format = self.valid_detailed_format.copy()
        invalid_format['type'] = 'invalid_type'

        with self.assertRaises(ValueError) as cm:
            MarkdownFrontmatterParser.validate_problem_frontmatter(invalid_format)

        self.assertIn('invalid_type', str(cm.exception))


class FillBlankImportIntegrationTestCase(TestCase):
    """集成测试：填空题导入完整流程"""

    def setUp(self):
        """设置测试环境"""
        from pathlib import Path
        import tempfile
        import shutil

        # 创建临时测试仓库
        self.test_repo = Path(tempfile.mkdtemp())

        # 创建课程目录结构
        self.courses_dir = self.test_repo / 'courses'
        self.courses_dir.mkdir()

        self.course_dir = self.courses_dir / 'test-course'
        self.course_dir.mkdir()

        # 创建 course.md
        course_md = self.course_dir / 'course.md'
        course_md.write_text('''---
title: 测试课程
description: 这是一个测试课程
---
测试课程内容
''', encoding='utf-8')

        # 创建 chapters 目录
        self.chapters_dir = self.course_dir / 'chapters'
        self.chapters_dir.mkdir()

        # 创建章节文件
        chapter_md = self.chapters_dir / 'chapter-01-intro.md'
        chapter_md.write_text('''---
title: 第一章
order: 1
---
第一章内容
''', encoding='utf-8')

        # 创建 problems 目录
        self.problems_dir = self.course_dir / 'problems'
        self.problems_dir.mkdir()

    def tearDown(self):
        """清理测试环境"""
        from pathlib import Path
        import shutil

        if self.test_repo.exists():
            shutil.rmtree(self.test_repo)

    def test_import_fillblank_problem_detailed_format(self):
        """测试导入详细格式的填空题"""
        from courses.course_import_services.course_importer import CourseImporter
        from courses.models import FillBlankProblem

        # 创建填空题文件（详细格式）
        problem_md = self.problems_dir / 'fillblank-detailed.md'
        problem_md.write_text('''---
title: Python 基础填空题
type: fillblank
difficulty: 1
chapter: 1
content_with_blanks: Python 是一种 [blank1] 编程语言，作者是 [blank2]。
blanks:
  blank1:
    answers:
      - 解释型
      - 脚本
    case_sensitive: false
  blank2:
    answers:
      - Guido van Rossum
      - Guido
    case_sensitive: false
blank_count: 2
---
详细格式的填空题示例
''', encoding='utf-8')

        # 执行导入
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()

        # 验证导入结果
        self.assertEqual(stats['courses_created'], 1)
        self.assertEqual(stats['chapters_created'], 1)
        self.assertEqual(stats['problems_created'], 1)

        # 验证填空题数据
        problem = FillBlankProblem.objects.first()
        self.assertIsNotNone(problem)
        self.assertEqual(problem.problem.title, 'Python 基础填空题')
        self.assertEqual(problem.problem.type, 'fillblank')
        self.assertEqual(problem.blank_count, 2)
        self.assertIn('[blank1]', problem.content_with_blanks)
        self.assertIn('[blank2]', problem.content_with_blanks)

    def test_import_fillblank_problem_simple_format(self):
        """测试导入简单格式的填空题"""
        from courses.course_import_services.course_importer import CourseImporter
        from courses.models import FillBlankProblem

        # 创建填空题文件（简单格式）
        problem_md = self.problems_dir / 'fillblank-simple.md'
        problem_md.write_text('''---
title: 简单填空题
type: fillblank
difficulty: 2
content_with_blanks: Python 是 [blank1] 语言，使用 [blank2] 进行包管理。
blanks:
  blanks:
    - 解释型
    - pip
  case_sensitive: false
---
简单格式的填空题示例
''', encoding='utf-8')

        # 执行导入
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()

        # 验证导入结果
        self.assertEqual(stats['problems_created'], 1)

        # 验证填空题数据
        problem = FillBlankProblem.objects.first()
        self.assertIsNotNone(problem)
        self.assertEqual(problem.problem.title, '简单填空题')
        self.assertEqual(problem.blank_count, 2)

    def test_import_fillblank_problem_list_format(self):
        """测试导入列表格式的填空题"""
        from courses.course_import_services.course_importer import CourseImporter
        from courses.models import FillBlankProblem

        # 创建填空题文件（列表格式）
        problem_md = self.problems_dir / 'fillblank-list.md'
        problem_md.write_text('''---
title: 列表格式填空题
type: fillblank
difficulty: 3
content_with_blanks: Python 的 [blank1] 是动态的。
blanks:
  blanks:
    - answers:
        - 类型系统
        - 类型
      case_sensitive: false
---
列表格式的填空题示例
''', encoding='utf-8')

        # 执行导入
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()

        # 验证导入结果
        self.assertEqual(stats['problems_created'], 1)

        # 验证填空题数据
        problem = FillBlankProblem.objects.first()
        self.assertIsNotNone(problem)
        self.assertEqual(problem.problem.title, '列表格式填空题')
        self.assertEqual(problem.blank_count, 1)

    def test_import_fillblank_problem_auto_calculate_blank_count(self):
        """测试自动计算 blank_count"""
        from courses.course_import_services.course_importer import CourseImporter
        from courses.models import FillBlankProblem

        # 创建不包含 blank_count 的填空题
        problem_md = self.problems_dir / 'fillblank-auto-count.md'
        problem_md.write_text('''---
title: 自动计算空格数
type: fillblank
difficulty: 1
content_with_blanks: Python 有 [blank1]、[blank2]、[blank3] 等特性。
blanks:
  blanks:
    - 简单
    - 易学
    - 开源
  case_sensitive: false
---
测试自动计算 blank_count
''', encoding='utf-8')

        # 执行导入
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()

        # 验证自动计算的 blank_count
        problem = FillBlankProblem.objects.first()
        self.assertIsNotNone(problem)
        self.assertEqual(problem.blank_count, 3)

    def test_import_fillblank_problem_update_mode(self):
        """测试更新模式"""
        from courses.course_import_services.course_importer import CourseImporter
        from courses.models import FillBlankProblem

        # 创建初始问题文件
        problem_md = self.problems_dir / 'fillblank-update.md'
        problem_md.write_text('''---
title: 更新测试题
type: fillblank
difficulty: 1
content_with_blanks: Python 是 [blank1] 语言。
blanks:
  blanks:
    - 脚本
  case_sensitive: false
---
测试更新模式
''', encoding='utf-8')

        # 第一次导入
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()
        self.assertEqual(stats['problems_created'], 1)

        # 修改问题文件
        problem_md.write_text('''---
title: 更新测试题
type: fillblank
difficulty: 2
content_with_blanks: Python 是 [blank1] 语言，创建于 [blank2]。
blanks:
  blank1:
    answers:
      - 脚本
      - 解释型
    case_sensitive: false
  blank2:
    answers:
      - "1991"
      - "1990"
    case_sensitive: false
---
测试更新模式 - 已修改
''', encoding='utf-8')

        # 第二次导入（更新模式）
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()
        self.assertEqual(stats['problems_updated'], 1)

        # 验证更新
        problem = FillBlankProblem.objects.first()
        self.assertIsNotNone(problem)
        self.assertEqual(problem.problem.difficulty, 2)
        self.assertEqual(problem.blank_count, 2)
        self.assertIn('[blank2]', problem.content_with_blanks)

    def test_import_fillblank_problem_skip_mode(self):
        """测试跳过模式"""
        from courses.course_import_services.course_importer import CourseImporter
        from courses.models import FillBlankProblem

        # 创建问题文件
        problem_md = self.problems_dir / 'fillblank-skip.md'
        problem_md.write_text('''---
title: 跳过测试题
type: fillblank
difficulty: 1
content_with_blanks: Python 是 [blank1] 语言。
blanks:
  blanks:
    - 脚本
  case_sensitive: false
---
测试跳过模式
''', encoding='utf-8')

        # 第一次导入
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()
        self.assertEqual(stats['problems_created'], 1)

        # 修改问题文件
        problem_md.write_text('''---
title: 跳过测试题
type: fillblank
difficulty: 3
content_with_blanks: Python 是 [blank1] 语言。
blanks:
  blanks:
    - 修改后的答案
  case_sensitive: false
---
测试跳过模式 - 已修改
''', encoding='utf-8')

        # 第二次导入（跳过模式）
        importer = CourseImporter(self.test_repo, update_mode=False)
        stats = importer.import_all()
        self.assertEqual(stats['courses_skipped'], 1)

        # 验证未被更新
        problem = FillBlankProblem.objects.first()
        self.assertIsNotNone(problem)
        self.assertEqual(problem.problem.difficulty, 1)  # 保持原值

    def test_import_fillblank_with_unlock_conditions(self):
        """测试带解锁条件的填空题导入"""
        from courses.course_import_services.course_importer import CourseImporter
        from courses.models import FillBlankProblem, ProblemUnlockCondition

        # 创建第一个问题（作为前置条件）
        problem1_md = self.problems_dir / 'problem-prerequisite.md'
        problem1_md.write_text('''---
title: 前置题目
type: fillblank
difficulty: 1
content_with_blanks: Python 是 [blank1]。
blanks:
  blanks:
    - 脚本
  case_sensitive: false
unlock_conditions:
  type: none
---
前置题目
''', encoding='utf-8')

        # 创建第二个问题（带解锁条件）
        problem2_md = self.problems_dir / 'problem-locked.md'
        problem2_md.write_text('''---
title: 后续题目
type: fillblank
difficulty: 2
content_with_blanks: Python 使用 [blank1]。
blanks:
  blanks:
    - pip
  case_sensitive: false
unlock_conditions:
  type: prerequisite
  prerequisites:
    - problem-prerequisite.md
---
带解锁条件的题目
''', encoding='utf-8')

        # 执行导入
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()

        # 验证导入结果
        self.assertEqual(stats['problems_created'], 2)

        # 验证解锁条件
        locked_problem = Problem.objects.get(title='后续题目')
        unlock_condition = ProblemUnlockCondition.objects.filter(problem=locked_problem).first()
        self.assertIsNotNone(unlock_condition)
        self.assertEqual(unlock_condition.unlock_condition_type, 'prerequisite')
        self.assertEqual(unlock_condition.prerequisite_problems.count(), 1)

    def test_backward_compatibility_with_algorithm_problems(self):
        """测试向后兼容：算法题导入仍能正常工作"""
        from courses.course_import_services.course_importer import CourseImporter
        from courses.models import AlgorithmProblem

        # 创建算法题
        problem_md = self.problems_dir / 'algorithm-problem.md'
        problem_md.write_text('''---
title: 两数之和
type: algorithm
difficulty: 1
solution_name: two_sum
test_cases:
  - input: "2 7\\n11 15"
    output: "0 1"
  - input: "3 2\\n3 3"
    output: "0 1"
time_limit: 1000
memory_limit: 256
---
算法题示例
''', encoding='utf-8')

        # 执行导入
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()

        # 验证算法题导入正常
        self.assertEqual(stats['problems_created'], 1)
        algo_problem = AlgorithmProblem.objects.first()
        self.assertIsNotNone(algo_problem)
        self.assertEqual(algo_problem.problem.title, '两数之和')
        self.assertEqual(algo_problem.time_limit, 1000)

    def test_backward_compatibility_with_choice_problems(self):
        """测试向后兼容：选择题导入仍能正常工作"""
        from courses.course_import_services.course_importer import CourseImporter
        from courses.models import ChoiceProblem

        # 创建选择题
        problem_md = self.problems_dir / 'choice-problem.md'
        problem_md.write_text('''---
title: Python 特点
type: choice
difficulty: 1
options:
  A: 编译型语言
  B: 解释型语言
  C: 汇编语言
  D: 机器语言
correct_answer: B
is_multiple_choice: false
---
选择题示例
''', encoding='utf-8')

        # 执行导入
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()

        # 验证选择题导入正常
        self.assertEqual(stats['problems_created'], 1)
        choice_problem = ChoiceProblem.objects.first()
        self.assertIsNotNone(choice_problem)
        self.assertEqual(choice_problem.problem.title, 'Python 特点')
        self.assertEqual(choice_problem.correct_answer, 'B')

    def test_import_multiple_fillblank_problems(self):
        """测试导入多个填空题"""
        from courses.course_import_services.course_importer import CourseImporter
        from courses.models import FillBlankProblem

        # 创建多个填空题
        for i in range(3):
            problem_md = self.problems_dir / f'fillblank-{i}.md'
            problem_md.write_text(f'''---
title: 填空题 {i+1}
type: fillblank
difficulty: {i+1}
content_with_blanks: 这是第 [blank1] 题。
blanks:
  blanks:
    - "{i+1}"
  case_sensitive: false
---
填空题 {i+1} 内容
''', encoding='utf-8')

        # 执行导入
        importer = CourseImporter(self.test_repo, update_mode=True)
        stats = importer.import_all()

        # 验证所有题目都被导入
        self.assertEqual(stats['problems_created'], 3)
        self.assertEqual(FillBlankProblem.objects.count(), 3)