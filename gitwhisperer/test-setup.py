#!/usr/bin/env python3
"""
GitWhisperer Setup and Test Script
Tests all components of the GitWhisperer system to ensure proper installation.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path


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
    print_colored(f"🧪 {text}", Colors.BOLD)
    print_colored(f"{'='*60}")


def run_command(command: list, cwd: str = None) -> tuple:
    """Run a command and return the result."""
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
        return None, "Command not found"


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    print_colored("Checking Python version...", Colors.BLUE)

    version_output, error = run_command([sys.executable, '--version'])
    if error:
        print_colored(f"❌ Error checking Python version: {error}", Colors.RED)
        return False

    print_colored(f"✅ Python version: {version_output}", Colors.GREEN)

    # Check if Python 3.8+
    if sys.version_info < (3, 8):
        print_colored("❌ Python 3.8+ required", Colors.RED)
        return False

    return True


def check_git_repository() -> bool:
    """Check if current directory is a Git repository."""
    print_colored("Checking Git repository...", Colors.BLUE)

    _, error = run_command(['git', 'rev-parse', '--git-dir'])
    if error:
        print_colored("❌ Not a Git repository", Colors.RED)
        print("Please run this script from a Git repository or initialize one:")
        print("  git init")
        return False

    branch, error = run_command(['git', 'branch', '--show-current'])
    if error:
        print_colored("❌ Could not get current branch", Colors.RED)
        return False

    print_colored(f"✅ Git repository detected (branch: {branch})", Colors.GREEN)
    return True


def check_python_dependencies() -> bool:
    """Check if Python dependencies are installed."""
    print_colored("Checking Python dependencies...", Colors.BLUE)

    try:
        import openai
        print_colored("✅ OpenAI package installed", Colors.GREEN)
    except ImportError:
        print_colored("❌ OpenAI package not installed", Colors.RED)
        return False

    try:
        import git
        print_colored("✅ GitPython package installed", Colors.GREEN)
    except ImportError:
        print_colored("❌ GitPython package not installed", Colors.RED)
        return False

    try:
        import fastapi
        print_colored("✅ FastAPI package installed", Colors.GREEN)
    except ImportError:
        print_colored("❌ FastAPI package not installed", Colors.RED)
        return False

    try:
        import uvicorn
        print_colored("✅ Uvicorn package installed", Colors.GREEN)
    except ImportError:
        print_colored("❌ Uvicorn package not installed", Colors.RED)
        return False

    try:
        import rich
        print_colored("✅ Rich package installed", Colors.GREEN)
    except ImportError:
        print_colored("❌ Rich package not installed", Colors.RED)
        return False

    return True


def check_openai_api_key() -> bool:
    """Check if OpenAI API key is configured."""
    print_colored("Checking OpenAI API key...", Colors.BLUE)

    # Load .env file if it exists
    env_file = Path('.env')
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print_colored("📄 Loaded .env file", Colors.BLUE)
        except ImportError:
            print_colored("⚠️  python-dotenv not available for .env loading", Colors.YELLOW)

    # Check environment variable
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print_colored("❌ OpenAI API key not found", Colors.RED)
        print("Please set your API key:")
        print("1. Add to .env file: OPENAI_API_KEY=your_actual_key_here")
        print("2. Or set environment variable: export OPENAI_API_KEY=your_key")
        print("3. Get your key from: https://platform.openai.com/api-keys")
        print("\n💡 Make sure to replace 'your_actual_key_here' with your real API key!")
        return False

    # Validate API key format (OpenAI keys start with 'sk-')
    if not api_key.startswith('sk-'):
        print_colored("❌ API key doesn't look valid (should start with 'sk-')", Colors.RED)
        return False

    print_colored("✅ OpenAI API key configured", Colors.GREEN)
    return True


def test_python_backend() -> bool:
    """Test the Python backend functionality."""
    print_colored("Testing Python backend...", Colors.BLUE)

    try:
        # Import the backend modules using absolute path
        backend_dir = Path('gitwhisperer/python-backend')
        sys.path.insert(0, str(backend_dir))

        from ai_commit_writer import generate_commit_message

        # Test with a simple diff
        test_diff = """diff --git a/test.txt b/test.txt
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/test.txt
@@ -0,0 +1 @@
+Hello, World!"""

        result = generate_commit_message(test_diff)

        if 'commit_message' in result and result['commit_message']:
            print_colored("✅ Backend generates commit messages successfully", Colors.GREEN)
            print(f"   Sample: {result['commit_message']}")
            return True
        else:
            print_colored("❌ Backend failed to generate commit message", Colors.RED)
            return False

    except Exception as e:
        print_colored(f"❌ Backend test failed: {e}", Colors.RED)
        return False


def check_node_dependencies() -> bool:
    """Check if Node.js dependencies are installed."""
    print_colored("Checking Node.js dependencies...", Colors.BLUE)

    vscode_path = 'gitwhisperer/vscode-extension'
    package_json_path = f'{vscode_path}/package.json'

    if not os.path.exists(package_json_path):
        print_colored(f"❌ VS Code extension package.json not found at {package_json_path}", Colors.RED)
        return False

    # Check if node_modules exists
    node_modules_path = f'{vscode_path}/node_modules'
    if not os.path.exists(node_modules_path):
        print_colored("❌ Node modules not installed", Colors.RED)
        print(f"Please run: cd {vscode_path} && npm install")
        return False

    print_colored("✅ Node modules installed", Colors.GREEN)
    return True


def test_cli_tool() -> bool:
    """Test the CLI tool."""
    print_colored("Testing CLI tool...", Colors.BLUE)

    cli_path = 'gitwhisperer/cli-tool/ai_git_cli.py'
    if not os.path.exists(cli_path):
        print_colored("❌ CLI tool not found", Colors.RED)
        return False

    # Test help command (without API key requirement)
    output, error = run_command([sys.executable, cli_path, '--help'])
    if error and "OPENAI_API_KEY" not in str(error):
        print_colored(f"❌ CLI tool error: {error}", Colors.RED)
        return False

    if '--help' in str(output).lower() or 'usage:' in str(output).lower():
        print_colored("✅ CLI tool runs successfully", Colors.GREEN)
        return True

    print_colored("❌ CLI tool help not accessible", Colors.RED)
    return False


def create_test_commit() -> bool:
    """Create a test commit to verify Git integration."""
    print_colored("Creating test commit...", Colors.BLUE)

    # Create a test file
    test_file = 'test_gitwhisperer.txt'
    with open(test_file, 'w') as f:
        f.write(f"Test file for GitWhisperer - {os.urandom(4).hex()}\n")

    # Stage and commit
    _, error = run_command(['git', 'add', test_file])
    if error:
        print_colored(f"❌ Failed to stage test file: {error}", Colors.RED)
        return False

    _, error = run_command(['git', 'commit', '-m', 'test: GitWhisperer test commit'])
    if error:
        print_colored(f"❌ Failed to create test commit: {error}", Colors.RED)
        return False

    print_colored("✅ Test commit created successfully", Colors.GREEN)
    return True


def cleanup_test_files() -> None:
    """Clean up test files."""
    test_file = 'test_gitwhisperer.txt'
    if os.path.exists(test_file):
        os.remove(test_file)
        print_colored("🧹 Cleaned up test files", Colors.YELLOW)


def main():
    """Main test function."""
    print_header("GitWhisperer Installation Test")

    tests = [
        ("Python Version", check_python_version),
        ("Git Repository", check_git_repository),
        ("Python Dependencies", check_python_dependencies),
        ("OpenAI API Key", check_openai_api_key),
        ("Python Backend", test_python_backend),
        ("Node Dependencies", check_node_dependencies),
        ("CLI Tool", test_cli_tool),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print_colored(f"\n🧪 Running: {test_name}", Colors.BOLD)
        if test_func():
            passed += 1

    # Test Git integration
    print_colored(f"\n🧪 Running: Git Integration", Colors.BOLD)
    if create_test_commit():
        passed += 1

    total += 1

    # Summary
    print_header("Test Summary")
    print_colored(f"Passed: {passed}/{total}", Colors.BOLD)

    if passed == total:
        print_colored("🎉 All tests passed! GitWhisperer is ready to use.", Colors.GREEN)
        print_colored("\nNext steps:", Colors.BLUE)
        print("1. VS Code: Use Command Palette → 'GitWhisperer: Generate AI Commit Message'")
        print("2. CLI: Run 'python cli-tool/ai_git_cli.py commit'")
        print("3. API: Start backend with 'python python-backend/ai_commit_writer.py'")
    else:
        print_colored("❌ Some tests failed. Please fix the issues above.", Colors.RED)
        print_colored("\nFor help, check:", Colors.BLUE)
        print("- README.md for installation instructions")
        print("- Troubleshooting section in README.md")
        return 1

    # Cleanup
    cleanup_test_files()

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)