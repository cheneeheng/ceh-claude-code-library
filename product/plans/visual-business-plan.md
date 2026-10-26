---
schema: plan/v1
title: Draw the business plan, render it as HTML, and teach design-ui the document archetype
status: ready
created: 2026-10-26
business_plan: none
---

## Goal

Carry the retro `product/retros/2026-10-25-90a119d8-business-plan-visuals.md` into the skills, so
the next business plan starts where the mcp-cassette one ended: diagrams beside the text, a
contents list, nested section numbers, and an HTML version rebuilt from the markdown by a generator
the plugin ships. `ceh-ui-design:design-ui` learns that a report or plan is a document, not a site,
and the Mermaid lessons that cost several render rounds land wherever a skill draws diagrams.

## Scope

**In:**

- The retro moves into `product/retros/`, because its fix lands in this repo.
- `ceh-ui-design:design-ui`: a Document archetype (one reading column, a contents rail, no hero,
  no primary action), contents depth h2 to h6 one indent per level, tables that wrap before they
  scroll (never `white-space: nowrap` on a sentence column, and `.badge` inside a table cell set to
  wrap), and a single-file theme install (keep `brand.css` its own file, inline it at build time).
- One shared "Mermaid source" block, the rules that hold wherever the diagram renders: chain
  subgraphs with `~~~` and `direction LR`, gantt `tickInterval`, `xychart-beta` height in front
  matter, validate with the Mermaid CLI and look at the rendered result. Canonical in `design-ui`,
  copied into the business-plan schema, `ceh-documentation`'s `docs-standard.md` and
  `ceh-codebase-explanation:document-architecture`, registered in `docs/CROSS_REFERENCES.md`. The
  page-only rules (`flowchart: { wrappingWidth: 200 }`, wait for `document.fonts.ready` before
  `mermaid.run()`) go in `design-ui` alone and in the business-plan page shell's code, because a
  Markdown file has no page to configure.
- `ceh-business-plan` format `business-plan/v2`: a linked contents list before §01, nested
  two-digit numbers on every heading below h2 (`### §04.01 Strategy`, `#### §12.01.01 Cap`),
  specialist subsections found by title so their number follows position, and a Diagrams section
  in the schema with the retro's default set, the rule that a diagram adds no claim, and "not
  stated" where a table summary meets silence in the plan. The schema's worked example moves to v2.
- `find-product-market-fit` draws the default diagrams and writes the contents list and numbers
  when it drafts v0, and keeps its own diagrams in step on each revision. A diagram belongs to the
  skill that owns the text beside it.
- `develop-business-plan` step 4 gains one pass after every specialist: renumber the headings
  below h2 and rewrite the `**Contents**` list, the one edit the router makes, so no specialist
  touches another's numbers.
- The generator moves into the plugin: `scripts/build-plan-html.cjs`, the page shell
  `assets/business-plan-page.html`, and a copy of Meridian's `brand.css` in `assets/`, registered as
  a duplicate. Run as `node ${CLAUDE_PLUGIN_ROOT}/scripts/build-plan-html.cjs <plan.md>`: it reads
  its assets from the plugin and writes `BUSINESS_PLAN.html` next to the plan. Heading ids use
  GitHub's slug, so the markdown's own anchor links work in the HTML. `develop-business-plan`
  rebuilds after every specialist, with a `compatibility` line naming Node 18+ and network access
  (npx fetches `marked`, Mermaid loads from a CDN). When Node is missing or the run fails, it says
  so and moves on, because the markdown is the source.
- `plugins/CLAUDE.md` names `ceh-business-plan`'s generator among the allowed script bundles and
  the generated HTML among the files outside the template rule. The plugin README row mentions the
  HTML.

**Out:**

- A generator for the markdown contents list: the author settled that a hand-kept list is fine
  (retro, "Settled after the session").
- A dark-theme HTML, or bundling Mermaid offline: the retro's own choices, kept as they were.
- Plan-specific badge words in the generator (`pass`, `fail, narrowed`, `Stage 1`) and the
  mcp-cassette product-name rewrite: bound to one plan.
