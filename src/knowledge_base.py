# =============================================================================
# File:    src/knowledge_base.py
# Purpose: Loads and caches the business knowledge base from disk.
#          Called once at startup. The formatted result is injected into
#          every Claude system prompt so answers stay grounded in real data.
# Author:  Abraham Macias
# Date:    2026-06-25
# =============================================================================

import os
import logging

logger = logging.getLogger(__name__)

# Path relative to the project root
_KB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge_base.txt")

# Module-level cache — file is read once, reused on every request
_cached_knowledge_base: str | None = None


def load_knowledge_base() -> str:
    """
    Reads knowledge_base.txt from disk and returns its contents as a string.

    Uses a module-level cache so the file is only read once per process.
    Raises RuntimeError if the file is missing or unreadable — a chatbot
    with no knowledge base should not start silently.
    """
    global _cached_knowledge_base

    if _cached_knowledge_base is not None:
        return _cached_knowledge_base

    kb_path = os.path.abspath(_KB_PATH)

    if not os.path.exists(kb_path):
        raise RuntimeError(
            f"knowledge_base.txt not found at: {kb_path}\n"
            "Create the file and populate it with your business FAQ before starting."
        )

    try:
        with open(kb_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except IOError as e:
        raise RuntimeError(f"Failed to read knowledge_base.txt: {e}") from e

    if not content:
        raise RuntimeError(
            "knowledge_base.txt is empty. "
            "Add your business information before starting."
        )

    _cached_knowledge_base = content
    logger.info("Knowledge base loaded: %d characters", len(content))
    return _cached_knowledge_base


def format_for_system_prompt(knowledge_base: str, business_name: str) -> str:
    """
    Wraps the raw knowledge base text in clear XML-style delimiters.

    Delimiters help Claude distinguish the knowledge base from conversation
    history and reduce the risk of the content being misread as instructions.
    """
    return (
        f"You are a helpful customer support assistant for {business_name}.\n\n"
        "IMPORTANT RULES YOU MUST FOLLOW:\n"
        "1. Only answer questions using the information in the KNOWLEDGE BASE below.\n"
        "2. If the answer is not in the knowledge base, say exactly: "
        "'I don't have that information. Please contact our team directly at "
        "hello@teocallidevs.tech.'\n"
        "3. Never make up information, prices, policies, or contact details.\n"
        "4. Be friendly, concise, and professional.\n"
        "5. If asked who you are, say you are a virtual assistant for "
        f"{business_name} — nothing more.\n\n"
        "<KNOWLEDGE_BASE>\n"
        f"{knowledge_base}\n"
        "</KNOWLEDGE_BASE>"
    )
