"""
AI Commit Writer - Main backend service for GitWhisperer.
Handles AI-powered commit message generation, branch name suggestions, and PR summaries.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Import our custom git handler
from utils.git_handler import GitHandler

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize FastAPI app
app = FastAPI(title="GitWhisperer AI Backend", version="1.0.0")

# Initialize Rich console for CLI output
console = Console()


class CommitRequest(BaseModel):
    """Request model for commit message generation."""
    diff_text: str
    max_length: Optional[int] = 50
    style: Optional[str] = "conventional"  # conventional, detailed, brief


class BranchRequest(BaseModel):
    """Request model for branch name suggestion."""
    diff_text: str
    context: Optional[str] = ""


class PRRequest(BaseModel):
    """Request model for PR summary."""
    branch_name: str
    diff_text: str


class CommitResponse(BaseModel):
    """Response model for commit message."""
    commit_message: str
    confidence: float
    suggestions: List[str]


class BranchResponse(BaseModel):
    """Response model for branch name suggestion."""
    branch_name: str
    alternatives: List[str]


class PRResponse(BaseModel):
    """Response model for PR summary."""
    summary: str
    impact: str
    testing_notes: str


def generate_commit_message(diff_text: str, max_length: int = 50, style: str = "conventional") -> Dict[str, Any]:
    """
    Generate a commit message using OpenAI API.

    Args:
        diff_text: Git diff text to analyze
        max_length: Maximum character length for the commit message
        style: Style preference (conventional, detailed, brief)

    Returns:
        Dictionary containing commit message and metadata
    """
    if not diff_text.strip():
        return {
            "commit_message": "No changes detected",
            "confidence": 0.0,
            "suggestions": []
        }

    # Create style-specific prompts
    style_prompts = {
        "conventional": "Write a conventional commit message (type: description). Keep it under {max_length} characters.",
        "detailed": "Write a detailed commit message explaining the changes comprehensively. Keep it under {max_length} characters.",
        "brief": "Write a brief, concise commit message. Keep it under {max_length} characters."
    }

    prompt = f"""
    Analyze this Git diff and create a commit message following these guidelines:
    - {style_prompts.get(style, style_prompts['conventional'])}
    - Focus on what changed and why
    - Use imperative mood (e.g., "Add", "Fix", "Update")
    - Be specific but concise
    - First line should be the main summary

    Git diff:
    {diff_text}

    Return only the commit message, nothing else:
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using the faster, cheaper model
            messages=[
                {"role": "system", "content": "You are an expert developer who writes clear, concise Git commit messages."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )

        commit_message = response.choices[0].message.content.strip()
        # Remove quotes if present
        commit_message = re.sub(r'^["\']|["\']$', '', commit_message)

        # Ensure message doesn't exceed max_length
        if len(commit_message) > max_length:
            commit_message = commit_message[:max_length-3] + "..."

        # Generate alternative suggestions
        suggestions = generate_alternative_messages(diff_text, style, 3)

        return {
            "commit_message": commit_message,
            "confidence": 0.9,  # High confidence for now
            "suggestions": suggestions
        }

    except Exception as e:
        console.print(f"[red]Error generating commit message: {e}[/red]")
        return {
            "commit_message": "Update project files",
            "confidence": 0.0,
            "suggestions": ["Add new feature", "Fix bug", "Update documentation"]
        }


def generate_alternative_messages(diff_text: str, style: str, count: int) -> List[str]:
    """Generate alternative commit message suggestions."""
    try:
        prompt = f"""
        Generate {count} alternative commit messages for this diff.
        Style: {style}
        Keep each under 50 characters.
        Return as a numbered list.

        Diff:
        {diff_text[:1000]}...  # Truncate for token limits
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Generate concise commit message alternatives."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5
        )

        alternatives = response.choices[0].message.content.strip()
        # Parse the numbered list
        suggestions = []
        for line in alternatives.split('\n'):
            line = re.sub(r'^\d+\.?\s*', '', line).strip()
            if line and len(line) <= 50:
                suggestions.append(line)

        return suggestions[:count]

    except Exception:
        return ["Update files", "Add changes", "Modify code"]


def suggest_branch_name(diff_text: str, context: str = "") -> Dict[str, Any]:
    """
    Suggest a branch name based on the diff content.

    Args:
        diff_text: Git diff text to analyze
        context: Additional context about the changes

    Returns:
        Dictionary containing branch name suggestion and alternatives
    """
    if not diff_text.strip():
        return {
            "branch_name": "feature/new-changes",
            "alternatives": ["feature/updates", "feature/modifications"]
        }

    prompt = f"""
    Analyze this Git diff and suggest a branch name following these conventions:
    - Use format: type/short-description (e.g., feature/user-auth, fix/login-bug, refactor/api-endpoints)
    - Keep it under 30 characters
    - Use hyphens for spaces
    - Be descriptive but concise

    Context: {context}

    Git diff:
    {diff_text}

    Suggest one primary branch name and 2-3 alternatives.
    Return format:
    Primary: branch-name
    Alternatives: alt1, alt2, alt3
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at naming Git branches based on code changes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.4
        )

        content = response.choices[0].message.content.strip()

        # Parse the response
        primary = "feature/new-feature"  # fallback
        alternatives = ["feature/alt1", "feature/alt2"]

        for line in content.split('\n'):
            if line.lower().startswith('primary:'):
                primary = re.sub(r'^primary:\s*', '', line).strip()
            elif line.lower().startswith('alternatives:'):
                alt_text = re.sub(r'^alternatives:\s*', '', line).strip()
                alternatives = [alt.strip() for alt in alt_text.split(',') if alt.strip()]

        # Clean up branch names
        primary = re.sub(r'[^a-zA-Z0-9/-]', '-', primary.lower())
        alternatives = [re.sub(r'[^a-zA-Z0-9/-]', '-', alt.lower()) for alt in alternatives]

        return {
            "branch_name": primary,
            "alternatives": alternatives[:3]
        }

    except Exception as e:
        console.print(f"[red]Error suggesting branch name: {e}[/red]")
        return {
            "branch_name": "feature/new-changes",
            "alternatives": ["feature/updates", "feature/modifications"]
        }


