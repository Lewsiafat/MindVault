# Lessons from Building Claude Code: How We Use Skills

**Author:** Thariq (@trq212) — Anthropic Engineer
**Date:** March 17, 2026
**Source:** https://x.com/trq212/status/2033949937936085378
**Saved:** 2026-03-25

---

Skills have become one of the most used extension points in Claude Code. They're flexible, easy to make, and simple to distribute. But this flexibility also makes it hard to know what works best. What type of skills are worth making? What's the secret to writing a good skill? When do you share them with others?

We've been using skills in Claude Code extensively at Anthropic with hundreds of them in active use. These are the lessons we've learned about using skills to accelerate our development.

---

## What are Skills?

A common misconception: Skills are **not** "just markdown files". They're folders that can include scripts, assets, data, etc. that the agent can discover, explore and manipulate. In Claude Code, skills also have a wide variety of configuration options including registering dynamic hooks.

---

## Types of Skills

### 1. Library & API Reference
Skills that explain how to correctly use a library, CLI, or SDK — including gotchas.
- `billing-lib` — edge cases and footguns for your internal billing library
- `internal-platform-cli` — every subcommand with examples
- `frontend-design` — make Claude better at your design system

### 2. Product Verification
Skills that test/verify code is working, often paired with playwright, tmux, etc.
- `signup-flow-driver` — headless browser through signup → email verify → onboarding
- `checkout-verifier` — drives checkout UI with Stripe test cards
- `tmux-cli-driver` — interactive CLI testing with TTY

### 3. Data Fetching & Analysis
Skills that connect to your data and monitoring stacks.
- `funnel-query` — event joins for signup → activation → paid
- `cohort-compare` — compare two cohorts' retention/conversion with stats
- `grafana` — datasource UIDs, cluster names, problem → dashboard lookup

### 4. Business Process & Team Automation
Skills that automate repetitive workflows. Save results in log files for consistency.
- `standup-post` — aggregates ticket tracker, GitHub activity, prior Slack → formatted standup
- `create-<ticket-system>-ticket` — enforces schema + post-creation workflow
- `weekly-recap` — merged PRs + closed tickets + deploys → formatted recap

### 5. Code Scaffolding & Templates
Skills that generate framework boilerplate.
- `new-<framework>-workflow` — scaffolds new service/workflow/handler with annotations
- `new-migration` — migration file template + gotchas
- `create-app` — new internal app with auth, logging, deploy config pre-wired

### 6. Code Quality & Review
Skills that enforce code quality and review code.
- `adversarial-review` — fresh-eyes subagent to critique → fix → iterate
- `code-style` — enforces code style Claude doesn't do well by default
- `testing-practices` — instructions on how to write tests and what to test

### 7. CI/CD & Deployment
Skills that help fetch, push, and deploy code.
- `babysit-pr` — monitors PR → retries flaky CI → resolves merge conflicts → auto-merge
- `deploy-<service>` — build → smoke test → gradual rollout → auto-rollback
- `cherry-pick-prod` — isolated worktree → cherry-pick → conflict resolution → PR

### 8. Runbooks
Skills that take a symptom, walk through investigation, produce a structured report.
- `<service>-debugging` — maps symptoms → tools → query patterns
- `oncall-runner` — fetches alert → checks usual suspects → formats finding
- `log-correlator` — pulls matching logs from every system given a request ID

### 9. Infrastructure Operations
Skills for routine maintenance with guardrails for destructive actions.
- `<resource>-orphans` — finds orphaned pods/volumes → Slack → soak period → cleanup
- `dependency-management` — your org's dependency approval workflow
- `cost-investigation` — "why did our storage/egress bill spike"

---

## Tips for Making Skills

**Don't State the Obvious**
Focus on information that pushes Claude out of its normal way of thinking. The `frontend-design` skill was built by iterating with customers to improve Claude's design taste — avoiding classic patterns like Inter font and purple gradients.

**Build a Gotchas Section**
The highest-signal content in any skill is the Gotchas section. Build it up from common failure points Claude runs into. Update it over time.

**Use the File System & Progressive Disclosure**
A skill is a folder, not just a markdown file. Use the entire file system as context engineering. Tell Claude what files are in your skill and it will read them at appropriate times. Split detailed function signatures into `references/api.md`, include templates in `assets/`, add folders of references, scripts, examples.

**Avoid Railroading Claude**
Give Claude the information it needs, but give it the flexibility to adapt to the situation. Don't be too prescriptive.

**Think through the Setup**
Store setup info in `config.json`. If the config is not set up, the agent asks the user for info. Use `AskUserQuestion` tool for structured multiple-choice setup.

**The Description Field Is For the Model**
Claude scans skill descriptions to decide "is there a skill for this request?" The description field is not a summary — it's a description of *when to trigger this skill*.

**Memory & Storing Data**
Store data in the skill directory: append-only text log, JSON files, or SQLite. Example: `standup-post` keeps `standups.log` so next time Claude can tell what's changed since yesterday. Use `${CLAUDE_PLUGIN_DATA}` for stable storage across upgrades.

**Store Scripts & Generate Code**
Giving Claude scripts and libraries lets it spend turns on *composition* rather than reconstructing boilerplate. Example: a data science skill with a library of fetch functions → Claude composes them on the fly for advanced analysis.

**On Demand Hooks**
Skills can include hooks activated only when the skill is called, lasting for the session duration:
- `/careful` — blocks `rm -rf`, `DROP TABLE`, force-push, `kubectl delete` via PreToolUse matcher
- `/freeze` — blocks any Edit/Write outside a specific directory (useful for debugging without accidentally "fixing" unrelated things)

---

## Distributing Skills

Two ways to share skills:
1. Check into your repo under `.claude/skills`
2. Make a plugin for an internal Claude Code Plugin marketplace

For smaller teams, checking into repos works well. As you scale, a marketplace lets teams pick which skills to install.

**Managing a Marketplace**
No centralized gating — skills gain traction organically. Upload to a sandbox folder in GitHub, share in Slack. Once a skill has traction, PR it into the marketplace. Curation is important — bad/redundant skills are easy to create.

**Composing Skills**
Reference other skills by name and Claude will invoke them if installed. Dependency management is not natively built in yet.

**Measuring Skills**
Use a PreToolUse hook to log skill usage. Find popular skills or ones that are undertriggering compared to expectations.

---

## Conclusion

The best way to understand skills is to get started, experiment, and see what works. Most skills began as a few lines and a single gotcha, and got better because people kept adding as Claude hit new edge cases.

---
*Saved from X (@trq212) + blocktempo.com mirror*
