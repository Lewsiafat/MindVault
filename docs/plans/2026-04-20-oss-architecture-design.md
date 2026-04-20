# MindVault OSS 化架構設計

**Date:** 2026-04-20
**Status:** Approved, pending implementation plan
**Scope:** v1 — make the repo usable by anyone, without changing core wiki behavior

---

## 1. 背景與目標

MindVault 原本是個人 knowledge base 專案，程式、部署流程與 `data/` 目錄高度綁定作者的 VPS（`/srv/projects/mind-vault/`、`lewsi` user、`lewsi.ddns.net`、GitHub Actions rsync、nano agent 同步）。

本次 OSS 化的目標是：**任何人 `git clone` 後依照 README 都能跑起來**，同時保留作者未來手動部署的可能性。不在此次範圍內的是架構升級（`index.md` / `log.md` / schema 文件機制對齊 Karpathy），留待 v2。

### 專案靈感

MindVault 的核心價值來自 [Andrej Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)：LLM 持續維護一層 wiki，作為 raw sources 與使用者之間的 synthesis layer；不是每個 query 都重新 retrieve，而是讓知識 compound。MindVault 的 `/api/wiki/*` endpoints 已具備這個雛形。OSS 化時 README 會明確標註此 inspiration。

### 成功標準（v1）

- 新使用者依 `docs/getting-started.md` 能用 `docker compose up` 在本地跑起來
- 支援 `AI_PROVIDER` 至少 5 種：gemini / claude / openai / openrouter / ollama
- Repo 不含作者個人筆記內容
- 作者個人 VPS 仍可透過手動方式維持運作（雖然自動 workflow 被移除）

---

## 2. 使用者決策摘要

逐題討論後確認的方向：

| 項目 | 決定 |
|---|---|
| 部署模式 | 本地桌面工具 + self-hosted 皆支援（同一份 code） |
| Data 來源 | `.env` 指定 `DATA_DIR` + Web UI 新增編輯，兩者並存 |
| AI Provider | 抽象化，支援多家 provider，無 API key 時程式無法運作 |
| 架構升級（Karpathy 對齊） | v2 再做，v1 僅做部署通用化 |
| Auth | 不做；存取控制交給 reverse proxy |
| Packaging | git clone 手動 + Dockerfile/docker-compose（不發布 image） |
| License | MIT |
| 專案名稱 | 保留 `MindVault`，README 重寫為產品導向 + Karpathy 標註 |
| Data 版控 | 程式不管；文件推薦「獨立 git repo」為預設模式 |
| GitHub Actions | **全部移除**（不留 CI/CD workflow） |

---

## 3. 整體架構

```
┌────────────────────────────────────────────┐
│ 使用者自己的反向代理 / auth（nginx, Caddy, │  ← 不在 repo 範圍
│ Cloudflare Access）                        │
└────────────────────────────────────────────┘
                   ↓
┌────────────────────────────────────────────┐
│ MindVault app (uvicorn :PORT)              │
│ ├─ FastAPI routes (src/main.py)            │
│ ├─ AI provider 層 (src/ai/*.py)            │  ← 新增
│ ├─ Config 層 (src/config.py)               │  ← 新增
│ └─ 靜態前端 (src/static/)                  │
└────────────────────────────────────────────┘
                   ↓ 讀寫
┌────────────────────────────────────────────┐
│ DATA_DIR (使用者指定路徑)                  │
│ ├─ notes.md / articles/ / saves/ / ...     │
│ └─ cache/                                  │
└────────────────────────────────────────────┘
```

**Repo 邊界調整**：

- 刪除 `.github/workflows/deploy.yml` 與整個 `.github/workflows/` 目錄（連 CI 都不保留）
- `data/` 從 git 移除、加入 `.gitignore`；改提供 `data.example/`
- `BASE_PATH`、`PORT`、`DATA_DIR`、AI 設定全由 `.env` 控制
- 個人部署用的 systemd / nginx snippet 從 workflow 抽到 `docs/deployment/systemd-example.md`

---

## 4. Config 層

所有環境變數集中在 `src/config.py`（使用 `pydantic-settings`），程式他處不再直接讀 `os.environ`。

```python
class Settings(BaseSettings):
    base_path: str = "mind-vault"
    port: int = 10016
    data_dir: Path = Path("./data")
    cache_dir: Path | None = None        # 預設 = data_dir / "cache"
    ai_provider: str = "gemini"
    ai_api_key: str | None = None
    ai_model: str | None = None          # None 時採用 provider 預設
    ai_base_url: str | None = None       # None 時採用 provider 預設

    class Config:
        env_file = ".env"
```

**啟動驗證**：

