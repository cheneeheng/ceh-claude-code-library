---
schema: plan/v2
generated_from: competitor-report-yaml.yaml
generated_note: "Do not edit. artifact.py renders this file from competitor-report-yaml.yaml: edit the YAML, then run artifact.py render."
title: The competitor report as a YAML format, competitor-report/v2
status: built
created: 2026-11-11
---

<!-- prettier-ignore-start -->

## Goal

The third format of Phase 6 of `product/plans/report-only-formats.yaml`: the per-competitor report
that `ceh-competitor-analysis:analyze-competitor` writes and
`ceh-competitor-analysis:compare-competitors` reads becomes a YAML format checked by a pydantic
model, because it is a handoff between two skills, which the user's instruction to make handoff
files deterministic and checkable covers. The skill's own completeness rule becomes a check:
every Partial or Gap component must be taken, built or skipped in "What we take". The tally and
the coverage legend are computed when the Markdown is rendered, so they cannot drift from the
rows. The flow that matters: the analysis writes `<slug>.yaml`, the hook checks it and renders
`<slug>.md` beside it, the HTML page is built from the YAML, and the comparison checks each report
and reads it by key.

## Scope

**In:**

- `competitor-report/v2`: a `.yaml` validated by `competitor-report-model.py`, with `<slug>.md`
  rendered beside it in the `competitor-report/v1` layout, written by `analyze-competitor`.
- `ceh-competitor-analysis` gains the render hook and the generated-Markdown guard, so a report
  is checked on every write.
- `analyze-competitor` step 8 writes the YAML and step 9 builds `<slug>.html` from it.
  `compare-competitors` step 1 checks each `v2` report with `artifact.py check` and reads it by
  key, and still reads a `v1` `.md` with no `.yaml` beside it. `analyze-competitor` converts a
  `v1` report to `v2` before amending it in place.
- Repo upkeep: copies registered in `docs/CROSS_REFERENCES.md`, hook fixtures in
  `tools/validate-plugins/checks/hooks.py`, the `ceh-competitor-analysis` README (the report
  path and a new Hooks section), the root `README.md` prerequisites naming the competitor
  report, `docs/ENVIRONMENT_VARIABLES.md` adding `ceh-competitor-analysis` to
  `CEH_ARTIFACT_CHECK` (with `competitor-report/v2` in its formats) and to
  `CEH_DISABLED_HOOKS`, `compatibility` lines on both skills naming uv,
  `decision-artifact-validation.md` and `decision-output-templates.md` listing
  `competitor-report/v2`, the changelog, the version bump in `plugin.json` and
  `.claude-plugin/marketplace.json`, and `docs/PLUGIN_VERSIONS.md`.
- Phase 6 of `product/plans/report-only-formats.yaml`: its `note` names this plan as the
  competitor report's, and the phase stays `unplanned` until the glossary, blog voice and
  repeat-mistake report are planned. The run state plan edits the same note, so whichever of the
  two builds second rebases and keeps both plans named.

**Out:**

- The comparison (`comparison.md`, `competitor-comparison/v1`).: `report-only-formats.yaml` lists it as report-only: a person reads it, and no skill reads it
  back.
- Bulk-moving existing `v1` reports to YAML.: `compare-competitors` still reads a `v1` report, and one is converted only when a second
  pass amends it, so untouched reports stay as written.
- The `competitor-analyst` agent's fact sheet.: It is returned to the calling skill in the conversation, never saved as a file.
- Generating the HTML page by script.: `ceh-ui-design:design-ui` fills `report-page.html` and runs its review pass, as today. Only
  its source changes from the Markdown to the YAML.

## Design

