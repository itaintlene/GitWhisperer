# GitWhisperer 🤖

An AI-powered Git commit assistant that whispers the perfect commit messages, suggests branch names, and summarizes pull requests.

GitWhisperer is a comprehensive AI-powered developer tool that integrates seamlessly with VS Code and Git CLI to automatically generate intelligent commit messages, suggest meaningful branch names, and create detailed pull request summaries using advanced AI. Boost your productivity, maintain consistent commit practices, and save valuable time on routine Git operations.

---

## Features ✨

* **🎯 AI-Powered Commit Messages**: Generate professional, concise commit messages based on staged changes with multiple style options (conventional, detailed, brief)
* **🌿 Smart Branch Name Suggestions**: Generate semantic branch names that follow best practices based on your code changes
* **📋 Pull Request Summaries**: Automatically create comprehensive PR descriptions with impact analysis and testing notes
* **💻 VS Code Integration**: Native VS Code extension with command palette integration and intelligent progress tracking
* **🖥️ CLI Support**: Full-featured command-line interface for terminal-based workflows
* **🔧 Configurable Settings**: Customize AI behavior, commit styles, and API settings through VS Code configuration
* **🚀 FastAPI Backend**: RESTful API server for reliable communication between components
* **📊 Rich Terminal UI**: Beautiful colored output with progress indicators and interactive prompts

---

## Tech Stack 🛠️

* **VS Code Extension**: JavaScript, Node.js, VS Code API, Axios
* **Python Backend**: Python 3.8+, OpenAI API (GPT-4o-mini), FastAPI, GitPython, Rich CLI
* **Development**: Git, VS Code, Command Line Interface

---

## Project Structure 📂

```
gitwhisperer/
│
├─ vscode-extension/
│   ├─ package.json          # Extension manifest and configuration
│   ├─ extension.js          # Main extension logic and API integration
│   └─ utils/
│       └─ gitUtils.js       # Git operations and utilities
│
├─ python-backend/
│   ├─ ai_commit_writer.py   # Main AI backend with FastAPI server
│   ├─ requirements.txt      # Python dependencies
│   └─ utils/
│       └─ git_handler.py    # Git operations and diff parsing
│
├─ cli-tool/
│   └─ ai_git_cli.py         # Command-line interface tool
│
├─ .gitignore               # Git ignore patterns
├─ LICENSE                  # MIT License
└─ README.md                # This file
```

---

## Installation 🚀

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** and npm
- **Git** installed and configured
- **OpenAI API Key** (get yours at [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys))

### 1. Clone and Setup

```bash
git clone <repository-url>
cd gitwhisperer
```

### 2. Python Backend Setup

```bash
cd python-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key (choose one method):
# Option 1: Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Option 2: Set environment variable
export OPENAI_API_KEY=your_api_key_here

# Test the backend
python ai_commit_writer.py cli
```

### 3. VS Code Extension Setup

```bash
# Install Node dependencies
cd ../vscode-extension
npm install

# Package the extension (optional, for distribution)
npm run package

# For development: Open in VS Code and press F5 to test
code .
```

### 4. CLI Tool Setup

The CLI tool is ready to use once the Python backend is installed:

```bash
# Make executable (optional, on Unix systems)
chmod +x ../cli-tool/ai_git_cli.py
```

---

## Usage 📝

### VS Code Extension

1. **Open VS Code** in your project directory
2. **Stage your changes**:
   ```bash
   git add .
   ```
3. **Generate AI Commit Message**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "GitWhisperer" and select "Generate AI Commit Message"
   - Review and edit the suggested message
   - Confirm to commit

4. **Suggest Branch Names**:
   - Use Command Palette: "GitWhisperer: Suggest Branch Name"
   - Choose from AI-generated suggestions
   - Branch name is copied to clipboard

5. **Summarize Pull Requests**:
   - Use Command Palette: "GitWhisperer: Summarize Pull Request"
   - Get comprehensive PR description with impact analysis

### Command Line Interface

#### Generate Commit Messages

```bash
# Navigate to your project (must be a Git repository)
cd /path/to/your/project

# Basic usage - interactive mode
python cli-tool/ai_git_cli.py commit

# With API key
python cli-tool/ai_git_cli.py --api-key YOUR_API_KEY commit
```

**Interactive Flow:**
1. Analyzes staged changes
2. Shows AI-generated commit message
3. Provides alternatives
4. Options: (y)es, (n)o, (e)dit, (q)uit

