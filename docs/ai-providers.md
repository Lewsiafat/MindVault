# AI Providers

MindVault talks to LLMs through a thin abstraction (`src/ai/`). Pick the provider that matches your budget, privacy preference, and model taste.

## Gemini (Google AI Studio)

- **Get a key:** https://aistudio.google.com/apikey
- Free tier is generous for personal use.

```env
AI_PROVIDER=gemini
AI_API_KEY=AIza...
AI_MODEL=gemini-3.1-flash   # or gemini-3.1-flash-latest, gemini-2.5-flash
```

SDK: `google-genai` (NOT the deprecated `google-generativeai`).

## Claude (Anthropic)

- **Get a key:** https://console.anthropic.com/

```env
AI_PROVIDER=claude
AI_API_KEY=sk-ant-...
AI_MODEL=claude-haiku-4-5   # or claude-sonnet-4-6, claude-opus-4-7
```

Haiku-tier is cost-effective for the ingest / synthesize workload.

## OpenAI

- **Get a key:** https://platform.openai.com/api-keys

```env
AI_PROVIDER=openai
AI_API_KEY=sk-...
AI_MODEL=gpt-4o-mini
```

## OpenRouter

OpenRouter is an OpenAI-compatible gateway to 100+ models across providers — useful if you want to A/B different models without juggling multiple SDK keys.

- **Get a key:** https://openrouter.ai/keys

```env
AI_PROVIDER=openrouter
AI_API_KEY=sk-or-...
AI_MODEL=google/gemini-2.5-flash   # see https://openrouter.ai/models
```

## Ollama (local, no API key)

Run Ollama locally, then point MindVault at it. Great for private or offline use — slower than cloud providers on typical hardware.

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull llama3.1`
3. Configure `.env`:

```env
AI_PROVIDER=ollama
AI_MODEL=llama3.1
AI_BASE_URL=http://localhost:11434/v1
# AI_API_KEY intentionally left blank
```

If MindVault runs in Docker and Ollama runs on the host, use `http://host.docker.internal:11434/v1` on macOS/Windows, or set `network_mode: host` in `docker-compose.yml` on Linux.

## Quality notes

- **Summary / categorize / ingest** are short prompts that work on any modern model.
- **Synthesize** (cross-document concept pages) is the most demanding call; weaker models may produce shorter pages.
- **Lint** outputs strict JSON — if a model struggles with JSON compliance, switch to a stronger one.

## Changing provider

Edit `.env`, then:

- Docker: `docker compose restart` (no rebuild needed — `--extra all` is pre-installed)
- Bare-metal: restart uvicorn

Existing cache is keyed by content fingerprint, not provider, so you may want to delete `CACHE_DIR/*.json` after switching if you want fresh LLM output.
