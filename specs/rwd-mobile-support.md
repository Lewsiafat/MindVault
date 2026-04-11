# feat: RWD 手機版支援

- **分支:** `feat/rwd-mobile-support`
- **日期:** 2026-04-11

## 描述

為 MindVault 加入 RWD 手機版支援。原本 sidebar 固定 220px 且無任何 mobile breakpoint，手機上無法正常瀏覽。

## 任務清單

- [x] 新增 `sidebarOpen` ref + `toggleSidebar()` / `closeSidebar()` 函式
- [x] `setView()` 改版後自動關閉 sidebar
- [x] 新增手機 top bar（hamburger + logo + 主題切換）
- [x] Sidebar 改為 slide-in overlay（position: fixed + transform: translateX）
- [x] 新增 sidebar backdrop 遮罩，點擊關閉
- [x] Sidebar 內加入 ✕ 關閉按鈕
- [x] 手機版隱藏 sidebar 內的主題切換按鈕（改用 top bar 的）
- [x] Grid 在 768px 以下改為單欄（recent-docs, doc-grid, categories-grid）
- [x] stats-dashboard 改為 2 欄（手機）
- [x] 調整 main padding、page-title 字體大小
- [x] Build 通過
