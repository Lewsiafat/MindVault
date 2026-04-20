# feat: RWD 手機版支援 — Walkthrough

- **分支:** `feat/rwd-mobile-support`（已合併進 main，merge commit `59dde79`）
- **原始 commit:** `a8e05c3`（2026-04-11）
- **收尾日期:** 2026-04-20

## 變更摘要

為 MindVault 加入手機版 RWD。原本 sidebar 固定 220px、無任何 mobile breakpoint，手機上無法正常瀏覽。此次改為：手機版顯示 top bar（漢堡選單 + logo + 主題切換）、sidebar 改成 slide-in overlay + backdrop 遮罩、768px 以下所有 grid 改單欄。

## 修改的檔案

- `frontend/src/App.vue` — 主要實作：
  - `<script>`：新增 `sidebarOpen` ref、`toggleSidebar()` / `closeSidebar()`，`setView()` 末端呼叫 `closeSidebar()`
  - `<template>`：頂部加入 `.mobile-header`（sticky）與 `.sidebar-backdrop`，sidebar 本身加上 `sidebar--open` modifier 與 `.sidebar-close` ✕ 按鈕
  - `<style scoped>`：新增 `.mobile-header`（桌機 `display:none`）與 `@media (max-width: 768px)` 區塊，總計約 +65 行
- `src/static/**` — `npm run build` 產生的 dist 產物（隨 commit 一併更新）
- `specs/rwd-mobile-support.md` — 任務規格（所有項目已打勾）

## 技術細節

- **Breakpoint 選擇：** 768px 為單一斷點，不做 tablet 分層。`stats-dashboard` 保持 2 欄（手機上 4 欄太擠、1 欄太稀疏），其他 grid 一律 `1fr`
- **Sidebar 行為：** 用 `position: fixed` + `transform: translateX(-100%)` 實作 slide-in，搭配 `transition: transform 0.25s ease`。`sidebarOpen` 改為 true 時套 `sidebar--open` modifier 觸發位移
- **Backdrop 層級：** `.sidebar-backdrop` z-index 299、`.sidebar` z-index 300，點擊遮罩觸發 `closeSidebar()`
- **導航後自動收合：** `setView()` 尾端呼叫 `closeSidebar()`，避免使用者手機切換 view 後 sidebar 還蓋著內容
- **主題切換位置：** 手機版把 sidebar 裡的 `.theme-toggle` 隱藏，改在 mobile header 右側放 `.theme-toggle-mobile`，避免使用者得先開 sidebar 才能切換主題
- **桌機不受影響：** mobile header `display: none`、sidebar 維持原本的 static 布局，所有 mobile 樣式都鎖在 `@media (max-width: 768px)` 內
