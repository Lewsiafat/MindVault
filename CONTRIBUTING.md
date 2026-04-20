# Contributing to MindVault

Thanks for your interest — PRs are welcome.

## Development setup

```bash
git clone https://github.com/yourname/MindVault
cd MindVault
uv sync --extra all
cp .env.example .env      # fill AI_API_KEY
uv run uvicorn src.main:app --reload --port 10016

# in another terminal
cd frontend && npm install && npm run dev
```

The Vite dev server proxies `/api/*` to port 10016, so frontend changes hot-reload against the live backend.

## Branch naming

- `feat/<scope>` — new user-facing capability
- `fix/<scope>` — bug fix
- `refactor/<scope>` — structural change with no behavior change
- `docs/<scope>` — docs-only
- `chore/<scope>` — tooling / CI / deps

## Commit style

- First line: `type(scope): imperative summary` (≤72 chars)
- Body: wrap at 72 chars, explain **why** more than **what**

## Before submitting

- `uv run python -c "from src import main"` imports cleanly
- `npm run build` succeeds
- If you touched `src/ai/`, verify at least one provider still works end-to-end

## Adding a new AI provider

1. Create `src/ai/<name>.py` subclassing `AIProvider` from `src/ai/base.py`
2. Register in `_PROVIDER_DEFAULTS` and the routing branch in `src/ai/__init__.py`
3. Add an optional extra in `pyproject.toml`
4. Document in `docs/ai-providers.md`

## Project architecture

See [`CLAUDE.md`](./CLAUDE.md) for internal design notes and gotchas.
