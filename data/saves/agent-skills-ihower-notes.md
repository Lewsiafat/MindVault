# Agent Skills 資料整理 — ihower's Notes

**來源：** https://ihower.tw/notes/agent-skills
**儲存日期：** 2026-04-16

---

## Agent Skills 可以指：

1. Claude Code 等 Coding Agent 提供的功能
2. Claude app 和 ChatGPT 提供的功能
3. Anthropic API 提供的一個 API 功能
4. 目前有一個標準規格簡單描述 skills markdown 文件格式和目錄結構

---

## 重要資源

- Claude Code Skills 入門中文介紹：https://kaochenlong.com/claude-code-skills
- Agent Skills 終極指南：https://mp.weixin.qq.com/s/jUylk813LYbKw0sLiIttTQ
- Claude Code Skills 官方文件：https://code.claude.com/docs/en/skills（Public repo: https://github.com/anthropics/skills）
- OpenAI Codex Skills：https://developers.openai.com/codex/skills
- 標準協議：https://agentskills.io/home
- Claude 製作 Skills 指南：https://claude.com/blog/complete-guide-to-building-skills-for-claude
- Claude API 文件：https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

---

## 演講：Don't Build Agents, Build Skills Instead

- 影片：https://www.youtube.com/watch?v=CEvIs9y1uog
- 摘要 blog：https://blog.aihao.tw/2026/02/24/dont-build-agents-build-skills/

---

## 課程：Agent Skills with Anthropic（Deeplearning.ai）

**日期：** 2026/1/29
**連結：** https://www.deeplearning.ai/short-courses/agent-skills-with-anthropic/

### 主要概念

- 從多個 specific single agents → 變成一個 general agent，有 bash + filesystem，按需載入 skills
- Skills 提供：domain expertise、procedural knowledge、repeatable workflow、new capabilities（透過 script 或 MCP servers）
- Skills 可移植性：Claude app、Claude Code、Claude Agent SDK、Claude API
- Skills 可組合性：多種 skills 結合
- 透過 **progressively disclosed** 保護 context window，只在需要時載入

### Tools vs MCP vs Skills vs Subagent

| 類型 | 比喻 | 特性 |
|------|------|------|
| MCP / Tools | 錘子 | 連結外部系統，持續佔用 context window |
| Skills | 如何用錘子做椅子的指南 | 按需載入，引導 agent 如何使用工具 |
| Subagent | 獨立工人 | 獨立上下文和工具，可平行執行 |

參考：https://claude.com/blog/skills-explained

### Custom Skills Best Practice

- skill name 建議用 **verb + -ing form** 開頭
- SKILL.md 建議 **500 lines 以內**，超過拆到 reference 檔案
- SKILL.md 內容包括：
  - Step-by-Step 指示
  - 輸入輸出格式
  - 舉例和 edge cases
  - Workflow
- 評估：Unit tests — 測試多個 queries 是否有正確載入 files 和 expected_behavior

### Claude Code 中的 Skills

- 放在 `.claude/skills/` 目錄
- Sub-agent 預設不會載入 skills，需在設定時手動指定 `skills:` preload

---

## 課程：Introduction to Agent Skills（Anthropic Academy）

https://anthropic.skilljar.com/introduction-to-agent-skills

- What are skills?
- Creating your first skill
- Configuration and multi-file skills
- Skills vs. other Claude Code features
- Sharing skills
- Troubleshooting skills

---

## 官方 Skills

- Claude 官方 Plugins（打包 skills + MCP）：
  - https://code.claude.com/docs/en/discover-plugins
  - https://github.com/anthropics/claude-plugins-official（寫程式類）
  - https://claude.com/plugins-for/cowork
  - https://github.com/anthropics/skills（文件類，Claude chat/cowork 內建）

---

## 第三方 Skills

- Tailwind UI Skills：https://www.ui-skills.com/
- Superpowers：https://github.com/obra/superpowers
- Context Engineering：https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering
- FinLab：https://github.com/koreal6803/finlab-claude-plugin
- MCP to Skill Converter：https://github.com/GBSOSS/-mcp-to-skill-converter
- PM Skills：https://github.com/bobchao/pm-skills-rfp-to-stories

---

## MCP vs Skills — 關鍵觀點

> Simon Willison（2025/10/16）：「自從我開始認真看待程式碼代理人後，我對 MCP 的興趣就逐漸減退了。幾乎所有我想用 MCP 達成的事情，其實都可以用 CLI 工具來處理。技能也有完全相同的優勢，只是現在我甚至不需要再實作新的 CLI 工具。」

> steipete（2025/10/14）：「依我看，大多數 MCP 都只是行銷部門用來打勾自豪的東西。幾乎所有 MCP 其實都應該只是 CLI。」

- 總結文：https://blog.aihao.tw/2026/03/12/post-mcp-era-skills-vs-mcp/
- Skills vs Dynamic MCP Loadouts：https://lucumr.pocoo.org/2025/12/13/skills-vs-mcp/（作者已把所有 MCP 移到 skills）

---

## 深入技術

- Anthropic 工程文章：https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Claude Code 逆向工程分析：https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/（用 tool call 做的）
- 通用載入器 openskills：https://github.com/numman-ali/openskills
- Claude Agent SDK Skills：https://platform.claude.com/docs/en/agent-sdk/skills

---

## Pro Tips

- 用 `uv` 做 portable Python：https://elite-ai-assisted-coding.dev/p/uv-for-portable-python-in-agent-skills
