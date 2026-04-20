# Welcome to MindVault

這是一份範例文章，示範 `articles/` 資料夾如何運作。

## 怎麼新增自己的內容

1. 在 `.env` 設定 `DATA_DIR` 指向你的筆記資料夾（預設 `./data`）。
2. 在 `DATA_DIR` 底下建立 `articles/`、`saves/`、`conversations/` 三個子資料夾（或其中幾個）。
3. 把你的 `*.md` 檔丟進對應的子資料夾。
4. 重新整理 MindVault 網頁，就能在 Library 看到它們。

## 三個子資料夾的差別

| 資料夾 | 定位 |
|---|---|
| `articles/` | 自己寫的、或從外部蒐集來的長篇文章 |
| `saves/` | 值得保存的參考資料、片段、短筆記 |
| `conversations/` | 匯出的 AI 對話或訪談逐字稿 |

這只是命名慣例，程式對三者一視同仁 —— 想改用途直接用就好。

## 下一步

- 讀 `docs/getting-started.md` 瞭解完整安裝流程。
- 讀 `docs/data-management.md` 學怎麼把筆記接到 git repo 做版控。
- 讀 `docs/ai-providers.md` 選擇適合你的 AI provider。
