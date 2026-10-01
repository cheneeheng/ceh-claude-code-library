# Theming and dark mode

## The core constraint

Cytoscape renders to `<canvas>`. The canvas does not participate in CSS cascade. So:

- `var(--my-color)` in a stylesheet value → **does not resolve**, renders as nothing or
  black.
- Tailwind classes, DOM `class` attributes, `:root` variables → **no effect**.
- `prefers-color-scheme` media queries → **no effect on the graph**.

You must resolve every colour to a concrete string (3- or 6-digit hex, `rgb()`, named) in
JavaScript and pass it into the stylesheet.

**Not 8-digit hex.** `'#534AB733'` is valid CSS and invalid here: Cytoscape's parser
rejects it, falls back to the property default (`#999` for `background-color`), logs
nothing, and throws nothing — so a tinted palette built by appending an alpha suffix comes
out uniformly grey. `rgba()` parses, but the alpha is dropped on read-back. Alpha belongs
in the dedicated properties — `background-opacity`, `line-opacity`, `text-opacity`,
`border-opacity` — not in the colour string:

```js
// wrong — silently grey
{ 'background-color': token + '33' }
// right
{ 'background-color': token, 'background-opacity': 0.2 }
```

## Resolving design tokens once

```js
function readTokens(el = document.documentElement) {
  const cs = getComputedStyle(el);
  const v = (name, fallback) => cs.getPropertyValue(name).trim() || fallback;
  return {
    text: v("--text-primary", "#1a1a1a"),
    muted: v("--text-secondary", "#666666"),
    bg: v("--surface-1", "#ffffff"),
    edge: v("--border-strong", "#b4b2a9"),
    accent: v("--accent", "#d85a30"),
  };
}
```

Read from `document.documentElement` if tokens are declared on `:root`, or from the
container element if they are scoped to a subtree.

## Detecting the mode

```js
function isDark() {
  const attr =
    document.documentElement.getAttribute("data-theme") ??
    document.documentElement.getAttribute("data-mode");
  if (attr) return attr === "dark";
  if (document.documentElement.classList.contains("dark")) return true;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}
```

Check the explicit app-level attribute _before_ the media query. An app with a manual
theme toggle set to light on a dark OS must render light.

## A two-mode palette

Define categorical ramps as `{ light, dark }` pairs and pick once at init. Canvas
rendering means you cannot rely on a single colour reading well against both
backgrounds — a fill that is subtle on white is invisible on near-black.

```js
const RAMPS = {
  purple: {
    light: { fill: "#EEEDFE", stroke: "#534AB7" },
    dark: { fill: "#3C3489", stroke: "#AFA9EC" },
  },
  teal: {
    light: { fill: "#E1F5EE", stroke: "#0F6E56" },
    dark: { fill: "#085041", stroke: "#5DCAA5" },
  },
  coral: {
    light: { fill: "#FAECE7", stroke: "#993C1D" },
    dark: { fill: "#712B13", stroke: "#F0997B" },
  },
  gray: {
    light: { fill: "#F1EFE8", stroke: "#5F5E5A" },
    dark: { fill: "#444441", stroke: "#B4B2A9" },
  },
};

function palette() {
  const mode = isDark() ? "dark" : "light";
  const t = readTokens();
  const c = Object.fromEntries(
    Object.entries(RAMPS).map(([k, v]) => [k, v[mode]]),
  );
  return { ...t, ...c, mode };
}
```

Assign colour by **category**, not by sequence. All services one colour, all datastores
another. Rainbow-cycling through node indices carries no information and reads as noise.
Two or three ramps plus grey for structural nodes is almost always enough.

**When the data has more categories than you have ramps** — Terraform resource types,
Kubernetes kinds, and file extensions routinely produce 8-20 — do not reach for more
colours. Past about six, hues stop being distinguishable at node size and the legend
becomes a lookup table nobody reads. Instead:

- **Roll up.** Map the long tail to a handful of meaningful groups: `aws_vpc`,
  `aws_subnet`, `aws_route_table` all become "network". A `GROUPS` map plus an
  `'other'` fallback keeps this honest and readable.
- **Split the encoding.** Colour carries the coarse group (3-4 ramps); `shape` carries a
  second dimension (`ellipse` / `round-rectangle` / `diamond` / `hexagon`), and the exact
  type goes in the label or the tooltip. Two weak channels beat one overloaded one.
- **Colour only what is asked about.** Grey everything, then colour the one category the
  user filtered or hovered. This scales to any number of categories.

Whatever you choose, render a legend — colour without a key is decoration.

## Reacting to a theme change at runtime

The graph will not update itself. Rebuild and apply the stylesheet:

```js
function applyTheme(cy) {
  cy.style().fromJson(buildStylesheet(palette())).update();
}

const mq = window.matchMedia("(prefers-color-scheme: dark)");
mq.addEventListener("change", () => applyTheme(cy));

// for an app-level toggle
new MutationObserver(() => applyTheme(cy)).observe(document.documentElement, {
  attributes: true,
  attributeFilter: ["data-theme", "class"],
});
```

`cy.style().fromJson(...).update()` swaps the whole sheet without touching positions,
zoom, pan, or selection. Do not recreate the instance to change theme.

## Container background

Leave the Cytoscape container's own background to CSS — that part _is_ a normal DOM
element and does respond to variables:

```css
#cy {
  background: var(--surface-1);
  border-radius: 12px;
}
```

Only the drawn elements need JS-resolved colours. One exception: `cy.png({ bg })` needs an
explicit background colour, because the canvas itself is transparent. Passing the
resolved token there keeps exports matching the screen.

## Legibility on canvas

- Give labels `text-outline-width: 2` in the background colour. Without it, labels
  crossing edges become unreadable, and this costs nothing visually.
- Node label text must contrast with the _page_ background, not the node fill, when using
  `text-valign: 'bottom'`. When using `text-valign: 'center'`, it must contrast with the
  node fill — use the darkest stop of the node's own ramp in light mode and the lightest
  in dark mode.
- Edges need less contrast than nodes. A mid-grey that reads as "quiet structure" beats a
  strong line colour that competes with the nodes.
- `min-zoomed-font-size: 8` stops unreadable label mush at low zoom and speeds up
  rendering at the same time.

## Fonts

Cytoscape reads font metrics at init. Two consequences:

- Custom WOFF/WOFF2 fonts must be **loaded before** `cytoscape()` runs, or labels fall
  back. `await document.fonts.ready` before init if you use one.
- `'font-family': 'inherit'` picks up the container's computed font, which keeps the
  graph typographically consistent with the surrounding page.
