# =============================================================================
# File:    src/app.py
# Purpose: Application entry point. Builds the Gradio chat interface and
#          wires it to the ChatbotEngine. Run this file to start the app.
# Author:  Abraham Macias
# Date:    2026-06-25
# Dependencies: gradio, src.chatbot
# Usage:   py -3.12 -m src.app
# =============================================================================

import os
import logging
import gradio as gr
from dotenv import load_dotenv

from src.chatbot import create_engine, ChatbotEngine

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def build_respond_fn(engine: ChatbotEngine):
    """
    Returns a closure that Gradio calls on each user message submission.
    Binds the engine instance to the response function without globals.
    """
    def respond(user_message: str, history: list) -> str:
        return engine.chat(user_message)

    return respond


def build_clear_fn(engine: ChatbotEngine):
    """
    Returns a function that resets the engine's conversation history.
    Called when the user starts a new session.
    """
    def clear():
        engine.clear_history()

    return clear


def create_ui() -> gr.Blocks:
    """
    Constructs the Gradio chat interface.

    Uses gr.ChatInterface with default components to avoid DuplicateBlockError
    in Gradio 4.x when pre-instantiated child components are passed in.
    """
    business_name = os.environ.get("BUSINESS_NAME", "Teocalli Devs")

    engine = create_engine()
    respond = build_respond_fn(engine)

    with gr.Blocks(
        title=f"{business_name} — AI Support",
        theme=gr.themes.Soft(),
        css=".gradio-container { max-width: 800px; margin: auto; }",
    ) as demo:

        gr.Markdown(f"## 💬 {business_name} — 24/7 Support")
        gr.Markdown(
            "Ask me anything about our services, process, or how to get started. "
            "I'm here to help around the clock."
        )

        gr.ChatInterface(
            fn=respond,
            examples=[
                "What services does Teocalli Devs offer?",
                "How do I get started on a project?",
                "How long does a typical project take?",
                "Do you work with clients outside the US?",
            ],
            cache_examples=False,
            retry_btn=None,
            undo_btn=None,
        )

        gr.Markdown(
            "<small>Powered by Claude AI · Responses are based on our knowledge base · "
            "Questions? Email us at hello@teocallidevs.tech</small>"
        )

    return demo


def main():
    """
    Launches the Gradio app. Port is read from environment so it can be
    overridden in production without a code change.
    """
    port = int(os.environ.get("PORT", 7860))

    logger.info("Starting AI Support Chatbot on port %d", port)

    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        show_error=False,  # Never expose stack traces to end users
    )


if __name__ == "__main__":
    main()
