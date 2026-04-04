# 筆記

## ClawFactory

### Nanobot 設定備忘
- 最後設定階段需要**增加時區設定**
  - 記錄時間：2026-03-31

### Nanobot Dashboard 功能需求
- Dashboard 需要能**取用資料夾**，顯示目前可用的資料夾清單
  - 記錄時間：2026-03-31
- Dashboard 要可以**顯示 system prompt**（平常隱藏，需要時展開查看）
  - 記錄時間：2026-04-02
- 增加**即時聊天**功能
  - 記錄時間：2026-04-02
- 增加**寵物**（互動元素）
  - 記錄時間：2026-04-02
- 顯示**目前記憶**（memory 狀態）
  - 記錄時間：2026-04-02

### Nanobot 設定功能需求
- 可以設定**所在地**（例如：台灣台北）
  - 記錄時間：2026-04-02
- 可以設定**時區**
  - 記錄時間：2026-04-02

---

## Claude Code

### CLAUDE.md 推薦 permissions 設定
記錄時間：2026-04-04

```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(git add*)",
      "Bash(git commit*)",
      "Bash(uv run*)",
      "Bash(uv sync*)",
      "Bash(uv add*)",
      "Bash(npm run *)",
      "Bash(npm test*)",
      "Bash(npx *)",
      "Bash(pnpm *)",
      "Bash(python -m pytest*)",
      "Bash(ls*)",
      "Bash(cat*)",
      "Bash(find*)",
      "Bash(grep*)",
      "Edit"
    ],
    "deny": [
      "Bash(rm -rf /)*",
      "Bash(rm -rf ~)*",
      "Bash(git push --force*)",
      "Bash(git push -f*)",
      "Bash(sudo *)"
    ]
  }
}
```

放在專案根目錄的 `.claude/settings.json`。
- `defaultMode: acceptEdits` — 自動接受檔案編輯，不需每次確認
- allow 清單：git 操作、uv/npm/pnpm 套件管理、pytest、基本讀取指令
- deny 清單：防止 rm -rf、force push、sudo
