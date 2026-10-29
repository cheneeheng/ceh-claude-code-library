---
schema: decision-rule/v2
decided: 2026-10-05
source: "CLAUDE.md (0ee2394)"
---

# No releases

This repo has no releases: no version tags, no GitHub releases, no release commits. If the user
asks for a release in any form ("cut a release", "ship it", "tag a release", the full ship
sequence, or `ceh-git-workflow:release`), do not start it. Reply with a warning that releases are
not intended or used in this repository, and stop.

Why: changes reach users through per-plugin version bumps and the dated `CHANGELOG.md` sections each PR adds.
