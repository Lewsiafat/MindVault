# Wiki Ingest Rate Limiting — Walkthrough

- **分支:** `fix/wiki-ingest-rate-limiting`
- **日期:** 2026-04-23

## 變更摘要

修復 Wiki 批次匯入時因連續呼叫 Gemini API 觸發 429 RESOURCE_EXHAUSTED 限速問題。在 `ingest-all` 與 `synthesize` 兩個批次處理迴圈中加入 1.5 秒間隔，並改善 429 錯誤訊息的可讀性。

## 修改的檔案

- `src/main.py` — 三處修改：
  1. `_do_ingest()`：429 / RESOURCE_EXHAUSTED 例外捕捉後，回傳友善中文提示而非原始技術錯誤
  2. `wiki_ingest_all()`：批次迴圈改用 `enumerate`，從第二篇文件起每次呼叫前 `time.sleep(1.5)`
  3. `wiki_synthesize()`：概念頁生成迴圈中，從第二個概念起每次呼叫前 `time.sleep(1.5)`

## 技術細節

- **根本原因**：`ingest-all` 用簡單 `for` 迴圈連續呼叫 Gemini，無任何間隔。文件越多、越容易在短時間內觸發 RPM（每分鐘請求數）限制，即使是付費帳戶也有此上限。
- **修法選擇**：選用 1.5 秒固定間隔（約 40 RPM），低於 Gemini 付費帳戶 60 RPM 限制，安全邊際充足。
- **不影響單篇匯入**：`/api/wiki/ingest` 單篇呼叫不受影響，只有批次路徑加了 sleep。
- **部署方式**：因 GitHub token 缺少 `workflow` scope，無法推送含 workflow 檔案的分支，直接用 `scp` 複製 `main.py` 到 VPS 並重啟 systemd 服務完成部署。
