"""
Centralized LLM Configuration.

Switch providers by setting environment variables in .env:
  LLM_PROVIDER = openai | anthropic | google | ollama
  LLM_MODEL    = model name (defaults per provider if empty)

Embeddings always use OpenAI to avoid re-ingestion.
"""
import os
from langchain_core.language_models import BaseChatModel


def get_llm(temperature: float = 0, provider: str = None, model: str = None) -> BaseChatModel:
    """Returns a Chat LLM based on provider/model params or LLM_PROVIDER env var."""
    provider = (provider or os.getenv("LLM_PROVIDER", "openai")).lower()
    model = model or os.getenv("LLM_MODEL", "")

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model or "gpt-5-nano", #gpt-5-nano gpt-4o-mini
            temperature=temperature,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model or "claude-haiku-4-5-20251001", #claude-haiku-4-5-20251001 claude-sonnet-4-20250514 claude-3-haiku-20240307
            temperature=temperature,
        )

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model or "gemini-3-flash-preview", # gemini-3-flash-preview gemini-2.5-flash-lite
            temperature=temperature,
        )

    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model or "llama3",
            temperature=temperature,
            format="json",  # Force JSON output — critical for agent pipeline
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider}'. "
            f"Supported: openai, anthropic, google, ollama"
        )


def get_embeddings():
    """Returns OpenAI embeddings (fixed provider to avoid re-ingestion)."""
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings()
