from src.ai.base import AIProvider
from src.config import settings

_PROVIDER_DEFAULTS = {
    "gemini":     {"model": "gemini-3.1-flash",         "base_url": None},
    "claude":     {"model": "claude-haiku-4-5",         "base_url": None},
    "openai":     {"model": "gpt-4o-mini",              "base_url": "https://api.openai.com/v1"},
    "openrouter": {"model": "google/gemini-2.5-flash",  "base_url": "https://openrouter.ai/api/v1"},
    "ollama":     {"model": "llama3.1",                 "base_url": "http://localhost:11434/v1"},
}


def get_provider() -> AIProvider:
    name = settings.ai_provider.lower()
    if name not in _PROVIDER_DEFAULTS:
        raise ValueError(
            f"Unknown AI_PROVIDER: {name!r}. Supported: {', '.join(_PROVIDER_DEFAULTS)}"
        )

    defaults = _PROVIDER_DEFAULTS[name]
    model = settings.ai_model or defaults["model"]
    base_url = settings.ai_base_url or defaults["base_url"]
    api_key = settings.ai_api_key

    if name != "ollama" and not api_key:
        raise ValueError(
            f"AI_API_KEY is required for provider {name!r}. Set it in .env."
        )

    if name == "gemini":
        from src.ai.gemini import GeminiProvider
        return GeminiProvider(api_key=api_key, model=model)
    if name == "claude":
        from src.ai.claude import ClaudeProvider
        return ClaudeProvider(api_key=api_key, model=model)
    # openai / openrouter / ollama share one implementation
    from src.ai.openai_compat import OpenAICompatProvider
    return OpenAICompatProvider(api_key=api_key, model=model, base_url=base_url)


__all__ = ["AIProvider", "get_provider"]
