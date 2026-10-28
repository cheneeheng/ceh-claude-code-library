---
schema: decision-rule/v1
---

# Changelog sections

Every PR adds its own `CHANGELOG.md` entry, in the PR's own commit, under a section headed by the
date the PR is opened, `## YYYY-MM-DD`. PRs opened on the same day share that day's section, and a
new one goes at the top, below the intro. A section holds prose on what changed and why, a
`### Plugin versions` table of every plugin bumped (merged with any table already there), then
`### Added` / `### Changed` / `### Fixed`. In the same commit, `docs/PLUGIN_VERSIONS.md` gets the
new version and the section date on every bumped plugin's row.

Why: with no releases, the dated sections are how a change is announced and traced. Decided 2026-10-05. Source: CLAUDE.md (0ee2394).
