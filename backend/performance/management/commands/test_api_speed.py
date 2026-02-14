"""
Django management command to test API endpoint response times.

Usage:
    python manage.py test_api_speed [--skip-data-setup] [--output-format=markdown|json]
"""
import time
import json
import factory
from datetime import datetime, timedelta
from io import StringIO
from typing import Dict, List, Tuple, Any

from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import get_resolver
from django.conf import settings
from django.urls.resolvers import URLPattern, URLResolver
from accounts.serializers import CustomTokenObtainPairSerializer


class Command(BaseCommand):
    help = 'Test all API endpoints and measure response times'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []
        self.test_data = {}
        self.client = Client()
        # Endpoints that require admin privileges
        self.admin_endpoints = [
            '/api/v1/users',
            '/api/v1/users/{user_pk}/delete/',
        ]
        # Endpoints to exclude from testing
        self.excluded_endpoints = [
            'submissions',  # Exclude all submission-related endpoints
        ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-data-setup',
            action='store_true',
            dest='skip_data_setup',
            help='Skip test data generation',
        )
        parser.add_argument(
            '--output-format',
            type=str,
            default='markdown',
            choices=['markdown', 'json', 'table'],
            help='Output format for the report',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Timeout in seconds for each request (default: 30)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting API Speed Test...'))
        self.stdout.write('=' * 60)

        # Setup test data
        if not options.get('skip_data_setup'):
            self.stdout.write('Setting up test data...')
            self.setup_test_data()
        else:
            self.stdout.write('Skipping test data setup...')
            self.load_existing_data()

        # Discover all API endpoints
        self.stdout.write('Discovering API endpoints...')
        endpoints = self.discover_api_endpoints()
        self.stdout.write(self.style.SUCCESS(f'Found {len(endpoints)} endpoints'))

        # Test each endpoint
        self.stdout.write('Testing endpoints...')
        self.stdout.write('-' * 60)

        # Show all endpoints
        self.stdout.write(f'Found {len(endpoints)} endpoints:')
        for i, (path, methods, info) in enumerate(endpoints, 1):
            self.stdout.write(f'  {i}. {path} [{", ".join(methods)}]')

        tested_count = 0
        for i, (path, methods, info) in enumerate(endpoints, 1):
            if '/admin/' in path or not path.startswith('/api/'):
                continue

            for method in methods:
                self.test_endpoint(path, method, info)
                tested_count += 1

        self.stdout.write(f'Total endpoints tested: {tested_count} out of {len(endpoints)}')

        # Generate report
        self.stdout.write('-' * 60)
        output_format = options.get('output_format', 'markdown')
        self.generate_report(output_format)

        self.stdout.write(self.style.SUCCESS('API Speed Test completed!'))

    def setup_test_data(self):
        """Generate test data for API testing."""
        try:
            from accounts.tests.factories import UserFactory
            from accounts.models import User
            from courses.tests.factories import (
                CourseFactory, ChapterFactory, AlgorithmProblemFactory,
                ChoiceProblemFactory, FillBlankProblemFactory,
                SubmissionFactory, EnrollmentFactory, ExamFactory
            )
            from courses.models import Exam

            # Create test users
            self.stdout.write('  - Creating test users...')
            try:
                # Generate unique user with random data
                regular_user = UserFactory(
                    username='test_user_regular',
                    st_number=1000001
                )
                regular_user.set_password('testpass123')
                regular_user.save()
            except Exception as e:
                self.stdout.write(f'  - Using existing test user: {e}')
                regular_user = User.objects.filter(username='test_user_regular').first()
                if not regular_user:
                    # Create with different random data
                    regular_user = UserFactory(
                        username='test_user_regular_alt',
                        st_number=1000002
                    )
                regular_user.set_password('testpass123')
                regular_user.save()

            try:
                admin_user = UserFactory(
                    username='test_admin',
                    is_staff=True,
                    is_superuser=True,
                    st_number=1000003
                )
                admin_user.set_password('adminpass123')
                admin_user.save()
            except Exception as e:
                self.stdout.write(f'  - Using existing admin user: {e}')
                admin_user = User.objects.filter(username='test_admin').first()

            # Create course data
            self.stdout.write('  - Creating test courses...')
            try:
                course = CourseFactory(title='Test Course for API Speed')
            except Exception as e:
                self.stdout.write(f'  - Using existing course: {e}')
                from courses.models import Course
                course = Course.objects.filter(title='Test Course for API Speed').first() or Course.objects.first()
            try:
                from courses.models import Chapter
                chapter = ChapterFactory(course=course, order=1)
            except Exception as e:
                self.stdout.write(f'  - Using existing chapter: {e}')
                chapter = course.chapters.first()

            # Create problems
            self.stdout.write('  - Creating test problems...')
            algo_problem = AlgorithmProblemFactory(
                problem__chapter=chapter,
                problem__title='Algorithm Problem Test'
            )
            choice_problem = ChoiceProblemFactory(
                problem__chapter=chapter,
                problem__title='Choice Problem Test'
            )
            fillblank_problem = FillBlankProblemFactory(
                problem__chapter=chapter,
                problem__title='FillBlank Problem Test'
            )

            # Create enrollment
            enrollment = EnrollmentFactory(user=regular_user, course=course)

            # Create exam
            self.stdout.write('  - Creating test exams...')
            from datetime import datetime, timedelta, timedelta
            exam = Exam.objects.create(
                course=course,
                title='Test Exam',
                description='A test exam for API speed testing',
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=7),
                duration_minutes=60,
                passing_score=60
            )

            # Create submission
            self.stdout.write('  - Creating test submissions...')
            submission = SubmissionFactory(
                user=regular_user,
                problem=algo_problem.problem
            )

            # Store test data IDs
            self.test_data = {
                'users': {
                    'regular_id': regular_user.id,
                    'regular_username': regular_user.username,
                    'admin_id': admin_user.id,
                },
                'courses': {
                    'course_id': course.id,
                    'chapter_id': chapter.id,
                },
                'problems': {
                    'algo_problem_id': algo_problem.problem.id,
                    'choice_problem_id': choice_problem.problem.id,
                    'fillblank_problem_id': fillblank_problem.problem.id,
                },
                'submissions': {
                    'submission_id': submission.id,
                },
                'exams': {
                    'exam_id': exam.id,
                }
            }

            # Verify users exist before generating tokens
            regular_user.refresh_from_db()
            if not regular_user.is_active:
                raise Exception("Regular user is not active")

            admin_user.refresh_from_db()
            if not admin_user.is_active:
                raise Exception("Admin user is not active")

            # Generate JWT token for regular user
            refresh = CustomTokenObtainPairSerializer.get_token(regular_user)
            self.test_data['auth_token'] = str(refresh.access_token)

            # Generate JWT token for admin user
            admin_refresh = CustomTokenObtainPairSerializer.get_token(admin_user)
            self.test_data['admin_auth_token'] = str(admin_refresh.access_token)

            # Store IDs AFTER generating tokens
            self.test_data['users'] = {
                'regular_id': regular_user.id,
                'regular_username': regular_user.username,
                'admin_id': admin_user.id,
            }

            # Verify users still exist after data setup
            from accounts.models import User
            reg_check = User.objects.filter(id=regular_user.id).first()
            admin_check = User.objects.filter(id=admin_user.id).first()

            if not reg_check:
                self.stdout.write(self.style.ERROR('  ERROR: Regular user deleted during setup!'))
            if not admin_check:
                self.stdout.write(self.style.ERROR('  ERROR: Admin user deleted during setup!'))

            self.stdout.write(self.style.SUCCESS('  Test data setup complete!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error setting up test data: {e}'))
            import traceback
            traceback.print_exc()

    def load_existing_data(self):
        """Load existing test data from database."""
        try:
            from accounts.models import User
            from courses.models import Course, Chapter, Problem, Submission, Exam

            # Find or create test user
            user = User.objects.filter(username='test_user_regular').first()
            if not user:
                user = User.objects.first()
            if user:
                refresh = CustomTokenObtainPairSerializer.get_token(user)
                self.test_data['auth_token'] = str(refresh.access_token)
                self.test_data['users'] = {'regular_id': user.id}

            # Find or create admin user
            admin_user = User.objects.filter(username='test_admin').first()
            if admin_user and admin_user.is_staff:
                admin_refresh = CustomTokenObtainPairSerializer.get_token(admin_user)
                self.test_data['admin_auth_token'] = str(admin_refresh.access_token)

            # Load sample data
            course = Course.objects.first()
            if course:
                self.test_data['courses'] = {'course_id': course.id}
                chapter = course.chapters.first()
                if chapter:
                    self.test_data['courses']['chapter_id'] = chapter.id
                    problem = chapter.problems.first()
                    if problem:
                        self.test_data['problems'] = {'algo_problem_id': problem.id}
                        submission = problem.submissions.first()
                        if submission:
                            self.test_data['submissions'] = {'submission_id': submission.id}

            exam = Exam.objects.first()
            if exam:
                self.test_data['exams'] = {'exam_id': exam.id}

            self.stdout.write(self.style.SUCCESS('  Loaded existing test data!'))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  Warning: Could not load test data: {e}'))

    def discover_api_endpoints(self) -> List[Tuple[str, List[str], dict]]:
        """Discover all API endpoints from URL configuration."""
        endpoints = []
        resolver = get_resolver()

        # Define all known API endpoints based on URL patterns
        known_endpoints = [
            # Accounts module
            ('/api/v1/auth/login', ['post'], 'LoginView'),
            ('/api/v1/auth/register', ['post'], 'RegisterView'),
            ('/api/v1/auth/logout', ['post'], 'LogoutView'),
            ('/api/v1/auth/me', ['get'], 'MeView'),
            ('/api/v1/auth/refresh', ['post'], 'TokenRefreshView'),
            ('/api/v1/auth/verify', ['post'], 'TokenVerifyView'),
            ('/api/v1/users', ['get'], 'UserListView'),
            ('/api/v1/users/{user_pk}/delete/', ['delete'], 'UserDeleteView'),
            ('/api/v1/users/me/update/', ['put', 'patch'], 'UserUpdateView'),
            ('/api/v1/users/me/change-password/', ['put', 'patch'], 'ChangePasswordView'),
            ('/api/v1/membership-types/', ['get'], 'MembershipTypeListView'),

            # Courses module
            ('/api/v1/courses/', ['get', 'post'], 'CourseViewSet'),
            ('/api/v1/courses/{course_pk}/', ['get', 'put', 'patch'], 'CourseViewSet'),
            ('/api/v1/courses/{course_pk}/enroll/', ['post'], 'enroll'),
            ('/api/v1/chapters/', ['get', 'post'], 'ChapterViewSet'),
            ('/api/v1/chapters/{chapter_pk}/', ['get', 'put', 'patch'], 'ChapterViewSet'),
            ('/api/v1/chapters/{chapter_pk}/mark_as_completed/', ['post'], 'mark_as_completed'),
            ('/api/v1/chapters/{chapter_pk}/threads/', ['get', 'post'], 'thread'),
            ('/api/v1/chapters/{chapter_pk}/unlock_status/', ['get'], 'unlock_status'),
            ('/api/v1/problems/', ['get', 'post'], 'ProblemViewSet'),
            ('/api/v1/problems/{problem_pk}/', ['get', 'put', 'patch'], 'ProblemViewSet'),
            ('/api/v1/problems/{problem_pk}/submissions/', ['get', 'post'], 'problem-submissions'),
            ('/api/v1/problems/{problem_pk}/drafts/', ['get', 'post'], 'problem-drafts'),
            ('/api/v1/problems/{problem_pk}/threads/', ['get', 'post'], 'thread'),
            ('/api/v1/problems/{problem_pk}/mark_as_solved/', ['post'], 'mark_as_solved'),
            ('/api/v1/problems/{problem_pk}/check_fillblank/', ['post'], 'check_fillblank'),
            ('/api/v1/problems/next/', ['get'], 'next'),
            ('/api/v1/submissions/', ['get', 'post'], 'SubmissionViewSet'),
            ('/api/v1/submissions/{submission_pk}/', ['get'], 'SubmissionViewSet'),
            ('/api/v1/drafts/', ['get', 'post'], 'CodeDraftViewSet'),
            ('/api/v1/drafts/recent/', ['get'], 'recent'),
            ('/api/v1/drafts/{draft_pk}/', ['get', 'put', 'patch'], 'CodeDraftViewSet'),
            ('/api/v1/enrollments/', ['get', 'post'], 'EnrollmentViewSet'),
            ('/api/v1/enrollments/{enrollment_pk}/', ['get'], 'EnrollmentViewSet'),
            ('/api/v1/chapter-progress/', ['get', 'post'], 'ChapterProgressViewSet'),
            ('/api/v1/chapter-progress/{progress_pk}/', ['get'], 'ChapterProgressViewSet'),
            ('/api/v1/problem-progress/', ['get', 'post'], 'ProblemProgressViewSet'),
            ('/api/v1/problem-progress/{progress_pk}/', ['get'], 'ProblemProgressViewSet'),
            ('/api/v1/threads/', ['get', 'post'], 'DiscussionThreadViewSet'),
            ('/api/v1/threads/{thread_pk}/', ['get', 'put', 'patch'], 'DiscussionThreadViewSet'),
            ('/api/v1/threads/{thread_pk}/replies/', ['get', 'post'], 'thread-replies'),
            ('/api/v1/replies/', ['get', 'post'], 'DiscussionReplyViewSet'),
            ('/api/v1/replies/{reply_pk}/', ['get', 'put', 'patch'], 'DiscussionReplyViewSet'),
            ('/api/v1/exams/', ['get', 'post'], 'ExamViewSet'),
            ('/api/v1/exams/{exam_pk}/', ['get'], 'ExamViewSet'),
            ('/api/v1/exams/{exam_pk}/start/', ['post'], 'start'),
            ('/api/v1/exams/{exam_pk}/submit/', ['post'], 'submit'),
            ('/api/v1/exams/{exam_pk}/results/', ['get'], 'results'),
            ('/api/v1/exam-submissions/', ['get', 'post'], 'ExamSubmissionViewSet'),
            ('/api/v1/exam-submissions/{submission_pk}/my-results/', ['get'], 'my-results'),

            # Commerce module
            ('/api/v1/orders/', ['get', 'post'], 'OrderViewSet'),
            ('/api/v1/orders/{order_pk}/', ['get'], 'OrderViewSet'),
            ('/api/v1/orders/{order_pk}/cancel/', ['post'], 'cancel'),
            ('/api/v1/orders/{order_number}/pay/', ['post'], 'CreatePaymentView'),
            ('/api/v1/payments/alipay/notify/', ['post'], 'AlipayNotifyView'),

            # File management module
            ('/api/v1/files/', ['get', 'post'], 'FileEntryViewSet'),
            ('/api/v1/files/{file_pk}/', ['get'], 'FileEntryViewSet'),
            ('/api/v1/folders/', ['get', 'post'], 'FolderViewSet'),
            ('/api/v1/folders/{folder_pk}/', ['get'], 'FolderViewSet'),
            ('/api/v1/path/', ['get', 'post'], 'UnifiedFileFolderViewSet'),
            ('/api/v1/path/upload/', ['post'], 'UnifiedFileFolderViewSet'),
            ('/api/v1/path/create-folder/', ['post'], 'UnifiedFileFolderViewSet'),
            ('/api/v1/path/move_copy/', ['post'], 'UnifiedFileFolderViewSet'),
            ('/api/v1/path/{full_path}/', ['get', 'delete'], 'UnifiedFileFolderViewSet'),
        ]

        # Convert the list to the expected format, filtering out excluded endpoints
        for endpoint in known_endpoints:
            path, methods, info = endpoint
            # Skip excluded endpoints (like submissions)
            is_excluded = any(excluded in path for excluded in self.excluded_endpoints)
            if not is_excluded:
                endpoints.append((path, methods, {'name': info, 'view_name': info}))

        return endpoints

    def test_endpoint(self, path: str, method: str, info: dict):
        """Test a single endpoint and measure response time."""
        # Skip admin and non-API paths
        if '/admin/' in path or not path.startswith('/api/v1/'):
            return

        # Skip excluded endpoints (like submissions)
        for excluded in self.excluded_endpoints:
            if excluded in path:
                self.stdout.write(f'  ⊘ {method.upper():6} {path[:50]:50}  SKIPPED (excluded)')
                return

        # Replace path parameters with test data IDs
        resolved_path = self.resolve_path(path)

        # Prepare request
        url = f'http://testserver{resolved_path}'
        headers = {}

        # Determine if this endpoint requires admin privileges
        requires_admin = any(
            pattern in path or
            pattern.replace('{user_pk}', str(self.test_data.get('users', {}).get('regular_id', 1))) in resolved_path
            for pattern in self.admin_endpoints
        )

        # Check users exist and refresh data
        from accounts.models import User
        reg_user = User.objects.filter(username=self.test_data.get('users', {}).get('regular_username')).first()
        admin_user = User.objects.filter(id=self.test_data.get('users', {}).get('admin_id')).first()

        # Regenerate tokens if users exist
        if reg_user:
            refresh = CustomTokenObtainPairSerializer.get_token(reg_user)
            headers['HTTP_AUTHORIZATION'] = f'Bearer {str(refresh.access_token)}'
        elif admin_user:
            refresh = CustomTokenObtainPairSerializer.get_token(admin_user)
            headers['HTTP_AUTHORIZATION'] = f'Bearer {str(refresh.access_token)}'
        else:
            self.stdout.write(f'  ERROR: No valid users found for {path}')

        # Prepare request body for POST/PUT/PATCH
        body = None
        if method in ['post', 'put', 'patch']:
            body = self.get_request_body(path, method)

        try:
            start_time = time.time()

            # Create a new client for each request to avoid state issues
            client = Client()

            if method == 'get':
                response = client.get(
                    resolved_path,
                    HTTP_HOST='testserver',
                    **headers
                )
            elif method == 'post':
                response = client.post(
                    resolved_path,
                    data=json.dumps(body or {}),
                    content_type='application/json',
                    HTTP_HOST='testserver',
                    **headers
                )
            elif method == 'put':
                response = client.put(
                    resolved_path,
                    data=json.dumps(body or {}),
                    content_type='application/json',
                    HTTP_HOST='testserver',
                    **headers
                )
            elif method == 'patch':
                response = client.patch(
                    resolved_path,
                    data=json.dumps(body or {}),
                    content_type='application/json',
                    HTTP_HOST='testserver',
                    **headers
                )
            elif method == 'delete':
                response = client.delete(
                    resolved_path,
                    HTTP_HOST='testserver',
                    **headers
                )
            else:
                return

            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)

            self.results.append({
                'path': path,
                'resolved_path': resolved_path,
                'method': method.upper(),
                'status_code': response.status_code,
                'duration_ms': duration_ms,
                'success': response.status_code < 400,
            })

            status_icon = '✓' if response.status_code < 400 else '✗'
            self.stdout.write(
                f'  {status_icon} {method.upper():6} {path[:50]:50} '
                f'{duration_ms:5}ms  {response.status_code}'
            )

            # Show detailed error for 401
            if response.status_code == 401:
                try:
                    content = response.content.decode()
                    self.stdout.write(f'    401 Error: {content[:200]}')
                except:
                    pass

        except Exception as e:
            self.results.append({
                'path': path,
                'resolved_path': resolved_path,
                'method': method.upper(),
                'status_code': 0,
                'duration_ms': -1,
                'success': False,
                'error': str(e),
            })
            self.stdout.write(
                self.style.ERROR(f'  ✗ {method.upper():6} {path[:50]:50}  ERROR: {e}')
            )

    def resolve_path(self, path: str) -> str:
        """Replace path parameters with test data IDs."""
        resolved = path

        # User ID
        if '{user_pk}' in resolved or '{int:pk}' in resolved:
            if self.test_data.get('users', {}).get('regular_id'):
                resolved = resolved.replace('{user_pk}', str(self.test_data['users']['regular_id']))
                resolved = resolved.replace('{int:pk}', str(self.test_data['users']['regular_id']))

        # Course ID
        if '{course_pk}' in resolved or '{int}' in resolved:
            if self.test_data.get('courses', {}).get('course_id'):
                resolved = resolved.replace('{course_pk}', str(self.test_data['courses']['course_id']))
                resolved = resolved.replace('{int}', str(self.test_data['courses']['course_id']))

        # Chapter ID
        if '{chapter_pk}' in resolved:
            if self.test_data.get('courses', {}).get('chapter_id'):
                resolved = resolved.replace('{chapter_pk}', str(self.test_data['courses']['chapter_id']))

        # Problem ID
        if '{problem_pk}' in resolved:
            if self.test_data.get('problems', {}).get('algo_problem_id'):
                resolved = resolved.replace('{problem_pk}', str(self.test_data['problems']['algo_problem_id']))

        # Submission ID
        if '{submission_pk}' in resolved:
            if self.test_data.get('submissions', {}).get('submission_id'):
                resolved = resolved.replace('{submission_pk}', str(self.test_data['submissions']['submission_id']))

        # Thread ID
        if '{thread_pk}' in resolved:
            resolved = resolved.replace('{thread_pk}', '1')

        # Reply ID
        if '{reply_pk}' in resolved:
            resolved = resolved.replace('{reply_pk}', '1')

        # Exam ID
        if '{exam_pk}' in resolved:
            if self.test_data.get('exams', {}).get('exam_id'):
                resolved = resolved.replace('{exam_pk}', str(self.test_data['exams']['exam_id']))

        # Order number (string)
        if '{order_number}' in resolved:
            resolved = resolved.replace('{order_number}', 'TEST-ORDER-001')

        # Full path
        if '{full_path}' in resolved:
            resolved = resolved.replace('{full_path}', 'test-folder/test-file.txt')

        return resolved

    def get_request_body(self, path: str, method: str) -> dict:
        """Generate appropriate request body for POST/PUT/PATCH requests."""
        if 'login' in path:
            return {
                'username': self.test_data.get('users', {}).get('regular_username', 'test_user_regular'),
                'password': 'testpass123',
            }

        if 'register' in path:
            return {
                'username': 'new_test_user',
                'email': 'newtest@example.com',
                'password': 'newpass123',
                'st_number': '2024000000',
            }

        if 'submissions' in path and method == 'post':
            return {
                'code': 'print("Hello, World!")',
                'language': 'python',
            }

        if 'drafts' in path and method == 'post':
            return {
                'code': 'print("Draft code")',
                'language': 'python',
            }

        if 'threads' in path and method == 'post':
            return {
                'title': 'Test Thread Title',
                'content': 'This is a test thread content.',
            }

        if 'replies' in path and method == 'post':
            return {
                'content': 'This is a test reply.',
            }

        if 'exams' in path and 'submissions' not in path:
            return {
                'title': 'Test Exam Submission',
                'description': 'Test description',
            }

        if 'chapter-progress' in path and 'mark' in path:
            return {'completed': True}

        if 'problems' in path and 'mark' in path:
            return {'solved': True}

        if 'orders' in path:
            return {
                'membership_type': 1,
            }

        return {}

    def generate_report(self, output_format: str = 'markdown'):
        """Generate and save the performance test report."""
        # Sort results by duration
        sorted_results = sorted(self.results, key=lambda x: x['duration_ms'])

        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if output_format == 'json':
            self.generate_json_report(sorted_results, successful, failed, timestamp)
        elif output_format == 'table':
            self.generate_table_report(sorted_results, successful, failed, timestamp)
        else:
            self.generate_markdown_report(sorted_results, successful, failed, timestamp)

    def generate_markdown_report(self, sorted_results, successful, failed, timestamp):
        """Generate markdown format report."""
        output = StringIO()

        output.write(f'# API响应时间测试报告\n\n')
        output.write(f'**生成时间**: {timestamp}\n\n')
        output.write(f'**总接口数**: {len(self.results)}\n')
        output.write(f'**成功**: {len(successful)} | **失败**: {len(failed)}\n\n')

        # Summary statistics
        if successful:
            durations = [r['duration_ms'] for r in successful]
            avg_time = sum(durations) / len(durations)
            max_time = max(durations)
            min_time = min(durations)

            output.write('## 性能统计\n\n')
            output.write(f'| 指标 | 值 |\n')
            output.write(f'|------|------|\n')
            output.write(f'| 平均响应时间 | {avg_time:.1f}ms |\n')
            output.write(f'| 最快响应时间 | {min_time}ms |\n')
            output.write(f'| 最慢响应时间 | {max_time}ms |\n')
            output.write(f'| 总测试时间 | {sum(durations)/1000:.1f}s |\n\n')

        # All results table
        output.write('## 全部接口测试结果\n\n')
        output.write('| 排名 | 端点 | 方法 | 响应时间 | 状态码 | 状态 |\n')
        output.write('|------|------|------|----------|--------|------|\n')

        for i, result in enumerate(sorted_results, 1):
            status = '✓ PASS' if result['success'] else '✗ FAIL'
            duration_str = f"{result['duration_ms']}ms" if result['duration_ms'] >= 0 else 'ERROR'
            output.write(f'| {i} | `{result["path"]}` | {result["method"]} | {duration_str} | {result["status_code"]} | {status} |\n')

        # Top 10 slowest endpoints
        slowest = sorted(successful, key=lambda x: x['duration_ms'], reverse=True)[:10]
        if slowest:
            output.write('\n## 最慢接口 TOP10\n\n')
            output.write('| 排名 | 端点 | 方法 | 响应时间 |\n')
            output.write('|------|------|------|----------|\n')
            for i, result in enumerate(slowest, 1):
                output.write(f'| {i} | `{result["path"]}` | {result["method"]} | {result["duration_ms"]}ms |\n')

        # Failed endpoints
        if failed:
            output.write('\n## 失败的接口\n\n')
            output.write('| 端点 | 方法 | 错误 |\n')
            output.write('|------|------|------|\n')
            for result in failed:
                error_msg = result.get('error', f'Status: {result["status_code"]}')
                output.write(f'| `{result["path"]}` | {result["method"]} | {error_msg} |\n')

        # Print to console
        report_content = output.getvalue()
        self.stdout.write('\n')
        self.stdout.write('=' * 60)
        self.stdout.write('REPORT:')
        self.stdout.write('=' * 60)
        self.stdout.write(report_content)

        # Save to file
        from pathlib import Path
        report_dir = Path(__file__).parent.parent.parent / 'reports'
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f'api_speed_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        self.stdout.write(f'\nReport saved to: {report_file}')

    def generate_json_report(self, sorted_results, successful, failed, timestamp):
        """Generate JSON format report."""
        report = {
            'timestamp': timestamp,
            'summary': {
                'total': len(self.results),
                'successful': len(successful),
                'failed': len(failed),
            },
            'statistics': {},
            'results': sorted_results,
            'slowest_top10': sorted(successful, key=lambda x: x['duration_ms'], reverse=True)[:10] if successful else [],
            'failed': failed,
        }

        if successful:
            durations = [r['duration_ms'] for r in successful]
            report['statistics'] = {
                'avg_ms': sum(durations) / len(durations),
                'min_ms': min(durations),
                'max_ms': max(durations),
                'total_ms': sum(durations),
            }

        from pathlib import Path
        report_dir = Path(__file__).parent.parent.parent / 'reports'
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f'api_speed_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.stdout.write(f'\nReport saved to: {report_file}')

    def generate_table_report(self, sorted_results, successful, failed, timestamp):
        """Generate simple table format report for console."""
        self.stdout.write('\n')
        self.stdout.write('=' * 80)
        self.stdout.write(f'API SPEED TEST REPORT - {timestamp}')
        self.stdout.write('=' * 80)

        if successful:
            durations = [r['duration_ms'] for r in successful]
            avg_time = sum(durations) / len(durations)
            self.stdout.write(f'Summary: Total={len(self.results)}, Success={len(successful)}, Failed={len(failed)}')
            self.stdout.write(f'Avg Response Time: {avg_time:.1f}ms')

        self.stdout.write('-' * 80)
        self.stdout.write(f'{"Rank":<6} {"Path":<45} {"Method":<8} {"Time":<10} {"Status":<8}')
        self.stdout.write('-' * 80)

        for i, result in enumerate(sorted_results, 1):
            status = 'OK' if result['success'] else 'FAIL'
            duration = f"{result['duration_ms']}ms" if result['duration_ms'] >= 0 else 'ERROR'
            self.stdout.write(f'{i:<6} {result["path"]:<45} {result["method"]:<8} {duration:<10} {status:<8}')
