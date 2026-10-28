---
schema: decision-rule/v1
---

# Shared-standards duplication

When a foundational standard is needed by more than one use-case plugin, duplicate the delta into
each rather than extracting a shared base plugin. Register every duplicated block in
`docs/CROSS_REFERENCES.md`. Before editing any skill, check that file: if the section you are
changing appears there, edit the canonical file first, then mirror the change to every listed copy
in the same session. New duplication gets a new entry.

Why: each use-case plugin stays self-contained so a user loads exactly one per use case, and the registry contains the drift that costs. Decided 2026-09-30. Source: CLAUDE.md (6df04b8).
