---
schema: decision-rule/v1
---

# No bundles

Ship no plugin that installs other plugins only to group them. `docs/GETTING_STARTED.md` is the
install entry point: a small core once, then one plugin per lifecycle stage as the user reaches it.

Why: scenario bundles loaded whole stages the user had not reached and refused to let them disable any of it (`archive/README.md`). Decided 2026-10-10. Source: CLAUDE.md (5afc00c).
