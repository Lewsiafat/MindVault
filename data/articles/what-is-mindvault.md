# What is MindVault?

MindVault is an AI-powered personal knowledge base that turns your markdown files into a searchable, categorized, and interconnected knowledge graph — all powered by Google Gemini AI.

## Core Concept

Most note-taking tools are passive archives. You dump information in, and it sits there. MindVault is different: it actively **processes** your notes using AI to:

1. **Summarize** — Generate concise AI summaries for every document
2. **Categorize** — Automatically group notes and articles into smart categories
3. **Synthesize** — Build a Wiki by connecting concepts across documents
4. **Visualize** — Map relationships between ideas in an interactive graph

## The File-First Philosophy

MindVault stores everything as plain markdown files. No proprietary database, no lock-in. Your data lives in `data/` as `.md` files that you can read, edit, and version-control with git.

```
data/
├── notes.md          # Your primary notes file
├── articles/         # Long-form articles and reading material
├── saves/            # Saved references and links
└── conversations/    # Exported conversations or logs
```

## AI Features

### Wiki System
The Wiki is MindVault's most powerful feature. It:
- Reads each document and generates a structured summary
- Extracts key concepts and stores them as wiki "pages"
- Runs cross-document synthesis to find connections
- Builds a knowledge graph from `[[concept]]` references

### Smart Categories
Gemini automatically categorizes all your content into themes. The results are **persistently cached** — so you pay the AI cost once, and results survive restarts until your files change.

### Concept Relationship Graph
An interactive D3.js visualization shows how your wiki concepts connect to each other and to your source documents. Zoom, pan, drag nodes, and click to navigate.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.13 |
| Frontend | Vue 3 + TypeScript + Vite |
| AI | Google Gemini 2.0 Flash |
| Styling | Hand-written CSS (dark theme) |
| Rendering | marked.js (Markdown) |

## Self-Hosting

MindVault is designed for self-hosting. Run it locally with just:

```bash
GEMINI_API_KEY=your-key uv run uvicorn src.main:app --port 8000
```

Or deploy with Docker:

```bash
cp .env.example .env  # add your GEMINI_API_KEY
docker compose up
```

Everything runs on a single server with no external dependencies beyond the Gemini API.
