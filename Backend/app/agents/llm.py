"""
Shared LLM instance for all agents

This module provides a singleton LLM instance that is shared across all agents
to improve performance and resource management.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import get_settings

settings = get_settings()

# Shared LLM instance
_llm_instance = None


def get_llm() -> ChatGoogleGenerativeAI:
    """
    Get or create shared LLM instance

    Returns:
        ChatGoogleGenerativeAI: Shared LLM instance configured with Gemini Pro
    """
    global _llm_instance

    if _llm_instance is None:
        _llm_instance = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3
        )

    return _llm_instance


def reset_llm():
    """
    Reset LLM instance (useful for testing)
    """
    global _llm_instance
    _llm_instance = None