- `data_dir` 若被明確設置但不存在 → fail-fast 錯誤訊息
- `data_dir` 未設置且 `./data` 不存在 → 自動從 `data.example/` 複製
- `ai_provider != "ollama"` 時 `ai_api_key` 必填，否則啟動失敗
- `base_path` 自動 strip `/`

新增依賴：`pydantic-settings`。

---

## 5. AI Provider 抽象層

```
src/ai/
├── __init__.py           # get_provider() 工廠
├── base.py               # AIProvider ABC
├── gemini.py             # google-genai SDK（不是 deprecated 的 google-generativeai）
├── claude.py             # anthropic SDK
└── openai_compat.py      # openai SDK，共用於 openai / openrouter / ollama
```

### 介面（最小化）

```python
class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        """Return raw text. Caller handles JSON parsing / code-fence stripping."""
```

JSON parse / code-fence stripping / category-item normalization 等 **輸出後處理** 邏輯保留在 `main.py`（不是 provider 的責任）。

### Provider 路由

| `AI_PROVIDER` | 實作類別 | `base_url` 預設 | 預設 `AI_MODEL` | 需 API key |
|---|---|---|---|---|
| `gemini` | `GeminiProvider` | — | `gemini-3.1-flash` | ✅ |
| `claude` | `ClaudeProvider` | — | `claude-haiku-4-5` | ✅ |
| `openai` | `OpenAICompatProvider` | `https://api.openai.com/v1` | `gpt-4o-mini` | ✅ |
| `openrouter` | `OpenAICompatProvider` | `https://openrouter.ai/api/v1` | `google/gemini-2.5-flash` | ✅ |
| `ollama` | `OpenAICompatProvider` | `http://localhost:11434/v1` | `llama3.1` | ❌ |

使用者在 `.env` 可覆寫 `AI_MODEL` / `AI_BASE_URL`。

### 依賴管理（optional extras）

```toml
[project.optional-dependencies]
gemini = ["google-genai>=1.0.0"]          # 注意：不是 google-generativeai
claude = ["anthropic>=0.40.0"]
openai = ["openai>=1.0.0"]                # 也服務 openrouter / ollama
all    = [...]
```

Provider 實作 import SDK 時若失敗，錯誤訊息提示 `uv sync --extra <provider>`。

### Gemini SDK 註解

`src/ai/gemini.py` 開頭註解：

```python
# Use `google-genai` (new SDK). Do NOT use `google-generativeai` — it's deprecated.
from google import genai as genai_sdk
```

### 待驗證

Gemini 3.1 Flash 的確切 model ID 字串（`gemini-3.1-flash` vs `gemini-3.1-flash-latest` vs `gemini-3.1-flash-preview-DD-YYYY`）。實作時啟動做一次試呼叫驗證，錯誤則 fail-fast 並提示改用 `-latest` 後綴。

---

## 6. Data 層

### Repo 變動

1. `git rm -r data/` 並加入 `.gitignore`
2. 新增 `data.example/`（進 git）：
   ```
   data.example/
   ├── notes.md              # Karpathy-style 範例筆記
   ├── articles/
   │   └── welcome.md        # 說明文件
   ├── saves/.gitkeep
   └── conversations/.gitkeep
   ```
3. `src/main.py` 的 `DATA_DIR` 從寫死路徑改為 `settings.data_dir`
4. **啟動行為**：若 `data_dir` 不存在且使用者未明確設置 → 自動從 `data.example/` 複製並 log `"Initialized DATA_DIR from data.example/"`；若有明確設但路徑不存在 → fail-fast
5. `load_all_docs()` 加 **跳過 `.` 開頭的資料夾** 邏輯（避免誤讀 `.git/` / `.obsidian/` / `.DS_Store`）
6. `SUBFOLDERS` **v1 不做可配置**（YAGNI），保持寫死在 `main.py`

### 作者個人部署的影響

VPS 上既有的 `/srv/projects/mind-vault/data/` 不會被動到，因為 deploy workflow 已被移除。作者未來要部署新版本時手動 SSH 進去 `git pull && uv sync` 或自己用 docker compose。

---

## 7. Data 管理與版控

**原則**：MindVault 本身不管版控、同步、備份。職責單純：讀寫 markdown。

`docs/data-management.md` 提供三種推薦模式，**預設推薦模式 A**：

### 模式 A — 獨立 git repo（預設推薦）

```bash
git clone git@github.com:yourname/my-notes.git ~/notes
# .env: DATA_DIR=/home/you/notes
```

使用者手動 commit / push，或自行 cron。

**Future helper（v2 TODO）**：`scripts/commit-notes.sh` + cron 範例，降低手動負擔。

### 模式 B — 雲端硬碟資料夾

