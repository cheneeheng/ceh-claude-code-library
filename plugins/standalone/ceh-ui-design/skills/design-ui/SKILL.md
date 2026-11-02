---
name: design-ui
description: >-
  Load this skill when making any frontend visual design decision: page or app-shell layout,
  navigation, hierarchy and spacing, a theme or brand, or a restyle. Trigger on "design the UI",
  "lay out this page", "make it look professional", "polish this UI".
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Design the Frontend UI

Deliver a UI that is modern, intuitive, and coherent. Done when the review pass at the end of the
Rules passes.

## Procedure

Work in this order:

1. **Design pass** — answer the five questions below _before_ writing any markup.
2. **Theme** — install one of the bundled token-driven templates (_Theme layer_, end of this file).
   Never hand-roll colors, type, or spacing.
3. **Build** — apply the _Rules_ below, core rules then _Finishing recipes_, consulting the chosen
   theme's `brand-guide.html` and only the sections of `references/examples.md` that a rule names.
4. **Review pass** — run the checklist before calling the UI done.

Two failure modes produce almost all bad UI, and this file targets both:

- **Unexamined defaults** — everything centered, everything boxed, uniform spacing, no visual
  priority. The design pass and core rules force those decisions explicitly.
- **The primitive draft** — structurally correct but unfinished: default table styling, raw
  symbols for data, status as plain text, buttons floating in space. The finishing recipes close
  that gap on the first build, not after review.

### The design pass

Answer these five questions and state the answers (one line each) so the choices are reviewable:

1. **What kind of surface is this?** Data-dense tool, content/marketing page, focused single-task
   flow, metric overview, or a document read top to bottom (a plan, report, or spec). This
   classification drives every later choice.
2. **Which layout archetype fits?** (table below)
3. **What is the one primary action per view?** Everything else is visually subordinate. A
   document has none: the reader reads.
4. **Which theme template?** (Theme layer below)
5. **What do empty, loading, and error look like?** Designed now, not retrofitted.

The user asks for options ("show me a few directions", "I can't picture it"), the design pass leaves
question 2 or 4 with two answers that both fit, or a flow's behavior is the open question: read
`references/examples.md` § Variants board and build the board before the real UI.

## Rules

### Layout

#### Pick one archetype per surface

| Archetype          | Use for                                               | Structure                                                                            |
| ------------------ | ----------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **App shell**      | Data-dense tools, ≥6 nav destinations, daily-use apps | Fixed sidebar (nav) + scrollable content pane; topbar only for global search/account |
| **Top-nav**        | Content and marketing sites, ≤5 destinations          | Horizontal nav bar + full-width sections below                                       |
| **Focused flow**   | Auth, checkout, onboarding, wizards, single forms     | Single centered column, minimal or no nav, one action per step                       |
| **Dashboard grid** | Metric overviews, monitoring                          | App shell + card grid; cards sized by importance, not uniformly                      |
| **Document**       | Business plans, reports, specs read top to bottom     | One reading column + contents rail; no hero, no primary action, no calls to action   |

The surface kind (design-pass question 1) picks the archetype; the destination count only breaks a
tie between two that both fit. A plan or report is a Document even when it ships as a web page:
it is read, not sold or operated, so site furniture only gets between the reader and the text.

Do not mix archetypes on one surface. An app does not get a marketing hero; a login page does not
get a sidebar. An in-page contents rail (_Navigation_) is the Document's own navigation, and a long
page in another archetype may add one without becoming a second archetype.

#### Content width

- Prose: 65–75 characters per line (`max-width: 65ch`). Never let body text span a wide viewport.
- Forms: 480–640px column, labels above inputs. Full-width forms read as broken.
- Data tables: may use the full content pane — density is the point.
- Page content in an app shell: cap around 1200–1400px and left-align within the pane; do not
  stretch to fill a 4K monitor.
- A Document with diagrams: one column, capped around 1100px, holds the title, headings, prose, and
  diagram panels, all ending on the same right edge. This overrides the prose cap above. A narrower
  text column above 1100px panels was rejected on sight as sloppy, so keep the paragraphs short
  instead.

