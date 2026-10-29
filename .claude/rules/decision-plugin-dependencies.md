---
schema: decision-rule/v2
decided: 2026-09-30
source: "CLAUDE.md (6df04b8)"
---

# Plugin dependencies

Declare `dependencies` in `plugin.json` only, never in the `marketplace.json` entry, as bare
strings with no version ranges. There is no optional dependency. A cross-plugin reference earns a
dependency only when it fires on every run of the skill: a conditional handoff stays prose, and
negative routing (`Not for tagging, use ceh-git-workflow:release`) never counts. A cross-cutting
plugin may depend only on other cross-cutting plugins. Where a dependency exists, the skill body
calls the target with `Invoke the Skill tool with skill="ceh-<plugin>:<skill>"`.

Why: dependencies install and enable automatically and transitively, so a needless one installs what the user steered away from.
