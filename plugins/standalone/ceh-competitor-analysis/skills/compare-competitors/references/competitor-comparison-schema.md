# Competitor comparison schema

The comparison `compare-competitors` saves to `.agents_workspace/competitor-analysis/comparison.md`,
rendered to HTML beside it. A new file is a copy of `../assets/competitor-comparison.template.md`,
relative to this file. The `schema: competitor-comparison/v1` line stays as written. The HTML page
renders the body, not the frontmatter.

## Frontmatter

- `snapshot`: the date the comparison was taken.
- `competitors`: the slugs of the per-competitor reports compared.

## Sections

- **Title and detail line:** each competitor and ours, then a link to each per-competitor report
  and the snapshot date.
- **At a glance:** one column per competitor plus ours. The seven rows are fixed, and a dimension
  the comparison needs is added as a further row.
- **Inventory by capability:** one row per capability. `—` means there is no equivalent.
- **Scores:** 1 to 5 per capability, with the evidence in the cell (for example
  `4 — a.md Inventory`), or `?` where there is none. No total.
- **Where each one is strongest:** one row per repo, ours included, one line each.
- **Positioning in one line:** one or two sentences on how each one positions itself, ours
  included.