`DATA_DIR` 指向 Dropbox / iCloud / Google Drive 的同步資料夾。零配置、多裝置自動同步，但無版本歷史。

### 模式 C — Obsidian vault 相容

`DATA_DIR` 指向既有 Obsidian vault。使用者繼續用 Obsidian Sync / Obsidian Git plugin 做同步，MindVault 當作 vault 的 AI 閱讀介面。`load_all_docs()` 跳過 `.obsidian/`。

### 不做

- 程式內偵測 git repo 並自動 commit
- 內建 sync UI
- 內建備份機制

---

## 8. Docker 打包

### `Dockerfile`（multi-stage）

```dockerfile
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --extra all --no-dev
COPY src/ ./src/
COPY --from=frontend /app/src/static/ ./src/static/
COPY data.example/ ./data.example/
ENV PORT=10016
EXPOSE 10016
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "10016"]
```

### `docker-compose.yml`

```yaml
services:
  mindvault:
    build: .
    ports:
      - "10016:10016"
    env_file: .env
    volumes:
      - ${DATA_DIR:-./data}:/app/data
    restart: unless-stopped
```

### 使用者流程

```bash
git clone https://github.com/yourname/MindVault
cd MindVault
cp .env.example .env
# 編輯 .env 填 AI_API_KEY
docker compose up -d
# http://localhost:10016/mind-vault/
```

### 不做（v1）

- `Dockerfile.dev`、多環境 compose file
- 發布到 GHCR / Docker Hub
- 多架構 build（arm64 / amd64）
- Healthcheck config（`/api/health` 已存在，v2 可補）

---

## 9. 文件與 README

### Repo 根

| 檔案 | 動作 |
|---|---|
| `README.md` | 重寫成產品導向 |
| `README.zh-TW.md` | 同步重寫 |
| `CHANGELOG.md` | 加 `[2.0.0]` OSS release |
| `LICENSE` | 新增 MIT |
| `CONTRIBUTING.md` | 新增 |
| `CLAUDE.md` | 移除個人 live URL / VPS path / user 名稱 |
| `.env.example` | 新增 |
| `.gitignore` | 加 `data/`、`.env`、`src/static/` |

### `docs/` 結構

```
docs/
├── getting-started.md
├── data-management.md       # 模式 A/B/C
├── configuration.md
├── ai-providers.md          # 各 provider 取得 key / 設定
├── deployment/
│   ├── docker.md
│   ├── bare-metal.md
│   ├── reverse-proxy.md
│   └── systemd-example.md
├── architecture.md          # Karpathy 對應 + 三層架構
└── screenshots/
```

### `docs/deployment/docker.md` 必含

- 三步驟快速啟動
- `.env` 每個變數說明
- Volume 掛載示意
- Port mapping 對照（本地 vs VPS + nginx 反代）
- 常見除錯（log、exec、health）
- 更新流程（`git pull && docker compose up -d --build`）
- nginx + Caddy 反代範本

### README 改寫重點

- 移除 `Live: https://lewsi.ddns.net/mind-vault/`，改放 screenshot
- 「personal knowledge base」→「your personal knowledge base」
- 標題旁加「Inspired by Karpathy's LLM Wiki」連結
- API endpoints 表搬到 `docs/api-reference.md`
- 「Data Sync / Daily cron at 2am」整段移除（那是作者個人的 nano agent）

---

## 10. 不在此次範圍（v2 候選）

- 對齊 Karpathy 架構：`index.md` / `log.md` / schema 文件機制
- 多租戶 auth + 資料隔離
- `SUBFOLDERS` 可配置
- `scripts/commit-notes.sh` 輔助腳本
- GHCR / Docker Hub image 發布
- Healthcheck、多架構 build
- i18n 文件（中英以外）

---

## 11. 改動清單總覽

### 新增
- `src/config.py`
- `src/ai/{__init__,base,gemini,claude,openai_compat}.py`
- `Dockerfile`、`docker-compose.yml`
- `.env.example`
- `data.example/` 目錄樹
- `LICENSE`、`CONTRIBUTING.md`
- `docs/` 整個樹

### 修改
- `src/main.py` — 改用 `settings.*`，AI 呼叫走 `get_provider()`，`load_all_docs()` 跳過隱藏資料夾
- `pyproject.toml` — 加 `pydantic-settings`、各 provider optional extras
- `README.md` / `README.zh-TW.md` — 重寫
- `CHANGELOG.md` — 加 2.0.0
- `CLAUDE.md` — 去個人化
- `.gitignore` — 加 `data/`、`.env`、`src/static/`

### 刪除
- `.github/workflows/deploy.yml`
- `.github/` 目錄（若無其他內容）
- `data/` 實際內容（從 git 移除，VPS 上的實體保留）
