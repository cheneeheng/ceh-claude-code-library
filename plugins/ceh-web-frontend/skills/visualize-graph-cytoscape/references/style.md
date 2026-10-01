# Stylesheet reference

The stylesheet separates presentation from data. It looks like CSS and is not CSS: it has
its own property names, its own selector language, and it is applied by Cytoscape's
canvas renderer. Browser CSS, CSS custom properties, and DOM classes have no effect on
what is drawn.

## Formats

**JSON (use this)** — an array of `{ selector, style }` blocks, applied in order, later
blocks winning:

```js
style: [
  { selector: "node", style: { "background-color": "#7F77DD" } },
  { selector: "node.important", style: { "border-width": 3 } },
];
```

**String** — `'node { background-color: cyan; }'`. Fine for loading a stylesheet from a
file; awkward otherwise.

**Function chain** — `cy.style().selector('node').style('background-color', 'magenta').update()`.
The trailing `.update()` is required or nothing applies.

Changing style after init:

```js
cy.style().fromJson(newStylesheet).update();     // replace wholesale
cy.style().selector('node').style({ ... }).update();  // append
cy.style().resetToDefault()... // start from the default sheet
cy.style().clear()...          // start from nothing
```

## Colour values

Every colour must be a 3- or 6-digit hex, an `rgb()`/`hsl()` string, or a named colour.
**8-digit hex (`#RRGGBBAA`) is silently rejected** — the property falls back to its
default (`#999` for `background-color`) with no error and no console warning, so an
alpha-suffixed palette renders uniformly grey. Alpha goes in `background-opacity`,
`line-opacity`, `text-opacity` or `border-opacity` instead.

## Mappers

Three ways to make a property depend on the element.

- **`data(field)`** — direct passthrough. `'label': 'data(name)'`.
- **`mapData(field, min, max, minVal, maxVal)`** — linear interpolation, works on numbers
  and colours. `'background-color': 'mapData(score, 0, 100, blue, red)'`. Out-of-range
  values clamp to the extremes.
- **`function(ele){ ... }`** — full control, but you lose the built-in style caching and
  it is measurably slower.

Rules for function mappers, from the docs: return a valid value for every element the
selector matches; depend only on `ele.data()`, `ele.scratch()`, or state that has a
matching selector (`ele.selected()` is fine because `:selected` exists); never mutate the
graph inside one; never read another style property (`ele.style()`) — that creates a
cyclic dependency.

**Guard your mappers with selectors.** If `mapData(weight, ...)` is declared on `node`
but only some nodes have `weight`, you get warnings and undefined behaviour. Scope it:
`{ selector: 'node[weight]', style: { ... } }`.

## Node body

**Shape** — `width`, `height`, `shape`, `shape-polygon-points`, `corner-radius`.

`shape` accepts: `ellipse` `triangle` `round-triangle` `rectangle` `round-rectangle`
`bottom-round-rectangle` `cut-rectangle` `barrel` `rhomboid` `right-rhomboid` `diamond`
`round-diamond` `pentagon` `round-pentagon` `hexagon` `round-hexagon` `concave-hexagon`
`heptagon` `round-heptagon` `octagon` `round-octagon` `star` `tag` `round-tag` `vee`
`polygon`.

Each shape fits inside `width` × `height`, so equilateral shapes need
`width !== height` adjustments. Compound parents support only `*rectangle` shapes,
because a parent's dimensions come from its children's bounding box.

**Background** — `background-color`, `background-blacken` (−1…1), `background-opacity`,
`background-fill` (`solid` | `linear-gradient` | `radial-gradient`),
`background-gradient-stop-colors`, `background-gradient-stop-positions`,
`background-gradient-direction` (`to-bottom` default, `to-top`, `to-left`, `to-right`,
and the four diagonals).

**Border** — `border-width`, `border-style` (`solid` `dotted` `dashed` `double`),
`border-color`, `border-opacity`, `border-cap`, `border-join`, `border-dash-pattern`
(e.g. `[6, 3]`), `border-dash-offset`, `border-position` (`center` | `inside` | `outside`).

**Outline** (outside the border) — `outline-width`, `outline-style`, `outline-color`,
`outline-opacity`, `outline-offset`.

**Padding** — `padding` (px or %), `padding-relative-to` (`width` `height` `average`
`min` `max`). Mainly for spacing compound parents from their children.

**Compound sizing** — `compound-sizing-wrt-labels` (`include` | `exclude`), `min-width`,
`min-height`, `min-width-bias-left`, `min-width-bias-right`, and the height equivalents.

If you set `corner-radius` on a compound parent, children can escape the rounded corner.
Setting `padding` equal to `corner-radius` is always safe.

