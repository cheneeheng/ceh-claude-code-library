---
schema: decision-rule/v2
decided: 2026-11-20
source: "CLAUDE.md (6df04b8)"
paths:
  - "plugins/**"
  - ".claude-plugin/**"
---

# Plugin boundaries

A stage holds plugins, a plugin is one use case, and a skill is one moment, per
`docs/VISION.md` "How the library is cut".

- A plugin is one use case: the moments a user reaches together, in one stage, for one kind of
  work. One that spans several stages splits.
- Skills trigger on moments, not topics: a verb ("I'm opening a PR"), not a noun ("PostgreSQL"),
  and each skill is cut to the repo-opinionated delta. A new skill passes the moment test in
  `docs/VISION.md`.
- Plugin names declare their scope (`ceh-python-service` vs `ceh-python-library`).
- Framework variants do not split into separate plugins when their skills trigger on disjoint
  file types.
- Every plugin lives in `plugins/standalone/`, one directory each, no stage subfolders.
- App-specific patterns are not standards: anything bound to one application's schema or design
  is removed rather than kept as a niche plugin.
- The Core plugins are orthogonal: they load alongside a stage plugin, never instead of one.
- Technique splits from tooling only when the content would be byte-identical across stacks.

Why: topic-named skills never auto-trigger or restate what the model knows, and splitting variants duplicates standards and reintroduces drift. Use case, stage and moment are one hierarchy, so the three words no longer compete as split axes (revised 2026-11-19).
