# Configuration

All runtime knobs live in `.env` (or the shell environment). Copy `.env.example` as a starting point:

```bash
cp .env.example .env
```

## Full variable reference

| Variable | Default | Required | Description |
|---|---|---|---|
| `AI_PROVIDER` | `gemini` | ✅ | One of `gemini` / `claude` / `openai` / `openrouter` / `ollama` |
| `AI_API_KEY` | — | ✅ (except `ollama`) | Provider API key |
| `AI_MODEL` | per-provider | — | Override the model; see table below |
| `AI_BASE_URL` | per-provider | — | Override the endpoint; usually only for `ollama` or a proxy |
| `DATA_DIR` | `./data` | — | Absolute or relative path to your markdown folder |
| `CACHE_DIR` | `DATA_DIR/cache` | — | Where AI response cache JSON files live |
| `BASE_PATH` | `mind-vault` | — | URL prefix. `""` to mount at root. Must match `base` in `frontend/vite.config.ts` |
| `PORT` | `10016` | — | Host port (container always listens on 10016) |

## Per-provider defaults

If you don't set `AI_MODEL` / `AI_BASE_URL`, MindVault picks:

| Provider | Default model | Default base URL |
|---|---|---|
| `gemini` | `gemini-3.1-flash` | — (SDK default) |
| `claude` | `claude-haiku-4-5` | — (SDK default) |
| `openai` | `gpt-4o-mini` | `https://api.openai.com/v1` |
| `openrouter` | `google/gemini-2.5-flash` | `https://openrouter.ai/api/v1` |
| `ollama` | `llama3.1` | `http://localhost:11434/v1` |

## Startup validation

- If `DATA_DIR` is set but points to a missing path → the server aborts with a clear error.
- If `DATA_DIR` is unset and `./data` is missing → auto-seeds from `data.example/`.
- If `AI_API_KEY` is missing for a non-`ollama` provider → the server still starts, but any AI endpoint call (e.g. `/api/summary`) returns the error until the key is set.

## Changing `BASE_PATH`

The frontend build bakes the URL prefix into asset paths. If you change `BASE_PATH`, also edit `frontend/vite.config.ts`:

```ts
base: '/your-prefix/',
```

Then rebuild: `cd frontend && npm run build` (or rebuild the Docker image).

Set `BASE_PATH=""` to mount at the root, but be aware the frontend expects a matching base URL.
