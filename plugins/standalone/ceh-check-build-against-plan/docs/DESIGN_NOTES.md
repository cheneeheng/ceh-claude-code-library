# ceh-check-build-against-plan design notes

## How the hooks work

The artifact check runs `scripts/artifact.py render` on each write to a
`.agents_workspace/product/plan/*.yaml`. The guard denies a hand edit to a Markdown file whose
frontmatter says `generated_from:`.
