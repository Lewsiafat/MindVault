# Claude Code 實戰指南：如何管理 Session 與善用百萬 Context

**來源：** Thariq（Claude Code 工程師）X 分享翻譯
**儲存日期：** 2026-04-17

---

## 背景

Thariq 在與使用者的交流中發現，Session 管理的「技術天花板」出乎意料地高。在 Claude Code 將 context window 更新為 **100 萬個 token** 之後，該如何精準控制 Context Window 變得更加重要。

---

## Context、Compact 與 Context Rot

- **Context window**：模型在生成回應時能「看到」的所有內容，包含 system prompt、對話記錄、tool calls 及輸出、讀取過的檔案
- **Context rot**：隨著 context 增加，模型效能隨之下降的現象。注意力被分散，較舊不相關的內容開始干擾當前任務
- **Compact**：當接近視窗上限時，將進行中任務總結成較短描述並在新 context 繼續工作

---

## 每個回合都是分支點

完成一項任務後，你有五種選擇：

| 選項 | 說明 |
|------|------|
| **Continue** | 在同一個 session 繼續發訊息 |
| **/rewind**（連按兩次 Esc） | 跳回上一條訊息，丟棄之後的內容重新 prompt |
| **/clear** | 開始全新 session，附帶提煉出的簡短說明 |
| **Compact** | 總結目前 session，在該總結基礎上繼續 |
| **Subagents** | 將下一階段委派給擁有乾淨 context 的 agent |

---

## 何時該開啟新 Session

- **原則**：開始一項新任務時，也開啟新 session
- **例外**：相關聯的任務仍需要部分 context（例如為剛實作的功能撰寫文件），可以繼續使用原 session，避免重新讀取檔案的時間與成本

---

## Rewind：最佳的修正方法

> 「如果要挑出一個代表良好 context 管理習慣的操作，那就是 rewind。」

**做法：** 連按兩下 Esc 鍵（或輸入 `/rewind`），跳回之前任何一條訊息並重新 prompt，之後的訊息會從 context 中丟棄。

**示範：**
- ❌ 差的做法：「那樣行不通，改試 X 方法。」
- ✅ 好的做法：rewind 到剛讀完檔案的時間點，然後重新 prompt：「不要使用 A 方法，foo 模組沒有提供該功能——直接使用 B 方法。」

**技巧：** 使用「從這裡總結（summarize from here）」讓 Claude 建立 handoff 訊息，就像未來失敗的 Claude 留給過去自己的備忘錄。

---

## Compact vs. 全新 Session

| | `/compact` | `/clear` |
|--|-----------|---------|
| **方式** | Claude 自動總結對話並替換歷史記錄 | 自己手寫重要內容後重新開始 |
| **特性** | 有損（lossy），相信 Claude 判斷重要性 | 無損，你完全掌控保留哪些 context |
| **優點** | 省力，Claude 可能更全面保留重要經驗 | 最終 context 完全由你決定 |
| **引導方式** | `/compact 將重點放在 auth 重構上，捨棄測試除錯的內容` | 自己寫：「正在重構 auth，限制是 X，重要檔案有 A、B，排除了 Y 方法」 |

---

## 什麼導致糟糕的 Compact？

**根本原因：當模型無法預測你的工作方向時。**

**示範：**
- 漫長的除錯 session 後觸發 autocompact
- 總結了調查過程
- 下一條訊息：「現在修復我們在 bar.ts 裡看到的另一個警告。」
- 問題：「那個警告」已從總結中被捨棄

**解決方法：** 有了 100 萬 context，可以主動使用 `/compact`，並附上接下來想做什麼的具體描述。

注意：Context rot 影響下，模型在 compact 時往往處於**智力最低迷的狀態**。

---

## Subagents：全新的 Context Window

**適用時機：** 事先知道某部分工作會產生大量但之後不再需要的中間輸出。

**心理準則：** 「我之後還會需要這個 tool output 嗎？還是我只需要結論？」

**使用範例：**
- 「啟動一個 subagent，根據以下 spec 檔案驗證這項工作的結果。」
- 「啟動一個 subagent 去閱讀另一個 codebase，總結它是如何實作 auth 流程的，然後你再以相同的方式自行實作。」
- 「啟動一個 subagent，根據我的 git 異動為這項功能撰寫文件。」

---

## 決策框架

```
Claude 結束一個回合
        ↓
   你要發新訊息
        ↓
  ┌─────────────────────────────────┐
  │ 這是全新任務？                   │ → /clear 開新 session
  │ 上一步方向錯了？                 │ → /rewind 重來
  │ Context 太長但任務相關？         │ → /compact（附說明）
  │ 下一步會產生大量中間輸出？       │ → Subagent
  │ 任務相關且 context 還可以？      │ → Continue
  └─────────────────────────────────┘
```

---

## 核心觀念

> 「我們期望隨著時間推移，Claude 能夠自行幫您處理好這些細節；但就目前而言，這是您可以主動引導 Claude 輸出的重要方法之一。」
