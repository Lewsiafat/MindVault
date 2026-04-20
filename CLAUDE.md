# MindVault — Developer Notes for Claude

## Project Overview

MindVault is an AI-powered personal knowledge base web service. It reads markdown files from a user-configured directory (`DATA_DIR`) and exposes them via a FastAPI backend + Vue 3 frontend.

**Inspiration:** [Andrej Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — raw sources stay immutable, an LLM maintains a wiki layer as persistent synthesis.

---

## Key Architectural Decisions

### Settings layer (`src/config.py`)
All runtime knobs go through `pydantic_settings.BaseSettings`. Read via `from src.config import settings`. Never read `os.environ` directly except at the `DATA_DIR`-exists fail-fast check in `main.py`.

### AI provider abstraction (`src/ai/`)
`AIProvider` ABC in `base.py` exposes one method: `generate(prompt, *, temperature) -> str`. Concrete implementations:
- `gemini.py` — `google-genai` SDK (NOT the deprecated `google-generativeai`)
- `claude.py` — `anthropic` SDK
- `openai_compat.py` — `openai` SDK, shared by `openai` / `openrouter` / `ollama` via `base_url`

`get_provider()` factory in `src/ai/__init__.py` routes by `AI_PROVIDER` and falls back to per-provider model/base_url defaults. Lazy-init: `_ai()` in `main.py` defers instantiation so the server can boot without a key (non-AI endpoints still work).

Output post-processing (code-fence stripping, JSON parsing, category-item normalization) stays in `main.py` — it's an output-format concern, not a provider concern.

### Single App.vue SPA
The entire frontend is one file: `frontend/src/App.vue`. Views are toggled with `v-if`, no router. Intentional — keep it simple.

### Data is files, not a database
All content lives in `DATA_DIR` as markdown files. No database. The backend reads files on every request (no persistent state except in-memory AI cache and the file cache).

### AI caching
AI calls are expensive. Results are cached at two levels:
1. **In-memory** (`_ai_cache` dict) — 1-hour TTL, resets on restart
2. **File cache** (`CACHE_DIR/*.json`) — survives restarts; validated by md5 fingerprint of all doc names + mtimes; auto-invalidates when files change

`get_file_cached(key)` / `set_file_cached(key, payload)` manage the file cache. Currently only `categorize` uses both levels; other AI calls use in-memory only.

### Document folders
```
DATA_DIR/
├── notes.md          # folder="root", label="📋 個人筆記"
├── articles/         # folder="articles", label="📰 文章"
├── saves/            # folder="saves", label="💾 儲存"
└── conversations/    # folder="conversations", label="💬 對話記錄"
```
`SUBFOLDERS` is a dict in `main.py`. To add a new folder: add to the dict and add emoji/label in `App.vue`'s `folderEmoji` / `folderLabel` mappings.

### Data directory auto-seeding
`_initialize_data_dir()` in `main.py` runs at import. Behavior:
- If `DATA_DIR` env var is set but the path is missing → fail-fast with error.
- If `DATA_DIR` is unset and `./data` is missing → copy `data.example/` into place.
- Otherwise → no-op.

### Hidden-folder skipping
`load_all_docs()` skips folders/filenames starting with `.`. Lets users point `DATA_DIR` at an Obsidian vault or git repo without polluting the reader.

---

## Common Development Tasks

### Add a new API endpoint
Add `@app.get("/api/...")` in `src/main.py`. No router files. Call `_ai().generate(prompt)` (or the legacy `gemini(prompt)` helper which also strips code fences).

### Add a new frontend view
1. Add view name to `type View` union in `App.vue`
2. Add nav button in sidebar
3. Add `<section v-if="view === 'xxx'">` block in template
4. Handle data fetching in `setView()`

### Add a new document folder
1. Add to `SUBFOLDERS` in `main.py`: `"folder_name": "emoji label"`
2. Create the folder under `DATA_DIR`
3. Add emoji + label in `App.vue`'s `folderEmoji` / `folderLabel`

### Add a new AI provider
1. Create `src/ai/<name>.py` subclassing `AIProvider`
2. Register in `_PROVIDER_DEFAULTS` + routing in `src/ai/__init__.py`
3. Add optional extra in `pyproject.toml`
4. Document in `docs/ai-providers.md`

### Local dev
```bash
uv sync --extra all
cp .env.example .env        # then fill AI_API_KEY
uv run uvicorn src.main:app --reload --port 10016
cd frontend && npm install && npm run dev    # in a second terminal
```

---

## Deployment

See `docs/deployment.md`. Primary path for end users is `docker compose up -d`. Bare-metal (systemd + nginx) is documented too but no longer automated via GitHub Actions.

---

## Known Issues & Gotchas

### Gemini SDK
**Use `google-genai`. Do NOT use the old deprecated `google-generativeai`.**

```python
from google import genai as genai_sdk
client = genai_sdk.Client(api_key=key)
resp = client.models.generate_content(model="gemini-3.1-flash", contents=prompt)
```

### AI response parsing
Providers sometimes return markdown-wrapped JSON (```json ... ```). The `gemini()` helper in `main.py` strips code fences. Always parse with `json.loads()` inside a try/except.

### Category items normalization
The LLM may return string items instead of dicts in category arrays. Always normalize with the post-processing loop in `get_categories()`.

### `load_all_docs()` vs `get_library()`
`load_all_docs()` returns raw fields: `name, label, folder, content, path`. It does NOT include `title` or `mtime` — those are computed in `get_library()`. Don't reference `d["title"]` on raw docs.

### `is_relative_to()` security check
In `get_doc()` and `_do_ingest()`, always verify `path.is_relative_to(DATA_DIR)` to prevent path-traversal attacks.

### `vite.config.ts` `base` and `BASE_PATH`
The frontend build hardcodes `base: '/mind-vault/'`. If you change `BASE_PATH` in `.env`, you must also change `base` in `vite.config.ts` and rebuild the frontend.

---

## Tech Versions

| Tool | Version |
|------|---------|
| Python | 3.13 |
| FastAPI | ≥0.115.0 |
| uvicorn | ≥0.30.0 (with standard extras) |
| pydantic-settings | ≥2.0.0 |
| google-genai | ≥1.0.0 (optional, `--extra gemini`) |
| anthropic | ≥0.40.0 (optional, `--extra claude`) |
| openai | ≥1.0.0 (optional, `--extra openai`) |
| Node.js | 20 |
| Vue | 3.5.x |
| Vite | 6.x |
| marked | 15.x |
| uv | latest |
