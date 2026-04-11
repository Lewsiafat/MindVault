# MindVault 🧠

AI 驅動的個人知識庫 — 透過簡潔的 Web 介面瀏覽筆記、文件與記憶，搭配 Gemini AI 摘要與分類功能。

**網址：** https://lewsi.ddns.net/mind-vault/

---

## 功能

- **概覽** — 統計儀表板（文件數、字數、筆記條目）+ 最近更新文件，可點擊開啟
- **文件庫** — 依資料夾分類的所有文件，含內嵌 Markdown 閱讀器與 AI 摘要
- **分類** — Gemini AI 自動分類所有筆記和文件
- **搜尋** — 跨所有筆記與文件的全文搜尋
- **原始筆記** — `notes.md` 的 Markdown 渲染檢視
- **Wiki** — 逐份文件 AI 摘要、概念萃取、跨文件知識合成
- **Lint** — AI 筆記品質健康檢查，含嚴重度評分與一鍵修正
- **RWD** — 完全響應式；手機版（≤768px）漢堡式側邊欄滑入

---

## 技術棧

| 層級 | 技術 |
|------|------|
| 後端 | FastAPI + uvicorn（Python 3.13） |
| 前端 | Vue 3 + TypeScript + Vite |
| AI | Google Gemini 2.0 Flash（`google-genai` SDK） |
| 部署 | GitHub Actions → rsync → VPS systemd |
| 反向代理 | nginx |

---

## 專案結構

```
MindVault/
├── src/
│   ├── main.py          # FastAPI 應用 — 所有 API 端點
│   ├── __init__.py
│   └── static/          # 已建構的前端（由 Vite 產生，已 commit）
├── frontend/
│   ├── src/
│   │   └── App.vue      # 單檔 Vue SPA（所有 view、CSS、邏輯）
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── data/                # 文件儲存（從 /workspace/group 同步）
│   ├── notes.md         # 主要筆記檔
│   ├── articles/        # 已儲存文章
│   ├── saves/           # 已儲存參考資料
│   └── conversations/   # 對話記錄
├── specs/               # 開發任務 walkthrough 文件
├── pyproject.toml       # Python 依賴（uv 管理）
└── .github/workflows/
    └── deploy.yml       # CI/CD 流程
```

---

## 資料同步

文件從 nano agent 的 `/workspace/group/` 同步：
- `notes.md` → `data/notes.md`
- `articles/*.md` → `data/articles/`
- `saves/*.md` → `data/saves/`
- `conversations/*.md` → `data/conversations/`

每天凌晨 2 點自動 cron 同步新檔案。

---

## 部署

推送至 `main` → GitHub Actions 建構前端 → rsync 至 VPS → 重啟 systemd 服務。

- **Port：** 10016
- **路徑：** `/srv/projects/mind-vault/`
- **日誌：** `journalctl -u mind-vault -f`

---

## 本地開發

```bash
uv sync && uv run uvicorn src.main:app --reload --port 10016
cd frontend && npm install && npm run dev
```
