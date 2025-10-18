/**
 * Main entry point for GitWhisperer VS Code extension.
 * Provides AI-powered Git commit message generation, branch name suggestions, and PR summaries.
 */

const vscode = require('vscode');
const axios = require('axios');
const { spawn } = require('child_process');
const path = require('path');
const GitUtils = require('./utils/gitUtils');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('GitWhisperer extension is now active!');

    // Configuration
    const config = vscode.workspace.getConfiguration('gitwhisperer');
    const apiKey = config.get('openaiApiKey');
    const backendPort = config.get('backendPort', 8000);

    // Check if API key is configured
    if (!apiKey) {
        vscode.window.showWarningMessage(
            'GitWhisperer: OpenAI API key not configured. Please set it in VS Code settings.',
            'Open Settings'
        ).then(action => {
            if (action === 'Open Settings') {
                vscode.commands.executeCommand('workbench.action.openSettings', 'gitwhisperer.openaiApiKey');
            }
        });
    }

    // Command: Generate AI Commit Message
    let generateCommitDisposable = vscode.commands.registerCommand('gitwhisperer.generateCommit', async () => {
        try {
            // Check if we're in a Git repository
            if (!(await GitUtils.checkGitRepository())) {
                return;
            }

            // Check for staged changes
            if (!(await GitUtils.checkStagedChanges())) {
                return;
            }

            const workspacePath = GitUtils.getWorkspacePath();
            if (!workspacePath) {
                return;
            }

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'GitWhisperer',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Analyzing changes...' });

                // Get the staged diff
                const diffText = await GitUtils.getStagedDiff(workspacePath);
                if (!diffText) {
                    vscode.window.showWarningMessage('No staged changes found to analyze.');
                    return;
                }

                progress.report({ increment: 25, message: 'Generating commit message...' });

                // Start Python backend if not running
                const backendRunning = await checkBackendServer(backendPort);
                if (!backendRunning) {
                    await startPythonBackend(workspacePath);
                    // Wait a moment for server to start
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }

                progress.report({ increment: 50, message: 'Contacting AI service...' });

                try {
                    // Call the Python backend API
                    const response = await axios.post(`http://localhost:${backendPort}/generate-commit`, {
                        diff_text: diffText,
                        max_length: config.get('maxCommitLength', 50),
                        style: config.get('commitStyle', 'conventional')
                    }, {
                        timeout: 30000,
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });

                    progress.report({ increment: 75, message: 'Processing response...' });

                    const result = response.data;

                    // Show input box for user to confirm/edit the message
                    const selectedMessage = await vscode.window.showInputBox({
                        prompt: 'AI-Generated Commit Message (edit if needed)',
                        value: result.commit_message,
                        placeHolder: 'Enter your commit message',
                        validateInput: (value) => {
                            if (!value || value.trim().length === 0) {
                                return 'Commit message cannot be empty';
                            }
                            if (value.length > 100) {
                                return 'Commit message should be under 100 characters (first line)';
                            }
                            return null;
                        }
                    });

                    if (selectedMessage) {
                        progress.report({ increment: 90, message: 'Committing changes...' });

                        // Commit the changes
                        const success = await GitUtils.commitChanges(workspacePath, selectedMessage);

                        if (success) {
                            vscode.window.showInformationMessage(
                                `Successfully committed with message: "${selectedMessage}"`
                            );

                            // Show alternative suggestions if available
                            if (result.suggestions && result.suggestions.length > 0) {
                                const showAlternatives = await vscode.window.showInformationMessage(
                                    'Would you like to see alternative commit message suggestions?',
                                    'Show Alternatives'
                                );

                                if (showAlternatives === 'Show Alternatives') {
                                    const alternativesText = result.suggestions
                                        .slice(0, 3)
                                        .map((alt, index) => `${index + 1}. ${alt}`)
                                        .join('\n');

                                    vscode.window.showInformationMessage(
                                        `Alternative suggestions:\n${alternativesText}`,
                                        { modal: true }
                                    );
                                }
                            }
                        } else {
                            vscode.window.showErrorMessage('Failed to commit changes. Please check your Git status.');
                        }
                    }

                } catch (error) {
                    console.error('Error calling backend API:', error);

                    if (error.code === 'ECONNREFUSED') {
                        vscode.window.showErrorMessage(
                            'Could not connect to GitWhisperer backend server. Please ensure the Python backend is running.',
                            'Start Backend',
                            'Retry'
                        ).then(action => {
                            if (action === 'Start Backend') {
                                startPythonBackend(workspacePath);
                            }
                        });
                    } else if (error.response && error.response.status === 401) {
                        vscode.window.showErrorMessage(
                            'Invalid OpenAI API key. Please check your configuration.',
                            'Open Settings'
                        ).then(action => {
                            if (action === 'Open Settings') {
                                vscode.commands.executeCommand('workbench.action.openSettings', 'gitwhisperer.openaiApiKey');
                            }
                        });
                    } else {
                        vscode.window.showErrorMessage(
                            `Error generating commit message: ${error.message}`
                        );
                    }
                }
            });

        } catch (error) {
            console.error('Error in generateCommit command:', error);
            vscode.window.showErrorMessage(`Unexpected error: ${error.message}`);
        }
    });

    // Command: Suggest Branch Name
    let suggestBranchDisposable = vscode.commands.registerCommand('gitwhisperer.suggestBranch', async () => {
        try {
            if (!(await GitUtils.checkGitRepository())) {
                return;
            }

            const workspacePath = GitUtils.getWorkspacePath();
            if (!workspacePath) {
                return;
            }

            // Get the diff for branch name suggestion
            const diffText = await GitUtils.getCombinedDiff(workspacePath);
            if (!diffText) {
                vscode.window.showWarningMessage('No changes found to analyze for branch name suggestion.');
                return;
            }

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'GitWhisperer',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Analyzing changes...' });

                // Start Python backend if not running
                const backendRunning = await checkBackendServer(backendPort);
                if (!backendRunning) {
                    await startPythonBackend(workspacePath);
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }

                progress.report({ increment: 50, message: 'Generating branch name...' });

                try {
                    const response = await axios.post(`http://localhost:${backendPort}/suggest-branch`, {
                        diff_text: diffText,
                        context: `Current branch: ${await GitUtils.getCurrentBranch(workspacePath)}`
                    });

                    const result = response.data;

                    // Show branch name suggestions
                    const selectedBranch = await vscode.window.showQuickPick(
                        [
                            {
                                label: result.branch_name,
                                description: 'Primary suggestion',
                                detail: 'Recommended branch name'
                            },
                            ...result.alternatives.map((alt, index) => ({
                                label: alt,
                                description: `Alternative ${index + 1}`,
                                detail: `Alternative suggestion ${index + 1}`
                            }))
                        ],
                        {
                            placeHolder: 'Select a branch name',
                            matchOnDescription: true,
                            matchOnDetail: true
                        }
                    );

                    if (selectedBranch) {
                        // Copy branch name to clipboard
                        await vscode.env.clipboard.writeText(selectedBranch.label);
                        vscode.window.showInformationMessage(
                            `Branch name "${selectedBranch.label}" copied to clipboard!`
                        );
                    }

                } catch (error) {
                    console.error('Error suggesting branch name:', error);
                    vscode.window.showErrorMessage(
                        `Error generating branch name suggestion: ${error.message}`
                    );
                }
            });

        } catch (error) {
            console.error('Error in suggestBranch command:', error);
            vscode.window.showErrorMessage(`Unexpected error: ${error.message}`);
        }
    });

    // Command: Summarize Pull Request
    let summarizePRDisposable = vscode.commands.registerCommand('gitwhisperer.summarizePR', async () => {
        try {
            if (!(await GitUtils.checkGitRepository())) {
                return;
            }

            const workspacePath = GitUtils.getWorkspacePath();
            if (!workspacePath) {
                return;
            }

            const currentBranch = await GitUtils.getCurrentBranch(workspacePath);
            if (!currentBranch) {
                vscode.window.showWarningMessage('Could not determine current branch.');
                return;
            }

            // Get the diff for PR summary
            const diffText = await GitUtils.getCombinedDiff(workspacePath);
            if (!diffText) {
                vscode.window.showWarningMessage('No changes found to summarize.');
                return;
            }

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'GitWhisperer',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Analyzing changes...' });

                // Start Python backend if not running
                const backendRunning = await checkBackendServer(backendPort);
                if (!backendRunning) {
                    await startPythonBackend(workspacePath);
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }

                progress.report({ increment: 50, message: 'Generating PR summary...' });

                try {
                    const response = await axios.post(`http://localhost:${backendPort}/summarize-pr`, {
                        branch_name: currentBranch,
                        diff_text: diffText
                    });

                    const result = response.data;

                    // Show PR summary in a formatted message
                    const summaryMessage = [
                        `**Summary:** ${result.summary}`,
                        `**Impact:** ${result.impact}`,
                        `**Testing Notes:** ${result.testing_notes}`
                    ].join('\n\n');

                    vscode.window.showInformationMessage(
                        summaryMessage,
                        { modal: true },
                        'Copy Summary'
                    ).then(action => {
                        if (action === 'Copy Summary') {
                            vscode.env.clipboard.writeText(summaryMessage);
                        }
                    });

                } catch (error) {
                    console.error('Error summarizing PR:', error);
                    vscode.window.showErrorMessage(
                        `Error generating PR summary: ${error.message}`
                    );
                }
            });

        } catch (error) {
            console.error('Error in summarizePR command:', error);
            vscode.window.showErrorMessage(`Unexpected error: ${error.message}`);
        }
    });

    // Register all commands
    context.subscriptions.push(generateCommitDisposable);
    context.subscriptions.push(suggestBranchDisposable);
    context.subscriptions.push(summarizePRDisposable);

    // Show welcome message on first activation
    if (context.globalState.get('gitwhisperer.welcomeShown') !== true) {
        vscode.window.showInformationMessage(
            'Welcome to GitWhisperer! 🤖 Your AI-powered Git assistant is ready. Make sure to configure your OpenAI API key in settings.',
            'Open Settings',
            'Got it'
        ).then(action => {
            if (action === 'Open Settings') {
                vscode.commands.executeCommand('workbench.action.openSettings', 'gitwhisperer.openaiApiKey');
            }
        });

        context.globalState.update('gitwhisperer.welcomeShown', true);
    }
}

