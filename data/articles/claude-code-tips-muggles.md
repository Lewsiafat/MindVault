# 給麻瓜們的 10 個 Claude Code 應用技巧

> 記錄日期：2026-04-10

身為麻瓜，我們要的是結果。
所以我看 Claude Code，不是想把自己變成工程師。
而是想知道：
像我這種不會寫程式的人，到底能不能真的用它把事情做得更快、更好。

---

## 1. 難題不要用預設 effort 去碰

很多人會把所有問題都用同一種模式丟給 Claude。
但真正困難的題目，像是：
• 架構設計
• 複雜 debug
• 效能瓶頸
• 關鍵 tradeoff

最怕的不是它慢，
而是它太快給你一個「看起來合理」但其實會讓你多繞好幾圈的答案。

這種時候可以直接在 prompt 裡加上：
```
ultrathink
```

**什麼是 Ultrathink：**
這是一個你在 Claude Code 終端機中添加到提示詞裡的關鍵字，它會觸發最大思考預算——讓 Claude 在回應之前進行多達約 32,000 個 token 的內部推理。本質上就是「用盡全力思考這個問題」。

---

## 2. 小問題不要污染主 context

平常工作時，一定會冒出很多小問題：
• OAuth token refresh 怎麼運作
• 某個參數到底是什麼意思
• 某個 CLI option 差在哪

大部分人都直接在主對話裡問。
但這些「順手問一下」，最後都會慢慢把 session 弄肥。
問多了之後，context 越來越髒，效能也會慢慢掉。

這時候可以用：
```
/btw
```

它會用一個暫時的 overlay 回答你，不進對話歷史，也不污染主 context。

- 可在 Claude 工作時使用 — 即使 Claude 正在處理回應，你也可以執行 /btw，旁支問題會獨立運行，不會中斷主要任務。
- 無工具存取 — 旁支問題只能從已在對話中的內容回答，Claude 無法讀取檔案或執行指令。
- 低成本 — 旁支問題重複使用父對話的提示快取，所以額外花費極少。

---

## 3. 先看計畫，再讓它動手

很多人一開 Claude Code 就直接進 coding。
但其實有一個很好用的模式：
```
claude --permission-mode plan
```

這樣 Claude 會先讀 codebase，整理出 implementation plan，但不會直接改檔。

然後你還可以按 **Ctrl+G**，把那份 plan 直接打開到編輯器裡自己改。

你可以先補上：
• 不想走的方向
• 已知限制
• 必須遵守的規則
• 不能碰的架構

在事前修正思路，不是事後幫它收拾戰場。

---

## 4. 不要急著做功能，先讓它訪談你

很多功能最後會做歪，
不一定是模型不夠強，
而是一開始需求就講得太模糊。

所以不要一開始就叫它直接做。你可以先叫它訪談你：

```
我想做一個 XXX
請用 AskUserQuestion tool 充分訪談我
問我技術實作、edge cases、tradeoffs
問到規格完整為止
最後寫成 SPEC.md
```

這很像先找一個資深工程師陪你把需求拆乾淨。
很多你以為自己想清楚的地方，其實一問下去才發現根本還沒。

---

## 5. 調查型工作，最好交給 subagent

如果你想查一件複雜的事情：
很多人會直接叫主 session 去翻。
但這樣最傷 context。
因為它一邊查，一邊把大量檔案內容塞進主工作區。

更好的做法是用 subagent。
讓它在旁邊自己讀檔、自己整理，最後只回傳摘要給你。
你主 context 保留的是結論，不是整個查案過程。

**提示：** 直接在 prompt 裡說「請用一個 subagent 去查 XXX，只回傳摘要給我」，不需要額外設定。

---

## 6. context 滿了，不是只有 /clear

很多人 session 一肥就直接：
```
/clear
```
等於整段失憶。

比較好的方式是用 `/compact`，
但如果只是一般 compact，保留什麼還是 Claude 自己決定。

更好的寫法是：
```
/compact Focus on the API changes and the failing tests
```

也就是你直接指定：哪些要保留，哪些可以壓縮。
這種 targeted compact，比整段清空好太多。

---

## 7. worktree 的 env 問題，可以先解掉

如果你有在用 Git worktree，應該很常遇到一個問題：
新 worktree 建好了，結果不能跑，因為 .env 沒跟過去。

Claude Code 有個很實用的小功能：
```
.worktreeinclude
```

你只要在專案 root 放這個檔案，例如：
```
.env
.env.local
config/secrets.json
```

之後新 worktree 就會自動把這些檔案帶過去。
這種東西看起來小，但它在消滅的是那種最煩、最零碎、最浪費時間的問題。

---

## 8. 把好的習慣設成預設值

如果你常做的是比較重的工程任務，其實可以直接在 .zshrc 設：
```bash
export CLAUDE_CODE_EFFORT_LEVEL=high
```

這樣每次開 session，預設就是 high effort。

這件事的重點不是單次更強，而是你不用每次都記得切。
很多真正拉開差距的地方，都不是技巧本身有多神，而是你有沒有把它變成預設。

---

## 9. 一個寫，一個審，品質真的差很多

不要總是同一個 session 寫完，再自己 review 自己。

比較好的方式是：
• Session A 負責實作
• Session B 負責 review

Review 的那個 Claude，因為不是作者，比較容易看到：
• edge cases
• race conditions
• 跟既有 pattern 不一致的地方
• 作者自己合理化過頭的問題

這跟真人團隊做 code review 很像。它沒有第一個的偏見。

---

## 10. 複雜任務先讓雲端規劃，終端機繼續做事

很多人做大型重構或複雜任務時，都卡在同一件事：
讓 Claude 規劃，等它想完，才能繼續動。
終端機被鎖住、什麼都不能做，就這樣等著。

這時候可以用：
```
/ultraplan
```

**什麼是 Ultraplan：**
它會把規劃任務送到 Anthropic 雲端處理，用 Opus 4.6 進行最多 30 分鐘的深度分析。計畫在雲端生成，你的終端機完全保持空閒，可以繼續做其他事。

跟普通 Plan Mode 最大的差別，不是它更聰明，而是它把「思考」和「執行」徹底分開了。
你不是在等它想，而是它在旁邊想，你繼續做自己的事。

**前提條件：**
• 需要 Claude Code 網頁版帳號（Pro、Max、Team 或 Enterprise）
• 需要連接 GitHub repo

---

## 總結

Claude Code 最容易被低估的地方，不是它多會寫 code。
而是它其實在幫你建立一套更好的工作方式：

• 難題要先深想
• 小問題不要污染主線
• 先把 spec 問清楚
• 調查和實作要拆開
• context 管理要有意識
• writer 跟 reviewer 分開

同樣在用 Claude Code，有些人只是多一個打字員，有些人像多了一個工程團隊。

---

## 補充說明

**關於第 1 項 Ultrathink：**
Ultrathink 曾在 2026 年初被移除，後來在 v2.1.68（2026年3月）重新加回。
如果你加了 ultrathink 卻沒有感覺到任何差異，很可能是版本太舊。用這個指令先更新再試：
```
npm update -g @anthropic-ai/claude-code
```

**關於第 5 項 Subagent：**
如果你不知道怎麼叫出 subagent，最簡單的方式是直接在 prompt 裡說：
「請用一個 subagent 去查 XXX，只回傳摘要給我」
不需要額外設定。

**關於第 10 項 Ultraplan：**
Ultraplan 目前有兩個前提條件，缺一不可：
• 需要 Claude Code 網頁版帳號（Pro、Max、Team 或 Enterprise）
• 需要連接 GitHub repo
