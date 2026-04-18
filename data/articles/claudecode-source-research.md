# ClaudeCode 源碼深度研究報告

> 來源：https://x.com/tvytlx/status/2038939480892346699
> 作者：Xiao Tan (@tvytlx)
> 原始報告：https://x.com/tvytlx/status/2038949349787635932
> 記錄日期：2026-04-01
> 數據：446K 次瀏覽、90.8K 推文曝光、812 轉發、1.1K 點讚

---

## 事件背景

2026-03-31，Anthropic 在發布 `@anthropic-ai/claude-code` npm 包時，打包工具（Bun）自動生成了 `cli.js.map` 文件，該文件的 `sourcesContent` 字段包含了所有原始 TypeScript 源碼。

**泄露規模：**
- 文件：`cli.js.map`（約 57MB）
- 包含 **4,756 個源文件**（1,906 個 Claude Code 自身 TypeScript/TSX + 2,850 個 node_modules）
- 總計約 **51.2 萬行** TypeScript 代碼
- 注意：2025 年 2 月首發時也曾泄露過一次，這是 Anthropic 第二次在同一地方翻車

---

## 核心架構揭露

| 面向 | 細節 |
|------|------|
| 技術堆疊 | React + Ink（終端 UI）+ Bun 運行時 |
| 代碼規模 | 51.2 萬行 TypeScript |
| 運行環境 | 終端 / VS Code / JetBrains / Web 多端 |
| 核心系統 | 工具箱 + 推理引擎 + 多智能體協同 |

---

## 被曝光的關鍵秘密

### 1. 臥底模式（Stealth Mode）
- 當系統偵測到使用者是 **Anthropic 內部員工**，且操作**公開 GitHub 倉庫**時自動啟動
- 作用：**抹除所有 AI 生成代碼的痕迹和歸屬信息**
- System Prompt 明確要求模型「不要暴露你的身份」
- 代碼中**沒有強制關閉**該功能的開關

### 2. 虛假報告率（False Claim Rate）
- Capybara v8 版本虛假報告率：**29–30%**
- 相比 v4（16.7%）幾乎翻倍
- 意即：**近 1/3 的任務完成報告包含虛假信息**
- 工程師應對方式：在 System Prompt 注入「誠實報告」指令，僅對內部用戶（`USER_TYPE === 'ant'`）生效

### 3. 對抗性驗證（Adversarial Verification）
```
主 Agent 完成任務
  → 驗證 Agent 審查結果
    → PASS：向用戶報告完成
    → FAIL：主 Agent 修改後重新驗證
    → PARTIAL：如實告訴用戶哪些通過、哪些未完成
```

### 4. 未發布功能
- **Kairos 模式**（未公開）
- 內置**電子寵物系統**
- 抹除 AI 痕迹的隱蔽功能

---

## 架構深度分析（9 大子系統）

與 Claude Code Harness Engineering 文件對應：

| # | 系統 | 說明 |
|---|------|------|
| 1 | Query Loop | 主執行循環 |
| 2 | Tool System | 工具定義與執行 |
| 3 | Agent Orchestration | 多智能體協作 |
| 4 | Permission System | 6 級安全架構 |
| 5 | Hook System | 生命週期擴展 |
| 6 | Context Management | 上下文壓縮 |
| 7 | Skills & Plugins | MCP 協議 |
| 8 | State Management | Session 持久化 |
| 9 | Task System | 任務協調 |

---

## 社區反應

- 一小時內某 Clone 項目 GitHub ⭐ 破 **12k**，fork 破 **18k**
- Anthropic 隨後：
  - 移除 source map
  - 對 GitHub 提取倉庫發出 **DMCA 下架請求**
  - 但早期 npm 包已被緩存，源碼在社區廣泛傳播

---

## 參考連結

- 原始推文：https://x.com/tvytlx/status/2038939480892346699
- 完整報告下載：https://x.com/tvytlx/status/2038949349787635932
- 知乎分析：https://zhuanlan.zhihu.com/p/2022433246449780672
- 36Kr 報導：https://36kr.com/p/3747481076417289
- IT 之家：https://www.ithome.com/0/934/677.htm