/**
 * Check if the Python backend server is running.
 * @param {number} port - Port number to check.
 * @returns {Promise<boolean>} True if server is running.
 */
async function checkBackendServer(port) {
    try {
        await axios.get(`http://localhost:${port}/health`, { timeout: 1000 });
        return true;
    } catch (error) {
        return false;
    }
}

/**
 * Start the Python backend server.
 * @param {string} workspacePath - Path to the workspace directory.
 */
async function startPythonBackend(workspacePath) {
    const pythonBackendPath = path.join(workspacePath, 'python-backend', 'ai_commit_writer.py');

    // Check if Python is available
    try {
        const { spawn } = require('child_process');
        const pythonProcess = spawn('python', [pythonBackendPath], {
            cwd: path.dirname(pythonBackendPath),
            detached: true,
            stdio: 'ignore'
        });

        pythonProcess.unref();

        vscode.window.showInformationMessage(
            'Starting GitWhisperer backend server... Please wait a moment before using AI features.'
        );

    } catch (error) {
        vscode.window.showErrorMessage(
            `Failed to start Python backend: ${error.message}. Please ensure Python and required packages are installed.`
        );
    }
}

function deactivate() {
    console.log('GitWhisperer extension is now deactivated!');
}

module.exports = {
    activate,
    deactivate
};