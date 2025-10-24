"""
Management command to populate sample Python courses, chapters, and algorithm problems
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import ChoiceProblem, Course, Chapter, Problem, AlgorithmProblem, TestCase

from django.contrib.auth.hashers import make_password
class Command(BaseCommand):
    help = 'Populate the database with sample Python courses, chapters, and algorithm problems'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Create a default user if none exists
        default_user, created = User.objects.get_or_create(
            username='default_student',
            defaults={
                'email': 'student@example.com',
                'is_active': True,
                'password': make_password('123456')
            }
        )
        
        # Check if sample data already exists
        if Course.objects.filter(title="Python编程入门").exists():
            self.stdout.write(
                self.style.WARNING('Sample data already exists. Skipping.')
            )
            return

        # Create Python Programming Course
        python_course = Course.objects.create(
            title="Python编程入门",
            description="学习Python编程的基础知识，包括语法、数据结构、函数等概念。"
        )
        
        self.stdout.write(f'Created course: {python_course.title}')

        # Create chapters for Python Programming Course
        chapter1 = Chapter.objects.create(
            course=python_course,
            title="Python基础语法",
            content="本章介绍Python的基本语法，包括变量、数据类型、运算符等。",
            order=1
        )
        
        self.stdout.write(f'Created chapter: {chapter1.title}')

        chapter2 = Chapter.objects.create(
            course=python_course,
            title="控制结构",
            content="本章介绍Python中的条件语句和循环语句。",
            order=2
        )
        
        self.stdout.write(f'Created chapter: {chapter2.title}')

        chapter3 = Chapter.objects.create(
            course=python_course,
            title="函数与模块",
            content="本章介绍如何定义和使用函数，以及Python模块的基本概念。",
            order=3
        )
        
        self.stdout.write(f'Created chapter: {chapter3.title}')

        chapter4 = Chapter.objects.create(
            course=python_course,
            title="数据结构",
            content="本章介绍Python中的列表、字典、集合等数据结构。",
            order=4
        )
        
        self.stdout.write(f'Created chapter: {chapter4.title}')

        # Create algorithm problems for Chapter 1
        problem1 = Problem.objects.create(
            chapter=chapter1,
            type='algorithm',
            title="两数之和",
            content="给定一个整数数组和一个目标值，找出数组中和为目标值的两个数的下标。",
            difficulty=1
        )
        
        algorithm_problem1 = AlgorithmProblem.objects.create(
            problem=problem1,
            time_limit=1000,
            memory_limit=256,
             code_template={
                "python": "def twoSum(nums, target):\n    # 请在此实现你的代码\n    pass"
            },
            solution_name={
                "python": "twoSum"
            }
        )
        
        # Add test cases for two sum problem
        TestCase.objects.create(
            problem=algorithm_problem1,
            input_data="[[2, 7, 11, 15], 9]",
            expected_output="[0, 1]",
            is_sample=True
        )
        
        TestCase.objects.create(
            problem=algorithm_problem1,
            input_data="[[3, 2, 4], 6]",
            expected_output="[1, 2]",
        )
        
        TestCase.objects.create(
            problem=algorithm_problem1,
            input_data="[[3, 3], 6]",
            expected_output="[0, 1]"
        )
        
        self.stdout.write(f'Created problem: {problem1.title}')
        
        problem2 = Problem.objects.create(
            chapter=chapter1,
            type='algorithm',
            title="回文数判断",
            content="判断一个整数是否是回文数。回文数是指正序（从左向右）和倒序（从右向左）读都是一样的整数。",
            difficulty=1
        )
        
        algorithm_problem2 = AlgorithmProblem.objects.create(
            problem=problem2,
            time_limit=1000,
            memory_limit=256,
            code_template={
                "python": "def isPalindrome(x: int) -> bool:\n    # 请在此实现你的代码\n    pass"
            },
            solution_name={
                "python": "isPalindrome"
            }
        )
        
        # Add test cases for palindrome problem
        TestCase.objects.create(
            problem=algorithm_problem2,
            input_data="[121]",
            expected_output="true",
            is_sample=True
        )
        
        TestCase.objects.create(
            problem=algorithm_problem2,
            input_data="[-121]",
            expected_output="false"
        )
        
        TestCase.objects.create(
            problem=algorithm_problem2,
            input_data="[10]",
            expected_output="false"
        )
        
        self.stdout.write(f'Created problem: {problem2.title}')

        # Create algorithm problems for Chapter 2
        problem3 = Problem.objects.create(
            chapter=chapter2,
            type='algorithm',
            title="FizzBuzz问题",
            content="写一个程序，输出从 1 到 n 的数字。但是，当数字是 3 的倍数时，输出 'Fizz'；当数字是 5 的倍数时，输出 'Buzz'；当数字是 3 和 5 的倍数时，输出 'FizzBuzz'。",
            difficulty=1
        )
        
        algorithm_problem3 = AlgorithmProblem.objects.create(
            problem=problem3,
            time_limit=1000,
            memory_limit=256,
             code_template={
                "python": "def fizzBuzz(n: int) -> list:\n    # 请在此实现你的代码\n    pass"
            },
            solution_name={
                "python": "fizzBuzz"
            }
        )
        
        # Add test cases for FizzBuzz problem
        TestCase.objects.create(
            problem=algorithm_problem3,
            input_data="[15]",
            expected_output='["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]',
            is_sample=True
        )
        
        self.stdout.write(f'Created problem: {problem3.title}')

        # Create algorithm problems for Chapter 3
        problem4 = Problem.objects.create(
            chapter=chapter3,
            type='algorithm',
            title="有效的括号",
            content="给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串，判断字符串是否有效。",
            difficulty=2
        )
        
        algorithm_problem4 = AlgorithmProblem.objects.create(
            problem=problem4,
            time_limit=1000,
            memory_limit=256,
            code_template={
                "python": "def isValid(s: str) -> bool:\n    # 请在此实现你的代码\n    pass"
            },
            solution_name={
                "python": "isValid"
            }
        )
        
        # Add test cases for valid parentheses problem
        TestCase.objects.create(
            problem=algorithm_problem4,
            input_data='["()"]',
            expected_output="true",
            is_sample=True
        )
        
        TestCase.objects.create(
            problem=algorithm_problem4,
            input_data='["()[]{}"]',
            expected_output="true"
        )
        
        TestCase.objects.create(
            problem=algorithm_problem4,
            input_data='["(]"]',
            expected_output="false"
        )
        
        self.stdout.write(f'Created problem: {problem4.title}')

        # Create algorithm problems for Chapter 4
        problem5 = Problem.objects.create(
            chapter=chapter4,
            type='algorithm',
            title="合并两个有序数组",
            content="给定两个排序后的数组 A 和 B，其中 A 的末端有足够的缓冲空间容纳 B。编写一个方法，将 B 合并入 A 并排序。",
            difficulty=2
        )
        
        algorithm_problem5 = AlgorithmProblem.objects.create(
            problem=problem5,
            time_limit=1000,
            memory_limit=256,
             code_template={
                "python": "def merge(nums1: list, m: int, nums2: list, n: int) -> None:\n    # 请在此实现你的代码（直接修改 nums1）\n    pass"
            },
            solution_name={
                "python": "merge"
            }
        )
        
        # Add test cases for merge sorted array problem
        TestCase.objects.create(
            problem=algorithm_problem5,
            input_data="[[1,2,3,0,0,0], 3, [2,5,6], 3]",
            expected_output="[1,2,2,3,5,6]",
            is_sample=True
        )
        
        self.stdout.write(f'Created problem: {problem5.title}')

        # Create an additional advanced problem for Chapter 4
        problem6 = Problem.objects.create(
            chapter=chapter4,
            type='algorithm',
            title="旋转数组中查找元素",
            content="给定一个经过旋转的升序数组和一个目标值，若目标值存在于数组中则返回其下标，否则返回 -1。",
            difficulty=3
        )
        
        algorithm_problem6 = AlgorithmProblem.objects.create(
            problem=problem6,
            time_limit=1000,
            memory_limit=256,
             code_template={
                "python": "def search(nums: list, target: int) -> int:\n    # 请在此实现你的代码\n    pass"
            },
            solution_name={
                "python": "search"
            }
        )
        
        # Add test cases for rotated array search
        TestCase.objects.create(
            problem=algorithm_problem6,
            input_data="[[4,5,6,7,0,1,2], 0]",
            expected_output="4",
            is_sample=True
        )
        
        TestCase.objects.create(
            problem=algorithm_problem6,
            input_data="[[4,5,6,7,0,1,2], 3]",
            expected_output="-1"
        )
        
        self.stdout.write(f'Created problem: {problem6.title}')
        # Chapter 1: Python基础语法 -> 变量命名
        choice_prob1 = Problem.objects.create(
            chapter=chapter1,
            type='choice',
            title="以下哪个是合法的 Python 变量名？",
            content="请选择符合 Python 变量命名规则的选项。",
            difficulty=1
        )
        ChoiceProblem.objects.create(
            problem=choice_prob1,
            options={
                "A": "123abc",
                "B": "my-variable",
                "C": "_private_var",
                "D": "class"
            },
            correct_answer="C",
            is_multiple_choice=False
        )
        self.stdout.write(f'Created choice problem: {choice_prob1.title}')

        # Chapter 2: 控制结构 -> 循环与条件
        choice_prob2 = Problem.objects.create(
            chapter=chapter2,
            type='choice',
            title="以下哪段代码会输出数字 0 到 4？",
            content="选择正确的 Python 代码片段。",
            difficulty=1
        )
        ChoiceProblem.objects.create(
            problem=choice_prob2,
            options={
                "A": "for i in range(5): print(i)",
                "B": "for i in range(1,5): print(i)",
                "C": "while i < 5: print(i)",
                "D": "for i in [0,1,2,3]: print(i)"
            },
            correct_answer="A",
            is_multiple_choice=False
        )
        self.stdout.write(f'Created choice problem: {choice_prob2.title}')

        # Chapter 3: 函数与模块 -> 函数定义
        choice_prob3 = Problem.objects.create(
            chapter=chapter3,
            type='choice',
            title="关于 Python 函数，以下说法正确的是？",
            content="请选择正确的描述。",
            difficulty=2
        )
        ChoiceProblem.objects.create(
            problem=choice_prob3,
            options={
                "A": "函数必须有 return 语句",
                "B": "函数参数不能有默认值",
                "C": "函数可以嵌套定义",
                "D": "lambda 函数可以包含多条语句"
            },
            correct_answer="C",
            is_multiple_choice=False
        )
        self.stdout.write(f'Created choice problem: {choice_prob3.title}')

        # Chapter 4: 数据结构 -> 列表与字典
        choice_prob4 = Problem.objects.create(
            chapter=chapter4,
            type='choice',
            title="以下哪些是可变（mutable）数据类型？（可多选）",
            content="Python 中的数据类型分为可变与不可变，请选择所有可变类型。",
            difficulty=2
        )
        ChoiceProblem.objects.create(
            problem=choice_prob4,
            options={
                "A": "list",
                "B": "tuple",
                "C": "dict",
                "D": "set"
            },
            correct_answer=["A", "C", "D"],
            is_multiple_choice=True
        )
        self.stdout.write(f'Created choice problem: {choice_prob4.title}')
        self.stdout.write(
            self.style.SUCCESS('Successfully populated sample data for Python teaching platform!')
        )