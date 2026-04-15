# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.2.0] - 2026-04-15

### Added
- **概念關聯圖** — 新增 `GET /api/wiki/graph` 端點，解析 wiki 頁面的 `[[slug]]` 引用關係；前端以 D3.js（CDN）繪製 force-directed 互動圖，支援 zoom/pan、drag、hover tooltip、點擊跳轉
- **Wiki 頁面連結可點擊** — markdown 渲染後攔截 `<a>` click 事件，匹配 `/mind-vault/wiki/` 路徑，改為 SPA 內部導航而不跳出頁面
- **收藏 / 標記重要文章** — localStorage `mv-favorites` 收藏清單；Library 每個文件卡片、Wiki 頁面標題旁均加入 ⭐ 按鈕；Overview 新增「⭐ 我的收藏」區塊
- **分類持久化快取** — 智能分類結果寫入 `data/cache/` JSON 檔案，服務重啟後直接讀取快取；以所有文件的 md5 fingerprint 自動偵測文件變更並失效快取；支援 `?force=true` 強制重新產生

### Changed
- `GET /api/categorize` 加入 `?force=true` 查詢參數，可強制略過快取重新呼叫 Gemini
- Overview 頁面新增收藏區塊，Library 卡片加入收藏按鈕列

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
