# =============================================================================
# File:    src/security.py
# Purpose: Input validation layer. Every user message passes through here
#          before reaching the Claude API. Catches abuse, injection attempts,
#          and malformed input early so the rest of the app stays clean.
# Author:  Abraham Macias
# Date:    2026-06-25
# =============================================================================

import re

# ---------------------------------------------------------------------------
# Constants — change these values to adjust limits app-wide
# ---------------------------------------------------------------------------
MAX_INPUT_LENGTH = 500   # Hard cap on message length to prevent token abuse
MIN_INPUT_LENGTH = 2     # Filters out empty pings and single-character noise

# Patterns that signal a prompt injection attempt.
# These phrases try to override the system prompt or impersonate the system.
INJECTION_PATTERNS = [
    r"ignore.{0,30}instructions",
    r"you are now",
    r"disregard (your |all )?",
    r"act as (a |an )?(?!customer)",
    r"system prompt",
    r"forget (everything|your instructions)",
    r"new instructions",
    r"pretend (you are|to be)",
    r"reveal your (prompt|instructions|system)",
]

# Pre-compile patterns once at import time — faster than compiling per call
_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def validate_message(message: str) -> tuple[bool, str]:
    """
    Validates a user message before it reaches the Claude API.

    Checks: presence, type, min/max length, and injection pattern matching.
    Returns a tuple of (is_valid: bool, error_message: str).
    On success, error_message is an empty string.
    """
    if not message or not isinstance(message, str):
        return False, "Please enter a message."

    cleaned = message.strip()

    if len(cleaned) < MIN_INPUT_LENGTH:
        return False, "Message is too short. Please ask a complete question."

    if len(cleaned) > MAX_INPUT_LENGTH:
        return False, (
            f"Message exceeds {MAX_INPUT_LENGTH} characters. "
            "Please shorten your question."
        )

    for pattern in _COMPILED_PATTERNS:
        if pattern.search(cleaned):
            return False, (
                "I can only help with questions about our services. "
                "How can I assist you today?"
            )

    return True, ""


def sanitize_message(message: str) -> str:
    """
    Strips leading/trailing whitespace and collapses internal whitespace runs.
    Called after validate_message confirms the input is safe.
    Does not remove content — only normalizes formatting.
    """
    return re.sub(r"\s+", " ", message.strip())
