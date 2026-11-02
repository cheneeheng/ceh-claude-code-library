# UI Design Examples

Worked markup for the `design-ui` finishing recipes, in the skill's order, plus the full rules of
each recipe that applies only when its component is present. `SKILL.md` names the section to read
and when, so read only that section. The core rules (Layout → Density) are fully stated in
`SKILL.md` and need no markup here. All snippets use the bundled theme contract (tokens + component
classes) and plain HTML — they translate 1:1 to Svelte or JSX.

## Variants board

When the user asks for options ("show me a few directions", "I can't picture it"), or the design
pass leaves question 2 or 4 with two answers that both fit, build a board before the real UI:

1. Write two to four throwaway static HTML files to `.agents_workspace/product/design-variants/<surface>/`,
   one per variant, plus an `index.html` that shows them side by side in labelled `<iframe>`s at
   the same width. Use the bundled theme tokens and real-looking content, never lorem ipsum.
2. Make each variant differ from the others on **one** design-pass answer (the archetype, the
   theme, or the density) and label it with that answer. Variants that differ on everything at once
   get feedback like "the second one", which maps to no decision.
3. Show the board's path and ask which to keep. On feedback, keep the chosen answer fixed and vary
   the next open one. Two or three rounds is the usual end.
4. Record the chosen answers in the design-pass list, then build the real UI from them. The board
   stays in `.agents_workspace/` and is never imported by the app.

The same board serves a logic prototype: when a flow's behavior is the open question (a multi-step
form, a drag interaction), make each variant a small self-contained HTML page with inline script
that behaves the way that option would. With no user to choose, pick by the Review pass checklist
and write the reason beside the chosen answer.

## Command dock

When app-wide state exists (a current run, round, or selection) with one primary action on it, do
not cram it into the topbar and do not repeat it per page. The topbar stays brand + nav on `--bg`
so the chrome recedes; the state gets a **dock**: a bordered, rounded card floating below the
chrome, width-aligned with the content column so its edges share the cards' gutter.

- **Three panels split by hairline vertical rules, each panel's content centered.** Centered
  blocks floating in open space read as accidental; centered inside delineated panels read as
  deliberate — the rules are what license the centering.
- **Left — identity:** eyebrow (`CURRENT ROUND`) → the state's name at display size (the dock's
  focal point), with metadata as quiet mono chips on the title line, not raw hyperlinks.
- **Center — the action:** the one primary action as an accent-filled pill with a one-line muted
  micro-caption beneath saying what it does ("runs the 2 queued orders"). The center always
  carries the state's _current_ call-to-action — a live progress line while running, the review
  action when finished — and collapses (rules included) when there is no action.
- **Right — outcome:** mirror the left's anatomy with an eyebrow + stat block for the last result;
  the whole panel is a quiet link to the detail/history view.
- Optionally crown the dock with a 2–3px accent rule across its top, echoing the primary button.
- Hide the dock entirely when there is no state and no history — a fresh install gets no empty band.
- **State lives once:** anything the dock shows disappears from individual views — no second
  primary button, no repeated status heading, no duplicate cost readout anywhere in the app.

```html
<section
  style="max-width: 1200px; margin: var(--space-4) auto; background: var(--surface);
                border: 1px solid var(--border); border-radius: var(--radius-lg);
                border-top: 3px solid var(--accent); box-shadow: var(--shadow-sm);
                display: flex; align-items: stretch;"
>
  <!-- left: identity -->
  <div
    style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: var(--space-2); padding: var(--space-4);"
  >
    <p class="eyebrow">Current round</p>
    <p
      style="font-family: var(--font-display); font-size: var(--fs-400); display: flex; align-items: center; gap: var(--space-3);"
    >
      Round 2
      <a
        class="mono"
        style="font-size: var(--fs-50); border: 1px solid var(--border); border-radius: var(--radius-full); padding: var(--space-1) var(--space-2); text-decoration: none;"
        href="#/round"
        >2 orders</a
      >
    </p>
    <!-- node-and-rail stepper goes here (see lifecycle stepper) -->
  </div>
  <!-- center: the action, with a micro-caption -->
  <div
    style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--space-2); border-inline: 1px solid var(--border); padding: var(--space-4);"
  >
    <button class="btn btn-primary" style="border-radius: var(--radius-full);">
      End turn
    </button>
    <p class="subtle" style="font-size: var(--fs-50);">
      runs the 2 queued orders
    </p>
  </div>
  <!-- right: outcome stat block, whole panel a quiet link -->
  <a
    href="#/history"
    style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: var(--space-2); padding: var(--space-4); text-decoration: none;"
  >
    <p class="eyebrow">Last round</p>
    <div style="display: flex; gap: var(--space-6);">
      <div style="text-align: center;">
        <p class="numeric text-success" style="font-size: var(--fs-500);">1</p>
        <p class="subtle mono" style="font-size: var(--fs-50);">succeeded</p>
      </div>
      <div style="text-align: center;">
        <p class="numeric" style="font-size: var(--fs-500);">$0.12</p>
        <p class="subtle mono" style="font-size: var(--fs-50);">est. cost</p>
      </div>
      <!-- a "failed" column appears only when nonzero — a red zero is noise -->
    </div>
  </a>
</section>
```

