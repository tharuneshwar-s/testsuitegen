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
import html


# =============================================================================
# SECURITY HELPER FUNCTIONS (Used by bug fixes)
# =============================================================================


def _validate_not_empty(value: str, field_name: str) -> None:
    """Validates that a string is not empty or whitespace-only."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty or whitespace-only")


def _detect_sql_injection(value: str, field_name: str) -> None:
    """Detects common SQL injection patterns."""
    # Detect actual injection patterns, not just single quotes (which are valid in SQL)
    injection_patterns = [
        r"'\s*(OR|AND)\s*'\d*'\s*=\s*'\d*",  # ' OR '1'='1
        r"'\s*(OR|AND)\s+\d+\s*=\s*\d+",     # ' OR 1=1
        r";\s*(DROP|DELETE|UPDATE|INSERT|SELECT)",  # ; DROP TABLE
        r"--",                                  # SQL comment
        r"/\*",                                 # Block comment start
        r"\*/",                                 # Block comment end
        r"UNION\s+SELECT",                     # UNION SELECT
        r"'\s*;\s*--",                         # Terminate and comment
    ]
    for pattern in injection_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError(
                f"Potential SQL injection detected in {field_name}"
            )


def _detect_xss(value: str, field_name: str) -> None:
    """Detects common XSS patterns."""
    dangerous_patterns = [
        "<script",
        "</script",
        "javascript:",
        "onerror=",
        "onclick=",
        "onload=",
        "onmouseover=",
        "<img",
        "<iframe",
        "<object",
        "<embed",
        "<svg",
        "&#",
    ]
    for pattern in dangerous_patterns:
        if pattern.lower() in value.lower():
            raise ValueError(
                f"Potential XSS attack detected in {field_name}: {pattern}"
            )


def _sanitize_html(value: str) -> str:
    """Escapes HTML entities to prevent XSS."""
    return html.escape(value, quote=True)


# =============================================================================
# FUNCTION 1: search_users - SQL INJECTION VULNERABILITY
# =============================================================================


def search_users(query: str) -> List[Dict[str, str]]:
    """
    Searches for users by name or email.

    Tests SQL_INJECTION with malicious query strings.

    Args:
        query: Search query, should be sanitized.

    Returns:
        List of matching users.
    """
    # === BUG FIX: Uncomment the following lines to enable security ===
    _validate_not_empty(query, "query")
    _detect_sql_injection(query, "query")
    _detect_xss(query, "query")
    # === END BUG FIX ===

    # VULNERABLE: No input validation - accepts any query including SQL injection
    return [{"id": "1", "name": "John", "query": query}]


# =============================================================================
# FUNCTION 2: execute_query - SQL INJECTION VULNERABILITY
# =============================================================================


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
    # === BUG FIX: Uncomment the following lines to enable security ===
    _validate_not_empty(table, "table")
    _validate_not_empty(conditions, "conditions")
    if not table.isalnum():
        raise ValueError("Invalid table name - must be alphanumeric")
    _detect_sql_injection(conditions, "conditions")
    _detect_xss(conditions, "conditions")
    # === END BUG FIX ===

    # VULNERABLE: Minimal validation - still allows some SQL injection patterns
    if not table:
        raise TypeError("table is required")
    return [{"table": table, "result": "success"}]


# =============================================================================
# FUNCTION 3: render_username - XSS VULNERABILITY
# =============================================================================


def render_username(username: str) -> str:
    """
    Renders a username for display in HTML.

    Tests XSS_INJECTION with script tags and event handlers.

    Args:
        username: Username to render, should be escaped.

    Returns:
        Safe HTML string.
    """
    # === BUG FIX: Uncomment the following lines to enable security ===
    _validate_not_empty(username, "username")
    _detect_xss(username, "username")
    _detect_sql_injection(username, "username")
    username = _sanitize_html(username)
    # === END BUG FIX ===

    # VULNERABLE: No XSS protection - renders unsanitized HTML
    return f"<span class='username'>{username}</span>"


# =============================================================================
# FUNCTION 4: render_comment - XSS VULNERABILITY
# =============================================================================


def render_comment(comment: str) -> str:
    """
    Renders a user comment for display.

    Tests XSS_INJECTION in user-generated content.

    Args:
        comment: Comment text, should be escaped.

    Returns:
        Safe HTML string.
    """
    # === BUG FIX: Uncomment the following lines to enable security ===
    _validate_not_empty(comment, "comment")
    _detect_xss(comment, "comment")
    _detect_sql_injection(comment, "comment")
    comment = _sanitize_html(comment)
    # === END BUG FIX ===

    # VULNERABLE: No validation - only escapes after the fact (doesn't reject)
    return f"<p class='comment'>{comment}</p>"


# =============================================================================
# FUNCTION 5: read_file - PATH TRAVERSAL VULNERABILITY
# =============================================================================


def read_file(filepath: str) -> str:
    """
    Reads contents of a file.

    Tests PATH_TRAVERSAL with ../ sequences.

    Args:
        filepath: Path to file, must be within allowed directory.

    Returns:
        File contents.
    """
    # === BUG FIX: Uncomment the following lines to enable security ===
    _validate_not_empty(filepath, "filepath")
    # Detect path traversal attempts
    if ".." in filepath:
        raise ValueError("Path traversal attempt detected: directory traversal")
    if filepath.startswith("/"):
        raise ValueError("Path traversal attempt detected: absolute unix path")
    # Allow Windows paths like C:\Users\... but block other colon usage
    # (colon after single letter at start is Windows drive letter)
    if ":" in filepath:
        # Check if it's NOT a valid Windows drive letter pattern
        if not re.match(r'^[A-Za-z]:\\', filepath):
            raise ValueError("Path traversal attempt detected: invalid colon usage")
    if any(c in filepath for c in ["~", "$", "|", "&", ";"]):
        raise ValueError("Invalid characters in path")
    # === END BUG FIX ===

    # VULNERABLE: No path validation - allows path traversal attacks
    if not filepath:
        raise TypeError("filepath is required")
    return f"Contents of {filepath}"


# =============================================================================
# FUNCTION 6: download_file - PATH TRAVERSAL VULNERABILITY
# =============================================================================


def download_file(filename: str) -> Dict[str, str]:
    """
    Downloads a file by name.

    Tests PATH_TRAVERSAL attacks in filename.

    Args:
        filename: Name of file to download, no directory traversal.

    Returns:
        File download info.
    """
    # === BUG FIX: Uncomment the following lines to enable security ===
    _validate_not_empty(filename, "filename")
    # Normalize and validate filename
    if "/" in filename or "\\" in filename:
        raise ValueError("Directory separators not allowed in filename")
    if filename.startswith("."):
        raise ValueError("Hidden files not allowed")
    if ".." in filename:
        raise ValueError("Path traversal not allowed")
    # === END BUG FIX ===

    # SECURE: This function already has good validation (keeping as-is)
    if "/" in filename or "\\" in filename:
        raise ValueError("Directory separators not allowed in filename")
    if filename.startswith("."):
        raise ValueError("Hidden files not allowed")
    return {"filename": filename, "status": "ready"}


# =============================================================================
# FUNCTION 7: execute_command - COMMAND INJECTION VULNERABILITY
# =============================================================================


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
    # Whitelist allowed actions (keep this - it's structural validation)
    allowed_actions = ["list", "show", "describe", "count"]
    if action not in allowed_actions:
        raise ValueError(f"Action must be one of: {allowed_actions}")

    # === BUG FIX: Uncomment the following lines to enable security ===
    _validate_not_empty(target, "target")
    _detect_sql_injection(target, "target")
    # Detect command injection
    dangerous_chars = [";", "|", "&", "$", "`", "(", ")", "{", "}", "<", ">", "'", '"']
    for char in dangerous_chars:
        if char in target:
            raise ValueError(f"Invalid character in target: {char}")
    # === END BUG FIX ===

    # VULNERABLE: Missing command injection detection for target parameter
    return f"Executed {action} on {target}"


# =============================================================================
# FUNCTION 8: run_script - COMMAND INJECTION VULNERABILITY
# =============================================================================


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
    # Whitelist scripts (keep this - it's structural validation)
    allowed_scripts = ["backup", "cleanup", "report", "status", "update_user_profile", "deploy", "test"]
    if script_name not in allowed_scripts:
        raise ValueError(f"Script must be one of: {allowed_scripts}")

    # === BUG FIX: Uncomment the following lines to enable security ===
    _validate_not_empty(args, "args")
    # Detect injection attempts
    if re.search(r"[;&|`$<>()'\"]", args):
        raise ValueError("Invalid characters in arguments")
    _detect_sql_injection(args, "args")
    # === END BUG FIX ===

    # VULNERABLE: Missing argument validation - allows command injection
    return f"Script {script_name} executed with args: {args}"
