---
schema: repeat-mistake/v1
date: 2026-10-22
other_file: none
---

# Repeat mistakes — 2026-10-22

| Mistake                                       | Evidence                                                                                                | Rung | Fix                                                                                        | Proof        | Status  |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ---- | ------------------------------------------------------------------------------------------ | ------------ | ------- |
| Wrote a new tool's code before any build plan | session de93dc4b `T:12` request, `T:136`-`T:157` writes, `T:164` "Why didnt you create the plan first?" | 5    | Rewrite `write-build-plan`'s description to fire on a build or create request with no plan | not provable | applied |

## Why this rung

- Wrote code before a plan: rungs 1 to 4 need a mechanical signal, and none exists. Whether a request is "a new app, tool, or feature" is a judgement, so no setting, lint or CI job can catch it. A hook that forces planning is ruled out by `docs/STRATEGY.md:27` ("Nothing routes, injects, or enforces the order") and by the user's rule to fix skill descriptions rather than enforce skills with a hook. A replay cannot prove it either, since skill triggering is a model judgement. A live session with the same prompt is the only test.

## Pending drafts

### Wrote code before a plan

In `plugins/standalone/ceh-build-planning/skills/write-build-plan/SKILL.md`, replace the `description`:

```yaml
description: >-
  Load this skill when deciding how to build an app or feature before writing code: one committed
  plan file with scope, design decisions, and phases that each end in a runnable check. Trigger on
  "plan this app", "plan the next feature", "how should we build this".
```

with (287 characters, under the 300 limit):

```yaml
description: >-
  Load this skill before the first code of a new app, tool, component, or feature that has no plan
  yet, even when the user only says build or create it: one committed plan file with scope, design
  decisions, and checked phases. Trigger on "create a new tool", "build me X", "plan this app".
```

The same commit carries the PATCH bump of `ceh-build-planning` in `plugin.json` and `marketplace.json`, the `docs/CATALOG.md` row if its wording changes, the `CHANGELOG.md` entry, the `docs/PLUGIN_VERSIONS.md` row, and a green `validate.py`.
