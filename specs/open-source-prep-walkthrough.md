# OSS 化架構調整 — Walkthrough

- **分支:** `refactor/open-source-prep`
- **日期:** 2026-04-20
- **設計文件:** [`docs/plans/2026-04-20-oss-architecture-design.md`](../docs/plans/2026-04-20-oss-architecture-design.md)
- **規格文件:** [`open-source-prep.md`](./open-source-prep.md)

## 變更摘要

將 MindVault 從個人 VPS 專案轉為可供任何人 clone 後跑起來的開源專案。核心解耦了「程式本身」與「作者的個人部署環境」，完成項目包括：抽象化 AI provider（5 家）、集中化 Config 層、`data/` 目錄通用化、Docker 多階段打包、完整文件與 OSS metadata、完全移除 GitHub Actions workflow、MIT license。架構升級（對齊 Karpathy `index.md` / `log.md` / schema 文件機制）列為 v2，不在此次範圍。

## Commit 歷史

| Commit | 範圍 |
|---|---|
| `3d48d72` | 設計文件（已在 main） |
| `4f4d71f` | Task spec |
| `4ea24fc` | Phase 1：Config + AI 抽象層 |
| `c2c9b50` | Phase 2：`main.py` 遷移到 settings + get_provider |
| `dfb9ba1` | Phase 4+5：Docker 打包 + 移除 GitHub Actions |
| `db9c87b` | Phase 3+6+7：untrack data/static、完整文件、LICENSE、驗證 |

## 修改的檔案

### 新增 — 程式碼
- `src/config.py` — pydantic-settings 集中管理所有環境變數
- `src/ai/base.py` — `AIProvider` ABC，單一 `generate()` 介面
- `src/ai/gemini.py` — `google-genai` SDK（非 deprecated 版本），預設 `gemini-3.1-flash`
- `src/ai/claude.py` — `anthropic` SDK，預設 `claude-haiku-4-5`
- `src/ai/openai_compat.py` — `openai` SDK，共用於 openai / openrouter / ollama
- `src/ai/__init__.py` — `get_provider()` 工廠與 per-provider 預設對照表

### 新增 — 打包
- `Dockerfile` — multi-stage（node:20 前端 build → python:3.13 runtime）
- `docker-compose.yml` — 掛 `DATA_DIR`、讀 `.env`
- `.dockerignore`
- `.env.example`
- `data.example/` —  `notes.md` + `articles/welcome.md` 等 seed 檔

### 新增 — 文件
- `LICENSE`（MIT）
- `CONTRIBUTING.md`
- `docs/getting-started.md`
- `docs/configuration.md`
- `docs/ai-providers.md`
- `docs/data-management.md`
- `docs/deployment.md`
- `docs/architecture.md`
- `docs/api-reference.md`
- `specs/open-source-prep.md`
- `specs/open-source-prep-walkthrough.md`（本檔）

### 修改
- `src/main.py` — 全面改用 `settings.*` 與 `get_provider()`；`load_all_docs()` 跳過 `.` 開頭；`_initialize_data_dir()` 處理 auto-seed / fail-fast
- `pyproject.toml` — 加 `pydantic-settings` 核心依賴；AI SDK 改為 optional extras（`gemini` / `claude` / `openai` / `all`）
- `README.md` / `README.zh-TW.md` — 重寫為產品導向 + Karpathy 連結，移除個人 live URL
- `CLAUDE.md` — 去個人化，補 Settings 層與 AI provider 段落
- `CHANGELOG.md` — 加 `[2.0.0]` OSS release
- `.gitignore` — 加 `data/`、`src/static/`、`temp/`、`.claude/`
- `uv.lock` — 新 SDK 解析結果

### 刪除
- `.github/workflows/deploy.yml` —— OSS repo 不再綁作者 VPS
- `data/*.md`（從 git untrack，本機與 VPS 實體保留）
- `src/static/*`（build 產物，gitignore + untrack）

## 技術細節

### Lazy AI provider 初始化
`main.py` 的 `_ai()` 在首次呼叫才實例化 provider。這讓 server 可以在沒有 API key 時啟動，非 AI endpoints（Library、Search、Raw Notes）仍可用；只有打到需要 AI 的 endpoint 才會 fail-fast。這比啟動期就要求 key 對試用者更友善。

### Provider 路由的分層設計
`_PROVIDER_DEFAULTS` 用一張表集中 5 個 provider 的 model / base_url 預設值。`openai` / `openrouter` / `ollama` 共用 `OpenAICompatProvider`，靠不同 `base_url` 區分。新增 provider 只要：加 dict entry → 加 routing branch → 加 optional extra，三步。

### Data 目錄 auto-seed / fail-fast
區分兩種情況：
1. 使用者 **明確設置** `DATA_DIR` env var 但路徑不存在 → fail-fast 清楚告知
2. 使用者 **未設置**（用預設 `./data`）且路徑不存在 → 從 `data.example/` 複製，讓新 clone 首次 boot 就有內容

用 `"DATA_DIR" in os.environ` 判斷是哪一種。

### Optional extras 的取捨
5 個 provider 的 SDK 不綁 default install：`uv sync` 基本只裝 FastAPI 依賴。使用者依需求選 `--extra gemini` / `--extra openai` / `--extra all`。Docker image 用 `--extra all` 打包，讓切 provider 不用重 build image。

### Gemini SDK 的版本陷阱
CLAUDE.md 與 `src/ai/gemini.py` 開頭都註解：**必須用 `google-genai`，不是 deprecated 的 `google-generativeai`**。這是作者先前踩過的坑，留在原始碼與文件提醒後續維護者。

### GitHub Actions 完全移除
不是搬位置、也不留 CI（lint / test / build）。OSS repo 的使用者要自己的 pipeline。作者個人 VPS 的自動部署隨之停止，未來要改用手動 `git pull && docker compose up -d --build` 或自己另寫 workflow。

### Git history 的個人筆記
`git rm --cached -r data/` 只從 index 移除，**git history 仍保留原始 markdown 內容**。公開前需要用 `git filter-repo` 或 `git filter-branch` 清理。這件事列為公開前 pre-flight check，不屬於這次任務。

### 驗證結果
- `uv run uvicorn src.main:app` 啟動 OK
- `/api/health` 回 `{"status":"ok","total_docs":29}`
- `/api/library` 回 29 份 doc（作者本地原有資料）
- `npm run build` 綠
- `uv sync --locked --extra all --no-dev` 無衝突
- grep `lewsi|ddns.net|/srv/projects/mind-vault|/workspace/group` 除 `specs/` 與 `docs/plans/`（設計文件保留上下文）外無殘留
- Docker image build 未驗證（本機無 Docker daemon）

## 未做（列為 v2 候選）

- 對齊 Karpathy 架構：使用者可編輯的 schema 文件、更結構化的 `index.md` / `log.md`
- `scripts/commit-notes.sh` 輔助腳本（配 cron，支援 Mode A 使用者）
- GHCR / Docker Hub image 發布
- 多租戶 auth + 資料隔離
- `SUBFOLDERS` 可配置
- Healthcheck、多架構 Docker build
- i18n 文件（中英以外）

## 公開前 pre-flight checklist（不屬本任務）

- [ ] `git filter-repo` 清 `data/` 的 git history
- [ ] 推新 repo（或強推覆蓋，且確認 fork 連結不會洩漏舊 history）
- [ ] 以乾淨環境 clone → `docker compose up` 驗證 full quickstart 流程
- [ ] 補 README 截圖 / GIF
- [ ] 決定 GitHub repo 名稱（預計沿用 `MindVault`）