#### Alignment and spacing rhythm

- Pick one alignment axis and keep it: **left-align** text-heavy and app UIs. Center only focused
  flows and marketing heroes. Centered body text is the single most common generic-AI tell.
- Proximity encodes relationship: space **within** a group must be visibly smaller than space
  **between** groups. Section gaps run 2–4× element gaps. If all gaps are equal, the page has no
  structure regardless of how many boxes it has.
- Use only the theme's spacing tokens (4px grid). No off-scale values.
- One gutter width per page. Elements that are conceptually aligned must be pixel-aligned.

#### Responsive behavior

Decide the mobile form of the archetype up front: sidebar collapses to a drawer or bottom tab bar
(pick one, not both); top-nav collapses to a menu button; dashboard grids stack to one column in
card-importance order; tables wrap their cells first, and only a table whose wrapped cells still
cannot fit reflows to key-value cards or, last, scrolls inside its own container — never squash
columns (see _Humanized tables_).

### Hierarchy

- **One primary action per view.** Exactly one filled/primary button; everything else outline,
  ghost, or link. Two primary buttons means no decision was made.
- **Three visible levels max.** Encode importance with size + weight + color _together_
  (large/bold/ink → medium/medium/ink → small/regular/muted). More levels than three and the eye
  ranks nothing.
- **Max ~4 type sizes per view** from the theme scale. Needing a fifth means the hierarchy is
  wrong, not the scale.
- **Boxes are not structure.** Use whitespace and alignment first, a border rule second, a card
  last. A card groups a set of _peer_ items that need separation from other sets — it is not a
  default wrapper. **Never nest cards in cards.** If everything is in a box, nothing is grouped.

#### When a page title appears — and when it doesn't

- Show a title (`h1`) when the page has an identity beyond its nav label: an entity name
  ("Invoice #1042"), a scope ("Settings — Billing"), or content the user navigated into.
- Skip the standalone title when it would only repeat the active nav item with zero added
  information — in an app shell, the highlighted nav item already says "Dashboard"; a lone
  "Dashboard" `h1` under it is noise. Either add value (count, date range, status) or drop it and
  promote the content — in app shells, the eyebrow-above-panel header (_Finishing recipes_) is the
  usual replacement.
- Focused flows title the _task_, not the app: "Create your account", not "Signup Page".
- Standard header anatomy when a title exists: optional eyebrow (uppercase micro-label for
  category/context) → title → one-line description → header-level actions right-aligned on the same
  row. One `h1` per page, always.

### Navigation

- **Placement follows the archetype:** sidebar for app shells (vertical scan, scales past 5 items),
  top bar for content sites, **tabs** only for peer views of the _same_ object or section (they
  switch content in place, never navigate away), **breadcrumbs** only when hierarchy is ≥3 levels
  deep.
- **Order by frequency of use**, never alphabetically. The most-used destination sits first/top;
  Settings, account, and sign-out go last (sidebar bottom or top-bar far right).
- **Max 7 top-level items.** Beyond that, group under labeled sections (sidebar) or consolidate:
  past about seven, users scan the list instead of finding the item.