#### Suggest Branch Names

```bash
python cli-tool/ai_git_cli.py branch
```

**Features:**
- Analyzes current changes
- Suggests semantic branch names
- Shows multiple alternatives
- Copies suggestion to clipboard (if pyperclip installed)

#### Summarize Pull Requests

```bash
python cli-tool/ai_git_cli.py pr
```

**Output includes:**
- Comprehensive change summary
- Impact level assessment
- Testing recommendations

### Configuration ⚙️

#### VS Code Settings

Open VS Code settings (`Ctrl+,`) and search for "GitWhisperer":

```json
{
  "gitwhisperer.openaiApiKey": "your-api-key-here",
  "gitwhisperer.backendPort": 8000,
  "gitwhisperer.commitStyle": "conventional",
  "gitwhisperer.maxCommitLength": 50
}
```

#### Environment Variables

```bash
# OpenAI API Key
export OPENAI_API_KEY=your_api_key_here

# Backend port (optional)
export GITWHISPERER_PORT=8000
```

---

## API Reference 🔌

The Python backend provides a RESTful API for external integrations:

### Endpoints

- **POST** `/generate-commit` - Generate commit messages
- **POST** `/suggest-branch` - Suggest branch names
- **POST** `/summarize-pr` - Summarize pull requests
- **GET** `/health` - Health check

### Example API Usage

```bash
# Start the API server
cd python-backend
python ai_commit_writer.py

# Generate commit message via API
curl -X POST http://localhost:8000/generate-commit \
  -H "Content-Type: application/json" \
  -d '{"diff_text": "your git diff here", "style": "conventional"}'
```

---

## Development 🛠️

### Running Tests

```bash
# Test Python backend
cd python-backend
python -m pytest

# Test VS Code extension
cd vscode-extension
npm test
```

### Debugging

**VS Code Extension:**
- Press `F5` to launch extension in debug mode
- Set breakpoints in `extension.js`

**Python Backend:**
- Run with debug logging: `python ai_commit_writer.py`
- Check API responses at `http://localhost:8000/docs`

### Project Structure Guidelines

- **Modular Design**: Keep utilities separate from main logic
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Type Hints**: Use Python type hints for better IDE support
- **Documentation**: Document all public functions and classes

---

## Troubleshooting 🔧

### Common Issues

**"OpenAI API key not found"**
- Ensure API key is set in `.env` file or environment variables
- Check that the key is valid and has credits

**"Not a Git repository"**
- Run commands from within a Git repository
- Initialize Git if needed: `git init`

**"Backend server not running"**
- Start the Python backend: `python ai_commit_writer.py`
- Check if port 8000 is available

**"Extension not working in VS Code"**
- Reload VS Code window (`Ctrl+Shift+P` → "Developer: Reload Window")
- Check that Python backend is running
- Verify API key configuration

### Getting Help

1. Check the [Issues](../../issues) page for known problems
2. Create a new issue with detailed error messages
3. Include your environment details (OS, Python version, VS Code version)

---

## Roadmap 🗺️

- [x] AI-generated commit messages
- [x] Branch name suggestions
- [x] Pull request summaries
- [ ] Local analytics dashboard
- [ ] Commit style learning from history
- [ ] Changelog generator
- [ ] Integration with popular Git hosting services
- [ ] Custom AI model support (local models)
- [ ] Team collaboration features

---

## Contributing 🤝

We welcome contributions! Here's how to get involved:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes with comprehensive tests
4. **Test** thoroughly across different environments
5. **Commit** with clear, descriptive messages (use GitWhisperer! 😉)
6. **Push** your branch and open a Pull Request

### Development Guidelines

- Follow existing code style and conventions
- Add tests for new features
- Update documentation for API changes
- Ensure cross-platform compatibility (Windows/macOS/Linux)

---

## License 📄

**MIT License** © 2024 Harleen

See [LICENSE](LICENSE) for full license text.

---

## Support 💬

- 📧 **Email**: [your-email@example.com]
- 🐛 **Issues**: [GitHub Issues](../../issues)
- 📖 **Documentation**: This README and inline code comments
- 💬 **Discussions**: [GitHub Discussions](../../discussions)

---

<div align="center">

**Made with ❤️ by Harleen**

[⭐ Star this repo](../../) • [🐛 Report issues](../../issues) • [💻 Contribute](../../)

</div>
