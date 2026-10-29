---
schema: decision-rule/v2
decided: 2026-10-23
source: 'conversation, `docs/STRATEGY.md` "Where files live"'
---

# Artifact locations

Commit a file in `product/` when another stage or session reads it (plans, fix records, retros whose
fix lands in the repo, `EVIDENCE.md`, `ARCHITECTURE.md`). Keep it in `.agents_workspace/` when only
its author reads it: a lifecycle skill's local output under `.agents_workspace/product/`, workflow
specs and runs under `.agents_workspace/workflow/`, and the session tools' files (decision log,
handoffs, research notes, questionnaires, `CODEBASE_EXPLAINED.md`, competitor analyses,
orchestration-lab runs) at the top of `.agents_workspace/`. Business material (the business plan,
investor deck, outreach notes) always stays in `.agents_workspace/product/business/`, even though
Build and Tell read the plan. Do not move everything to `.agents_workspace/`, and do not git-ignore
single `product/` files instead.

Why: business material is confidential, and readers work without it. Moving everything would cut the
audit trail off from fresh clones, cloud sessions, and PR review. A per-file git-ignore is forgotten
and breaks when a name changes.
