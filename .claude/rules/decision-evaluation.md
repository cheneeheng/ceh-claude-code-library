---
schema: decision-rule/v1
---

# Evaluation

Evals use Anthropic's own tools, nothing bespoke: `skill-creator:skill-creator` for one skill, with
its workspace in `.agents_workspace/skill-evals/<skill>/`, never under `plugins/`, and
`claude plugin eval` for a whole plugin. Eval only when asked. Do not run the archived
`ceh-evaluation` plugin.

Why: every run and judge grader is a real model call on the user's account. Decided 2026-10-01. Source: CLAUDE.md (b5fcb75).
