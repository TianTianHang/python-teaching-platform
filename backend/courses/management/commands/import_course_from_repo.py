"""
Django management command to import courses from a Git repository.

Usage:
    python manage.py import_course_from_repo <repo_url> [options]

Examples:
    # Import from public repository
    python manage.py import_course_from_repo https://github.com/org/courses.git

    # Import from specific branch with update mode
    python manage.py import_course_from_repo https://github.com/org/courses.git --branch develop --update

    # Import without updating existing courses
    python manage.py import_course_from_repo https://github.com/org/courses.git --no-update
"""

from django.core.management.base import BaseCommand
from courses.course_import_services.git_repo_service import GitRepoService
from courses.course_import_services.course_importer import CourseImporter


class Command(BaseCommand):
    help = 'Import courses from a Git repository containing markdown files'

    def add_arguments(self, parser):
        parser.add_argument(
            'repo_url',
            type=str,
            help='Git repository URL (HTTPS or SSH)'
        )
        parser.add_argument(
            '--branch',
            type=str,
            default='main',
            help='Git branch to clone (default: main)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing courses (default: skip them)'
        )

    def handle(self, *args, **options):
        repo_url = options['repo_url']
        branch = options['branch']
        update_mode = options['update']

        self.stdout.write(f"Cloning repository: {repo_url} (branch: {branch})")

        try:
            with GitRepoService(repo_url, branch) as repo_path:
                self.stdout.write(f"Repository cloned to: {repo_path}")

                importer = CourseImporter(repo_path, update_mode=update_mode)

                self.stdout.write("Starting import...")
                stats = importer.import_all()

                # Print results
                self.stdout.write(self.style.SUCCESS("\n=== Import Summary ==="))
                self.stdout.write(f"Courses created: {stats['courses_created']}")
                self.stdout.write(f"Courses updated: {stats['courses_updated']}")
                self.stdout.write(f"Courses skipped: {stats['courses_skipped']}")
                self.stdout.write(f"Chapters created: {stats['chapters_created']}")
                self.stdout.write(f"Chapters updated: {stats['chapters_updated']}")
                self.stdout.write(f"Problems created: {stats['problems_created']}")
                self.stdout.write(f"Problems updated: {stats['problems_updated']}")

                if stats['errors']:
                    self.stdout.write(self.style.ERROR(f"\nErrors: {len(stats['errors'])}"))
                    for error in stats['errors'][:10]:  # Show first 10 errors
                        self.stdout.write(self.style.ERROR(f"  - {error}"))

                    if len(stats['errors']) > 10:
                        self.stdout.write(self.style.ERROR(f"  ... and {len(stats['errors']) - 10} more errors"))

                self.stdout.write(self.style.SUCCESS("\nImport completed successfully!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Import failed: {str(e)}"))
            raise
