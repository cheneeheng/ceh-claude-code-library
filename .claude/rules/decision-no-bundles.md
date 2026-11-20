---
schema: decision-rule/v2
decided: 2026-11-20
source: "CLAUDE.md (5afc00c)"
paths:
  - "plugins/**"
  - ".claude-plugin/**"
---

# No bundles

Ship no plugin that installs other plugins only to group them. `docs/GETTING_STARTED.md` is the
install entry point: a small core once, then one plugin per lifecycle stage as the user reaches it.

Why: scenario bundles loaded whole stages the user had not reached and refused to let them disable any of it (`archive/README.md`).
