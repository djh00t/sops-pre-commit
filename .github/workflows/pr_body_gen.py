#!/usr/bin/env python3
"""
This script generates a pull request body using commit messages and templates.

It fetches commit messages from the current branch, categorizes them, and
renders a pull request body using a Jinja2 template.

Typical usage example:
    $ python .github/workflows/pr_body_gen.py
"""

import os
import re
import subprocess
import sys
from jinja2 import Template

# Path to the Jinja2 template for the pull request body
TEMPLATE_PATH = ".github/workflows/pr_body_template.j2"
# Load the Jinja2 template
with open(TEMPLATE_PATH, "r", encoding="utf-8") as file_:
    template = Template(file_.read())

# Dictionary to categorize commit messages by type
types: dict[str, list[str]] = {
    "build": [],
    "chore": [],
    "ci": [],
    "docs": [],
    "feat": [],
    "fix": [],
    "other": [],
    "perf": [],
    "refactor": [],
    "revert": [],
    "style": [],
    "test": [],
}

# Regular expression pattern to match emojis
emoji_pattern = re.compile(
    "["
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\u2702-\u27B0"  # Dingbats
    "\u24C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)


def remove_emojis_and_leading_spaces(text: str) -> str:
    """
    Removes emojis and leading spaces from the given text.

    Args:
        text (str): The input text containing emojis and leading spaces.

    Returns:
        str: The text with emojis and leading spaces removed.
    """
    text = emoji_pattern.sub("", text).strip()
    if len(text) > 1 and text[1] == " ":
        text = text[2:]
    return text


def get_branch_name() -> str:
    """
    Get the name of the current branch.

    Returns:
        str: The name of the current branch.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


# Get the source and destination branches from the command-line arguments
source_branch = sys.argv[1] if len(sys.argv) > 1 else get_branch_name()
dest_branch = sys.argv[2] if len(sys.argv) > 2 else "main"


def fetch_latest_changes(branch: str) -> None:
    """
    Fetch the latest changes from the specified branch.

    Args:
        branch (str): The branch to fetch changes from.
    """
    subprocess.run(["git", "fetch", "origin", branch], check=True)


fetch_latest_changes(dest_branch)


def get_commit_messages(destination: str) -> list[str]:
    """
    Get commit messages from the source branch that are not in the destination
    branch.

    Args:
        source (str): The source branch.
        destination (str): The destination branch.

    Returns:
        list[str]: A list of commit messages.
    """
    result = subprocess.run(
        ["git", "log", f"origin/{destination}..HEAD", "--pretty=format:%s"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.split("\n")


commit_messages = get_commit_messages(dest_branch)

# Process each commit message to categorize it
for message in commit_messages:
    # Remove emojis and leading spaces from the message
    message = remove_emojis_and_leading_spaces(message)
    MATCHED = False
    for change_type, _changes in types.items():
        if re.match(
            rf"^[\U0001F300-\U0001F5FF\u2000-\u3300]*{change_type}"
            rf"\(\S+\):",
            message,
            re.UNICODE,
        ) or re.match(
            rf"^[\U0001F300-\U0001F5FF\u2000-\u3300]*{change_type}:",
            message,
            re.UNICODE,
        ):
            _changes.append(message)
            MATCHED = True
            break
    if not MATCHED:
        # Remove the first and second character if the second char is a space
        # and try matching again
        if len(message) > 1 and message[1] == " ":
            message = message[2:]
            for change_type, _changes in types.items():
                if re.match(
                    rf"^[\U0001F300-\U0001F5FF\u2000-\u3300]*{change_type}"
                    rf"\(\S+\):",
                    message,
                    re.UNICODE,
                ) or re.match(
                    rf"^[\U0001F300-\U0001F5FF\u2000-\u3300]*{change_type}:",
                    message,
                    re.UNICODE,
                ):
                    _changes.append(message)
                    MATCHED = True
                    break
    if not MATCHED:
        types["other"].append(message)


def generate_summary() -> str:
    """
    Generate the summary by running the 'pr-summary-generate' command.

    Returns:
        str: The summary generated by the command.
    """
    result = subprocess.run(
        ["pr-summary-generate"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def generate_motivation_context() -> str:
    """
    Generates the motivation context by running the 'pr-context-generate'
    command.

    Returns:
        str: The motivation context generated by the command.
    """
    result = subprocess.run(
        ["pr-context-generate"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_pr_number() -> str:
    """
    Get the pull request number.

    Returns:
        str: The pull request number.
    """
    result = subprocess.run(
        ["gh", "pr", "view", "--json", "number", "--jq", ".number"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


# Generate the summary and motivation context
try:
    SUMMARY = generate_summary()
except subprocess.CalledProcessError as e:
    SUMMARY = "Summary generation failed."
    print(f"Error generating summary: {e}", file=sys.stderr)

try:
    MOTIVATION_CONTEXT = generate_motivation_context()
except subprocess.CalledProcessError as e:
    MOTIVATION_CONTEXT = "Motivation context generation failed."
    print(f"Failed to generate PR context: {e}", file=sys.stderr)

try:
    PR_NUMBER = get_pr_number()
except subprocess.CalledProcessError as e:
    PR_NUMBER = "Unknown"
    print(f"Failed to get PR number: {e}", file=sys.stderr)

try:
    PR_NUMBER = get_pr_number()
except subprocess.CalledProcessError as e:
    PR_NUMBER = "Unknown"
    print(f"Failed to get PR number: {e}", file=sys.stderr)

# Render the pull request body using the template and the collected data
pr_body = template.render(
    summary=SUMMARY,
    branch_name=source_branch,
    dest_branch=dest_branch,
    actor=os.getenv("GITHUB_ACTOR"),
    pr_number=PR_NUMBER,
    motivation_context=MOTIVATION_CONTEXT,
    types=types,
)

# Add a newline at the end of the pull request body
pr_body += "\n"

# Print the generated pull request body
print(pr_body)
