/**
 * Git utilities for GitWhisperer VS Code extension.
 * Handles Git operations using Node.js child_process.
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const vscode = require('vscode');

/**
 * Git utility class for handling Git operations in the VS Code extension.
 */
class GitUtils {
    /**
     * Get the path of the current workspace folder.
     * @returns {string|null} Workspace path or null if no workspace is open.
     */
    static getWorkspacePath() {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        return workspaceFolders && workspaceFolders.length > 0
            ? workspaceFolders[0].uri.fsPath
            : null;
    }

    /**
     * Check if the current directory is a Git repository.
     * @param {string} workspacePath - Path to the workspace directory.
     * @returns {Promise<boolean>} True if it's a Git repository, false otherwise.
     */
    static async isGitRepository(workspacePath) {
        try {
            await execAsync('git rev-parse --git-dir', { cwd: workspacePath });
            return true;
        } catch (error) {
            return false;
        }
    }

    /**
     * Get the staged Git diff.
     * @param {string} workspacePath - Path to the workspace directory.
     * @returns {Promise<string>} The staged diff as a string.
     */
    static async getStagedDiff(workspacePath) {
        try {
            const { stdout } = await execAsync('git diff --cached', {
                cwd: workspacePath,
                encoding: 'utf8'
            });
            return stdout;
        } catch (error) {
            console.error('Error getting staged diff:', error);
            return '';
        }
    }

    /**
     * Get the unstaged Git diff.
     * @param {string} workspacePath - Path to the workspace directory.
     * @returns {Promise<string>} The unstaged diff as a string.
     */
    static async getUnstagedDiff(workspacePath) {
        try {
            const { stdout } = await execAsync('git diff', {
                cwd: workspacePath,
                encoding: 'utf8'
            });
            return stdout;
        } catch (error) {
            console.error('Error getting unstaged diff:', error);
            return '';
        }
    }

    /**
     * Get the combined diff (staged + unstaged changes).
     * @param {string} workspacePath - Path to the workspace directory.
     * @returns {Promise<string>} The combined diff as a string.
     */
    static async getCombinedDiff(workspacePath) {
        try {
            const { stdout } = await execAsync('git diff HEAD', {
                cwd: workspacePath,
                encoding: 'utf8'
            });
            return stdout;
        } catch (error) {
            console.error('Error getting combined diff:', error);
            return '';
        }
    }

    /**
     * Get the current branch name.
     * @param {string} workspacePath - Path to the workspace directory.
     * @returns {Promise<string>} The current branch name.
     */
    static async getCurrentBranch(workspacePath) {
        try {
            const { stdout } = await execAsync('git branch --show-current', {
                cwd: workspacePath,
                encoding: 'utf8'
            });
            return stdout.trim();
        } catch (error) {
            console.error('Error getting current branch:', error);
            return '';
        }
    }

    /**
     * Get a list of changed files.
     * @param {string} workspacePath - Path to the workspace directory.
     * @returns {Promise<string[]>} Array of changed file paths.
     */
    static async getChangedFiles(workspacePath) {
        try {
            const { stdout } = await execAsync('git diff --name-only HEAD', {
                cwd: workspacePath,
                encoding: 'utf8'
            });
            return stdout.trim().split('\n').filter(file => file.length > 0);
        } catch (error) {
            console.error('Error getting changed files:', error);
            return [];
        }
    }

    /**
     * Check if there are staged changes ready for commit.
     * @param {string} workspacePath - Path to the workspace directory.
     * @returns {Promise<boolean>} True if there are staged changes.
     */
    static async hasStagedChanges(workspacePath) {
        try {
            const { stdout } = await execAsync('git diff --cached --name-only', {
                cwd: workspacePath,
                encoding: 'utf8'
            });
            return stdout.trim().length > 0;
        } catch (error) {
            console.error('Error checking staged changes:', error);
            return false;
        }
    }

