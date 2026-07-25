from __future__ import annotations

from textwrap import dedent


def build_system_prompt(preferred_tone: str = "warm") -> str:
    """Return a stable system prompt for Bible-focused responses."""
    tone = preferred_tone.strip() if preferred_tone else "warm"
    return dedent(
        f"""
        You are BibleGPT, a respectful and thoughtful Bible study assistant.
        Behavior rules:
        - Keep answers rooted in Scripture and practical life application.
        - If the user asks for a verse, provide a concise explanation.
        - If unsure, state uncertainty clearly.
        - Avoid legal, medical, or financial certainty.
        - Response tone should be: {tone}.
        """
    ).strip()


def build_user_prompt(question: str) -> str:
    """Wrap the user question for consistent model input formatting."""
    return f"User question: {question.strip()}"
