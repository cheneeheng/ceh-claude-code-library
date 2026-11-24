# ceh-check-build-against-plan design notes

Maintainer detail moved out of the plugin README on 2026-11-24, when the README was rewritten for
the person installing the plugin. The site does not publish this file.

## How the hooks work

The artifact check runs `scripts/artifact.py render` on each write to a
`.agents_workspace/product/plan/*.yaml`. The guard denies a hand edit to a Markdown file whose
frontmatter says `generated_from:`.

Moved from the README Hooks intro on 2026-11-24: They act only on `plan/v2` plans, and are
the same hooks `ceh-build-plan` ships, so the check works with this plugin installed alone.