    /**
     * Stage all changes in the repository.
     * @param {string} workspacePath - Path to the workspace directory.
     * @returns {Promise<boolean>} True if successful.
     */
    static async stageAllChanges(workspacePath) {
        try {
            await execAsync('git add .', { cwd: workspacePath });
            return true;
        } catch (error) {
            console.error('Error staging changes:', error);
            return false;
        }
    }

    /**
     * Commit changes with a specific message.
     * @param {string} workspacePath - Path to the workspace directory.
     * @param {string} message - The commit message.
     * @returns {Promise<boolean>} True if successful.
     */
    static async commitChanges(workspacePath, message) {
        try {
            await execAsync(`git commit -m "${message.replace(/"/g, '\\"')}"`, {
                cwd: workspacePath
            });
            return true;
        } catch (error) {
            console.error('Error committing changes:', error);
            return false;
        }
    }

    /**
     * Get recent commit history for context.
     * @param {string} workspacePath - Path to the workspace directory.
     * @param {number} limit - Number of commits to retrieve (default: 10).
     * @returns {Promise<string[]>} Array of recent commit messages.
     */
    static async getCommitHistory(workspacePath, limit = 10) {
        try {
            const { stdout } = await execAsync(`git log -${limit} --oneline`, {
                cwd: workspacePath,
                encoding: 'utf8'
            });
            return stdout.trim().split('\n').filter(line => line.length > 0);
        } catch (error) {
            console.error('Error getting commit history:', error);
            return [];
        }
    }

    /**
     * Get Git status information.
     * @param {string} workspacePath - Path to the workspace directory.
     * @returns {Promise<object>} Object containing status information.
     */
    static async getStatus(workspacePath) {
        try {
            const { stdout } = await execAsync('git status --porcelain', {
                cwd: workspacePath,
                encoding: 'utf8'
            });

            const lines = stdout.trim().split('\n').filter(line => line.length > 0);
            const staged = [];
            const unstaged = [];
            const untracked = [];

            for (const line of lines) {
                const status = line.substring(0, 2);
                const file = line.substring(3);

                if (status[0] !== ' ') {
                    staged.push({ file, status: status[0] });
                }
                if (status[1] !== ' ') {
                    if (status[1] === '?') {
                        untracked.push(file);
                    } else {
                        unstaged.push({ file, status: status[1] });
                    }
                }
            }

            return {
                staged,
                unstaged,
                untracked,
                hasChanges: staged.length > 0 || unstaged.length > 0 || untracked.length > 0
            };
        } catch (error) {
            console.error('Error getting Git status:', error);
            return { staged: [], unstaged: [], untracked: [], hasChanges: false };
        }
    }

    /**
     * Show an error message if not in a Git repository.
     * @returns {Promise<boolean>} True if in Git repository, false otherwise.
     */
    static async checkGitRepository() {
        const workspacePath = this.getWorkspacePath();
        if (!workspacePath) {
            vscode.window.showErrorMessage('No workspace folder is open.');
            return false;
        }

        const isGitRepo = await this.isGitRepository(workspacePath);
        if (!isGitRepo) {
            vscode.window.showErrorMessage(
                'Current workspace is not a Git repository. Please initialize a Git repository first.'
            );
            return false;
        }

        return true;
    }

    /**
     * Show an error message if no staged changes exist.
     * @returns {Promise<boolean>} True if staged changes exist, false otherwise.
     */
    static async checkStagedChanges() {
        const workspacePath = this.getWorkspacePath();
        if (!workspacePath) {
            return false;
        }

        const hasStaged = await this.hasStagedChanges(workspacePath);
        if (!hasStaged) {
            const action = await vscode.window.showWarningMessage(
                'No staged changes found. Would you like to stage all changes?',
                'Stage All',
                'Cancel'
            );

            if (action === 'Stage All') {
                const success = await this.stageAllChanges(workspacePath);
                if (!success) {
                    vscode.window.showErrorMessage('Failed to stage changes.');
                    return false;
                }
                return true;
            }
            return false;
        }

        return true;
    }
}

module.exports = GitUtils;