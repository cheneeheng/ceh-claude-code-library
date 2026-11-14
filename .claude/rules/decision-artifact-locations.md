---
schema: decision-rule/v2
decided: 2026-11-14
source: "product/plans/consolidate-product-artifacts.yaml"
---

# Artifact locations

Every product artifact a skill saves or reads lives in `.agents_workspace/product/`: plans, vision,
strategy, architecture, evidence, fix records, retros, reviews, audits, and the business material
in `business/`. Workflow specs and runs go under `.agents_workspace/workflow/`, and the session
tools' files (decision log, handoffs, research notes, questionnaires, `CODEBASE_EXPLAINED.md`,
competitor analyses, orchestration-lab runs) at the top of `.agents_workspace/`. A reference to a
format with a YAML source names the `.yaml`, never its generated `.md`. A repo whose `CLAUDE.md`
names another location keeps it: this repo keeps its own `product/` until a plan moves it. Do not
git-ignore single product files.

Why: two product folders confuse a person reviewing them, and a reference from an artifact in one
folder to an artifact in the other breaks. A per-file git-ignore is forgotten and breaks when a
name changes.
