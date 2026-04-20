# Data Management

MindVault doesn't do version control, sync, or backups — it only reads and writes markdown files. Pick whichever external tool you prefer for those concerns. This doc covers three recommended patterns.

## Mode A — Independent git repo (recommended)

Keep your notes in their own private git repo. You get version history, multi-device sync, and GitHub (or self-hosted) as a backup — for free.

```bash
git clone git@github.com:yourname/my-notes.git ~/notes
```

```env
# .env
DATA_DIR=/home/you/notes
```

Commit whenever you like:

```bash
cd ~/notes
git add -A && git commit -m "update" && git push
```

**Why this is the default recommendation:** it matches how most technical users already manage plain-text files, it gives you `git log` / `git blame` for free, and it decouples your notes from MindVault entirely — you can run other tools against the same folder.

**Future helper** (v2 TODO): `scripts/commit-notes.sh` + cron sample so you don't have to remember to commit manually.

## Mode B — Cloud-synced folder

Point `DATA_DIR` at a folder that's synced by Dropbox / iCloud / Google Drive / OneDrive.

```env
DATA_DIR=/Users/you/Library/CloudStorage/Dropbox/mindvault-notes
```

**Pros:** zero configuration, automatic multi-device sync.
**Cons:** no version history (beyond whatever your cloud provider keeps).

## Mode C — Existing Obsidian vault

If you already have an Obsidian vault, point `DATA_DIR` at it and let MindVault serve as a read-only AI lens. Keep using Obsidian Sync or the Obsidian Git plugin for sync.

```env
DATA_DIR=/Users/you/Documents/obsidian-vault
```

MindVault's `load_all_docs()` **skips folders and filenames that start with `.`**, so `.obsidian/` and other Obsidian metadata won't pollute the reader.

## What MindVault writes

MindVault treats your markdown files as read-only in the Library / Search / Raw Notes views. But the Wiki feature *does* create new files:

- `DATA_DIR/wiki/summaries/<slug>.md` — per-document AI summaries
- `DATA_DIR/wiki/pages/<slug>.md` — cross-document concept pages
- `DATA_DIR/wiki/index.md` — wiki index rebuilt on every ingest
- `DATA_DIR/wiki/log.md` — append-only chronological record
- `DATA_DIR/cache/*.json` — AI response cache

If you version-control your notes, you'll want to decide whether to commit `wiki/` (recomputable but saves re-ingest time) and `cache/` (entirely recomputable — gitignore recommended).

A suggested `.gitignore` inside your notes repo:

```
cache/
# optionally also: wiki/
```

## Migrating from the author's original layout

Not applicable — MindVault v2.0 ships without the author's personal notes. Start fresh.
