"""
Git handler utility for GitWhisperer.
Handles all Git operations including diff parsing, status checking, and commit operations.
"""

import subprocess
import os
from typing import Optional, List, Tuple
from git import Repo, GitCommandError
from pathlib import Path


class GitHandler:
    """Handles Git operations for the AI commit assistant."""

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize Git handler.

        Args:
            repo_path: Path to the Git repository. If None, uses current directory.
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.repo = None

        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            print(f"Warning: Could not initialize Git repository at {self.repo_path}: {e}")

    def is_git_repository(self) -> bool:
        """Check if the current directory is a Git repository."""
        try:
            Repo(self.repo_path)
            return True
        except Exception:
            return False

    def get_staged_diff(self) -> str:
        """
        Get the diff of staged changes.

        Returns:
            String containing the staged diff.
        """
        try:
            # Use git diff --cached to get staged changes
            result = subprocess.run(
                ['git', 'diff', '--cached'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error getting staged diff: {e}")
            return ""
        except FileNotFoundError:
            print("Git command not found. Please ensure Git is installed.")
            return ""

    def get_unstaged_diff(self) -> str:
        """
        Get the diff of unstaged changes.

        Returns:
            String containing the unstaged diff.
        """
        try:
            result = subprocess.run(
                ['git', 'diff'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error getting unstaged diff: {e}")
            return ""
        except FileNotFoundError:
            print("Git command not found. Please ensure Git is installed.")
            return ""

    def get_combined_diff(self) -> str:
        """
        Get both staged and unstaged changes.

        Returns:
            String containing combined diff.
        """
        try:
            result = subprocess.run(
                ['git', 'diff', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error getting combined diff: {e}")
            return ""
        except FileNotFoundError:
            print("Git command not found. Please ensure Git is installed.")
            return ""

    def get_commit_history(self, limit: int = 10) -> List[str]:
        """
        Get recent commit messages for context.

        Args:
            limit: Number of recent commits to retrieve.

        Returns:
            List of commit messages.
        """
        try:
            if not self.repo:
                return []

            commits = list(self.repo.iter_commits(max_count=limit))
            return [commit.message.strip() for commit in commits]
        except Exception as e:
            print(f"Error getting commit history: {e}")
            return []

    def get_current_branch(self) -> str:
        """
        Get the current branch name.

        Returns:
            Current branch name or empty string if error.
        """
        try:
            if self.repo:
                return self.repo.active_branch.name
            else:
                result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
        except Exception as e:
            print(f"Error getting current branch: {e}")
            return ""

    def get_changed_files(self) -> List[str]:
        """
        Get list of files that have been modified.

        Returns:
            List of file paths that have changes.
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            files = result.stdout.strip().split('\n')
            return [f for f in files if f]  # Filter out empty strings
        except subprocess.CalledProcessError as e:
            print(f"Error getting changed files: {e}")
            return []
        except FileNotFoundError:
            print("Git command not found. Please ensure Git is installed.")
            return []

    def has_staged_changes(self) -> bool:
        """
        Check if there are staged changes ready for commit.

        Returns:
            True if there are staged changes, False otherwise.
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
        except FileNotFoundError:
            print("Git command not found. Please ensure Git is installed.")
            return False

    def stage_all_changes(self) -> bool:
        """
        Stage all changes (git add .).

        Returns:
            True if successful, False otherwise.
        """
        try:
            subprocess.run(
                ['git', 'add', '.'],
                cwd=self.repo_path,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error staging changes: {e}")
            return False
        except FileNotFoundError:
            print("Git command not found. Please ensure Git is installed.")
            return False

    def commit_changes(self, message: str) -> bool:
        """
        Commit staged changes with the given message.

        Args:
            message: Commit message to use.

        Returns:
            True if successful, False otherwise.
        """
        try:
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.repo_path,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error committing changes: {e}")
            return False
        except FileNotFoundError:
            print("Git command not found. Please ensure Git is installed.")
            return False