- A validator rule for the numbering or the contents list, or a `node --check` step for `.cjs`
  scripts in `validate.py`: principle 7, no measured miss yet. The Phase 2 run is the generator's
  check.
- `ceh-competitor-analysis`: its skills forbid Mermaid on purpose.
- Migrating the mcp-cassette plan to v2: the schema's v1-to-v2 rule does it on its next revision.

## Design

- Plan format v2, because heading text changes for every specialist subsection. A v1 plan gets the
  contents list and numbers on its next revision, like the v1 `artifact:` line migration.
- Specialists match their subsection on the title after the number, so `§12.01 Premortem` stays
  found when another subsection is added above it.
- The generator drops the markdown contents list by its literal `**Contents**` line through the
  next `## ` heading, not by HTML comments, because the templates check forbids comments in a
  template.
- The HTML is not a versioned template: it is generated from the markdown, which stays the source.
- `brand.css` is copied into `ceh-business-plan`, not read from `ceh-ui-design`, because a user may
  install one plugin without the other (Shared-Standards Duplication Policy).
- The rebuild lives in `develop-business-plan` step 4, the one point every specialist returns
  through, so no specialist carries it.
- Staged PRs: 1 retro, plan and `ceh-ui-design`; 2 `ceh-business-plan`; 3 the Mermaid copies in
  `ceh-documentation` and `ceh-codebase-explanation`. Each PATCH-bumps its plugins.

## Phases

### Phase 1: retro, plan, design-ui (PR 1)

- **Builds:** the moved retro; this plan; the design-ui changes, including the lines the Document
  archetype contradicts today (the rail "is not an archetype", the ≤5-section top-bar rule, h3 only
  for long sections, tables that scroll in their own container); the canonical Mermaid block; the
  `docs/CROSS_REFERENCES.md` entry; version, catalog, changelog rows.
- **Check:** `python tools/validate-plugins/validate.py` green; a grep finds `| **Document**` and
  "h2 to h6" in `design-ui/SKILL.md`, and finds none of "add `h3` one indent down only for long
  sections", "scroll horizontally in their own container", "is not an archetype".
- **Status:** done

### Phase 2: ceh-business-plan (PR 2)

- **Builds:** schema, worked example and template v2; numbered headings in the five specialists;
  the draft and revise lines in `find-product-market-fit`; the Diagrams section with the Mermaid
  copy; the generator, page shell and `brand.css`; the renumber, contents and rebuild pass and
  `compatibility` in `develop-business-plan`; the `plugins/CLAUDE.md` lines; the README row.
- **Check:** convert a scratch copy of the mcp-cassette plan to v2 (drop its toc comments), run
  the generator on it, then compare the number of `^#{2,6} ` lines in the markdown, counted by
  `grep`, with the number of `<h2>` to `<h6>` and contents links in the HTML, and grep that the
  HTML holds no `**Contents**` list and every `href="#…"` in the body has a matching `id`. Look at
  the page in a browser. `validate.py` green.
- **Status:** todo

### Phase 3: Mermaid copies (PR 3)

- **Builds:** the Mermaid block in `docs-standard.md` and `document-architecture`, their rows in
  the cross-reference entry, version and changelog rows.
- **Check:** `validate.py` green, and the block text is identical in all four files by a diff of
  the extracted lines.
- **Status:** todo

## Open

Whether the HTML should also open in the reader's browser after each rebuild: assumed no, the
skill reports its path.

## Record

- 2026-10-26 Planned: status ready
- 2026-10-26 Reviewed: ready with fixes, 3 blocking (no owner for renumbering and the contents
  list, find-product-market-fit missing from Phase 2, Phase 1 check passed before any change), all
  fixed in this plan with the 10 advisory findings
- 2026-10-26 Built Phase 1: greps found 1 Document row, 1 "h2 to h6", 0 old lines; validate.py
  failed only on 20 hygiene hits in the git-ignored local `docs/starlight/node_modules/`
- 2026-10-26 PR: #158 https://github.com/cheneeheng/ceh-claude-code-library/pull/158
