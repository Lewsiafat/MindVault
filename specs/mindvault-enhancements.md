# MindVault Enhancements — 概念關聯圖、Wiki 連結、收藏功能

- **分支:** `feat/mindvault-enhancements`
- **日期:** 2026-04-15

## 描述

為 MindVault 新增三個功能：
1. **概念關聯圖** — D3.js 互動式節點圖，視覺化 Wiki 概念與文件間的引用關係
2. **Wiki 頁面內連結可點擊** — 攔截 wiki 頁面中的 markdown 連結，點擊後在 SPA 內導航到對應 wiki 頁面
3. **收藏 / 標記重要文章** — localStorage 收藏清單，Library 和 Wiki 頁面加 ⭐ 按鈕，Overview 顯示收藏區塊

## 任務清單

### 後端 (src/main.py)
- [ ] 新增 `GET /api/wiki/graph` 端點 — 解析所有 wiki 頁面引用關係，回傳 `{nodes: [...], edges: [...]}`
- [ ] nodes 包含：`id, label, type (summary|concept), slug`
- [ ] edges 包含：`source, target, label`

### 前端 (frontend/src/App.vue)

#### 概念關聯圖
- [ ] 新增 `graph` view（sidebar 加入「🗺 關聯圖」按鈕）
- [ ] 引入 D3.js via CDN（加到 index.html）
- [ ] 實作 force-directed graph：概念節點（💡 藍）、摘要節點（📝 灰）
- [ ] 節點 hover 顯示 tooltip（title + type）
- [ ] 節點點擊跳轉到對應 wiki 頁面
- [ ] 加入 zoom / pan 操作

#### Wiki 連結可點擊
- [ ] markdown 渲染後，攔截 wiki 頁面內的 `<a>` click 事件
- [ ] 匹配 `/mind-vault/wiki/...` 或 `[[slug]]` 格式，改為 SPA 內部導航
- [ ] 點擊後：`setView('wiki')` + 載入對應頁面

#### 收藏功能
- [ ] 新增 `favorites` ref（從 localStorage 讀取，key: `mv-favorites`）
- [ ] `toggleFavorite(slug)` — 加入/移除收藏並寫回 localStorage
- [ ] Library 每個文件卡片加 ⭐ 按鈕
- [ ] Wiki 頁面加 ⭐ 按鈕（頁面標題旁）
- [ ] Overview 新增「⭐ 我的收藏」區塊，列出收藏文件（可點擊開啟）
- [ ] 收藏按鈕樣式：已收藏 ⭐ 亮黃色，未收藏 ☆ 灰色

## 注意事項

- D3.js 用 CDN 引入（不走 npm，保持輕量）
- favorites 純 localStorage，不需要後端 API
- Wiki 連結攔截需在 `v-html` 渲染後（nextTick）才能 querySelector
