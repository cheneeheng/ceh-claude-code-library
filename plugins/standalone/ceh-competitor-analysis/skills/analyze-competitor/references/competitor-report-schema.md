# Competitor report schema

The per-competitor report `analyze-competitor` saves to
`.agents_workspace/competitor-analysis/<slug>.md`, rendered to HTML beside it. A new report is a
copy of `../assets/competitor-report.template.md`, relative to this file. The
`schema: competitor-report/v1` line stays as written. The HTML page renders the body, not the
frontmatter.

## Frontmatter

- `competitor`: the competitor's name.
- `source`: the repo or product URL read.
- `analysed`: the analysis date.

## Header

- **Summary:** one sentence under the title: what it is and its core idea.
- **Verdict:** one or two sentences: its real moat and what is worth taking.
- **Field table:** Source is the URL, how it was read (`shallow clone` or `web pages`), and the
  date. Author is who made it. Version is the version and where it came from. License is the
  license. Size is the counts and the command that measured them.

## Sections

1. **What we take:** three tables. **Adopt now** holds effort-S ideas, **Build** holds effort M or
   L, and **Skip** holds ideas not worth copying, each with the reason. Lands in names the
   component of ours the idea goes into.
2. **How it works:** three to five steps, one line each, from the user's first action to the
   result.
3. **"Oh wow" moments:** one numbered row per moment: what it is, one line, how it works, and the
   evidence.
4. **Inventory:** one row per group. A repo lists skills, agents, hooks, scripts, commands, and
   configs. A product lists features, plans, and integrations. Largest group first, and a group
   with nothing gets a `0` row.
5. **Coverage in our work:** a legend for `Covered`, `Partial`, `Gap`, and `N/A`, stating that
   coverage is inferred from our skill names and descriptions, not tested. Then the tally, then
   one `###` table per component group, named in the competitor's own terms.
