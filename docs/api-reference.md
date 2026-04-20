# API Reference

All endpoints are mounted under `${BASE_PATH}` (default `/mind-vault`).

## Core

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check — returns doc count |
| GET | `/api/stats` | Total docs, words, notes items, folder counts |
| GET | `/api/notes` | Parse `notes.md` into sections + bullet items |
| GET | `/api/library` | All docs with metadata, preview, mtime |
| GET | `/api/doc?folder=&name=` | Full content of one document |
| GET | `/api/search?q=` | Full-text search across notes and docs |

## AI (cached)

| Method | Path | Cache |
|---|---|---|
| GET | `/api/summary` | In-memory, 1-hour TTL |
| GET | `/api/categorize?force=bool` | In-memory + file cache (persistent) |
| GET | `/api/doc-summary?folder=&name=` | In-memory, 1-hour TTL |

## Wiki

| Method | Path | Description |
|---|---|---|
| GET | `/api/wiki/status` | Build status + pending docs to ingest |
| GET | `/api/wiki/pages` | All wiki pages (from index.md) |
| GET | `/api/wiki/page?slug=&type=` | Single wiki page (`type`: summary / concept) |
| GET | `/api/wiki/log` | Append-only history (`log.md`) |
| GET | `/api/wiki/graph` | Node-edge graph — `{nodes, edges}` from `[[link]]` references |
| GET | `/api/wiki/lint` | AI health-check |
| POST | `/api/wiki/ingest` | Ingest a document |
| POST | `/api/wiki/ingest-all` | Ingest every pending document |
| POST | `/api/wiki/synthesize?force=bool` | Build concept pages from extracted concepts |
| POST | `/api/wiki/fix` | Auto-fix a lint issue |

## Request / response shapes

See `src/main.py` for the source of truth — FastAPI's automatic `/docs` endpoint also gives you an interactive OpenAPI UI at `${BASE_PATH}/docs`.
