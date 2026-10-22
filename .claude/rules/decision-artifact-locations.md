---
schema: decision-rule/v1
---

# Artifact locations

Commit a file in `product/` when another stage or session reads it (plans, fix records, retros whose
fix lands in the repo, `EVIDENCE.md`, `ARCHITECTURE.md`). Keep it in `.agents_workspace/` when only
its author reads it. Business material (the business plan, investor deck, outreach notes) always
stays in `.agents_workspace/business/`, even though Build and Tell read the plan. Do not move
everything to `.agents_workspace/`, and do not git-ignore single `product/` files instead.

Why: business material is confidential, and readers work without it. Moving everything would cut the
audit trail off from fresh clones, cloud sessions, and PR review. A per-file git-ignore is forgotten
and breaks when a name changes. Decided 2026-10-22. Source: conversation, `docs/STRATEGY.md` "Where
files live".
