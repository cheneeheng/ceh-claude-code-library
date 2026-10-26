---
date: 2026-10-25
session: 90a119d8-ce62-4267-b718-301793016cd9
subject: Visualizing the business plan, and an HTML version of it
files: product/business/BUSINESS_PLAN.md, BUSINESS_PLAN.html, BUSINESS_PLAN.template.html, brand.css, build_html.cjs
---

# Retro: a visual business plan, in markdown and HTML

The author asked for the business plan to be easier to read for a visual reader. The session
produced diagrams in the markdown, an HTML version in the Meridian theme, and a generator that
rebuilds the HTML. Most of what the author asked for is not specific to this plan: it belongs
in the skills that write business plans and design documents, so the next plan starts this way.

Written in `mcp-cassette` and moved here on 2026-10-26, where the changes land, per the build plan
`product/plans/visual-business-plan.md`.

## What the author asked for, in order

| #   | Request                                                                                                                                                                           | What was done                                                                                                                                                  |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Add visualizations to the plan, because it is text heavy. Keep the text as it is, because it is clear.                                                                            | 11 Mermaid diagrams and one capability table added next to the text each illustrates. The diff added lines and removed none.                                   |
| 2   | Make an HTML version to compare readability, in the Meridian theme. It is a business plan, not a site to impress visitors.                                                        | `BUSINESS_PLAN.html`: one reading column, a contents list, evidence tags as coloured labels, tables and diagrams in plain panels. No hero, no calls to action. |
| 3   | Avoid horizontal table scrolling in the HTML.                                                                                                                                     | Table cells wrap. No table scrolls at desktop width. The 7-column premortem table still scrolls below about 800px.                                             |
| 4   | Keep the generator (picked from the options offered).                                                                                                                             | `build_html.cjs` and `BUSINESS_PLAN.template.html` saved next to the plan. Run `node product/business/build_html.cjs` after every plan edit.                   |
| 5   | Why does the contents list stop at h3? List down to h6, each level indented one step, because markdown renders up to h6.                                                          | The HTML contents list covers h2 to h6.                                                                                                                        |
| 6   | Why is the CSS written into the template instead of copied from the skill? Keep it as a separate `brand.css` that the generator copies into the HTML, so the HTML stays one file. | `brand.css` copied unchanged from the skill. The generator copies it in at build time.                                                                         |
| 7   | Add a contents list to the markdown, just before the first chapter.                                                                                                               | Linked list added before §01. The HTML build leaves it out, because the HTML has its own contents list.                                                        |
| 8   | Number every subsection with nested two-digit numbers.                                                                                                                            | §04.01, §12.01, §12.01.01 to §12.01.03, §13.01.                                                                                                                |

## What the author's requests say about the skills

Each item below is a change to a skill, so the next document starts where this one ended.

### ceh-business-plan (the skills that draft and revise `BUSINESS_PLAN.md`)

- **Draw the plan, not only write it.** The author is a visual reader and found the validated
  plan "very text heavy". A drafted plan should ship with diagrams where the text describes a flow,
  a funnel, a split of hours or a timeline. This session's set is a usable default: the payoff
  chain, scope (what the product does and does not do), the core loop, a positioning quadrant,
  build stages, the market funnel, the channel funnel, an hours chart, and a milestone timeline
  with kill criteria marked.
- **Diagrams sit beside the text, never replace it.** The author kept every sentence. A diagram
  is a reading aid next to the paragraph it shows, with no new claims. A diagram that summarises a
  table (the capability table in §06) uses only facts already in the plan and says "not stated"
  where the plan is silent.
- **A contents list before the first chapter.** Linked, nested, in the markdown itself.
- **Nested two-digit section numbers on every heading**, such as §04.01 and §12.01.01, not just on
  the h2 chapters.
- **An HTML version is wanted for comparison.** Whether it replaces reading the markdown is still
  open (see "Still open").

### ceh-ui-design:design-ui

- **Add a "document" archetype.** The skill's archetypes (app shell, top-nav, focused flow,
  dashboard) all describe sites or apps. A business plan, report or spec is a document: one reading
  column, a contents list, no primary action, no hero. The author had to say "this is a business
  plan and not some online site", which the skill should already know.
- **Contents list depth: h2 to h6.** The skill lists h2 and adds h3 only for long sections. The
  author wants every heading level markdown renders, h2 to h6, each indented one step.
- **Tables wrap before they scroll.** The skill allows a table to scroll inside its own container.
  The author wants to avoid that wherever wrapping cells can fit the table. Never set
  `white-space: nowrap` on a column with sentences in it, which is what caused the scrolling here.
- **Theme install for a single-file output.** Keep `brand.css` as its own file copied from the
  skill, and inline it at build time, rather than pasting the theme into the template by hand. The
  skill's install step covers linked stylesheets only.

### Mermaid, wherever a skill draws diagrams (business plan, design-ui, documentation)

These cost several render-and-check rounds in this session:

- Mermaid 12 caps node labels at 120px, so flowcharts render as tall, narrow boxes. Set
  `flowchart: { wrappingWidth: 200 }`. A larger value makes wide diagrams scale down until the text
  is too small to read.
- Wait for `document.fonts.ready` before `mermaid.run()`, so labels are measured in the web font.
- Subgraphs lay out in an arbitrary order unless they are chained with invisible links (`~~~`) and
  given `direction LR`.
- In a gantt chart, `axisFormat %b %Y` labels overlap unless `tickInterval 2month` is set.
- A horizontal `xychart-beta` with few bars renders far too tall unless its height is set in the
  diagram's front matter.
- Validate every diagram with the Mermaid CLI before handing over, and look at the rendered page
  in a browser, because a diagram can render without errors and still be unreadable.

## Choices made without asking

- Light theme only in the HTML, for printing and a calm reading page. Meridian has a dark theme
  if wanted.
- Mermaid loads from a CDN (jsDelivr). Offline, each diagram shows its source text instead.
- The markdown's GitHub link anchors were written by hand and not checked on GitHub.

## Settled after the session

- **HTML is good, and the markdown stays** (the author, 2026-10-25). The markdown is the source:
  the HTML is generated from it, and both are kept. So the business plan skill should produce the
  HTML by default alongside the markdown, and the generator should move from this repo into the
  skill.
- **A hand-maintained markdown contents list is fine** (the author, 2026-10-25), because Claude
  models keep such a list in step with the headings reliably. No generator for it.

## Still open

- The skill changes above. The author will make them on 2026-10-26.
