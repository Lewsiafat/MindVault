# MindVault 🧠

> **An AI-powered personal knowledge base that builds a living wiki from your markdown notes.**
> Inspired by [Andrej Karpathy's LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Point MindVault at a folder of markdown files — articles, notes, conversation exports — and let an LLM ingest them into a cross-referenced wiki. Your data stays in your filesystem. No database. No lock-in.

[繁體中文 README](./README.zh-TW.md)

---

## Why MindVault

Unlike per-query RAG, MindVault treats the LLM as a **long-running librarian** for your knowledge:

- **Raw sources are immutable** — your markdown files are the source of truth.
- **The LLM maintains a wiki layer** — per-document summaries, cross-document concept pages, concept graph.
- **Knowledge compounds** — synthesis accumulates instead of being recomputed every time.

What you get:

- 📋 **Overview** dashboard (stats, recent docs, ⭐ favorites)
- 📚 **Library** with inline markdown reader and per-doc AI summary
- 🏷️ **Categories** — LLM auto-groups notes & documents
- 🔍 **Search** across everything
- 📖 **Wiki** — ingest docs, synthesize concepts, click `[[links]]` to navigate
- 🕸️ **Concept Graph** (D3 force-directed)
- 🩺 **Lint** — LLM health-check of wiki quality
- 📱 **Responsive** mobile layout

---

## Quick Start (Docker)

```bash
git clone https://github.com/yourname/MindVault
cd MindVault
cp .env.example .env
# edit .env — at minimum set AI_PROVIDER and AI_API_KEY
docker compose up -d
```

Open `http://localhost:10016/mind-vault/`. On first boot MindVault seeds `./data` from `data.example/`, so there's content to browse immediately.

---

## AI Providers

Pick one in `.env` — `AI_PROVIDER=<name>`:

| Provider | Default model | Install extra |
|---|---|---|
| `gemini` | `gemini-3.1-flash` | `uv sync --extra gemini` |
| `claude` | `claude-haiku-4-5` | `uv sync --extra claude` |
| `openai` | `gpt-4o-mini` | `uv sync --extra openai` |
| `openrouter` | `google/gemini-2.5-flash` | `uv sync --extra openai` |
| `ollama` | `llama3.1` (no API key) | `uv sync --extra openai` |

The Docker image is pre-built with `--extra all` so you can switch providers by changing `.env` and restarting the container — no rebuild.

See [`docs/ai-providers.md`](./docs/ai-providers.md) for key-acquisition links and per-provider tips.

---

## Your Data

`DATA_DIR` points to a folder of markdown files. Recommended layouts:

- **Independent git repo** *(recommended)* — one repo for your notes, commit whenever you like. Version control + multi-device sync for free. See [`docs/data-management.md`](./docs/data-management.md).
- **Cloud-synced folder** — Dropbox / iCloud / Google Drive. Zero-config sync, no version history.
- **Existing Obsidian vault** — point `DATA_DIR` at it, keep using Obsidian's sync and plugins. MindVault becomes a read-only AI lens over the vault.

MindVault never writes outside `DATA_DIR` (except for its cache at `DATA_DIR/cache/`).

---

## Configuration

All knobs live in `.env`. See [`docs/configuration.md`](./docs/configuration.md) for the full table.

| Key | Purpose |
|---|---|
| `AI_PROVIDER` | Which LLM backend |
| `AI_API_KEY` | Provider API key (not needed for `ollama`) |
| `AI_MODEL` | Override the per-provider default model |
| `AI_BASE_URL` | Override endpoint (useful for proxies) |
| `DATA_DIR` | Path to your markdown folder |
| `CACHE_DIR` | Where AI response cache lives (defaults to `DATA_DIR/cache`) |
| `BASE_PATH` | URL prefix (defaults to `mind-vault`) |
| `PORT` | Host port (container always listens on 10016) |

---

## Deployment

- **Docker Compose** — single-command setup, covered in [`docs/deployment.md`](./docs/deployment.md)
- **Bare-metal** — uv + systemd + nginx, for users who want to skip Docker

Access control (auth) is **out of scope** — put MindVault behind nginx basic auth, Cloudflare Access, Tailscale, or a VPN. `docs/deployment.md` includes reverse-proxy templates for nginx and Caddy.

---

## Local Development

```bash
uv sync --extra all
cp .env.example .env      # fill AI_API_KEY
uv run uvicorn src.main:app --reload --port 10016

# in a second terminal
cd frontend && npm install && npm run dev
```

Frontend dev server proxies `/api/*` to the uvicorn backend on 10016.

---

## Architecture

See [`docs/architecture.md`](./docs/architecture.md) for the three-layer breakdown (raw sources → wiki → schema) and how MindVault maps to Karpathy's original gist.

---

## Contributing

PRs welcome — see [`CONTRIBUTING.md`](./CONTRIBUTING.md).

---

## License

[MIT](./LICENSE)
