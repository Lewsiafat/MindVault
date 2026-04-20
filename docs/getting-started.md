# Getting Started

MindVault has two supported installation paths: **Docker Compose** (recommended) and **bare-metal**. Pick whichever you're more comfortable with.

## Prerequisites

- An API key from one of: Google AI Studio (Gemini), Anthropic, OpenAI, OpenRouter — or a local Ollama server
- A folder of markdown files you want to ingest (or just use the shipped `data.example/`)

## Option A — Docker Compose (recommended)

```bash
git clone https://github.com/yourname/MindVault
cd MindVault
cp .env.example .env
# edit .env — at minimum set AI_PROVIDER and AI_API_KEY
docker compose up -d
```

Open `http://localhost:10016/mind-vault/`. On first boot MindVault seeds `./data` from `data.example/` so there's content to browse.

To point at your own notes:

```bash
# in .env
DATA_DIR=/absolute/path/to/your/notes
```

Then `docker compose up -d` again. The compose file mounts `${DATA_DIR}` into the container.

### Updating

```bash
git pull
docker compose up -d --build
```

## Option B — Bare-metal

Requires [uv](https://docs.astral.sh/uv/) and Node.js 20+.

```bash
git clone https://github.com/yourname/MindVault
cd MindVault

# Install only the provider you need (or --extra all)
uv sync --extra gemini

cd frontend && npm install && npm run build && cd ..

cp .env.example .env   # fill AI_API_KEY

uv run uvicorn src.main:app --host 0.0.0.0 --port 10016
```

For a production setup with systemd + nginx, see [`deployment.md`](./deployment.md).

## What to read next

- **[`configuration.md`](./configuration.md)** — every env var explained
- **[`ai-providers.md`](./ai-providers.md)** — how to get keys for each provider
- **[`data-management.md`](./data-management.md)** — how to back up / version-control your notes
- **[`architecture.md`](./architecture.md)** — how MindVault works internally