- **The active location must be visibly marked** — a filled/edged state on the current nav item
  (the theme's `.has-edge.is-active` exists for exactly this). A user should know where they are
  from the nav alone.
- Icons in nav are optional; if used, every item gets one (no partial icon rows) and each icon is
  paired with its text label. Icon-only nav requires an established, unambiguous icon set.

#### In-page contents

A long single document (report, spec, docs page) lists its own sections. Those links scroll, they
do not navigate, so the frequency-order and max-7 rules above do not apply.

- **Show it** when the page has ≥4 `h2` sections or runs past ~3 screens.
- **A Document gets a contents rail.** Its headings go below `h2`, and a top bar cannot carry
  nested levels.
- **On a Top-nav content page, the top bar comes first.** A page with ≤5 sections and no
  subheadings puts its section links in the top bar, and that is its whole navigation. More than
  that, or a top bar already full of site destinations, gets a rail. In an app shell the rail is
  the only option.
- **Rail placement:** sticky beside the content on wide screens, on the right when a sidebar
  already holds the left. On narrow screens it becomes a static list above the first section,
  never a horizontal scroller.
- **Document order, h2 to h6.** Link every heading from `h2` to `h6` with its heading text, each
  level indented one step further than its parent. Markdown renders all five levels, and a reader
  jumps to a subsection as often as to a chapter.
- **Mark the section in view** with `.has-edge.is-active` plus `aria-current="location"`, driven by
  an `IntersectionObserver` on the sections. The URL cannot say where the reader is.
- **Offset jumps:** with any sticky header, set `scroll-padding-top` to its height so a jumped-to
  heading never lands under it.

### Color and depth

- **Neutral-dominant:** roughly 90% of any view is surface + ink + border tokens. Brand color is
  reserved for the primary action, active/selected states, and focus — that scarcity is what makes
  it read as "the important thing".
- **Semantic colors carry meaning only.** Success/warning/danger appear when something _is_
  successful, at risk, or destructive — never as decoration or variety.
- **One depth language.** The templates each pick it (Meridian: soft shadows; Tidewater: borders).
  Do not add both a border and a shadow and a background tint to the same element.
- **Layer the page with the surface ladder.** The three background tokens are a depth ladder, not
  interchangeable fills: page chrome (topbar, sidebar) sits on `--bg` and recedes; command
  surfaces (docks, framed panels) sit on `--surface`; interactive, clickable cards step up to
  `--surface-2` so the brightest things on screen are the ones that open. When chrome, toolbar,
  and content all share one background they blend into a single slab.
- Data-viz uses the `--data-*` ramp in order; do not invent chart colors.

### States: design the unhappy paths first

Every list, table, and detail view ships with all four states designed:

- **Empty:** not a blank pane — one line of what belongs here plus the primary action to create it.
  First-run empty states are the highest-leverage screen in an app; give them the header anatomy
  (title, one-liner, action).
- **Loading:** skeleton blocks that mirror the real layout for anything structural; a spinner only
  for sub-second, in-place waits (button click). Never a full-page spinner for a partial update.
- **Error:** what happened + what the user can do (retry, go back), in place, using the danger
  token. Never a raw error string as the whole view.
- **Overflow:** long names truncate with ellipsis + title/tooltip; tables cap visible rows and
  paginate; numbers use tabular figures (`.numeric`) so columns align.

### Density

Match density to usage frequency: tools someone uses all day run dense (32–36px table rows,
`--fs-50/-100` in tables, compact `--space-2/-3` padding); occasional consumer flows run airy
(generous `--space-8+` sections, larger type). Choose once per surface and apply consistently —
mixed density inside one view reads as broken.

### Finishing recipes

The core rules make a UI _correct_; these recipes make it _finished_. Apply them on the first
build. In page order: the command dock (global state), section headers, then how data is displayed
(tables, lifecycle colors, monograms, stat blocks, diagrams), then controls and motion. Worked markup
for tables and diagrams lives in `references/examples.md`.

A recipe that applies only when its component is present lives there too. Read only the section
named, when its condition holds:

- App-wide state exists (a current run, round, or selection) with one primary action on it:
  `references/examples.md` § Command dock.
- A domain state machine exists (draft → running → review → done): `references/examples.md` §
  Lifecycle stepper.
- Entity cards or rows need a visual identity: `references/examples.md` § Identity monogram.
- A field sits inside a card, or takes free text of unpredictable length: `references/examples.md` §
  Input as recessed well.

#### Section headers — eyebrow above the panel

- Label every list, table, and grid section with an uppercase eyebrow plus count (`PROJECTS · 2`)
  and a one-line muted caption explaining what the section is.
- The header sits on the page **above** the panel — never inside the card.
- Use the same vocabulary on every view (`PROJECTS`, `QUEUED ORDERS`, `ROUND HISTORY`) so the
  pages read as one system. This replaces the redundant page title.

#### Humanized tables

Default table styling is the strongest primitive tell. Every data table gets this treatment:

- **Frame it:** the table lives alone in a surface panel; its eyebrow header sits above the panel.
- **Cells read as words, not symbols:** "Round 2", not a `#` column with a bare integer; outcomes
  as color-coded words ("1 succeeded" in success, "2 failed" in danger).
- **Show only what happened:** a red zero is noise — omit zero counts, use an em dash when
  nothing ran.
- **Status is a colored pill** from the lifecycle palette, never plain text.
- Numbers use tabular figures; rows get a hover wash and pointer; rows that navigate are keyboard
  operable (`tabindex="0"` + Enter); the last row drops its separator.
- **Highlight the semantically current row, not the first row:** key the highlight to state
  ("the open one") so it retires when the state closes. Idiom: a 2–3px brand edge on the leading
  side plus a faint brand wash, drawn with an inset shadow so column alignment does not shift.
- Any table containing form fields uses `table-layout: fixed` so content cannot renegotiate
  column widths.
- **Wrap before scrolling:** cells wrap (`overflow-wrap: anywhere`), so a wide table fits its
  column. Never set `white-space: nowrap` on a column that holds sentences, and set a `.badge` with
  long text inside a cell to `white-space: normal`, because the theme's badge does not wrap and one
  long label forces the whole table to scroll. Scroll the table's own container only when wrapped
  cells still cannot fit, as with a wide table on a phone.

#### Stat blocks

- Summary numbers are stats, not sentences: the value at stat size (`--fs-500`, tabular figures)
  over a tiny muted label, an eyebrow above the group.
- Semantic color on the value only when it carries state, and only when nonzero.
- A stat block that navigates is one quiet link — no underline; tint the eyebrow on hover.

#### Diagrams

Diagrams are Mermaid, each in a plain panel beside the text it illustrates. A diagram can render
without an error and still be unreadable:

- Chain subgraphs with invisible links (`A ~~~ B`) and give each `direction LR`, or Mermaid lays
  them out in an arbitrary order.
- In a `gantt` chart with `axisFormat %b %Y`, set `tickInterval 2month` or wider, or the axis
  labels overlap.
- Set a horizontal `xychart-beta`'s height under `config.xyChart.height` in the diagram's front
  matter, or a chart with few bars renders far too tall.
- Validate every diagram with the Mermaid CLI,
  `npx -p @mermaid-js/mermaid-cli mmdc -i <file>.md -o <out>.md`, then look at the rendered
  result, because overflowing labels and a diagram scaled down to unreadable text both pass the
  CLI.

On a page that renders Mermaid itself:

- Pass `flowchart: { wrappingWidth: 200 }` to `mermaid.initialize`. Mermaid 12 wraps node labels at
  120px, so flowcharts render as tall, narrow boxes; a larger value scales wide diagrams down until
  the text is too small to read.
- `await document.fonts.ready` before `mermaid.run()`, so labels are measured in the web font, not
  the fallback.
- Give every diagram the same fit rule, never a cutoff that treats some differently: fit its panel,
  do not grow past natural size, and do not draw labels below `--fs-50`. Past that, the panel scrolls
  on screen and the diagram scales to one page in print (worked markup in `references/examples.md`).
- Past about 9 nodes or 12 edges, split the diagram into an overview and a detail before fitting it,
  or use a table if the relationships are only pairs. A bigger diagram shrinks until it is unreadable.
- Measure each diagram's natural width against the column. Flowchart, sequence, and state labels are
  16px, so a diagram past the panel width divided by 11/16, about 1550px in a 1100px column, cannot
  fit readably. Break long labels with `<br/>`, then turn the flow top to bottom, then split it at a
  natural pause. Check after a split that no node or edge was lost. `xychart-beta` labels start at
  14px and `gantt` labels at 10px, so check those two by eye.
- Put the panel's scroller inside any `overflow: hidden` card, or the diagram clips with no scrollbar.

#### Micro-interactions

Exactly one small motion per interactive element, using the theme's motion tokens: the primary
action may lift with a deeper shadow or rotate its glyph on hover; affordances (the monogram `→`)
slide in on hover/focus; state changes transition color rather than snapping. Never animate more
than one property group per element, and never decorate static content with motion.

#### Motion

Motion explains a change: where an element came from, where it went, or that the app heard the
input. Motion that explains nothing is decoration, and it gets cut.

- **Pick the duration by distance and size**, from the theme's tokens only: `--dur-fast` for
  hover, press, and color changes; `--dur-base` for an element entering, expanding, or a menu
  opening; `--dur-slow` for an overlay, drawer, or route change. Nothing in product UI runs longer.
- **Pick the easing by direction.** Entering or settling uses `--ease-out`, so it starts fast and
  lands soft. Moving between two on-screen positions uses `--ease-standard`. An exit runs at the
  next shorter duration than its enter, because the user has already moved on.
- **Keep the layout still.** Content that appears pushes nothing that the user is reading or about
  to click: reserve its space or overlay it.
- **Show progress, not suspense.** A skeleton or `.spinner` after about 300 ms of waiting; no
  entrance animation on page load, no staggered list reveals, no looping motion outside a
  loading or live state (`.dot-live`).
- **Reduced motion covers JavaScript too.** The template's `prefers-reduced-motion` rule stops CSS
  transitions and animations only. Motion driven from script (the Web Animations API, a motion
  library, a scroll handler) checks `matchMedia('(prefers-reduced-motion: reduce)')` itself and
  swaps the movement for an instant change or a fade.

### Anti-patterns — reject on sight

- Gradient hero / glassmorphism on an app surface, or on every page of a content site.
- Emoji as icons or bullet decoration in product UI.
- Brand color as background wash for entire sections "to add visual interest".
- A state machine rendered as plain text when its stages are known.
- OS-default scrollbars inside a themed surface. Theme scrollbars app-wide: `scrollbar-width: thin`
  with a `--border-strong` thumb on transparent — the OS-default chunky scrollbar breaks any polished
  surface it appears on.

### Review pass

Before calling the UI done, verify:

1. **Squint test:** blur your mental view — does the primary action and the page's structure still
   read? If it's a uniform gray blur, hierarchy failed.
2. **Alignment audit:** every element sits on the grid; one gutter; no accidental center/left mix.
3. **Spacing audit:** within-group < between-group everywhere; only token values.
4. **One primary action** per view; active nav state visible; title rule applied.
5. **State coverage:** empty, loading, error, overflow all handled.
6. **Token compliance:** no hardcoded hex, shadows, or font sizes, and spacing only from
   `--space-*`. A px value is allowed for a fixed component dimension no token covers (a stepper
   node, a monogram tile, a content-column cap).
7. **Finish audit:** depth ladder distinct (chrome vs command surfaces vs clickable cards); table
   cells read as words with lifecycle colors consistent across every representation; section
   eyebrows share one vocabulary; global state and its action appear exactly once.
8. **Document audit:** the theme installed whole, per Install, with its fonts; a contents list where
   In-page contents calls for one; for a Mermaid page, `document.fonts.ready` awaited and every
   diagram measured. A `less-code` comment is no exemption: the theme is the shortcut, and a partial
   copy of it is the drift Install warns about.

### Theme layer

Colors, type, spacing values, and component styles come from a bundled template. Do not hand-roll
them — every value is a CSS custom property so the whole app re-themes from one file. Prefer this
bundled style over a generic component library (shadcn/ui, MUI, Mantine) for one coherent look.

#### Choose and install

| Template      | Feel                                                      | Type                                       | Palette                               |
| ------------- | --------------------------------------------------------- | ------------------------------------------ | ------------------------------------- |
| **Meridian**  | Restrained mainstream SaaS; soft elevation, calm neutrals | Inter · JetBrains Mono                     | Cool-gray, blue primary, amber accent |
| **Tidewater** | Editorial / boutique; flat, border-led depth              | Fraunces · Hanken Grotesk · JetBrains Mono | Cool mint ground, terracotta + teal   |

- **Choose:** let the user pick via `AskUserQuestion` (single-select) unless they already named one.
  With no human to answer, take Meridian, the neutral default, and say so. Both templates ship
  the same token names and component classes except Meridian's `--shadow-lg` and `--weight-heavy`,
  so the choice is look-and-feel — swap later by replacing one CSS file, and keep markup off those
  two tokens so it survives the swap. To preview, open
  `references/<name>/brand-guide.html` in a browser or send it with `SendUserFile`.
- **Install:** copy `references/<name>/brand.css` to the project's global stylesheet location
  (follow the project's existing convention) and load it **first**, before any app styles —
  `@import "./brand.css";` at the top of the entry CSS, or
  `<link rel="stylesheet" href="/brand.css">` for plain HTML. The file brings its own web fonts,
  reset, and bare-element styles, so unclassed markup already looks right.
- **Single-file output** (a generated report or plan that must stay one HTML file): still copy
  `brand.css` unchanged as its own file next to the generator, and have the build inline it into a
  `<style>` element. Never paste the theme into the page template by hand: a pasted copy drifts
  from the theme, and a later swap or update means editing the template instead of replacing one
  file.
- **Light/dark:** `data-theme="light"` or `"dark"` on `<html>` forces a theme; omit it to follow
  `prefers-color-scheme`.

#### Build UI against the contract

Use the tokens and classes below — never hardcode a hex, shadow, or font size, and take spacing
from `--space-*`. A px value is fine for a fixed component dimension no token covers. Anything the
template does not cover, build with `var(--token)` values so it re-themes with the rest.

##### Tokens (CSS custom properties)

- **Type:** `--font-display`, `--font-ui`, `--font-mono`; scale `--fs-50 … --fs-700`; `--lh-*`,
  `--tracking-*`, `--weight-light … --weight-bold` (Meridian adds `--weight-heavy`).
- **Spacing:** `--space-1 … --space-16` (4px grid).
- **Radius:** `--radius-sm|md|lg|full`.
- **Color:** surfaces `--bg`, `--surface`, `--surface-2`; ink `--fg`, `--fg-muted`, `--fg-subtle`;
  lines `--border`, `--border-strong`; brand `--secondary(-hi/-wash)`, `--accent(-hi/-wash)`;
  state `--success`, `--warning`, `--danger` (+ `-wash`); data ramp `--data-1 … --data-6`;
  `--on-text` for text on a brand fill.
- **Elevation:** `--shadow-sm`, `--shadow-md` (Meridian adds `--shadow-lg`, used for overlays only).
- **Motion:** `--ease-out`, `--ease-standard`, `--dur-fast|base|slow`.

##### Component classes

- **Surface:** `.card`.
- **Buttons:** `.btn` + `.btn-primary` (one per view), `.btn-outline`, `.btn-ghost`, `.btn-danger`,
  `.btn-sm`. Bare `<button>` is already styled.
- **Inputs:** `.input`, `.input-mono`, `.toggle` (checkbox switch). Bare `<input>`/`<select>`/`<textarea>`
  are already styled.
- **Indicators:** `.badge` (+ `.badge-accent`, `.badge-secondary`, `.badge-dashed`), `.dot`
  (+ `.dot-live`, `.dot-success`, `.dot-warning`, `.dot-danger`), `.spinner`,
  `.text-success|warning|danger`.
- **Data:** `.table`, `.bar-track` > `.bar-fill` (`.is-1 … .is-4` for data colors), `.legend-dot`.
- **Typography helpers:** `.eyebrow` (uppercase micro-label), `.lead`, `.muted`, `.subtle`, `.mono`,
  `.numeric` (tabular figures).
- **Signature — active-edge:** `.has-edge` marks a leading brand rule; add `.is-active` to flag the
  element the user has activated (switches the edge to the accent + wash). It means _state_, not
  decoration — only put it on something actually active.

Accessibility is built in: `:focus-visible` rings and `prefers-reduced-motion` are handled by the
template. Keep semantic HTML (`<button>`, `<nav>`, `<main>`) — see `ceh-web-frontend:make-ui-accessible`.

To restyle the whole app later: replace the project's `brand.css` with the other template's — the
shared token + class contract means markup does not change, provided it avoids Meridian's
`--shadow-lg` and `--weight-heavy`.
