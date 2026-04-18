# Harness Engineering for Coding Agent Users

記錄時間：2026-04-05
來源：https://martinfowler.com/articles/harness-engineering.html
作者摘要：Birgitta Böckeler

## 核心概念

**Agent = Model + Harness**

Agent 的最底層是 LLM（自迴歸模型，只會生成符合機率分佈的文字）。除了 LLM 以外的所有東西統稱為 **Harness**。

## Harness 的層次

- **基礎 Harness（Base Harness）**：Agent 內建的元件，如內建工具與系統提示詞。目前大多數 Coding Agent（例如 Claude Code）主要停留在這個層次。
- **使用者 Harness（User Harness）**：為了完成一整個系統，使用者自行建構的外層架構。這是一個新興領域，目前缺乏完整的工程體系或最佳實踐。

## 兩個核心元件

### Guides（指南）- 前饋（Feedforward）
使用者設法餵給 Coding Agent 的資料。

### Sensors（感測器）- 回饋（Feedback）
Coding Agent 根據自身運作加上外部監督所產生的資料。

在兩者之間，透過**控制流程**不斷將系統導向正確方向，這門學問就是 Harness Engineering。

## 資料來源分類

- **運算型（Computational）**：執行確定性程式所產生的標準結果（如 CLI 工具回傳值、Docker Log）。結果確定、不具隨機性。
- **推論型（Inferential）**：由 LLM 推論出的結果，不見得 100% 準確但能產出預期結果（如 CLAUDE.md、AGENTS.md）。

## 實例解析

**Computer Use（Claude Code）** = 標準的 Inferential Sensor
- 不是為了與競品比拚
- 用途：開發本機應用軟體時，驗證「按下某個滑鼠按鍵後是否出現指定畫面」
- 所獲取的測試結果，能大幅幫助程式碼正確持續開發

## 重要觀察

- 舊有的 Harness 會隨著新模型發布而消失（被內建到新模型中）
- 例如：當模型熟悉 gh 指令後，GitHub MCP 可能被淘汰
- Harness 架構隨模型進化不斷演進
- 快速掌握 Harness 的應用，能讓工程師職涯延續得更長久

## 作者心得

這並非軟體工程專屬的概念，而是未來會影響大家生活的核心技術。科技巨頭各有一套方法，但不輕易對外公開。
