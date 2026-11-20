---
schema: decision-rule/v2
decided: 2026-11-20
source: "CLAUDE.md (6df04b8)"
paths:
  - "plugins/**"
  - ".claude-plugin/marketplace.json"
  - "docs/PLUGIN_VERSIONS.md"
---

# Version levels

Each plugin's version lives in its `plugin.json`, mirrored in `marketplace.json`, and both are
bumped in the same commit, at commit time, not during iterative edits. PATCH for content or
description updates, MINOR for a new skill or agent or a `dependencies` entry added or removed,
MAJOR when the plugin is renamed or removed, or one of its skills is renamed (decided 2026-11-17).

Why: the per-plugin version is load-bearing for auto-update, and a renamed skill breaks every
workflow, `CLAUDE.md` and prompt that names the old one.
