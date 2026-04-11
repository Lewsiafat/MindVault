# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - 2026-04-11

### Added
- Core knowledge base: Overview dashboard (stats + recently updated docs), Library (docs grouped by folder), Categories (Gemini AI auto-categorize), Search (full-text), Raw Notes (markdown render)
- Wiki system: per-document AI summarization, concept ingestion, knowledge synthesis across all docs
- Lint health-check: AI-powered notes quality analysis with severity scoring, one-click issue fix
- Light / dark theme toggle with localStorage persistence
- RWD mobile support: hamburger slide-in sidebar, mobile top bar, single-column grids on ≤768px
- Daily cron data sync from nano agent workspace (notes, articles, saves, conversations)
- FastAPI backend with Gemini 2.0 Flash AI — 1-hour in-memory cache for all AI calls
- GitHub Actions CI/CD: frontend build → rsync → VPS systemd service restart
