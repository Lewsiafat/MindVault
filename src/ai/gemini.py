# Use `google-genai` (new SDK). Do NOT use `google-generativeai` — it's deprecated.
try:
    from google import genai as genai_sdk
except ImportError as e:
    raise ImportError(
        "google-genai is required for AI_PROVIDER=gemini. "
        "Install with: uv sync --extra gemini  (or --extra all)"
    ) from e

from google.genai import types as genai_types

from src.ai.base import AIProvider


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        self._client = genai_sdk.Client(api_key=api_key)
        self._model = model

    def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        resp = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(temperature=temperature),
        )
        return (resp.text or "").strip()
