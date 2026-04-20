# MindVault 🧠

> **AI 驅動的個人知識庫 —— 從你的 Markdown 筆記建出一個活生生的 wiki。**
> 靈感來自 [Andrej Karpathy 的 LLM Wiki 概念](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)。

把 MindVault 指到一個 Markdown 資料夾 —— 文章、筆記、對話匯出 —— 讓 LLM 把它們 ingest 成一個交叉引用的 wiki。資料留在你的檔案系統。無資料庫、無鎖定。

[English README](./README.md)

---

## 為什麼是 MindVault

不像「每次查詢都 retrieve 一次」的 RAG，MindVault 把 LLM 當成**長期守館員**：

- **Raw sources 不可變** —— 你的 markdown 就是唯一真相。
- **LLM 維護一層 wiki** —— 每份文件的摘要、跨文件的概念頁、概念關聯圖。
- **知識會累積** —— 合成結果持續存在，不用每次重算。

你會得到：

- 📋 **Overview** 儀表板（統計、最近文件、⭐ 收藏）
- 📚 **Library** —— 行內 Markdown 閱讀器 + 單文件 AI 摘要
- 🏷️ **Categories** —— LLM 自動歸類所有筆記與文件
- 🔍 **Search** —— 全文搜尋
- 📖 **Wiki** —— ingest 文件、合成概念、`[[連結]]` 內部導航
- 🕸️ **概念關聯圖**（D3 force-directed）
- 🩺 **Lint** —— LLM 幫你健檢 wiki 品質
- 📱 **RWD** 行動版支援

---

## 快速開始（Docker）

```bash
git clone https://github.com/yourname/MindVault
cd MindVault
cp .env.example .env
# 編輯 .env —— 至少要填 AI_PROVIDER 和 AI_API_KEY
docker compose up -d
```

開啟 `http://localhost:10016/mind-vault/`。首次啟動時 MindVault 會從 `data.example/` 自動產生 `./data`，馬上有範例內容可瀏覽。

---

## AI Provider 選擇

在 `.env` 設 `AI_PROVIDER=<name>`：

| Provider | 預設 model | 安裝 |
|---|---|---|
| `gemini` | `gemini-3.1-flash` | `uv sync --extra gemini` |
| `claude` | `claude-haiku-4-5` | `uv sync --extra claude` |
| `openai` | `gpt-4o-mini` | `uv sync --extra openai` |
| `openrouter` | `google/gemini-2.5-flash` | `uv sync --extra openai` |
| `ollama` | `llama3.1`（不需 API key） | `uv sync --extra openai` |

Docker image 預設已裝 `--extra all`，切 provider 只要改 `.env` 並重啟 container，不用重 build。

詳見 [`docs/ai-providers.md`](./docs/ai-providers.md)。

---

## 你的資料

`DATA_DIR` 指向一個 Markdown 資料夾。推薦模式：

- **獨立 git repo**（推薦）—— 一個 repo 專放筆記，愛什麼時候 commit 就什麼時候。版控 + 多裝置同步一次到位。見 [`docs/data-management.md`](./docs/data-management.md)。
- **雲端硬碟同步** —— Dropbox / iCloud / Google Drive。零配置，但沒有版本歷史。
- **既有 Obsidian vault** —— 把 `DATA_DIR` 指過去繼續用 Obsidian 的同步和 plugin，MindVault 當成 vault 的 AI 閱讀介面。

MindVault 不會寫入 `DATA_DIR` 之外的地方（只會在 `DATA_DIR/cache/` 存快取）。

---

## 設定

全部設定都在 `.env`，完整表格見 [`docs/configuration.md`](./docs/configuration.md)。

| 變數 | 用途 |
|---|---|
| `AI_PROVIDER` | 使用哪個 LLM 後端 |
| `AI_API_KEY` | Provider API key（`ollama` 不需要） |
| `AI_MODEL` | 覆寫預設 model |
| `AI_BASE_URL` | 覆寫 endpoint（proxy 用） |
| `DATA_DIR` | Markdown 資料夾路徑 |
| `CACHE_DIR` | AI 回應快取位置（預設 `DATA_DIR/cache`） |
| `BASE_PATH` | URL 前綴（預設 `mind-vault`） |
| `PORT` | 對外 port（container 內固定 10016） |

---

## 部署

- **Docker Compose** —— 一行指令，見 [`docs/deployment.md`](./docs/deployment.md)
- **Bare-metal** —— uv + systemd + nginx，給想避開 Docker 的人

存取控制（auth）**不在範圍內** —— 請自己用 nginx basic auth、Cloudflare Access、Tailscale 或 VPN 擋在前面。`docs/deployment.md` 附了 nginx 與 Caddy 反向代理範本。

---

## 本地開發

```bash
uv sync --extra all
cp .env.example .env
uv run uvicorn src.main:app --reload --port 10016

# 另開一個 terminal
cd frontend && npm install && npm run dev
```

前端 dev server 會把 `/api/*` proxy 到 10016 的 uvicorn。

---

## 架構

三層分離（raw sources → wiki → schema）與 Karpathy 原始 gist 的對應，詳見 [`docs/architecture.md`](./docs/architecture.md)。

---

## 貢獻

歡迎 PR —— 見 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

---

## License

[MIT](./LICENSE)