- **Keys** Each required unless marked optional, and no other key:

  - `schema`: `competitor-report/v2`. `competitor`: the name. `source`: the repo or product URL
    read. `analysed`: the date, `YYYY-MM-DD`.
  - `summary`: one line, what it is and its core idea. `verdict`: one line, its moat and what is
    worth taking.
  - `fields`: `read` (`shallow clone`, `web pages`, `local checkout` or `pasted material`, the
    four sources the skill's `compatibility` line allows), `author`, `version`, `version_from`,
    `license`, `size` (the counts), `size_command` (the command that measured them), and
    `missing` (optional, one line: sources or paths that could not be read, rendered in the
    Source row after the date).
  - `take`: `adopt_now`, each `idea`, `lands_in`, `why` and `covers`; `build`, each `idea`,
    `lands_in`, `effort` (`M` or `L`), `why` and `covers`; `skip`, each `idea`, `why_not` and
    `covers`. Each list may be `[]`. `covers` is a list, `[]` when the idea comes from no
    coverage row, of coverage component names the row takes, written as a block list so a name
    holding a comma stays whole. `notes` (optional): a `|` block rendered under `## 1.` before
    Adopt now.
  - `how_it_works`: a list of three to five one-line steps, rendered numbered.
  - `oh_wow`: a list, `[]` when none, each `what`, `one_line`, `how` and `evidence`.
  - `inventory`: `groups`, at least one, each `group`, `count` (an integer, 0 or more) and
    `items` (one line, `—` when the count is 0), largest count first, and `notes` (optional, a
    `|` block rendered under the table).
  - `coverage_notes` (optional): a `|` block rendered after the fixed legend, for a scope note
    that holds for this competitor only.
  - `extra_sections` (optional): a list, each `after` (1 to 5, the section it follows),
    `heading` and `body` (a `|` block of Markdown), for a section the user asked for, which
    `analyze-competitor` step 1 allows. Rendered `## <heading>` after that section, unnumbered,
    so the five numbered headings keep their numbers.
  - `coverage`: at least one group, each `group` (named in the competitor's own terms) and
    `rows`, at least one, each `component` (its name), `evidence` (its path or URL), `what`,
    `rating` (`Covered`, `Partial`, `Gap` or `N/A`) and `ours` (optional). The component cell
    renders `<component> (<evidence>)`, so `covers` matches the name alone.

  Cross-key checks: component names are unique across all coverage groups. `Covered` and
  `Partial` need `ours`, one line that contains at least one `ceh-<plugin>:<name>`,
  `ceh-<plugin>` or a path holding `/`, because a rating with no component of ours to name is a
  Gap. It may name several and add a note, as real reports do. `Gap` and `N/A` take no `ours`
  and render `—` in that cell, and a Gap's note goes in `what`. Every `Partial` or `Gap`
  component appears in the `covers` of some `take` row, and every `covers` name is a `Partial`
  or `Gap` component. Both halves must land together, so `competitor-report-schema.md` says to
  write `coverage` and `take` in one Write or MultiEdit. `inventory.groups` is sorted by
  `count`, largest first, and a `0` count has `items: —`. Every value is one line except the
  `notes`, `coverage_notes` and `body` blocks.
- **Rendering** `render(doc, source)` writes the `v1` layout of `competitor-report.template.md`, with
  `generated_from` and the do-not-edit `generated_note` in its frontmatter and the body in a
  prettier-ignore range, as the other formats do. Three parts come from code, not the YAML: a
  `take` row's `why` (or `why_not`) is followed by a `Covers` sentence when `covers` is not
  empty, each name in backticks: `` Covers `a`. ``, `` Covers `a` and `b`. ``, or
  `` Covers `a`, `b` and `c`. ``, the legend under section 5 is fixed text (the four ratings and "coverage is
  inferred from our skill names and descriptions, not tested"), and the tally line is counted
  from the rows, `**Tally (<N> components):** <n> covered, <n> partial, <n> gaps, <n> N/A.`
  Section 5's table header names the competitor, `<competitor> component`. An empty `oh_wow`
  renders `None found.` under its heading, and an empty Adopt now, Build or Skip list renders
  `None.` under its `###`.

  The HTML page keeps its fixed blocks. On it, an empty `oh_wow` shows `None found.` in place of
  the cards, and an empty board column shows `None`. The `notes` blocks and `extra_sections`
  stay in the Markdown only, because the template's layout is fixed and the skill forbids adding
  sections to it.
- **Quoting** `competitor-report-schema.md` gives the same Quoting rule as `workflow-spec-schema.md`:
  single-quote any value that starts with `*`, `{` or `[`, contains `: ` or ` #`, or holds a
  backslash, and inside a `{...}` flow mapping or `[...]` flow list any value holding `,`, `?`,
  `[`, `]`, `{` or `}`. Lists such as `covers` are shown as block lists in the template.
  A `size_command` such as `find . -name '*.md' | wc -l` holds a `*` and a quote, so it goes in
  double quotes or a `|` block, which the schema shows.
- **Files and paths** `analyze-competitor` writes `.agents_workspace/competitor-analysis/<slug>.yaml`, the hook
  renders `<slug>.md` beside it, and step 9 builds `<slug>.html` from the YAML, adding no claim
  the YAML lacks and rebuilt whenever the YAML changes. Step 8 runs `artifact.py check` after the
  last write, and `render` when the hook is off, and Done gains "the check exits 0". Without uv
  the reply says the report went unchecked and unrendered, and the HTML is still built from the
  YAML.

  **Amending a `v1` report.** Real reports record a second pass made in place, and a new
  `<slug>.yaml` would render straight over the `v1` `<slug>.md`. So before the first write that
  amends a `v1` slug, `analyze-competitor` converts it to `v2`: every `v1` row and paragraph is
  carried word for word into its key, a paragraph or section with no key of its own going into
  `notes`, `coverage_notes` or `extra_sections`. A fresh analysis of a slug that already has a
  report replaces it, and the reply says which file it replaced.

  `compare-competitors` step 1 reads every report in the folder: a stem with a `.yaml` is
  checked first with `artifact.py check` and read by key. On exit 1 it stops and reports the
  errors, because a comparison built on a broken report carries the error into every cell,
  unless the only error is a stale `.md`, when it runs `render` and goes on. On exit 2 or 3,
  without uv, or when the call is denied, it reads the YAML unchecked and says so. A `.md` with
  no `.yaml` beside it is a `v1` report only when it has `schema: competitor-report/v1` or opens
  with a `# Competitor analysis:` title, because most real `v1` reports have no `schema:` line
  and the folder also holds `comparison.md`, a `CLAUDE.md` and side-by-side notes. Any other
  `.md` is skipped.
- **Models and copies** `competitor-report-model.py` and `competitor-report.template.yaml` sit beside
  `competitor-report-schema.md` in `analyze-competitor` (canonical), which keeps
  `competitor-report.template.md` as the rendered layout. `compare-competitors` gets copies of
  all four and both skills get `scripts/artifact.py`. A new "Competitor report format" entry in
  `docs/CROSS_REFERENCES.md` registers the copies, and the two skills' `scripts/artifact.py`
  and the plugin root's three scripts are rows in the "Build plan format" entry.
- **Hooks in ceh-competitor-analysis** `artifact.py`, `artifact-render-hook.py` and `generated-md-guard.py` copied to
  `plugins/standalone/ceh-competitor-analysis/scripts/`, and a new `hooks/hooks.json` with the
  PreToolUse guard and PostToolUse render entries on `Edit|Write|MultiEdit`, the same file as
  `ceh-workflow-builder`'s. The hooks need `python3` and the check needs uv, which both skills'
  `compatibility` lines say. The plugin holds no other model, so its hook checks only
  competitor reports. The cost is about 85 ms per Edit or Write in sessions with the plugin
  enabled, carried over from the handoff plan and not measured here.
- **Versions and pull requests** One phase and one PR, because the writer, the reader and the hooks are all in
  `ceh-competitor-analysis`. It bumps MINOR, 1.1.13 to 1.2.0, because it gains hooks, as
  `ceh-workflow-builder` did for `workflow-spec/v2`.

## Phases

### Phase 1: The format, the hooks, the writer and the reader

- **Builds:** All of Scope In: `competitor-report-model.py`, `competitor-report.template.yaml` and a
  `competitor-report/v2` section in `competitor-report-schema.md` beside its `v1` text, with
  the Quoting rule, in `analyze-competitor` (canonical) and `compare-competitors` (copies, with
  `competitor-report.template.md`); `scripts/artifact.py` in both skills; `analyze-competitor`
  steps 7 to 9, its Done, its `v1` conversion and its Output, and `compare-competitors` step 1
  with its `v1` detection, per Design "Files and paths", and the empty states of step 9's page
  per Design "Rendering";
  both `compatibility` lines; the plugin's root scripts and `hooks/hooks.json`; the hook
  fixtures; the registry rows, docs, rule files, version and changelog; and the
  `report-only-formats.yaml` Phase 6 note.
- **Check:** With uv, a scratchpad `acme.yaml` with two coverage groups (one `Covered` row with `ours`, one
  `Partial` taken under `adopt_now`, one `Gap` under `skip`, one `N/A`), a `build` row with
  `effort: M` and `covers: []`, an empty `oh_wow` and a `0`-count inventory group last renders
  (exit 0) to Markdown whose headings match `competitor-report.template.md`, with
  `**Tally (4 components):** 1 covered, 1 partial, 1 gaps, 1 N/A.`, the fixed legend,
  `Covers` after the two taken rows' reasons, and `None found.` under section 3. The same file
  also carries `fields.missing`, a `Covered` row whose `ours` names two components with a note,
  a `notes` block under section 1, and one `extra_sections` entry with `after: 5`, which render
  in the Source row, the table, under `## 1.` and after section 5. Files with a `Gap` no `take`
  row covers, a `covers` naming the `Covered` row, a `Covered` row without `ours`, an `ours`
  naming no component, a `Gap` row with `ours`, an unsorted inventory, a duplicate component
  name, `effort: S` under `build`, two `how_it_works` steps, and an extra key each exit 1,
  naming the key or rule. The largest real `v1` report in
  `.agents_workspace/competitor-analysis/` with an extra section, hand-converted to a
  scratchpad YAML per Design "Files and paths", passes `artifact.py check` (exit 0), which shows
  the keys fit a real report. `git grep -F` finds `<slug>.yaml` in both `SKILL.md` files,
  `artifact.py check` in both, `from the YAML` and `before the first write that amends` in
  `analyze-competitor/SKILL.md`, `# Competitor analysis:` in `compare-competitors/SKILL.md`, and
  `one Write or MultiEdit` in both `competitor-report-schema.md` copies.
  `python tools/validate-plugins/validate.py`, whose fixtures render a good
  `competitor-report/v2` file and block a bad one through the `ceh-competitor-analysis` render
  hook, print "uv is not installed" without uv, stay silent on a plan YAML, and have its guard
  deny an edit to a generated `.md`, prints "OK: all plugin checks passed".
- **Status:** done, a scratchpad `acme.yaml` rendered (exit 0) with the five numbered headings,
  `**Tally (4 components):** 1 covered, 1 partial, 1 gaps, 1 N/A.`, the fixed legend, `Covers`
  after the two taken rows' reasons, `None found.` under section 3, `fields.missing` in the
  Source row, a two-component `ours` with a note, `notes` under `## 1.` and `## Memory system`
  after section 5; the ten bad copies each exited 1 naming their rule (`no take row covers`,
  `names no Partial or Gap`, `needs ours`, `names no ceh-`, `takes no ours`,
  `sorted by count`, `repeat`, `take.build.0.effort`, `how_it_works`, `tagline`); the real
  `openclaw.md` (306 lines, with a section 6), converted to a scratchpad YAML, passed
  `artifact.py check` and `render` (exit 0), its computed tally equal to the hand tally
  (79 components: 5, 31, 22, 21); every `git grep -F` named in the Check matched; `python
  tools/validate-plugins/validate.py` printed "OK: all plugin checks passed". Beyond Design, from the real reports: a table cell's bare `|` is escaped by the renderer, a
  name holding a backtick renders in a double-backtick code span, and several size commands are
  joined with `; `. See Open for the `evidence` of a converted `v1` row.

## Open

- Is a section the user asked for still honoured in `v2`?: Yes, through `extra_sections` and the `notes` blocks, because `analyze-competitor` step 1
  puts the user's request over the defaults and 3 of the 10 real reports have one. Raised by
  the review.
- Does a second pass on a `v1` report convert it to `v2` first?: Yes, on the first write that amends it, so the render cannot overwrite the first pass.
  Raised by the review.
- May a report have no "oh wow" moment?: Yes: `oh_wow` may be `[]` and renders `None found.`, because forcing a row invites a slogan,
  which the skill's rules forbid.
- How does a `covers` name match a coverage row?: Exactly, by the row's `component` text, which is why component names are unique. A looser
  match would let a typo pass the completeness check.
- What `evidence` does a converted `v1` coverage row get, when none of the 10 real `v1` reports
  records a path per row?: `evidence: not recorded in v1`, because `evidence` stays required for new reports, as step 6
  demands, and a converted row may not gain a claim the `v1` report lacks. Found while building.

## Record

- 2026-11-11 Planned: status ready
- 2026-11-11 Reviewed: Revise first, 4 blocking (no key for user-requested sections and section notes, a second pass on a v1 report has no path and the render overwrites it, the `ours` check is unsettled against multi-component cells, `read` rejects a local checkout or pasted material and nothing records missing sources), 10 advisory, all fixed as recommended, with notes and extra
  sections kept out of the HTML page because its layout is fixed. Both owner questions went
  under Open on their recommended answers.
- 2026-11-11 PR: #244 https://github.com/cheneeheng/ceh-claude-code-library/pull/244
- 2026-11-11 Built Phase 1: `python tools/validate-plugins/validate.py`, "OK: all plugin checks passed"
- 2026-11-11 Checked: 17 Built, 2 Extra, 0 Gap, 0 Deviation, 0 Failing. Extra: the renderer escapes a bare `|` in
  table cells and fences a name holding a backtick in a double-backtick span
  (`competitor-report-model.py:199`, `:209`), both needed to render the real `openclaw.md`.

<!-- prettier-ignore-end -->
