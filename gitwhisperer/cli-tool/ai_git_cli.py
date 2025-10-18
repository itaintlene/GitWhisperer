#!/usr/bin/env python3
"""
GitWhisperer CLI Tool - Command line interface for AI-powered Git commit messages.
Provides a simple terminal interface to generate commit messages using AI.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# Add the python-backend to the path so we can import from it
backend_path = Path(__file__).parent.parent / "python-backend"
sys.path.insert(0, str(backend_path))

try:
    from ai_commit_writer import generate_commit_message, suggest_branch_name, summarize_pull_request
    from utils.git_handler import GitHandler
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print("Please ensure the Python backend is properly installed.")
    print(f"Looking for modules in: {backend_path}")
    print(f"Python path includes: {sys.path[0]}")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_colored(text: str, color: str = Colors.GREEN) -> None:
    """Print colored text to terminal."""
    print(f"{color}{text}{Colors.END}")


def print_header(text: str) -> None:
    """Print a header with emphasis."""
    print_colored(f"\n{'='*60}")
    print_colored(f"🤖 {text}", Colors.BOLD)
    print_colored(f"{'='*60}")


def run_git_command(command: List[str], cwd: str = None) -> tuple:
    """Run a Git command and return the result."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip(), None
    except subprocess.CalledProcessError as e:
        return None, str(e)
    except FileNotFoundError:
        return None, "Git command not found. Please ensure Git is installed."


def check_git_repository() -> bool:
    """Check if current directory is a Git repository."""
    _, error = run_git_command(['git', 'rev-parse', '--git-dir'])
    return error is None


def get_staged_diff() -> str:
    """Get the staged Git diff."""
    stdout, error = run_git_command(['git', 'diff', '--cached'])
    if error:
        print_colored(f"Error getting staged diff: {error}", Colors.RED)
        return ""
    return stdout


def get_current_branch() -> str:
    """Get the current branch name."""
    stdout, error = run_git_command(['git', 'branch', '--show-current'])
    if error:
        print_colored(f"Error getting current branch: {error}", Colors.RED)
        return "unknown"
    return stdout


def stage_all_changes() -> bool:
    """Stage all changes."""
    _, error = run_git_command(['git', 'add', '.'])
    if error:
        print_colored(f"Error staging changes: {error}", Colors.RED)
        return False
    return True


def commit_changes(message: str) -> bool:
    """Commit staged changes with the given message."""
    # Escape quotes in the message
    escaped_message = message.replace('"', '\\"')
    _, error = run_git_command(['git', 'commit', '-m', escaped_message])
    if error:
        print_colored(f"Error committing changes: {error}", Colors.RED)
        return False
    return True


def interactive_commit_flow() -> None:
    """Interactive flow for generating and committing with AI."""
    print_header("GitWhisperer AI Commit Assistant")

    # Check if we're in a Git repository
    if not check_git_repository():
        print_colored("❌ Error: Not a Git repository!", Colors.RED)
        print("Please run this command from within a Git repository.")
        return

    # Check for staged changes
    staged_diff = get_staged_diff()
    if not staged_diff:
        print_colored("No staged changes found.", Colors.YELLOW)
        stage = input("Would you like to stage all changes? (y/n): ").lower().strip()
        if stage == 'y':
            if stage_all_changes():
                print_colored("✅ Changes staged successfully!", Colors.GREEN)
                staged_diff = get_staged_diff()
            else:
                print_colored("❌ Failed to stage changes.", Colors.RED)
                return
        else:
            print("Please stage your changes first using 'git add' and try again.")
            return

    if not staged_diff:
        print_colored("No changes to commit.", Colors.YELLOW)
        return

    # Generate commit message
    print_colored("🔍 Analyzing changes...", Colors.BLUE)
    try:
        result = generate_commit_message(staged_diff)

        # Display the suggested message
        print_colored("\n📝 Suggested Commit Message:", Colors.BOLD)
        print_colored(f"  {result['commit_message']}", Colors.GREEN)

        # Show alternatives if available
        if result['suggestions']:
            print_colored("\n💡 Alternative suggestions:", Colors.BLUE)
            for i, alt in enumerate(result['suggestions'][:3], 1):
                print(f"  {i}. {alt}")

        # Get user input
        print_colored("\n" + "="*60, Colors.YELLOW)
        choice = input("Use this message? (y = yes, n = no, e = edit, q = quit): ").lower().strip()

        if choice == 'y':
            if commit_changes(result['commit_message']):
                print_colored("✅ Changes committed successfully!", Colors.GREEN)
                print(f"📋 Commit message: {result['commit_message']}")
            else:
                print_colored("❌ Failed to commit changes.", Colors.RED)

        elif choice == 'e':
            custom_message = input("Enter your commit message: ").strip()
            if custom_message:
                if commit_changes(custom_message):
                    print_colored("✅ Changes committed successfully!", Colors.GREEN)
                    print(f"📋 Commit message: {custom_message}")
                else:
                    print_colored("❌ Failed to commit changes.", Colors.RED)
            else:
                print_colored("❌ Commit message cannot be empty.", Colors.RED)

        elif choice == 'q':
            print_colored("👋 Goodbye!", Colors.BLUE)

        else:
            print_colored("❌ Commit cancelled.", Colors.YELLOW)

    except Exception as e:
        print_colored(f"❌ Error generating commit message: {e}", Colors.RED)
        print("Please check your OpenAI API key and internet connection.")