## Humanized table

**Bad** — the primitive draft: symbol headers, bare integers, plain-text status, red zero:

```html
<table class="table">
  <tr>
    <th>#</th>
    <th>Status</th>
    <th>OK</th>
    <th>Fail</th>
  </tr>
  <tr>
    <td>2</td>
    <td>done</td>
    <td>1</td>
    <td class="text-danger">0</td>
  </tr>
</table>
```

**Good** — eyebrow header above the panel, words, lifecycle pill, only what happened, semantic
current-row highlight:

```html
<p class="eyebrow">Round history · 2</p>
<p
  class="muted"
  style="font-size: var(--fs-75); margin-bottom: var(--space-3);"
>
  each round runs the orders queued when its turn ended
</p>
<section class="card" style="padding: 0;">
  <table class="table">
    <tr>
      <th>Round</th>
      <th>Status</th>
      <th>Outcome</th>
      <th class="numeric">Cost</th>
    </tr>
    <!-- current (non-done) row: leading edge + wash via inset shadow, keyed to state not position -->
    <tr
      tabindex="0"
      style="background: var(--secondary-wash); box-shadow: inset 3px 0 0 var(--secondary); cursor: pointer;"
    >
      <td>Round 3</td>
      <td><span class="badge badge-secondary">executing</span></td>
      <td class="muted">—</td>
      <td class="numeric">0.04</td>
    </tr>
    <tr tabindex="0" style="cursor: pointer;">
      <td>Round 2</td>
      <td>
        <span class="badge"><span class="dot dot-success"></span> done</span>
      </td>
      <td>
        <span class="text-success">1 succeeded</span> ·
        <span class="text-danger">2 failed</span>
      </td>
      <td class="numeric">0.12</td>
    </tr>
  </table>
</section>
```

## Lifecycle stepper

For any domain state machine (draft → running → review → done):

- Assign each stage one color **once** and use it in every representation — status badge, stepper
  node, history pill — so color alone identifies the stage anywhere in the app.
- Show progression as a **node-and-rail stepper**, not text: small nodes joined by a continuous
  rail, stage labels beneath.
- Past stages muted; the current node lit in its stage color with a soft halo, pulsing only while
  actively running; future stages ghosted. The rail fills through the current node so a transition
  visibly flows forward.

```html
<div
  role="img"
  aria-label="Status: executing"
  style="display: flex; align-items: center;"
>
  <!-- past -->
  <span
    style="width: 10px; height: 10px; border-radius: var(--radius-full); background: var(--fg-subtle);"
  ></span>
  <span
    style="width: var(--space-8); height: 2px; background: var(--secondary);"
  ></span>
  <!-- current: stage color + halo (add a pulse animation only while actively running) -->
  <span
    style="width: 10px; height: 10px; border-radius: var(--radius-full); background: var(--warning); box-shadow: 0 0 0 4px var(--warning-wash);"
  ></span>
  <span
    style="width: var(--space-8); height: 2px; background: var(--border);"
  ></span>
  <!-- future -->
  <span
    style="width: 10px; height: 10px; border-radius: var(--radius-full); background: var(--border);"
  ></span>
</div>
```

## Identity monogram

- Entity cards and rows lead with a small rounded monogram tile: the entity's initial on a wash
  tint picked from the `--data-*` ramp by a stable name hash, with a matching hairline border —
  every entity keeps its color everywhere it appears.
