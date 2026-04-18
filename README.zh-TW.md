# MindVault 🧠

> AI 驅動的個人知識庫 — 使用 Google Gemini AI 瀏覽、搜尋並合成你的筆記與文件。

**[English README](README.md)**

---

## 功能

- **概覽** — 統計儀表板（文件數、字數、筆記條目）+ 最近更新文件 + ⭐ 我的收藏
- **文件庫** — 依資料夾分類的所有文件，含內嵌 Markdown 閱讀器、AI 摘要與 ⭐ 收藏按鈕
- **分類** — Gemini AI 自動分類所有筆記和文件（持久化快取，服務重啟後不需重新產生）
- **搜尋** — 跨所有筆記與文件的全文搜尋
- **原始筆記** — `notes.md` 的 Markdown 渲染檢視
- **Wiki** — 逐份文件 AI 摘要、概念萃取、跨文件知識合成
- **概念關聯圖** — D3.js force-directed 互動圖，視覺化 Wiki 概念與文件的引用關係
- **Lint** — AI 筆記品質健康檢查，含嚴重度評分與一鍵修正
- **RWD** — 完全響應式；手機版（≤768px）漢堡式側邊欄滑入

---

## 快速開始

### 方式 A：Docker（推薦）

```bash
git clone https://github.com/Lewsiafat/MindVault.git
cd MindVault
cp .env.example .env
# 編輯 .env，填入你的 GEMINI_API_KEY
docker compose up
```

開啟 http://localhost:8000/mind-vault/

### 方式 B：手動安裝

**前置需求：** Python 3.11+、Node.js 20+、[uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/Lewsiafat/MindVault.git
cd MindVault

# 安裝相依套件
uv sync
cd frontend && npm install && npm run build && cd ..

# 設定環境變數
cp .env.example .env
# 編輯 .env，填入你的 GEMINI_API_KEY

# 啟動
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

開啟 http://localhost:8000/mind-vault/

---

## 取得 Gemini API Key

1. 前往 [Google AI Studio](https://aistudio.google.com/)
2. 點選 **Get API Key** → **Create API Key**
3. 將 key 填入 `.env` 檔案

免費方案（每天 1,500 次請求）對個人使用完全足夠。

---

## 新增你的內容

將 markdown 檔案放入 `data/` 資料夾：

```
data/
├── notes.md          # 主要筆記（解析為可瀏覽的條目）
├── articles/         # 長篇文章與閱讀材料
├── saves/            # 儲存的參考資料與連結
└── conversations/    # 對話記錄或日誌
```

放進去的 `.md` 檔案會自動出現在 MindVault 中。

---

## 技術棧

| 層級 | 技術 |
|------|------|
| 後端 | FastAPI + uvicorn（Python 3.13） |
| 前端 | Vue 3 + TypeScript + Vite |
| AI | Google Gemini 2.0 Flash（`google-genai` SDK） |
| 樣式 | 手寫 CSS（暗色主題） |
| 容器 | Docker + docker-compose |

---

## 專案結構

```
MindVault/
├── src/
│   ├── main.py          # FastAPI 應用 — 所有 API 端點
│   └── static/          # 已建構的前端（由 Vite 產生）
├── frontend/
│   └── src/
│       └── App.vue      # 單檔 Vue SPA（所有 view、CSS、邏輯）
├── data/                # 你的 markdown 檔案放這裡
│   ├── notes.md
│   ├── articles/
│   ├── saves/
│   ├── conversations/
│   └── cache/           # AI 快取（自動產生，gitignore）
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## 部署

### VPS + nginx

```nginx
location /mind-vault/ {
    proxy_pass http://127.0.0.1:8000/mind-vault/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### Systemd 服務

```ini
[Unit]
Description=MindVault
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/MindVault
ExecStart=/path/to/.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000
EnvironmentFile=/path/to/MindVault/.env
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 本地開發

```bash
# 後端（熱重載）
uv run uvicorn src.main:app --reload --port 8000

# 前端（另一個終端機）
cd frontend && npm run dev
```

---

## 授權

MIT
