"""
Security Category - Security Fuzzing Tests

This module contains functions designed to test security-related intents:
- SQL_INJECTION: SQL injection attack payloads
- XSS_INJECTION: Cross-site scripting payloads
- PATH_TRAVERSAL: Path traversal attempts
- COMMAND_INJECTION: Command injection attempts

Recommended Intents:
- HAPPY_PATH
- SQL_INJECTION
- XSS_INJECTION
- PATH_TRAVERSAL
- COMMAND_INJECTION
"""

from typing import Dict, List, Optional
import re


def search_users(query: str) -> List[Dict[str, str]]:
    """
    Searches for users by name or email.

    Tests SQL_INJECTION with malicious query strings.

    Args:
        query: Search query, should be sanitized.

    Returns:
        List of matching users.
    """
    # This simulates a function that might be vulnerable to SQL injection
    # In real code, this would use parameterized queries
    dangerous_patterns = ["'", '"', ";", "--", "/*", "*/", "OR", "AND"]
    for pattern in dangerous_patterns:
        if pattern.upper() in query.upper():
            raise ValueError(f"Invalid character in query: {pattern}")
    return [{"id": "1", "name": "John", "query": query}]


def execute_query(table: str, conditions: str) -> List[Dict[str, str]]:
    """
    Executes a database query.

    Tests SQL_INJECTION attacks in conditions parameter.

    Args:
        table: Table name to query.
        conditions: WHERE clause conditions, must be sanitized.

    Returns:
        Query results.
    """
    # Validate table name
    if not table.isalnum():
        raise ValueError("Invalid table name")
    # Basic SQL injection detection
    if re.search(r"('|--|;|/\*|\*/|DROP|DELETE|UPDATE|INSERT)", conditions, re.I):
        raise ValueError("Potential SQL injection detected")
    return [{"table": table, "result": "success"}]


def render_username(username: str) -> str:
    """
    Renders a username for display in HTML.

    Tests XSS_INJECTION with script tags and event handlers.

    Args:
        username: Username to render, should be escaped.

    Returns:
        Safe HTML string.
    """
    # Basic XSS detection
    dangerous_patterns = ["<script", "javascript:", "onerror=", "onclick=", "<img"]
    for pattern in dangerous_patterns:
        if pattern.lower() in username.lower():
            raise ValueError("Potential XSS attack detected")
    return f"<span class='username'>{username}</span>"


def render_comment(comment: str) -> str:
    """
    Renders a user comment for display.

    Tests XSS_INJECTION in user-generated content.

    Args:
        comment: Comment text, should be escaped.

    Returns:
        Safe HTML string.
    """
    # Escape HTML entities
    escaped = (
        comment.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
    return f"<p class='comment'>{escaped}</p>"


def read_file(filepath: str) -> str:
    """
    Reads contents of a file.

    Tests PATH_TRAVERSAL with ../ sequences.

    Args:
        filepath: Path to file, must be within allowed directory.

    Returns:
        File contents.
    """
    # Detect path traversal attempts
    if ".." in filepath or filepath.startswith("/") or ":" in filepath:
        raise ValueError("Path traversal attempt detected")
    if any(c in filepath for c in ["~", "$", "|", "&", ";"]):
        raise ValueError("Invalid characters in path")
    return f"Contents of {filepath}"


def download_file(filename: str) -> Dict[str, str]:
    """
    Downloads a file by name.

    Tests PATH_TRAVERSAL attacks in filename.

    Args:
        filename: Name of file to download, no directory traversal.

    Returns:
        File download info.
    """
    # Normalize and validate filename
    if "/" in filename or "\\" in filename:
        raise ValueError("Directory separators not allowed in filename")
    if filename.startswith("."):
        raise ValueError("Hidden files not allowed")
    return {"filename": filename, "status": "ready"}


def execute_command(action: str, target: str) -> str:
    """
    Executes a predefined action on a target.

    Tests COMMAND_INJECTION with shell metacharacters.

    Args:
        action: Action to perform (must be whitelisted).
        target: Target of the action, should be sanitized.

    Returns:
        Command result.
    """
    # Whitelist allowed actions
    allowed_actions = ["list", "show", "describe", "count"]
    if action not in allowed_actions:
        raise ValueError(f"Action must be one of: {allowed_actions}")

    # Detect command injection
    dangerous_chars = [";", "|", "&", "$", "`", "(", ")", "{", "}", "<", ">"]
    for char in dangerous_chars:
        if char in target:
            raise ValueError(f"Invalid character in target: {char}")

    return f"Executed {action} on {target}"


def run_script(script_name: str, args: str) -> str:
    """
    Runs a named script with arguments.

    Tests COMMAND_INJECTION in script arguments.

    Args:
        script_name: Name of script to run (whitelisted).
        args: Arguments to pass, should be sanitized.

    Returns:
        Script output.
    """
    # Whitelist scripts
    allowed_scripts = ["backup", "cleanup", "report", "status"]
    if script_name not in allowed_scripts:
        raise ValueError(f"Script must be one of: {allowed_scripts}")

    # Detect injection attempts
    if re.search(r"[;&|`$<>()]", args):
        raise ValueError("Invalid characters in arguments")

    return f"Script {script_name} executed with args: {args}"
