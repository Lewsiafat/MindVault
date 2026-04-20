# OSS 化架構調整

- **分支:** `refactor/open-source-prep`
- **日期:** 2026-04-20
- **設計文件:** [`docs/plans/2026-04-20-oss-architecture-design.md`](../docs/plans/2026-04-20-oss-architecture-design.md)

## 描述

將 MindVault 從個人專案轉為可供任何人 `git clone` 後跑起來的開源專案。核心工作是解耦「程式本身」與「作者個人部署環境」，包含：抽象化 AI provider（支援 gemini / claude / openai / openrouter / ollama）、集中化 Config 層、`data/` 目錄通用化、docker 打包、文件重寫、MIT license、完全移除 GitHub Actions workflow。

架構升級（對齊 Karpathy `index.md` / `log.md` / schema 文件機制）不在此次範圍，留待 v2。

## 任務清單

### Phase 1 — 基礎設施（Config + AI 抽象）

- [x] 新增 `pydantic-settings` 依賴到 `pyproject.toml`
- [x] 建立 `src/config.py`：`Settings` class 包含 `base_path` / `port` / `data_dir` / `cache_dir` / `ai_provider` / `ai_api_key` / `ai_model` / `ai_base_url`
- [x] `Settings` 啟動驗證：`data_dir` 存在性、`ai_api_key` 條件必填、`base_path` strip `/`
- [x] `pyproject.toml` 新增 optional extras：`gemini` / `claude` / `openai` / `all`
- [x] 建立 `src/ai/base.py`：`AIProvider` ABC 定義 `generate(prompt, *, temperature)` 介面
- [x] 建立 `src/ai/gemini.py`：搬移現有 gemini 邏輯，加 `# Use google-genai, NOT google-generativeai` 註解，預設 model 改為 `gemini-3.1-flash`
- [x] 建立 `src/ai/claude.py`：使用 `anthropic` SDK，預設 `claude-haiku-4-5`
- [x] 建立 `src/ai/openai_compat.py`：使用 `openai` SDK，`base_url` 可配置，服務 openai / openrouter / ollama
- [x] 建立 `src/ai/__init__.py`：`get_provider()` 工廠依 `AI_PROVIDER` 路由，處理 base_url / model 預設對照表
- [x] Provider import 失敗時錯誤訊息提示 `uv sync --extra <provider>`
- [x] 實作時驗證 Gemini 3.1 Flash 確切 model ID 字串（可能需要 `-latest` 後綴）

### Phase 2 — 改造 `main.py`

- [x] `main.py` 所有 `os.environ.get(...)` 改讀 `settings`
- [x] `DATA_DIR` 常數改為 `settings.data_dir`；`cache_dir` 改為 `settings.cache_dir or settings.data_dir / "cache"`
- [x] AI 呼叫全改走 `get_provider().generate(...)`
- [x] 輸出後處理（code-fence 剝除、JSON parse、category item 正規化）保留在 `main.py`
- [x] `load_all_docs()` 加 **跳過 `.` 開頭資料夾** 邏輯
- [x] 啟動邏輯：`data_dir` 若使用者未設且不存在 → 自動從 `data.example/` 複製；若明確設置但不存在 → fail-fast

### Phase 3 — Data 目錄重整

- [x] `git rm -r data/`（本機保留備份，VPS 上 `/srv/projects/mind-vault/data/` 不動）
- [x] `.gitignore` 新增 `data/`、`.env`、`src/static/`
- [x] 建立 `data.example/` 目錄結構：`notes.md`（Karpathy-style 範例）、`articles/welcome.md`、`saves/.gitkeep`、`conversations/.gitkeep`
- [x] 撰寫 `data.example/articles/welcome.md` 說明內容

### Phase 4 — Packaging

- [x] 建立 `Dockerfile`（multi-stage：node frontend build → python runtime）
- [x] 建立 `docker-compose.yml`（volume 掛載 `DATA_DIR`、env_file、restart policy）
- [x] 建立 `.env.example`（含所有變數與註解）

### Phase 5 — 移除 GitHub Actions

- [x] 刪除 `.github/workflows/deploy.yml`
- [x] 刪除 `.github/workflows/` 目錄（若為空）
- [x] 刪除 `.github/` 目錄（若無其他內容）
- [x] 確認 VPS 仍可手動 `git pull && uv sync && systemctl restart mind-vault` 維運

### Phase 6 — 文件

- [x] 新增 `LICENSE`（MIT，作者署名 Lewsifat）
- [x] 新增 `CONTRIBUTING.md`（dev 環境、branch 規則、PR 規範）
- [x] 重寫 `README.md`：產品導向、移除個人 live URL、加 Karpathy inspiration 連結、API 表搬出
- [x] 重寫 `README.zh-TW.md`：與英文版同步
- [x] `CHANGELOG.md` 新增 `[2.0.0] - 2026-04-XX` 條目
- [x] 修正 `CLAUDE.md`：移除 `lewsi.ddns.net`、`/srv/projects/mind-vault/`、`lewsi` user、個人 nano agent sync 說明
- [x] 建立 `docs/getting-started.md`
- [x] 建立 `docs/data-management.md`（模式 A 預設推薦 + B/C + Future helpers TODO）
- [x] 建立 `docs/configuration.md`（所有 `.env` 變數完整表格）
- [x] 建立 `docs/ai-providers.md`（5 個 provider 取得 key / 設定範例）
- [x] 建立 `docs/deployment.md`（整合原本規劃的四份：docker quickstart / bare-metal / reverse-proxy / systemd — 合併為單檔降低導航負擔）
- [x] 建立 `docs/architecture.md`（Karpathy 三層對應 + MindVault 具體實作）
- [x] 建立 `docs/api-reference.md`（從 README 搬過來的 endpoint 表）

### Phase 7 — 驗證

- [x] 本地 `uv sync --extra all && uv run uvicorn src.main:app --port 10016` 能啟動並瀏覽
- [x] 切換 `AI_PROVIDER=openai` + 無 key，確認 fail-fast 錯誤訊息清楚
- [ ] `docker compose up --build` 成功啟動且可瀏覽（本機無 Docker daemon，未端對端驗證；Dockerfile 靜態檢查 + `uv sync --locked --extra all --no-dev` + `npm run build` 皆綠）
- [x] `load_all_docs()` 邏輯上會跳過 `.git/` / `.obsidian/` / `.DS_Store`（glob + 新增的 `.`-prefix 過濾）
- [x] `grep lewsi|ddns.net|/srv/projects/mind-vault|/workspace/group` 除 `specs/` 與 `docs/plans/`（設計文件保留上下文）外無殘留

## 不在此次範圍（v2 候選）

- 對齊 Karpathy 架構：`index.md` / `log.md` / schema 文件機制
- 多租戶 auth + 資料隔離
- `SUBFOLDERS` 可配置
- `scripts/commit-notes.sh` 輔助腳本
- GHCR / Docker Hub image 發布
- Healthcheck、多架構 build
- i18n 文件（中英以外）
