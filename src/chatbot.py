# =============================================================================
# File:    src/chatbot.py
# Purpose: Core AI engine. Manages conversation history, builds the system
#          prompt from the knowledge base, and calls the Claude API.
#          No UI logic lives here — this module is purely business logic.
# Author:  [Your Name]
# Date:    [Date]
# Dependencies: anthropic, python-dotenv, src.knowledge_base, src.security
# =============================================================================

import os
import logging
from anthropic import Anthropic
from dotenv import load_dotenv

from src.knowledge_base import load_knowledge_base, format_for_system_prompt
from src.security import validate_message, sanitize_message

# Load .env file values into os.environ (no-op in production where env vars
# are already set by the platform)
load_dotenv()

logger = logging.getLogger(__name__)

# Claude model to use — centralized so a model upgrade is a one-line change
CLAUDE_MODEL = "claude-sonnet-4-6"

# Max tokens in Claude's response — keeps answers concise and costs predictable
MAX_RESPONSE_TOKENS = 1024


class ChatbotEngine:
    """
    Manages a single customer support chat session.

    Each instance holds its own conversation history, allowing multiple
    simultaneous users without state bleeding between sessions.
    Gradio creates one instance per user session via the factory function below.
    """

    def __init__(self, business_name: str):
        """
        Initializes the engine: loads the knowledge base, builds the system
        prompt, and creates the Anthropic client.

        Raises RuntimeError if ANTHROPIC_API_KEY is missing or the knowledge
        base fails to load — both are unrecoverable at startup.
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Add it to your .env file (local) or platform secrets (production)."
            )

        self.client = Anthropic(api_key=api_key)
        self.business_name = business_name

        # Build the system prompt once — reused on every API call
        knowledge_base = load_knowledge_base()
        self.system_prompt = format_for_system_prompt(knowledge_base, business_name)

        # Conversation history in Claude's required format:
        # [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
        # The full list is sent on every API call so Claude has complete context.
        self.history: list[dict] = []

        logger.info("ChatbotEngine initialized for business: %s", business_name)

    def chat(self, user_message: str) -> str:
        """
        Processes a single user message and returns Claude's response.

        Flow: validate → sanitize → append to history → call Claude API
              → append response to history → return response text.

        Returns a user-facing error string (never raises) so the UI always
        has something safe to display.
        """
        # --- Validation gate ---
        is_valid, error_message = validate_message(user_message)
        if not is_valid:
            return error_message

        clean_message = sanitize_message(user_message)

        # Append user turn to history before the API call
        self.history.append({"role": "user", "content": clean_message})

        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_RESPONSE_TOKENS,
                system=self.system_prompt,  # System prompt is separate from history
                messages=self.history,       # Full history gives Claude context
            )

            # Extract the text content from the first content block
            assistant_reply = response.content[0].text

            # Append assistant turn so the next call includes this exchange
            self.history.append({"role": "assistant", "content": assistant_reply})

            return assistant_reply

        except Exception as e:
            # Remove the user message we just appended — the turn failed
            # and we don't want a dangling user message with no reply in history
            self.history.pop()
            logger.error("Claude API call failed: %s", str(e))
            return (
                "I'm having trouble connecting right now. "
                "Please try again in a moment or contact our support team directly."
            )

    def clear_history(self) -> None:
        """
        Resets conversation history to empty.
        Called when the user clicks 'Clear' in the UI to start a fresh session.
        """
        self.history = []
        logger.info("Conversation history cleared.")


def create_engine() -> ChatbotEngine:
    """
    Factory function that creates a ChatbotEngine with config from environment.

    Gradio calls this once per user session. Keeps engine creation logic
    centralized and testable independently of the UI.
    """
    business_name = os.environ.get("BUSINESS_NAME", "Customer Support")
    return ChatbotEngine(business_name=business_name)
