"""
Management command to clean up old cache keys from Redis
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from common.utils.cache import delete_cache_pattern


class Command(BaseCommand):
    help = "Clean up old cache keys from Redis (api:ChapterViewSet:*, api:ProblemViewSet:*)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what keys will be deleted without actually deleting them",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        old_patterns = [
            "api:ChapterViewSet:*",
            "api:ProblemViewSet:*",
        ]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No keys will be deleted"))
            self.stdout.write("")

        total_deleted = 0
        for pattern in old_patterns:
            if dry_run:
                self.stdout.write(f"Would delete keys matching: {pattern}")
            else:
                deleted = delete_cache_pattern(pattern)
                total_deleted += deleted
                self.stdout.write(
                    self.style.SUCCESS(f"Deleted {deleted} keys matching: {pattern}")
                )

        if dry_run:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    f"Run without --dry-run to delete {total_deleted} keys"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully cleaned up {total_deleted} old cache keys"
                )
            )
