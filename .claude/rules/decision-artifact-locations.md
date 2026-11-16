---
schema: decision-rule/v2
decided: 2026-11-14
source: ".agents_workspace/product/plans/consolidate-product-artifacts.yaml"
---

# Artifact locations

Every product artifact a skill saves or reads lives in `.agents_workspace/product/`: plans, vision,
strategy, architecture, evidence, fix records, retros, reviews, audits, and the business material
in `business/`. Reviews, audits and evals go one folder per kind, in `product/review/<kind>/`,
`product/audit/<kind>/` and `product/eval/<kind>/`. Workflow specs and runs go under
`.agents_workspace/workflow/`, experiments such as orchestration-lab runs under
`.agents_workspace/experiment/`, and the session tools' files (decision log, handoffs, research
notes, questionnaires, `CODEBASE_EXPLAINED.md`, competitor analyses) at the top of
`.agents_workspace/`, in the layout of the shared workspace `AGENTS.md`. A reference to a
format with a YAML source names the `.yaml`, never its generated `.md`. A repo whose `CLAUDE.md`
names another location keeps it. Do not git-ignore single product files.

Why: two product folders confuse a person reviewing them, and a reference from an artifact in one
folder to an artifact in the other breaks. A per-file git-ignore is forgotten and breaks when a
name changes.
