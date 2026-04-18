# MindVault — Developer Notes for Claude

## Project Overview

MindVault is an AI-powered personal knowledge base web service. It reads markdown files from `data/` and exposes them via a FastAPI backend + Vue 3 frontend.

**Live URL:** https://lewsi.ddns.net/mind-vault/
**Port:** 10016
**VPS path:** `/srv/projects/mind-vault/`

---

## Key Architectural Decisions

### Single App.vue SPA
The entire frontend is one file: `frontend/src/App.vue`. Views are toggled with `v-if`, no router. This is intentional — keep it simple.

### Data is files, not a database
All content lives in `data/` as markdown files. No database. The backend reads files on every request (no persistent state except in-memory AI cache).

### AI caching
Gemini calls are expensive. Results are cached at two levels:
1. **In-memory** (`_ai_cache` dict) — 1-hour TTL (`_cache_ttl = 3600`), resets on restart
2. **File cache** (`data/cache/*.json`) — survives restarts; validated by md5 fingerprint of all doc names+mtimes; auto-invalidates when files change

The `get_file_cached(key)` / `set_file_cached(key, payload)` helpers manage the file cache. Currently only `categorize` uses both levels; other AI calls use in-memory only.

### Document folders
```
data/
├── notes.md          # folder="root", label="📋 個人筆記"
├── articles/         # folder="articles", label="📰 文章"
├── saves/            # folder="saves", label="💾 儲存"
└── conversations/    # folder="conversations", label="💬 對話記錄"
```
To add a new folder: add it to `SUBFOLDERS` dict in `main.py` and create the directory.

---

## Common Development Tasks

### Add a new API endpoint
Add a new `@app.get("/api/...")` function in `src/main.py`. No router files needed.

### Add a new frontend view
1. Add view name to `type View` union in `App.vue`
2. Add nav button in sidebar
3. Add `<section v-if="view === 'xxx'">` block in template
4. Handle data fetching in `setView()` function

### Add a new document folder
1. Add to `SUBFOLDERS` in `main.py`: `"folder_name": "emoji label"`
2. Create `data/folder_name/` directory
3. Add emoji + label mappings in `App.vue`: `folderEmoji` and `folderLabel`

### Sync a file from workspace to MindVault data
```bash
cp /workspace/group/articles/new-file.md /workspace/group/projects/MindVault/data/articles/
```
Then commit and push — the deploy workflow syncs `data/` to VPS.

---

## Deployment

Push to `main` branch triggers GitHub Actions:
1. Build Vue frontend (`npm run build` → output to `frontend/dist/`)
2. The build step in `vite.config.ts` copies dist to `src/static/` (check config)
3. Rsync `src/static/`, `src/main.py`, `pyproject.toml`, `data/` to VPS
4. SSH: `uv sync` to install/update Python deps
5. `systemctl restart mind-vault`

**Check deployment:** `gh run list --limit 5`
**Check service:** `journalctl -u mind-vault -f`

---

## Known Issues & Gotchas

### SSH in GitHub Actions
When using `appleboy/ssh-action`, secrets like `GEMINI_API_KEY` must be passed via `envs:` parameter and referenced as shell vars — NOT interpolated directly in the `script:` block (causes YAML parse errors).

### Gemini SDK
Use `google-genai` package (NOT the old `google-generativeai` which is deprecated).
```python
from google import genai as genai_sdk
client = genai_sdk.Client(api_key=key)
resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
```

### Model name
Current model: `gemini-2.0-flash`. The old `gemini-2.0-flash-lite` model is no longer available.

### AI response parsing
Gemini sometimes returns markdown-wrapped JSON (```json ... ```). The `gemini()` helper strips code fences. Always parse with `json.loads()` inside a try/except.

### Category items normalization
Gemini may return string items instead of dicts in category arrays. Always normalize with the post-processing loop in `get_categories()`.

### `load_all_docs()` vs `get_library()`
`load_all_docs()` returns raw fields: `name, label, folder, content, path`. It does NOT have `title` or `mtime`. Those are computed in `get_library()`. Don't use `d["title"]` on raw docs.

### `is_relative_to()` security check
In `get_doc()`, always verify `path.is_relative_to(DATA_DIR)` to prevent path traversal attacks.

---

## File Sync Schedule

A scheduled nano task runs daily at 2am to sync new workspace files to MindVault:
- `notes.md` is always synced
- New articles/saves/conversations added by nano are manually synced at time of creation

---

## Frontend Styling

- CSS variables defined in `index.html` `<style>` block (dark theme)
- Scoped styles in `App.vue` `<style scoped>` for component layout
- Global styles for `.md-body` (markdown renderer) in unscoped `<style>` block at bottom
- No external CSS framework — everything is hand-written
- Markdown rendered with `marked` library → `v-html` binding

---

## Tech Versions

| Tool | Version |
|------|---------|
| Python | 3.13 |
| FastAPI | ≥0.115.0 |
| uvicorn | ≥0.30.0 (with standard extras) |
| google-genai | ≥1.0.0 |
| Node.js | 20 |
| Vue | 3.5.x |
| Vite | 6.x |
| marked | 15.x |
| uv | latest (installed on VPS) |