**Background images** — `background-image` (URL or array), `background-image-opacity`,
`background-width`, `background-height`, `background-fit` (`none` `contain` `cover`),
`background-repeat`, `background-position-x/y`, `background-offset-x/y`,
`background-clip`, `background-image-crossorigin`, `background-image-smoothing`,
`background-image-containment`.

**Pie / stripe charts** — nodes can render a pie or stripe chart as background:
`pie-size`, `pie-i-background-color`, `pie-i-background-size`,
`pie-i-background-opacity` (i from 1 to 16); and the `stripe-*` equivalents.

## Edge line

- `width` — line thickness.
- `curve-style` — **the property that most often needs changing**:
  - `haystack` (default) — straight, bundled, cheapest. **No arrows, no loops, no
    compound support.**
  - `straight` — straight with full arrow support.
  - `straight-triangle` — tapered straight edges.
  - `bezier` — bundled curves; the safe general default when you need arrows.
  - `unbundled-bezier` — curves with manual `control-point-distances` /
    `control-point-weights`.
  - `segments` / `round-segments` — polylines via `segment-distances` /
    `segment-weights`.
  - `taxi` / `round-taxi` — orthogonal right-angled routing, hierarchically bundled.
    Excellent for tree and org-chart looks. Tune with `taxi-direction`
    (`auto` `vertical` `horizontal` `upward` `downward` `leftward` `rightward`),
    `taxi-turn`, `taxi-turn-min-distance`, `taxi-radius`.
- `line-color`, `line-style` (`solid` `dotted` `dashed`), `line-cap`, `line-opacity`,
  `line-fill` (`solid` | `linear-gradient` | `radial-gradient`),
  `line-dash-pattern`, `line-dash-offset` (animate this for "flowing" edges),
  `line-outline-width`, `line-outline-color`.
- `box-selection` — `contain` (default, edge must be fully inside the box), `overlap`,
  or `none`.

**Bezier bundling**: `control-point-step-size` sets how far apart parallel edges bow.
Increase it when multiple edges between the same pair overlap.

**Loops**: `loop-direction`, `loop-sweep`. Not supported on haystack.

## Edge arrows

For each of `source`, `mid-source`, `target`, `mid-target`:

- `<pos>-arrow-color`
- `<pos>-arrow-shape` — `triangle` `triangle-tee` `circle-triangle` `triangle-cross`
  `triangle-backcurve` `vee` `tee` `square` `circle` `diamond` `chevron` `none`
- `<pos>-arrow-fill` — `filled` | `hollow`
- `<pos>-arrow-width` — `match-line`, a number, or a value with units

Plus the global `arrow-scale`.

Only mid arrows work on haystack edges. Set `target-arrow-color` to the same value as
`line-color` unless you deliberately want a two-tone edge — mismatched defaults look
like a bug.

**Edge endpoints** — `source-endpoint` / `target-endpoint` accept `outside-to-node`
(default), `outside-to-node-or-label`, `inside-to-node`, `outside-to-line`, a
`{x} {y}` offset, or a `{deg} {radius}` polar spec. `source-distance-from-node` and
`target-distance-from-node` add a gap between arrowhead and node.

## Labels

**Text** — `label`, `source-label`, `target-label`.

**Font** — `color`, `text-opacity`, `font-family`, `font-size`, `font-style`,
`font-weight`, `text-transform` (`none` `uppercase` `lowercase`).

**Wrapping** — `text-wrap` (`none` | `wrap` | `ellipsis`), `text-max-width`,
`text-overflow-wrap` (`whitespace` default, `anywhere` for CJK), `text-justification`
(`left` `center` `right` `auto`), `line-height`.

To honour only manual `\n` newlines, set `text-wrap: 'wrap'` and
`text-max-width: '1000px'`.

**Alignment** — `text-halign` (`left` `left-inside` `center` `right` `right-inside`),
`text-valign` (`top` `top-inside` `center` `bottom` `bottom-inside`).

`text-valign: 'center'` puts the label inside the node — you must then size the node to
fit the text, since nodes do not auto-size to labels. For variable-length labels,
`text-valign: 'bottom'` with a `text-margin-y` is far more forgiving.

**Offsets & rotation** — `text-margin-x/y`, `source-text-margin-x/y`,
`target-text-margin-x/y`, `source-text-offset`, `target-text-offset`, `text-rotation`
(a number, `none`, or `autorotate` for edges).

**Outline / background / border** — `text-outline-color`, `text-outline-width`,
`text-outline-opacity`; `text-background-color`, `text-background-opacity`,
`text-background-shape` (`rectangle` `round-rectangle` `circle`),
`text-background-padding`; `text-border-color`, `text-border-width`, `text-border-style`,
`text-border-opacity`.

