---
schema: plan/v1
title: design-ui gets a width rule, a fit rule, and worked markup for Mermaid pages
status: building
created: 2026-11-02
---

## Goal

An agent building a Document page with `ceh-ui-design:design-ui` gets one column width, one fit rule
for every Mermaid diagram, and markup it can copy, so it stops improvising a cutoff per page. The
flow that matters most: an agent renders a page with wide diagrams, and each one fits its panel at a
readable size or scrolls inside it, on any screen and on paper. The source is the width, skipped
rules, `classDef`, and fit-gap rows of `product/retros/2026-10-30-repeat-mistake.md`.

## Scope

**In:**

- A Content width bullet: one capped column for a Document with diagrams.
- A fit rule, a size budget, an order of fixes for too-wide diagrams, and a scroller rule, under "On
  a page that renders Mermaid itself".
- A "Mermaid diagrams in a column" section in `references/examples.md`: the panel HTML, CSS, JS, and
  page-CSS node colours, complete enough to copy.
- The list of what `examples.md` holds, at the top of Finishing recipes, gains diagrams.
- A Document audit item in the Review pass.
- `docs/CROSS_REFERENCES.md` lists the new bullets among the page-only rules.
- The retro's status updated in place, with its stale lines fixed and quotes of the private page
  described in words.

**Out:**

- The prose cap investigation: the user set it for after this lands, and the override is correct
  while the cap stands.
- Slimming `design-ui`: gets its own plan once this has landed, with no eval, per the user.
- Any change to the four shared Mermaid source rules. The new bullets are page-only, including the
  budget, which exists to stop fitting a diagram too big for a page. `document-architecture` keeps
  its own "about a dozen edges".
- The `ceh-business-plan` page shell: it is outside the retro, and its generator owns its own page.
- A validator or hook: nothing can see a page in a git-ignored folder, and this is the first
  measured miss.
- `validate.py`'s `hygiene` check scanning git-ignored files: a separate defect, reported to the user.
- Editing the current page: it is private and no longer uses Mermaid.

## Design

- **Test page:** the page the retro measured has since been redrawn as inline SVG and moved to a
  private workspace. The Mermaid version, 23 flowcharts with the first draft's fit, is at commit
  `7f99276` of this repo's `.agents_workspace` nested repo. Phase 1 tests a copy in the session
  scratchpad. Nothing from the test is committed.
- **Browser:** installed Chrome, headless, because it adds no dependency. Measurements are written
  to the DOM and read with `--dump-dom --virtual-time-budget=40000`. A window under 500px is clamped,
  so 400px is measured inside a 400px iframe, and the JSON reports `innerWidth`. Print is checked by
  looking at a `--print-to-pdf` file, because no flag measures print media.
- **Mermaid version:** the recipe pins `mermaid@12`, because `design-ui` and the business plan shell
  already describe 12. Phase 1 runs on 11, the page's version, and on 12.
- **Markup:** the retro's replacement CSS and JS, because inline `min-width` cannot be released by a
  print rule. Added after Phase 1: `.diagram { break-inside: avoid; }` and `max-height: 90vh` in
  print, because the tall diagrams otherwise split across pages and overlap the next section. Added
  after review: the panel HTML, `startOnLoad: false`, the failure state, and the rule hiding raw
  source, because the tested page needs them. `.diagram` and `.doc-column` are the page's own classes.
- **Label floor:** Phase 1 measured flowchart, sequence, and state labels at 16px, `xychart-beta` at
  14px, and `gantt` at 10px. The fit bullet names the 16px types and says to check the other two by
  eye. Computing a floor per type would add code for a case no page has yet.
- **Document audit:** it cites the skill's existing rules instead of the retro's "past four `h2`" and
  "inlined whole", because `SKILL.md` shows a contents list at 4 or more `h2` or about 3 screens, and
  Install allows a linked theme as well as an inlined one.
- **Placement:** the new `examples.md` section goes between "Identity monogram" and "Input as
  recessed well", because that file follows the skill's order and Diagrams sits between those two
  recipes in `SKILL.md`.
- **Version:** `ceh-ui-design` 1.0.8 to 1.0.9, PATCH, because this is a content update. It rides in
  the PR with a `## 2026-11-02` changelog section and a `docs/PLUGIN_VERSIONS.md` row.
