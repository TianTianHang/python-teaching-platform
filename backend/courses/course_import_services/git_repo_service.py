"""
Git repository service for cloning and managing course repositories.

This service handles cloning Git repositories to temporary directories,
with automatic cleanup using context manager pattern.
"""

import os
import tempfile
import logging
from typing import Optional
from pathlib import Path

import git

logger = logging.getLogger(__name__)


class GitRepoService:
    """
    Service for cloning and managing Git repositories containing course content.

    Usage:
        with GitRepoService('https://github.com/org/courses.git', 'main') as repo_path:
            # Process files in repo_path
            pass  # Auto cleanup on exit
    """

    def __init__(self, repo_url: str, branch: str = 'main'):
        """
        Initialize the Git repository service.

        Args:
            repo_url: Git repository URL (HTTPS or SSH)
            branch: Git branch to clone (default: 'main')
        """
        self.repo_url = repo_url
        self.branch = branch
        self.temp_dir: Optional[tempfile.TemporaryDirectory] = None
        self.repo_path: Optional[Path] = None

    def clone(self) -> Path:
        """
        Clone repository to temporary directory and return path.

        Uses shallow clone (depth=1) for faster download and less disk usage.

        Returns:
            Path: Path to the cloned repository

        Raises:
            git.GitCommandError: If clone operation fails
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_path = Path(self.temp_dir.name)

        logger.info(f"Cloning repository {self.repo_url} (branch: {self.branch}) to {self.repo_path}")

        try:
            git.Repo.clone_from(
                self.repo_url,
                self.repo_path,
                branch=self.branch,
                depth=1,  # Shallow clone for faster download
                single_branch=False  # Allow all branches for local repos
            )
            logger.info(f"Repository cloned successfully")
        except git.GitCommandError as e:
            self.cleanup()
            raise ValueError(f"Failed to clone repository: {e.stderr}") from e

        return self.repo_path

    def cleanup(self):
        """Clean up temporary repository directory."""
        if self.temp_dir:
            logger.info(f"Cleaning up temporary directory: {self.repo_path}")
            self.temp_dir.cleanup()
            self.temp_dir = None
            self.repo_path = None

    def __enter__(self) -> Path:
        """Context manager entry - clone repository."""
        return self.clone()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup temporary files."""
        self.cleanup()
        return False  # Don't suppress exceptions