A `text-outline-width: 2` in the background colour is the cheapest way to keep labels
legible over edges.

**Zoom-dependent** — `min-zoomed-font-size` skips rendering labels below a given
on-screen size. Set it (e.g. `8`) on any graph over a few hundred nodes; it is the
single best label-related performance win.

**Interactivity** — `text-events` (`yes` | `no`) controls whether the label area
responds to taps.

## Visibility

- `display`: `element` | `none` — `none` removes the element from layout, hides connected
  edges, excludes it from viewport fitting, and makes it non-interactive.
- `visibility`: `visible` | `hidden` — still occupies space, still counted by layouts and
  fitting, still hides interaction.
- `opacity`: 0–1 — occupies space, does not hide connected edges. A parent's opacity
  multiplies into its children.

For filtering UIs, `display: none` is usually what you want (removes from layout);
for dimming, use `opacity`.

## Interaction feedback

**Overlay** (drawn above) — `overlay-color`, `overlay-padding`, `overlay-opacity`,
`overlay-shape`, `overlay-corner-radius`.
**Underlay** (drawn below) — same properties prefixed `underlay-`. Use underlay for
persistent highlight rings; it does not obscure the node.
**Ghost** — `ghost`, `ghost-offset-x/y`, `ghost-opacity`, for motion trails.

Overlays cannot be cached, so limit how many are visible at once.

## Transitions

```js
{ selector: 'node.highlighted', style: {
    'border-width': 3,
    'transition-property': 'border-width, background-color',
    'transition-duration': '0.2s',
    'transition-timing-function': 'ease-out'
}}
```

`transition-timing-function` accepts `linear` (default), `ease`, `ease-in`, `ease-out`,
`ease-in-out`, the `ease-in-*`/`ease-out-*`/`ease-in-out-*` family (`sine`, `quad`,
`cubic`, `quart`, `quint`, `expo`, `circ`, `back`, `bounce`, `elastic`),
`spring(tension, friction)`, and `cubic-bezier(x1, y1, x2, y2)`.

Declare `transition-property` only in the states you actually want animated. Putting it
in the base `node` block makes the renderer attempt transitions constantly.

## Core properties

Set on a `core` selector: `active-bg-color`, `active-bg-opacity`, `active-bg-size`,
`selection-box-color`, `selection-box-border-color`, `selection-box-border-width`,
`selection-box-opacity`, `outside-texture-bg-color`, `outside-texture-bg-opacity`.

```js
{ selector: 'core', style: {
    'selection-box-color': '#378ADD',
    'selection-box-opacity': 0.15,
    'active-bg-opacity': 0
}}
```

## A sane default stylesheet

Adapt rather than invent. Colours here are placeholders — resolve real ones per
`theming.md`.

```js
const style = [
  {
    selector: "node",
    style: {
      width: 34,
      height: 34,
      "background-color": C.nodeFill,
      "border-width": 1.5,
      "border-color": C.nodeStroke,
      label: "data(label)",
      "font-family": "inherit",
      "font-size": 11,
      color: C.text,
      "text-valign": "bottom",
      "text-margin-y": 5,
      "text-wrap": "ellipsis",
      "text-max-width": "90px",
      "text-outline-width": 2,
      "text-outline-color": C.bg,
      "min-zoomed-font-size": 8,
    },
  },
  {
    selector: "edge",
    style: {
      "curve-style": "bezier",
      width: 1.5,
      "line-color": C.edge,
      "target-arrow-shape": "triangle",
      "target-arrow-color": C.edge,
      "arrow-scale": 0.9,
    },
  },
  {
    selector: "node:selected",
    style: {
      "border-width": 3,
      "border-color": C.accent,
    },
  },
  { selector: ".dimmed", style: { opacity: 0.15 } },
  { selector: ".hidden", style: { display: "none" } },
  {
    selector: ".hot",
    style: {
      "border-color": C.accent,
      "border-width": 3,
      "transition-property": "border-width, border-color",
      "transition-duration": "0.15s",
    },
  },
  {
    selector: "edge.hot",
    style: {
      "line-color": C.accent,
      "target-arrow-color": C.accent,
      width: 3,
      opacity: 1,
    },
  },
  {
    selector: "core",
    style: {
      "selection-box-color": C.accent,
      "selection-box-opacity": 0.12,
      "active-bg-opacity": 0,
    },
  },
];
```

Note `'font-family': 'inherit'` — Cytoscape reads the computed font from the container,
so this keeps labels in the host page's typeface. Custom WOFF fonts must be loaded
_before_ `cytoscape()` is called or they will not be used.
