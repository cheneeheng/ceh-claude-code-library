# Competitor report schema

The per-competitor report `analyze-competitor` saves to
`.agents_workspace/competitor-analysis/<slug>.yaml`, a `competitor-report/v2` file (see the last
section), with `<slug>.md` generated beside it in the `v1` layout of
`../assets/competitor-report.template.md`, relative to this file, and `<slug>.html` built from the
YAML. The sections below describe that layout, which a `v1` report holds by hand. The HTML page
shows the body, not the frontmatter.

## Frontmatter

- `competitor`: the competitor's name.
- `source`: the repo or product URL read.
- `analysed`: the analysis date.

## Header

- **Summary:** one sentence under the title: what it is and its core idea.
- **Verdict:** one or two sentences: its real moat and what is worth taking.
- **Field table:** Source is the URL, how it was read (`shallow clone` or `web pages`, and in `v2`
  also `local checkout` or `pasted material`), and the date. Author is who made it. Version is the version and where it came from. License is the
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

## competitor-report/v2: YAML with generated Markdown

A `competitor-report/v2` report is `.agents_workspace/competitor-analysis/<slug>.yaml`, a copy of
`../assets/competitor-report.template.yaml`, and the `.md` of the same stem is generated from it in
the `v1` layout above, beside it. The YAML is the source: agents read and edit it, and nobody edits
the Markdown, which opens with `generated_from: <file>.yaml` and a do-not-edit `generated_note`. A
`v1` `.md` with no `.yaml` beside it is still read as `v1`, and converted before anything amends
it. The format in code is `competitor-report-model.py` beside this file, and `scripts/artifact.py`
in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. A rule across sections, such as completeness,
reports `(top level)` and names the components in its message.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `competitor-report/v2`. `competitor`: the name. `source`: the repo or product URL
  read. `analysed`: the date, `YYYY-MM-DD`.
- `summary`: one line, what it is and its core idea. `verdict`: one line, its moat and what is
  worth taking.
- `fields`: `read` (`shallow clone`, `web pages`, `local checkout` or `pasted material`),
  `author`, `version`, `version_from`, `license`, `size` (the counts), `size_command` (the command
  that measured them, several joined with `; `), and `missing` (optional, one line: sources or
  paths that could not be read, rendered in the Source row after the date).
- `take`: `adopt_now`, each `idea`, `lands_in`, `why` and `covers`; `build`, each `idea`,
  `lands_in`, `effort` (`M` or `L`), `why` and `covers`; `skip`, each `idea`, `why_not` and
  `covers`. Each list may be `[]`, rendered `None.` under its `###`. `covers` is a list of the
  coverage component names the row takes, `[]` when the idea comes from no coverage row, written
  as a block list so a name holding a comma stays whole. The renderer adds
  ``Covers `a`, `b` and `c`.`` after the `why` or `why_not`, so neither repeats it. `notes`
  (optional): a `|` block rendered under `## 1.` before Adopt now.
- `how_it_works`: three to five one-line steps, rendered numbered.
- `oh_wow`: a list, `[]` when none, rendered `None found.`, each `what`, `one_line`, `how` and
  `evidence`.
- `inventory`: `groups`, at least one, each `group`, `count` (an integer, 0 or more) and `items`
  (one line, `—` when the count is 0), largest count first, and `notes` (optional, a `|` block
  rendered under the table).
- `coverage_notes` (optional): a `|` block rendered after the fixed legend, for a scope note that
  holds for this competitor only.
- `extra_sections` (optional): a list, each `after` (1 to 5, the section it follows), `heading`
  and `body` (a `|` block of Markdown), for a section the user asked for. Rendered
  `## <heading>` after that section, unnumbered, so the five numbered headings keep their numbers.
- `coverage`: at least one group, each `group` (named in the competitor's own terms) and `rows`,
  at least one, each `component` (its name), `evidence` (its path or URL), `what`, `rating`
  (`Covered`, `Partial`, `Gap` or `N/A`) and `ours` (optional). The component cell renders
  `<component> (<evidence>)`, so `covers` matches the name alone.

**Computed, not written.** The legend under section 5 is fixed text, and the tally line is counted
from the rows: `**Tally (<N> components):** <n> covered, <n> partial, <n> gaps, <n> N/A.`

**Across sections.** Component names are unique across all coverage groups. `Covered` and
`Partial` need `ours`, one line that contains at least one `ceh-<plugin>:<name>`, `ceh-<plugin>` or
a path holding `/`, because a rating with no component of ours to name is a Gap. It may name
several and add a note. `Gap` and `N/A` take no `ours` and render `—` in that cell, and their note
goes in `what`. Every `Partial` or `Gap` component appears in the `covers` of some `take` row, and
every `covers` name is a `Partial` or `Gap` component, matched exactly. So write `coverage` and
`take` in one Write or MultiEdit, never one at a time, or the check rejects the file in between.
`inventory.groups` is sorted by `count`, largest first. Every value is one line except the
`notes`, `coverage_notes` and `body` blocks.

**Converting a `v1` report.** Every `v1` row and paragraph is carried word for word into its key:
a paragraph or section with no key of its own goes into `notes`, `coverage_notes` or
`extra_sections`, a "Covers" sentence moves into `covers`, a note in a Gap or N/A row's Ours cell
moves into `what`, and a coverage row that never recorded its path gets
`evidence: not recorded in v1`. The `v1` legend and tally are dropped, because `v2` computes them.

**Quoting:** single-quote any value that starts with `*`, `{` or `[`, contains `: ` or ` #`, or
holds a backslash, such as `'C:\tools\kit'`. Inside a `{...}` flow mapping or `[...]` flow list,
also quote a value holding `,`, `?`, `[`, `]`, `{` or `}`, or YAML splits it or fails to parse it.
Lists such as `covers` are block lists in the template, which needs none of that. A
`size_command` such as `find . -name '*.md' | wc -l` holds a `*` and a quote, so write it in double
quotes, `"find . -name '*.md' | wc -l"`, or as a `|` block. Write `|` in a value as it is: the
renderer escapes it in table cells. Every value is strict, so quote a value such as `1.10` that
must stay text.
