# GitWhisperer 🤖

An AI that whispers your commits to git.

GitWhisperer is a local AI-powered developer tool that integrates with VS Code and the CLI to automatically generate commit messages, suggest branch names, and summarize pull requests using AI. Boost your workflow, maintain consistent commit practices, and save time on routine Git operations.

---

## Features ✨

* **AI-Powered Commit Messages**: Generate professional, concise commit messages based on staged changes.
* **Pull Request Summaries (future enhancement)**: Automatically summarize code changes for PR descriptions.
* **Branch Name Suggestions (future enhancement)**: Generate semantic branch names based on the feature or fix.
* **VS Code Integration**: Trigger AI commit suggestions directly inside VS Code with a simple command.
* **CLI Support**: Run AI commit generation from the terminal for non-VS Code workflows.
* **Modular Design**: Python backend handles AI logic, while the JS VS Code extension provides seamless integration.

---

## Tech Stack 🛠️

* **Frontend / VS Code Extension**: JavaScript, Node.js, VS Code API
* **Backend / AI Engine**: Python, OpenAI API or HuggingFace models, GitPython
* **Optional Backend / Analytics**: FastAPI, SQLite/JSON

---

## Project Structure 📂

ai-git-assistant/
│
├─ vscode-extension/
│   ├─ package.json
│   ├─ extension.js
│   └─ utils/
│       └─ gitUtils.js
│
├─ python-backend/
│   ├─ ai_commit_writer.py
│   ├─ utils/
│   │   └─ git_handler.py
│   └─ requirements.txt
│
├─ cli-tool/
│   └─ ai_git_cli.py
│
├─ README.md
└─ .gitignore


---

## Installation 🚀

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/yourusername/ai-git-assistant.git](https://github.com/yourusername/ai-git-assistant.git)
    cd ai-git-assistant
    ```

2.  **Set Up Python Backend**
    ```bash
    cd python-backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Install VS Code Extension Locally**
    ```bash
    cd ../vscode-extension
    code .
    ```
    Press `F5` in VS Code to launch a new window with your extension active.

---

## Usage 📝

### VS Code Command

1.  Stage your changes with Git:
    ```bash
    git add .
    ```
2.  Run the **AI Commit Message** command from the VS Code Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`).
3.  Review or edit the AI-suggested commit message.
4.  The commit is created automatically.

### CLI Usage

1.  Navigate to the CLI tool directory:
    ```bash
    cd cli-tool
    ```
2.  Run the script:
    ```bash
    python ai_git_cli.py
    ```
    This outputs AI-generated commit messages directly into your terminal.

---

## Roadmap / Future Enhancements 🗺️

-   [ ] Pull request summary generator
-   [ ] Branch name suggestions
-   [ ] Automatic changelog generation
-   [ ] Analytics dashboard (track AI commit adoption, time saved, commit stats)
-   [ ] AI learning based on your personal commit style

---

## Contributing 🤝

Contributions are welcome!

1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/AmazingFeature`).
3.  Add your features or enhancements.
4.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
5.  Push to the branch (`git push origin feature/AmazingFeature`).
6.  Submit a Pull Request with a detailed description.

---

## License 📄

**MIT License** © Harleen
