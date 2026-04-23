# Agent Skills — Addy Osmani

**來源：** https://github.com/addyosmani/agent-skills
**記錄日期：** 2026-04-23

---

## 是什麼

由 Google Chrome 工程師 Addy Osmani 製作的 AI coding agent 技能包。
把資深工程師的最佳實踐封裝成可重複使用的 skill modules，讓 AI agent 按照完整的軟體開發流程工作。

---

## 六大開發階段

| 階段 | 說明 |
|------|------|
| Define | 釐清需求 |
| Plan | 拆解工作 |
| Build | 實作功能 |
| Verify | 驗證正確性 |
| Review | 品質把關 |
| Ship | 安全部署 |

---

## 七個指令入口

| 指令 | 用途 |
|------|------|
| `/spec` | 定義需求（Spec before code）|
| `/plan` | 拆解任務（Small, atomic tasks）|
| `/build` | 實作功能（One slice at a time）|
| `/test` | 驗證功能（Tests are proof）|
| `/review` | 品質審查（Improve code health）|
| `/code-simplify` | 降低複雜度（Clarity over cleverness）|
| `/ship` | 部署上線（Faster is safer）|

---

## 20 個 Skills 清單

**Define 階段**
- `idea-refine` — 結構化思考模糊概念
- `spec-driven-development` — 撰寫完整 PRD

**Plan 階段**
- `planning-and-task-breakdown` — 把 spec 拆成可驗證的任務

**Build 階段**
- `incremental-implementation` — 垂直切片逐步實作
- `test-driven-development` — Red-Green-Refactor
- `context-engineering` — 提供 AI 最佳資訊
- `source-driven-development` — 以官方文件為依據
- `frontend-ui-engineering` — 元件架構與無障礙
- `api-and-interface-design` — Contract-first API 設計

**Verify 階段**
- `browser-testing-with-devtools` — 執行期驗證工具
- `debugging-and-error-recovery` — 五步驟排錯流程

**Review 階段**
- `code-review-and-quality` — 五軸程式碼評估
- `code-simplification` — Chesterton's Fence 原則
- `security-and-hardening` — OWASP Top 10 防護
- `performance-optimization` — Core Web Vitals

**Ship 階段**
- `git-workflow-and-versioning` — Trunk-based 開發
- `ci-cd-and-automation` — Shift Left 實踐
- `deprecation-and-migration` — Code as liability 思維
- `documentation-and-adrs` — 架構決策記錄（ADR）
- `shipping-and-launch` — 上線前檢查清單

---

## 三個專家 Persona

- `code-reviewer` — Staff Engineer 視角
- `test-engineer` — QA 專家
- `security-auditor` — 資安工程師

---

## 安裝方式

### Claude Code（推薦）
```bash
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@addy-agent-skills
```

### 其他平台
| 工具 | 方式 |
|------|------|
| Cursor | 複製 SKILL.md 到 `.cursor/rules/` |
| Gemini CLI | `gemini skills install https://github.com/addyosmani/agent-skills.git --path skills` |
| GitHub Copilot | 在 `.github/copilot-instructions.md` 引用 |

---

## 設計理念

- Actionable workflows，不是模糊指南
- Anti-rationalization tables（文件化藉口與反駁）
- Verification requirements（驗證是強制的，不是可選的）
- Token efficiency（漸進式揭露資訊）

參考書：《Software Engineering at Google》
關鍵概念：Hyrum's Law、Beyonce Rule、Chesterton's Fence
