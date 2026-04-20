# Architecture

MindVault is an implementation of [Andrej Karpathy's LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): a persistent, LLM-maintained synthesis layer sitting between your raw markdown files and you.

## Three-layer model

```
┌───────────────────────────────────┐
│ Layer 3 — Schema / Instructions   │   prompts in src/main.py
│ ─────────────────────────────     │   (future: docs/schema/*.md)
│ - How to summarize                │
│ - How to synthesize concepts      │
│ - What a "concept page" looks like│
└───────────────────────────────────┘
                 ▼
┌───────────────────────────────────┐
│ Layer 2 — Wiki (derived)          │   DATA_DIR/wiki/
│ ─────────────────────────         │
│ - summaries/<slug>.md             │   one per ingested source
│ - pages/<slug>.md                 │   cross-document concept pages
│ - index.md                        │   rebuilt on every ingest
│ - log.md                          │   append-only history
└───────────────────────────────────┘
                 ▼
┌───────────────────────────────────┐
│ Layer 1 — Raw sources (immutable) │   DATA_DIR/notes.md + subfolders
│ ─────────────────────────         │
│ - articles/*.md                   │
│ - saves/*.md                      │
│ - conversations/*.md              │
└───────────────────────────────────┘
```

The human curates Layer 1. The LLM maintains Layer 2 under rules set in Layer 3. MindVault is the UI + orchestration that wires them together.

## Component map

```
┌──────────────────────────────────────────────────────────┐
│  Reverse proxy + auth (your responsibility — not shipped)│
└──────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│  uvicorn :PORT                                            │
│  ├─ src/main.py          FastAPI routes + prompts        │
│  ├─ src/config.py        Settings (pydantic-settings)     │
│  ├─ src/ai/*             AIProvider abstraction + router  │
│  └─ src/static/          Built Vue SPA (served inline)    │
└──────────────────────────────────────────────────────────┘
                         ▼ read / write
┌──────────────────────────────────────────────────────────┐
│  DATA_DIR (your filesystem)                              │
│  ├─ notes.md, articles/, saves/, conversations/          │
│  ├─ wiki/{summaries,pages,index.md,log.md}               │
│  └─ cache/*.json                                         │
└──────────────────────────────────────────────────────────┘
```

## Why files, not a database

- **Zero lock-in** — you can leave at any time and your data is still usable.
- **Diffable** — `git diff` works. You can version-control everything MindVault produces, not just your inputs.
- **Tool-agnostic** — Obsidian, VSCode, ripgrep, other LLMs can operate on the same folder.
- **Simpler reasoning** — the server is stateless; restart freely.

## Why the AI provider abstraction

Gemini was the original backend. Abstracting provider lets users:

- Try cheaper models (Haiku, 4o-mini) or more capable ones (Sonnet, gpt-4o) without code changes
- Run offline with Ollama for privacy
- Route through OpenRouter to A/B dozens of models
- Swap at runtime by editing `.env` and restarting — no rebuild

`src/ai/base.py` exposes one method: `generate(prompt, *, temperature) -> str`. Everything else (JSON parsing, code-fence stripping, category normalization) is post-processing handled in `main.py`.

## Caching strategy

Two levels of cache for expensive AI calls:

1. **In-memory** (`_ai_cache` dict) — 1-hour TTL, resets on restart. Hot cache for the current session.
2. **File cache** (`CACHE_DIR/*.json`) — survives restarts. Fingerprinted by md5(all doc names + mtimes), auto-invalidates when any source file changes.

Currently only `/api/categorize` writes to both. Other AI endpoints use in-memory only — they're cheap enough that the extra persistence isn't worth the code.

## Data flow on first boot

1. `main.py` imports → `settings` loads `.env`
2. `_initialize_data_dir()` checks `DATA_DIR`:
   - Exists → no-op
   - Missing & env var set → abort with clear error
   - Missing & env var unset → copy `data.example/` into place
3. FastAPI app mounts routes
4. First AI request → `_ai()` lazy-instantiates the provider from `AI_PROVIDER` config

## What v1 deliberately doesn't do

- **Authentication** — delegated to reverse proxy
- **Multi-tenant** — one `DATA_DIR` per process
- **Version control / sync** — your markdown, your tooling
- **Automatic git commits** — would conflict with user workflows

## Future (v2) direction

Aligning more closely with Karpathy's gist:

- **User-editable schema files** — let users override the summary / synthesis / lint prompts without touching Python
- **Richer `index.md` / `log.md`** — both already exist but could be more structured
- **Configurable `SUBFOLDERS`** — current folders are hardcoded in `main.py`
- **Auto-commit helpers** — optional `scripts/commit-notes.sh` + cron samples for Mode A users
