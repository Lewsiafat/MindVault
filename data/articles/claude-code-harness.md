# Claude Code Harness Engineering

> 來源：https://claude-code-harness-blog.vercel.app/
> 記錄日期：2026-04-01

## 概述

探討 Claude Code 如何從對話式 AI 轉變為自主工程代理（Autonomous Engineering Agent）的技術架構文件。涵蓋工具管理、代理協作、權限分層、鉤子擴展、狀態管理等核心系統設計。

---

## 九大核心子系統

| # | 系統 | 說明 |
|---|------|------|
| 1 | **Query Loop** | 主執行循環與串流工具處理 |
| 2 | **Tool System** | 工具定義、驗證與執行生命週期 |
| 3 | **Agent Orchestration** | 多代理協作與快取共享 |
| 4 | **Permission System** | 多層存取控制（含 ML 分類）|
| 5 | **Hook System** | 生命週期事件與擴展點 |
| 6 | **Context Management** | 多層合併與壓縮策略 |
| 7 | **Skills & Plugins** | MCP 協議整合 |
| 8 | **State Management** | Session 持久化與恢復 |
| 9 | **Task System** | 任務協調框架 |

---

## 11 章結構（由淺入深）

1. ChatBot → Agent 的演化
2. Tool 系統設計
3. 多代理協作
4. 權限架構
5. 生命週期 Hooks
6. Context 策略
7. 並發排程
8. Plugin 整合
9. 狀態持久化
10. 設計模式整合
11. 進階模式

---

## 核心主題

- **工具作為一等公民**：工具在系統設計中的核心地位
- **Leader/Worker 模式**：代理間的協作模式
- **多層權限控制**：Permission 的分層執行
- **Context 壓縮策略**：管理大型上下文的方法
- **並行執行協調**：多任務同時處理

---

*這份文件強調 LLM 轉向自主、有權限意識的代理系統的工程嚴謹性*