- On hover or keyboard focus, slide in a `→` at the card's corner so "this opens" is unmistakable.

```html
<span
  aria-hidden="true"
  style="display: inline-grid; place-items: center; width: 28px; height: 28px;
      border-radius: var(--radius-md); background: color-mix(in srgb, var(--data-3) 14%, transparent);
      border: 1px solid var(--data-3); color: var(--data-3); font-weight: var(--weight-bold);
      font-size: var(--fs-75);"
  >A</span
>
```

## Mermaid diagrams in a column

Each diagram fits its panel, stops at natural size, and keeps 16px labels at 11px or larger. Past
that the panel scrolls, and in print the diagram scales to one page. `.diagram` and `.doc-column`
are the page's own classes, not the theme's.

```html
<div class="diagram card">
  <pre class="mermaid">
flowchart LR
  a["Written"]:::ok --> b["Reviewed"]
</pre>
</div>
```

Colour nodes from page CSS, not `classDef`. Mermaid's parser rejects `var()` there, and a dark-theme
`rgba()` wash breaks on its commas. `:::ok` still adds the class, and the tokens follow the theme:

```css
.doc-column {
  min-width: 0; /* the grid or flex column beside the contents rail */
}
.diagram {
  padding: var(--space-4);
  overflow-x: auto;
}
html:not(.no-diagrams) pre.mermaid:not([data-processed]) {
  visibility: hidden;
}
pre.mermaid svg {
  display: block;
  margin-inline: auto;
  height: auto;
  max-width: var(--natural);
  min-width: calc(var(--natural) * 11 / 16);
}
.node.ok :is(rect, path, polygon) {
  fill: var(--success-wash) !important;
  stroke: var(--success) !important;
}
@media print {
  .diagram {
    overflow-x: visible;
    break-inside: avoid;
  }
  pre.mermaid svg {
    min-width: 0;
    max-height: 90vh;
  }
}
```

`themeVariables` also needs real colours, so read each from `getComputedStyle` before
`mermaid.initialize`. If the CDN fails, each panel shows its source text.

```html
<script type="module">
  const mermaid = (
    await import("https://cdn.jsdelivr.net/npm/mermaid@12/dist/mermaid.esm.min.mjs").catch(
      () => null,
    )
  )?.default;
  if (!mermaid) {
    document.documentElement.classList.add("no-diagrams");
  } else {
    const token = (name) =>
      getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    mermaid.initialize({
      startOnLoad: false,
      deterministicIds: true,
      theme: "base",
      flowchart: { useMaxWidth: false, wrappingWidth: 200 },
      themeVariables: {
        background: token("--surface"),
        primaryTextColor: token("--fg"),
        lineColor: token("--fg-muted"),
        clusterBkg: token("--surface-2"),
        clusterBorder: token("--border-strong"),
        titleColor: token("--fg"),
        edgeLabelBackground: token("--surface"),
        fontFamily: token("--font-ui"),
      },
    });
    await document.fonts.ready;
    await mermaid.run();
    document.querySelectorAll("pre.mermaid svg").forEach((s) => {
      s.style.setProperty("--natural", s.viewBox.baseVal.width + "px");
      s.setAttribute("width", "100%");
      s.removeAttribute("height");
    });
  }
</script>
```

## Input as recessed well, auto-growing

- A field inside a card is a **recessed well**: `--bg` fill one rung below its card, hairline
  border, brightening on hover, brand border on focus — visible at rest, never a ghost that only
  appears on hover.
- Free text of unpredictable length is an auto-growing textarea: `field-sizing: content` with a
  one-line min-height and a viewport-relative max, plus `overflow-wrap: anywhere` so an unbroken
  string wraps instead of widening the layout.
- Placeholders are ≤3 words ("add instruction…"); the full explanation goes in the tooltip. A long
  placeholder wraps and forces scrollbars in an empty field.

```html
<td>
  <!-- parent table uses table-layout: fixed -->
  <textarea
    class="input mono"
    placeholder="add instruction…"
    title="optional — blank uses the project's instruction template"
    style="background: var(--bg); font-size: var(--fs-75); field-sizing: content;
                   min-height: 38px; max-height: 40vh; resize: vertical; overflow-wrap: anywhere;"
  ></textarea>
</td>
```