def suggest_branch_names() -> None:
    """Suggest branch names based on current changes."""
    print_header("GitWhisperer Branch Name Suggestions")

    if not check_git_repository():
        print_colored("❌ Error: Not a Git repository!", Colors.RED)
        return

    # Get the diff for analysis
    stdout, error = run_git_command(['git', 'diff', 'HEAD'])
    if error:
        print_colored("❌ Error getting diff for branch suggestion.", Colors.RED)
        return

    if not stdout:
        print_colored("No changes found to analyze.", Colors.YELLOW)
        return

    print_colored("🔍 Analyzing changes for branch name...", Colors.BLUE)

    try:
        current_branch = get_current_branch()
        result = suggest_branch_name(stdout, f"Current branch: {current_branch}")

        print_colored("\n🌿 Suggested Branch Names:", Colors.BOLD)
        print_colored(f"Primary: {result['branch_name']}", Colors.GREEN)

        if result['alternatives']:
            print_colored("Alternatives:", Colors.BLUE)
            for i, alt in enumerate(result['alternatives'], 1):
                print(f"  {i}. {alt}")

        # Copy primary suggestion to clipboard if possible
        try:
            import pyperclip
            pyperclip.copy(result['branch_name'])
            print_colored(f"\n📋 '{result['branch_name']}' copied to clipboard!", Colors.GREEN)
        except ImportError:
            print(f"\n📋 Primary suggestion: {result['branch_name']}")
            print("💡 Tip: Install pyperclip for automatic clipboard copying")

    except Exception as e:
        print_colored(f"❌ Error suggesting branch names: {e}", Colors.RED)


def summarize_pr() -> None:
    """Summarize the current pull request."""
    print_header("GitWhisperer PR Summary")

    if not check_git_repository():
        print_colored("❌ Error: Not a Git repository!", Colors.RED)
        return

    current_branch = get_current_branch()
    if current_branch == "unknown":
        print_colored("❌ Could not determine current branch.", Colors.RED)
        return

    # Get the diff for analysis
    stdout, error = run_git_command(['git', 'diff', 'HEAD'])
    if error:
        print_colored("❌ Error getting diff for PR summary.", Colors.RED)
        return

    if not stdout:
        print_colored("No changes found to summarize.", Colors.YELLOW)
        return

    print_colored(f"🔍 Analyzing branch '{current_branch}'...", Colors.BLUE)

    try:
        result = summarize_pull_request(current_branch, stdout)

        print_colored("\n📋 Pull Request Summary:", Colors.BOLD)
        print_colored(f"Summary: {result['summary']}", Colors.GREEN)
        print_colored(f"Impact: {result['impact']}", Colors.BLUE)
        print_colored(f"Testing Notes: {result['testing_notes']}", Colors.YELLOW)

        # Copy summary to clipboard if possible
        try:
            import pyperclip
            summary_text = f"Summary: {result['summary']}\nImpact: {result['impact']}\nTesting Notes: {result['testing_notes']}"
            pyperclip.copy(summary_text)
            print_colored("\n📋 Summary copied to clipboard!", Colors.GREEN)
        except ImportError:
            print(f"\n📋 Summary: {result['summary']}")
            print("💡 Tip: Install pyperclip for automatic clipboard copying")

    except Exception as e:
        print_colored(f"❌ Error summarizing PR: {e}", Colors.RED)


def check_api_key() -> bool:
    """Check if OpenAI API key is configured."""
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print_colored("❌ OpenAI API key not found!", Colors.RED)
        print("Please set your OpenAI API key in one of these ways:")
        print("1. Create a .env file with: OPENAI_API_KEY=your_key_here")
        print("2. Set environment variable: export OPENAI_API_KEY=your_key_here")
        print("3. Get your API key from: https://platform.openai.com/api-keys")
        return False
    return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GitWhisperer - AI-powered Git commit assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ai_git_cli.py commit     # Interactive commit message generation
  python ai_git_cli.py branch     # Suggest branch names
  python ai_git_cli.py pr         # Summarize current PR
  python ai_git_cli.py --help     # Show this help message
        """
    )

    parser.add_argument(
        'command',
        choices=['commit', 'branch', 'pr'],
        help='Command to run'
    )

    parser.add_argument(
        '--api-key',
        help='OpenAI API key (can also be set via OPENAI_API_KEY environment variable)'
    )

    args = parser.parse_args()

    # Set API key if provided
    if args.api_key:
        os.environ['OPENAI_API_KEY'] = args.api_key

    # Check API key
    if not check_api_key():
        return 1

    # Run the appropriate command
    try:
        if args.command == 'commit':
            interactive_commit_flow()
        elif args.command == 'branch':
            suggest_branch_names()
        elif args.command == 'pr':
            summarize_pr()
    except KeyboardInterrupt:
        print_colored("\n👋 Goodbye!", Colors.BLUE)
        return 0
    except Exception as e:
        print_colored(f"❌ Unexpected error: {e}", Colors.RED)
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)