---
schema: decision-rule/v1
---

# Plugin boundaries

Plugins split on one axis: use case.

- Skills trigger on moments, not topics: a verb ("I'm opening a PR"), not a noun ("PostgreSQL"),
  and each skill is cut to the repo-opinionated delta.
- Plugin names declare their scope (`ceh-python-service` vs `ceh-python-library`).
- Framework variants do not split into separate plugins when their skills trigger on disjoint
  file types.
- Every plugin lives in `plugins/standalone/`, one directory each, no tier subfolders.
- App-specific patterns are not standards: anything bound to one application's schema or design
  is removed rather than kept as a niche plugin.
- The cross-cutting tier is orthogonal: it loads alongside a use-case plugin, never instead of one.
- Technique splits from tooling only when the content would be byte-identical across stacks.

Why: topic-named skills never auto-trigger or restate what the model knows, and splitting variants duplicates standards and reintroduces drift. Decided 2026-09-30. Source: CLAUDE.md (6df04b8).
