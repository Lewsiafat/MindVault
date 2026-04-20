try:
    from openai import OpenAI
except ImportError as e:
    raise ImportError(
        "openai is required for AI_PROVIDER=openai / openrouter / ollama. "
        "Install with: uv sync --extra openai  (or --extra all)"
    ) from e

from src.ai.base import AIProvider


class OpenAICompatProvider(AIProvider):
    """Shared implementation for openai, openrouter, and ollama (OpenAI-compatible API)."""

    def __init__(self, api_key: str | None, model: str, base_url: str | None):
        self._client = OpenAI(
            api_key=api_key or "ollama",  # ollama ignores key but SDK requires non-empty
            base_url=base_url,
        )
        self._model = model

    def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return (resp.choices[0].message.content or "").strip()
