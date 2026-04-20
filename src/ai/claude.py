try:
    import anthropic
except ImportError as e:
    raise ImportError(
        "anthropic is required for AI_PROVIDER=claude. "
        "Install with: uv sync --extra claude  (or --extra all)"
    ) from e

from src.ai.base import AIProvider


class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        return "".join(parts).strip()