def summarize_pull_request(branch_name: str, diff_text: str) -> Dict[str, Any]:
    """
    Generate a summary for a pull request.

    Args:
        branch_name: Name of the branch being merged
        diff_text: Git diff text to analyze

    Returns:
        Dictionary containing PR summary and metadata
    """
    if not diff_text.strip():
        return {
            "summary": "No changes to summarize",
            "impact": "Minimal",
            "testing_notes": "No specific testing required"
        }

    prompt = f"""
    Analyze this Git diff for a pull request and provide:

    1. A clear summary of the changes (2-3 sentences)
    2. The impact level (High/Medium/Low)
    3. Testing considerations

    Branch: {branch_name}

    Git diff:
    {diff_text}

    Format your response as:
    Summary: [summary text]
    Impact: [High/Medium/Low]
    Testing: [testing notes]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior developer reviewing pull requests."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()

        # Parse the structured response
        summary = "Changes made to the codebase"
        impact = "Medium"
        testing_notes = "Standard testing procedures apply"

        for line in content.split('\n'):
            if line.startswith('Summary:'):
                summary = re.sub(r'^Summary:\s*', '', line).strip()
            elif line.startswith('Impact:'):
                impact = re.sub(r'^Impact:\s*', '', line).strip()
            elif line.startswith('Testing:'):
                testing_notes = re.sub(r'^Testing:\s*', '', line).strip()

        return {
            "summary": summary,
            "impact": impact,
            "testing_notes": testing_notes
        }

    except Exception as e:
        console.print(f"[red]Error summarizing PR: {e}[/red]")
        return {
            "summary": "Pull request contains code changes",
            "impact": "Medium",
            "testing_notes": "Review changes before merging"
        }


# FastAPI endpoints
@app.post("/generate-commit", response_model=CommitResponse)
async def api_generate_commit(request: CommitRequest):
    """API endpoint for generating commit messages."""
    result = generate_commit_message(
        request.diff_text,
        request.max_length,
        request.style
    )
    return CommitResponse(**result)


@app.post("/suggest-branch", response_model=BranchResponse)
async def api_suggest_branch(request: BranchRequest):
    """API endpoint for suggesting branch names."""
    result = suggest_branch_name(request.diff_text, request.context)
    return BranchResponse(**result)


@app.post("/summarize-pr", response_model=PRResponse)
async def api_summarize_pr(request: PRRequest):
    """API endpoint for summarizing pull requests."""
    result = summarize_pull_request(request.branch_name, request.diff_text)
    return PRResponse(**result)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "GitWhisperer AI Backend"}


# CLI Functions
def run_cli():
    """Run the CLI interface for GitWhisperer."""
    console.print(Panel.fit(
        "[bold blue]GitWhisperer AI[/bold blue]\nAI-powered Git commit assistant",
        style="blue"
    ))

    # Initialize git handler
    git_handler = GitHandler()

    if not git_handler.is_git_repository():
        console.print("[red]Error: Not a Git repository![/red]")
        return

    # Check for staged changes
    if not git_handler.has_staged_changes():
        console.print("[yellow]No staged changes found.[/yellow]")
        stage = console.input("Stage all changes? (y/n): ")
        if stage.lower() == 'y':
            if git_handler.stage_all_changes():
                console.print("[green]Changes staged successfully![/green]")
            else:
                console.print("[red]Failed to stage changes.[/red]")
                return

    # Get the diff
    diff_text = git_handler.get_staged_diff()
    if not diff_text:
        console.print("[yellow]No changes to commit.[/yellow]")
        return

    # Generate commit message
    console.print("[cyan]Generating commit message...[/cyan]")
    result = generate_commit_message(diff_text)

    # Display result
    console.print(Panel(
        f"[bold green]Suggested Commit Message:[/bold green]\n{result['commit_message']}",
        title="GitWhisperer",
        style="green"
    ))

    # Show alternatives if available
    if result['suggestions']:
        console.print("[cyan]Alternative suggestions:[/cyan]")
        for i, alt in enumerate(result['suggestions'][:3], 1):
            console.print(f"  {i}. {alt}")

    # Get user confirmation
    use_message = console.input("\nUse this message? (y/n/edit): ")

    if use_message.lower() == 'y':
        if git_handler.commit_changes(result['commit_message']):
            console.print("[green]Changes committed successfully![/green]")
        else:
            console.print("[red]Failed to commit changes.[/red]")
    elif use_message.lower() == 'edit':
        custom_message = console.input("Enter your commit message: ")
        if git_handler.commit_changes(custom_message):
            console.print("[green]Changes committed successfully![/green]")
        else:
            console.print("[red]Failed to commit changes.[/red]")
    else:
        console.print("[yellow]Commit cancelled.[/yellow]")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Run CLI mode
        run_cli()
    else:
        # Run API server
        console.print("[green]Starting GitWhisperer API server...[/green]")
        console.print("API available at: http://localhost:8000")
        console.print("CLI mode: python ai_commit_writer.py cli")
        uvicorn.run(app, host="127.0.0.1", port=3500)