---
schema: decision-rule/v2
decided: 2026-09-30
source: "CLAUDE.md (6df04b8)"
---

# Version levels

Each plugin's version lives in its `plugin.json`, mirrored in `marketplace.json`, and both are
bumped in the same commit, at commit time, not during iterative edits. PATCH for content or
description updates, MINOR for a new skill or agent or a `dependencies` entry added or removed,
MAJOR when the plugin is renamed or removed.

Why: the per-plugin version is load-bearing for auto-update.
