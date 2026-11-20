---
schema: decision-rule/v2
decided: 2026-11-20
source: ".agents_workspace/research/20261120-102653-ddd1b3aa-fd5e-4598-89d8-eaafbbc98df7-instruction-file-loading.md"
---

# Localized rules

Write decisions and rules in `.claude/rules/`, never in a folder-level `CLAUDE.md`. One that
concerns one part of the tree takes `paths` frontmatter. A folder-level `CLAUDE.md` holds only
context an agent should know about that subtree, as `plugins/CLAUDE.md` does. A nuance of one
function goes in a code comment on that function. A rule that must hold right after compaction
stays unscoped.

Why: a folder-level `CLAUDE.md` and a `paths`-scoped rule load the same way, once on the first matching read and again on demand after compaction, so a second mechanism adds nothing.