- **Local gate:** `validate.py` is red in this checkout on 25 `hygiene` problems, all in git-ignored
  files (`docs/starlight/node_modules/`, an eval report). The local gate runs on a clean export of
  the staged index, and CI runs on a fresh clone.
- **Private material:** the committed files name no private repo and quote no private page, per the
  user's rule on private workspace documents. Numbers measured on the page stay, because they quote
  nothing.
- **Retro status:** the width, skipped-rules, `classDef`, and fit-gap rows become `applied` and their
  drafts leave Pending drafts, as `prevent-repeat-mistake` requires. The prose cap and slimming rows
  stay `awaiting approval` with their drafts, updated to what the user has since decided.

## Phases

### Phase 1: Prove the markup on the Mermaid page

- **Builds:** nothing committed. Scratchpad copies of the page at `7f99276` with the first-draft fit
  swapped for the replacement CSS and JS, a measuring script, a copy forced onto a `240px 1fr` grid to
  test `.doc-column`, and a small page with one `sequenceDiagram`, `stateDiagram-v2`, `gantt`, and
  `xychart-beta`.
- **Check:** headless Chrome dumps JSON showing: at 1760px, 23 of 23 diagrams rendered and the
  smallest rendered label at 11px or larger; at 400px, panels scroll while the document does not; at
  a 1000px window on the forced grid, the document does not scroll with `.doc-column` and does
  without it; the label floor of each diagram type; and `.node.ok` filled from the theme. Print is a
  manual check, because no flag measures print media: the PDF shows every diagram whole, with no
  overlap. The final Phase 2 markup is re-run the same way.
- **Status:** done. Headless Chrome on Mermaid 11 and 12: 23 of 23 rendered, smallest label 11px, no
  page scroll at 1760px, 1280px, and 400px. The forced grid scrolls only without `.doc-column`.

### Phase 2: Edit design-ui

- **Builds:** the Content width bullet, the Mermaid bullets, the Finishing recipes list, the Document
  audit item, the `examples.md` section, and the `docs/CROSS_REFERENCES.md` line.
- **Check:** `grep -l "one column, capped\|fit rule\|Document audit" SKILL.md` and
  `grep -c "^## Mermaid diagrams in a column" references/examples.md` under
  `plugins/standalone/ceh-ui-design/skills/design-ui/` print the file and `1`, and the page built
  from the `examples.md` blocks passes the Phase 1 measures.
- **Status:** done. The strings are found, and the page built from `examples.md` passes: 23 of 23,
  smallest label 11px, `.node.ok` filled `rgb(231, 246, 236)`, three diagrams past the floor scroll
  in their panels at 1760px on Mermaid 12. The two tallest print whole on one page.

### Phase 3: Record and land

- **Builds:** the version bump, changelog section, `docs/PLUGIN_VERSIONS.md` row, and retro update,
  per Design, then the PR through `ceh-git-workflow:pull-request`.
- **Check:** `python tools/validate-plugins/validate.py` passes on a clean export of the index and in
  CI, `grep -c "awaiting approval" product/retros/2026-10-30-repeat-mistake.md` prints `2`, and a
  `git grep -i` for the private repo and page names finds nothing.
- **Status:** todo

## Open

None

## Record

- 2026-11-02 Planned: status ready
- 2026-11-02 Reviewed: Revise first, 2 blocking (validate.py is red locally on git-ignored files; committing publishes a private repo name and page quotes)
- 2026-11-02 Design changed: was "Mermaid comes from the CDN the page already imports (`mermaid@11`)", now the recipe pins `mermaid@12` and Phase 1 runs both, because the review found the repo already describes 12
- 2026-11-02 Built Phase 1: headless Chrome measurements, 23 of 23 rendered, smallest label 11px, no page scroll at 1760px, 1280px, or 400px
- 2026-11-02 Design changed: was "the replacement CSS and JS in the retro, unchanged unless Phase 1 fails it", now print adds `break-inside: avoid` and `max-height: 90vh`, because Phase 1 printed the tall diagrams split and overlapping the next section
- 2026-11-02 Built Phase 2: page built from `references/examples.md` passes the Phase 1 measures, and the recipe also sets `deterministicIds` and the cluster and edge-label theme variables, as the tested page did
